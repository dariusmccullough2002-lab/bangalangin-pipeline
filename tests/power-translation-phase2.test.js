import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {createHash} from 'node:crypto';
import {benchmarkSample,risk} from '../power-translation-math.js';
const read=f=>JSON.parse(readFileSync(new URL('../'+f,import.meta.url)));
const d=read('data/research/power-translation-v1.json');
test('25-point display retains selection, references and extremes without changing source',()=>{
 for(const year of ['all',2024,2025,2026]){
  const rows=d.seasons.filter(p=>p.qualified&&(year==='all'||p.year===year)),copy=JSON.stringify(rows),selected=rows.at(-1),sample=benchmarkSample(rows,selected,d.model);
  assert.equal(sample.length,25);assert.equal(new Set(sample.map(p=>p.id)).size,25);assert.ok(sample.some(p=>p.id===selected.id));
  assert.equal(JSON.stringify(rows),copy);assert.deepEqual(sample,benchmarkSample(rows,selected,d.model));
  for(const fn of [p=>risk(p,d.model),p=>p.hard_hit]){assert.equal(Math.min(...sample.map(fn)),Math.min(...rows.map(fn)));assert.equal(Math.max(...sample.map(fn)),Math.max(...rows.map(fn)));}
 }
 assert.equal(benchmarkSample(d.seasons.slice(0,3),d.seasons[0],d.model).length,3);
 assert.equal(benchmarkSample([],null,d.model).length,0);
});
test('MiLB records are observed same-season level panels and never get MLB outputs',()=>{
 const data=read('data/research/power-translation-minor.json'),coverage=read('data/research/power-translation-coverage.json');
 assert.equal(data.records.length,58);assert.equal(data.records.filter(p=>p.adequate).length,52);assert.equal(new Set(data.records.filter(p=>p.adequate).map(p=>p.mlbamId)).size,46);
 assert.equal(new Set(data.records.map(p=>p.id)).size,data.records.length);assert.equal(data.sources.length,12);assert.equal(data.errors.length,0);
 for(const s of data.sources){const content=readFileSync(new URL('../'+s.file,import.meta.url));assert.equal(createHash('sha256').update(content).digest('hex'),s.sha256);const u=new URL(s.url);assert.equal(u.searchParams.get('hfGT'),'R|');assert.equal(u.searchParams.get('hfSea'),s.year+'|');assert.equal(u.searchParams.get('minors'),'true');assert.equal(u.searchParams.has('type'),false);if(s.outsideZoneOnly)assert.equal(u.searchParams.get('hfZ'),'11|12|13|14|');}
 for(const p of data.records){assert.ok(coverage.players.some(x=>x.mlbamId===p.mlbamId));assert.ok(['AAA','FSL A'].includes(p.level));for(const k of ['chase','whiff','hard_hit','barrel'])assert.ok(p[k]===null||Number.isFinite(p[k])&&p[k]>=0&&p[k]<=100);for(const k of ['probability','score','endpoint','mlbEquivalent'])assert.equal(k in p,false);if(p.adequate){assert.ok(p.complete&&p.pa>=100&&p.swings>=100&&p.outsidePitches>=100&&p.trackedBBE>=50);}}
});
test('Phase 2 remains experimental with explicit reused-test and attrition limits',()=>{
 const p=read('data/research/phase2/summary.json');assert.equal(p.candidateTests,900);assert.match(p.status,/no model promotion/);assert.match(p.design,/Reused Phase 1/);assert.equal(p.primary.length,15);assert.equal(p.rolling.length,84);assert.ok(p.limitations.some(x=>x.includes('attrition')));for(const r of p.primary){assert.equal(r.n,409);assert.ok(r.auc>=0&&r.auc<=1&&r.brier>=0&&r.brier<=1);}assert.ok(p.calibration.every(m=>m.buckets.reduce((s,b)=>s+b.n,0)===409));
});
