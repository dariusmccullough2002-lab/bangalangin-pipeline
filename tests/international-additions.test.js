import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import {amateurSearchText,amateurRank,profile} from '../amateurs.js';
const data=JSON.parse(fs.readFileSync('data/international/2027.json'));
test('ranked additions do not invent source ranks or IDs, bonuses, projections or signed organizations',()=>{
 for(const id of ['sebastian-perez-acuna','shoki-oda']){const p=data.players.find(p=>p.id===id);assert.equal(p.consensusRank,null);assert.ok(p.pipelineRank>0);assert.ok(p.ranking.rationale);assert.equal(p.officialOrganization,null);assert.equal(p.mlbamId,null);assert.equal(p.signingBonus,null);assert.equal(p.toolGrades,null);assert.equal(p.projections,null);assert.ok(p.sourceIds.length>=2);for(const sid of p.sourceIds)assert.ok(data.sources.some(s=>s.id===sid));}
 const p=data.players.find(p=>p.id==='sebastian-perez-acuna');assert.equal(p.classYear,2027);assert.equal(p.expectedOrganization,'NYY');assert.match(p.signingStatus,/not official/);assert.equal(p.measurements,null);
 const o=data.players.find(p=>p.id==='shoki-oda');assert.equal(o.classYear,null);assert.equal(amateurRank(o),'#3*');assert.equal(o.ranking.conditional,true);assert.equal(o.expectedOrganization,null);assert.match(amateurSearchText(o),/織田翔希/);assert.equal(o.measurements.weightKg,81);assert.equal(o.measurements.height,'186 cm');
});

test('FYPD editorial insertions preserve missing publication ranks',()=>{const draft=JSON.parse(fs.readFileSync('data/draft/2026.json'));for(const[id,n]of [['anthony-potestio',70],['tyce-armstrong',95]]){const p=draft.players.find(p=>p.id===id);assert.equal(p.pipelineRank,n);assert.equal(p.consensusRank,null);assert.equal(p.consensusScore,null);assert.ok(Object.values(p.sourceRanks).every(x=>x===null));assert.equal(p.actualFypdPick,null);assert.equal(p.ranking.asOf,'2026-10-10');for(const sid of p.ranking.sourceIds)assert.ok(draft.sources.some(s=>s.id===sid));}assert.ok(!draft.players.some(p=>['shoki-oda','sebastian-perez-acuna'].includes(p.id)));});

test('Reyes re-evaluation separates reported contact from verified measurements',()=>{
 const p=data.players.find(p=>p.id==='wilson-reyes');
 assert.equal(p.pipelineRank,10);assert.equal(p.expectedOrganization,'COL');assert.equal(p.officialOrganization,null);
 for(const key of ['measurements','toolGrades','projections','signingBonus','mlbamId'])assert.equal(p[key],null);
 assert.ok(!('seasonStats' in p));assert.deepEqual(p.sourceRanks,{});
 assert.match(p.scoutingParagraphs.join(' '),/not an official K%/);
 assert.match(p.ranking.rationale,/contact.*Rodríguez.*Pérez Acuña/);
 assert.match(p.scoutingParagraphs.join(' '),/Statcast\/Prospect Savant/);
 for(const id of p.sourceIds)assert.ok(data.sources.some(s=>s.id===id));
 assert.match(amateurSearchText(p),/wilson reyes/);
});

test('Oda October 15 announcement preserves route uncertainty and separates amateur samples',()=>{
 const o=data.players.find(p=>p.id==='shoki-oda');
 assert.equal(o.signingStatus,'US-bound / Acquisition route pending');
 assert.equal(o.classLabel,'2027 J15 Candidate — Unconfirmed');
 assert.equal(o.classYear,null);assert.equal(o.officialOrganization,null);assert.equal(o.expectedOrganization,null);
 assert.equal(o.eta,'TBD — unsigned amateur');assert.equal(o.research.asOf,'2026-10-19');
 const text=o.scoutingParagraphs.join(' ');
 for(const pattern of [/American university/,/44.0 IP/,/not independently expose/,/five walks/,/October 22/,/Do not assume the 2027 MLB Draft/,/not average/])assert.match(text,pattern);
 assert.ok(data.sources.some(s=>s.id==='oda-us-announcement'&&s.date==='2026-10-15'));
});

test('Nogami is a signed 2026 international addition, separate from 2027 provisional agreements',()=>{
 const p=data.players.find(p=>p.id==='tatsuya-nogami');assert.equal(p.classYear,2026);assert.equal(p.pipelineRank,15);assert.equal(p.mlbamId,845037);assert.equal(p.officialOrganization,'San Diego Padres');assert.match(p.classLabel,/2026/);assert.match(p.signingStatus,/Officially signed/);
 const pro=JSON.parse(fs.readFileSync('data/international/professionals-2026.json'));assert.ok(!pro.players.some(x=>x.id===p.id));
});

test('all international profiles carry a sourced dated comparison and show uncertainty separately from development risk',()=>{
 assert.equal(data.players.length,19);assert.equal(new Set(data.players.map(p=>p.pipelineRank)).size,19);
 for(const p of data.players){
  assert.equal(p.ranking.asOf,'2026-10-19');assert.ok(p.ranking.rationale.length>150);assert.ok(p.ranking.confidence);assert.equal(p.riskLevel,'Very high');
  assert.ok(p.ranking.sourceIds.length);for(const sid of p.ranking.sourceIds)assert.ok(data.sources.some(s=>s.id===sid));
  const app={innerHTML:'',querySelector:()=>null,querySelectorAll:()=>[]};profile(app,data,'international',p.id);
  assert.ok(app.innerHTML.includes(amateurRank(p)));assert.ok(app.innerHTML.includes('Development risk:'));assert.ok(app.innerHTML.includes('Research confidence'));
  assert.ok(app.innerHTML.includes(p.ranking.confidence));
 }
 assert.equal(data.players.filter(p=>p.classYear===2027).length,17);
 assert.equal(data.players.filter(p=>p.ranking.conditional).length,1);
 const y=data.players.find(p=>p.id==='eudi-yuten');assert.equal(y.ranking.previousRank,9);assert.equal(y.pipelineRank,2);
 const r=data.players.find(p=>p.id==='wilson-reyes');assert.ok(r.sourceIds.includes('rd-u18-roster'));
});
