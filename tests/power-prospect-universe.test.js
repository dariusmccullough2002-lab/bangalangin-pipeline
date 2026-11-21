import test from 'node:test';import assert from 'node:assert/strict';import {readFileSync} from 'node:fs';import {gunzipSync} from 'node:zlib';
const read=name=>JSON.parse(gunzipSync(readFileSync(new URL('../data/research/'+name+'.json.gz',import.meta.url))));
const catalog=read('power-prospect-catalog'),panel=read('power-prospect-records');
test('expanded directory covers every requested level and preserves MLB identity',()=>{
 assert.ok(catalog.players.length>10000);assert.equal(new Set(catalog.players.map(p=>p.mlbamId)).size,catalog.players.length);
 assert.equal(catalog.sources.filter(s=>s.provider==='MLB Stats API').length,5);assert.equal(catalog.sources.filter(s=>s.provider==='Prospect Savant').length,15);
 for(const name of ['Xavier Neyens','Emil Morales','Ethan Holliday','Cris Rodriguez','Yostin Pena','Owen Ayers','Cristian Arguelles','Franklin Primera','Kevin Alvarez']){const clean=s=>s.normalize('NFD').replace(/[\u0300-\u036f]/g,'').toLowerCase();assert.ok(catalog.players.some(p=>[p.name,...p.aliases].some(n=>clean(n)===clean(name))),name);}
 for(const p of catalog.players){assert.ok(Number.isInteger(p.mlbamId)&&p.mlbamId>0);assert.ok(p.name.length>0);}
});
test('source-aware masks preserve unavailable metrics rather than fabricating zero impact',()=>{
 const ps=panel.records.filter(p=>p.source==='Prospect Savant');
 for(const p of ps.filter(p=>['AA','High-A','DSL (Rookie)','A (Carolina / California)'].includes(p.level))){assert.equal(p.hard_hit,null,p.id);assert.equal(p.barrel,null,p.id);assert.equal(p.adequate,false);}
 const neyens=ps.find(p=>p.mlbamId===815832&&p.year===2026&&p.level==='High-A');assert.ok(neyens.chase>0&&neyens.whiff>0);assert.equal(neyens.hard_hit,null);assert.equal(neyens.sourceReportedMetrics.hard_hit,0);
 const matos=ps.find(p=>p.mlbamId===837864&&p.year===2026);assert.equal(matos.level,'DSL (Rookie)');assert.ok(matos.chase>0&&matos.whiff>0);assert.equal(matos.barrel,null);
 const morales=ps.find(p=>p.mlbamId===815896&&p.year===2025&&p.level==='Complex (Rookie)');assert.equal(morales.hard_hit,66.7);assert.equal(morales.barrel,0);assert.equal(morales.adequate,false);
});
test('records never pool levels/providers and sample guards reject missing denominators',()=>{
 assert.equal(new Set(panel.records.map(p=>p.id)).size,panel.records.length);
 assert.equal(new Set(panel.records.map(p=>`${p.mlbamId}|${p.year}|${p.level}`)).size,panel.records.length);
 assert.ok(panel.records.length>13000);assert.ok(panel.records.filter(p=>p.adequate).length>2000);
 const ids=new Set(catalog.players.map(p=>p.mlbamId));
 for(const p of panel.records){assert.ok(ids.has(p.mlbamId));assert.ok([2024,2025,2026].includes(p.year));assert.ok(['Baseball Savant','Prospect Savant'].includes(p.source));assert.ok(p.sourceUrl.startsWith('https://'));for(const k of ['chase','whiff','hard_hit','barrel'])assert.ok(p[k]===null||Number.isFinite(p[k])&&p[k]>=0&&p[k]<=100);if(p.adequate)assert.ok(p.complete&&p.pa>=100&&p.swings>=100&&p.outsidePitches>=100&&p.trackedBBE>=50);for(const k of ['probability','mlbEquivalent','officialGrade','rank'])assert.equal(k in p,false);}
});
test('official snapshots take priority without borrowing metrics from the PS snapshot',()=>{
 const tibbs=panel.records.find(p=>p.mlbamId===696486&&p.year===2026&&p.level==='AAA');assert.equal(tibbs.source,'Baseball Savant');assert.equal(tibbs.pa,643);assert.equal(tibbs.hard_hit,48.40425531914894);
 assert.ok(panel.records.some(p=>p.level==='Complex (Rookie)'));assert.ok(panel.records.some(p=>p.level==='DSL (Rookie)'));assert.ok(panel.records.some(p=>p.level==='High-A'));assert.ok(panel.records.some(p=>p.level==='AA'));
 assert.ok(catalog.players.some(p=>p.isPitcher));
});
