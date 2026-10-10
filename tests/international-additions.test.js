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
