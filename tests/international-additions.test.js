import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import {amateurSearchText} from '../amateurs.js';
const data=JSON.parse(fs.readFileSync('data/international/2027.json'));
test('unranked additions do not invent IDs, bonuses, projections or signed organizations',()=>{
 for(const id of ['sebastian-perez-acuna','shoki-oda']){const p=data.players.find(p=>p.id===id);assert.equal(p.pipelineRank,null);assert.equal(p.officialOrganization,null);assert.equal(p.mlbamId,null);assert.equal(p.signingBonus,null);assert.equal(p.toolGrades,null);assert.equal(p.projections,null);assert.ok(p.sourceIds.length>=2);for(const sid of p.sourceIds)assert.ok(data.sources.some(s=>s.id===sid));}
 const p=data.players.find(p=>p.id==='sebastian-perez-acuna');assert.equal(p.classYear,2027);assert.equal(p.expectedOrganization,'NYY');assert.match(p.signingStatus,/not official/);assert.equal(p.measurements,null);
 const o=data.players.find(p=>p.id==='shoki-oda');assert.equal(o.classYear,null);assert.equal(o.expectedOrganization,null);assert.match(amateurSearchText(o),/織田翔希/);assert.equal(o.measurements.weightKg,81);assert.equal(o.measurements.height,'186 cm');
});
