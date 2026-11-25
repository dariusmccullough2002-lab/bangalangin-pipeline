import test from 'node:test';import assert from 'node:assert/strict';import fs from 'node:fs';
const data=JSON.parse(fs.readFileSync('data/international/2027.json')),rows=data.players,by=id=>rows.find(p=>p.id===id);
test('all retained profiles have independent dynasty and talent ranks; BA source ranks remain separate',()=>{
 assert.equal(rows.length,86);assert.equal(new Set(rows.map(p=>p.id)).size,86);for(const field of ['pipelineRank','pipelineTalentRank','pipelineDynastyRank'])assert.deepEqual(rows.map(p=>p[field]).sort((a,b)=>a-b),Array.from({length:86},(_,i)=>i+1));
 assert.ok(rows.every(p=>p.pipelineDynastyRank===p.pipelineRank));assert.deepEqual(rows.filter(p=>p.baBonusRank).map(p=>p.baBonusRank).sort((a,b)=>a-b),Array.from({length:50},(_,i)=>i+1));
 assert.equal(by('jose-tarifa').pipelineRank,4);assert.equal(by('jose-tarifa').baBonusRank,19);assert.equal(by('jose-tarifa').researchTalentRank,7);assert.equal(by('shoki-oda').pipelineTalentRank,3);
 const supplied=rows.filter(p=>p.researchDynastyRank&&p.id!=='shoki-oda');assert.deepEqual([...supplied].sort((a,b)=>a.pipelineRank-b.pipelineRank).map(p=>p.id),[...supplied].sort((a,b)=>a.researchDynastyRank-b.researchDynastyRank).map(p=>p.id));
 for(const id of ['yoel-king','ashton-hernandez'])assert.equal(by(id).independentReview.omittedFromSupplied58,true);
});
test('Oda route uncertainty is separate from dynasty value; watches do not acquire eligibility through rank',()=>{
 const p=by('shoki-oda');assert.equal(p.pipelineRank,5);assert.equal(p.routeRiskPenalty,0);assert.equal(p.researchDynastyRank,7);assert.equal(p.baBonusRank,null);assert.equal(p.expectedOrganization,null);assert.match(p.ranking.rationale,/first-round|pitching ceiling/);assert.ok(p.sourceIds.includes('oda-fangraphs-first-round-20261106'));assert.ok(p.rankingHistory.length);
 const y=by('yeremy-de-leon');assert.equal(y.fypdEligibility,'pending-league-confirmation');assert.equal(y.actualSigningPeriod,2026);assert.equal(y.classYear,2027);
});
