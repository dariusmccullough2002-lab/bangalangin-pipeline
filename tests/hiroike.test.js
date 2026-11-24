import test from 'node:test';import assert from 'node:assert/strict';import fs from 'node:fs';
import {internationalUpdateHtml,amateurSearchText,internationalAge,internationalStatus} from '../amateurs.js';
const data=JSON.parse(fs.readFileSync(new URL('../data/international/2027.json',import.meta.url))),p=data.players.find(p=>p.id==='kosei-hiroike');
test('Hiroike is one independently ranked collegiate amateur with provisional eligibility',()=>{
 assert.equal(data.players.filter(x=>x.id===p.id).length,1);assert.equal(p.pipelineRank,24);assert.equal(internationalAge(p,'2026-11-24').label,'22');assert.equal(p.officialOrganization,null);assert.equal(p.fypdEligibility,'provisional');assert.match(internationalStatus(p).label,/pending/i);assert.match(amateurSearchText(p),/広池浩成/);assert.equal(p.signingEvidence.actualSigningDate,null);assert.deepEqual(data.players.map(p=>p.pipelineRank),Array.from({length:data.players.length},(_,i)=>i+1));
});
test('Published evidence keeps rate denominators, peak context and uncertainty explicit',()=>{
 const html=internationalUpdateHtml(p,data);for(const text of ['30.8%','10.6%','not a conventional BB%','bullpen','Physical Pending','Pitch arsenal','Developmental outcomes','2029–2030','provisionally'])assert.ok(html.includes(text),text);assert.ok(!html.includes('undefined'));for(const id of p.sourceIds)assert.ok(data.sources.some(s=>s.id===id));assert.equal(p.toolGrades,null);assert.equal(p.projections,null);
 assert.equal((51*9/44).toFixed(2),'10.43');assert.equal((13*9/44).toFixed(2),'2.66');assert.equal((32/104*100).toFixed(1),'30.8');assert.equal((11/104*100).toFixed(1),'10.6');
});
