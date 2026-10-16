import {createHash} from 'node:crypto';
import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import {amateurSearchText,amateurRank} from '../amateurs.js';
const data=JSON.parse(fs.readFileSync('data/international/2027.json'));
test('ranked additions do not invent source ranks or IDs, bonuses, projections or signed organizations',()=>{
 for(const id of ['sebastian-perez-acuna','shoki-oda']){const p=data.players.find(p=>p.id===id);assert.equal(p.consensusRank,null);assert.ok(p.pipelineRank>0);assert.ok(p.ranking.rationale);assert.equal(p.officialOrganization,null);assert.equal(p.mlbamId,null);assert.equal(p.signingBonus,null);assert.equal(p.toolGrades,null);assert.equal(p.projections,null);assert.ok(p.sourceIds.length>=2);for(const sid of p.sourceIds)assert.ok(data.sources.some(s=>s.id===sid));}
 const p=data.players.find(p=>p.id==='sebastian-perez-acuna');assert.equal(p.classYear,2027);assert.equal(p.expectedOrganization,'NYY');assert.match(p.signingStatus,/not official/);assert.equal(p.measurements,null);
 const o=data.players.find(p=>p.id==='shoki-oda');assert.equal(o.classYear,null);assert.equal(amateurRank(o),'#2*');assert.equal(o.ranking.conditional,true);assert.equal(o.expectedOrganization,null);assert.match(amateurSearchText(o),/織田翔希/);assert.equal(o.measurements.weightKg,81);assert.equal(o.measurements.height,'186 cm');
});

test('FYPD editorial insertions preserve missing publication ranks',()=>{const draft=JSON.parse(fs.readFileSync('data/draft/2026.json'));for(const[id,n]of [['anthony-potestio',70],['tyce-armstrong',95]]){const p=draft.players.find(p=>p.id===id);assert.equal(p.pipelineRank,n);assert.equal(p.consensusRank,null);assert.equal(p.consensusScore,null);assert.ok(Object.values(p.sourceRanks).every(x=>x===null));assert.equal(p.actualFypdPick,null);assert.equal(p.ranking.asOf,'2026-10-10');for(const sid of p.ranking.sourceIds)assert.ok(draft.sources.some(s=>s.id===sid));}assert.ok(!draft.players.some(p=>['shoki-oda','sebastian-perez-acuna'].includes(p.id)));});

test('Reyes addition preserves prior profiles and separates reports from measurements',()=>{
 const prior=data.players.filter(p=>!['wilson-reyes','shoki-oda',...['kendry-morales','luis-garcia-nicaragua-2027','enyel-gonzalez','erick-gonzalez-nicaragua-2027']].includes(p.id));
 assert.equal(createHash('sha256').update(JSON.stringify(prior)).digest('hex'),'244bb5d9bff0276bd5f88b75ee5e57417be0f3ec2d2d3c28b729c08692fe019a');
 const p=data.players.find(p=>p.id==='wilson-reyes');
 assert.equal(p.pipelineRank,14);assert.equal(p.expectedOrganization,'COL');assert.equal(p.officialOrganization,null);
 for(const key of ['measurements','toolGrades','projections','signingBonus','mlbamId'])assert.equal(p[key],null);
 assert.ok(!('seasonStats' in p));assert.deepEqual(p.sourceRanks,{});
 assert.match(p.scoutingParagraphs.join(' '),/not an official K%/);
 assert.match(p.ranking.rationale,/Quintero.*Fortunato.*Pérez Acuña/);
 assert.match(p.scoutingParagraphs.join(' '),/Statcast\/Prospect Savant/);
 for(const id of p.sourceIds)assert.ok(data.sources.some(s=>s.id===id));
 assert.match(amateurSearchText(p),/wilson reyes/);
});

test('Oda October 15 announcement preserves route uncertainty and separates amateur samples',()=>{
 const o=data.players.find(p=>p.id==='shoki-oda');
 assert.equal(o.signingStatus,'US-bound / Acquisition route pending');
 assert.equal(o.classLabel,'2027 J15 Candidate — Unconfirmed');
 assert.equal(o.classYear,null);assert.equal(o.officialOrganization,null);assert.equal(o.expectedOrganization,null);
 assert.equal(o.eta,'TBD — unsigned amateur');assert.equal(o.research.asOf,'2026-10-15');
 const text=o.scoutingParagraphs.join(' ');
 for(const pattern of [/American university/,/44.0 IP/,/not independently expose/,/five walks/,/October 22/,/Do not assume the 2027 MLB Draft/,/not average/])assert.match(text,pattern);
 assert.ok(data.sources.some(s=>s.id==='oda-us-announcement'&&s.date==='2026-10-15'));
});
