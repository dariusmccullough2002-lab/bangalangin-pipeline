import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
const read=p=>JSON.parse(readFileSync(p));
const reports=read('data/profile-reports.json'),coverage=read('docs/rescout-20261018/Coverage.json');
test('research coverage distinguishes completed reports from the remaining full-site scope',()=>{
 assert.equal(coverage.uniquePlayers,649);assert.equal(coverage.profileEntries,695);
 assert.equal(coverage.completedUniquePlayers,12);assert.equal(coverage.pendingUniquePlayers,637);
 assert.equal(Object.values(coverage.players).filter(p=>p.status==='individual research complete').length,12);
 for(const[id,key]of Object.entries(reports.byMlbam)){
  const p=reports.profiles[key];assert.equal(p.mlbamId,Number(id));assert.equal(p.reviewedAsOf,'2026-10-18');
  assert.equal(p.paragraphs.length,3);assert.ok(p.sources.length>=2);assert.ok(p.sources.every(s=>s.url.startsWith('https://')));
  assert.match(p.context,/Source dates remain separate/);
 }
 assert.match(reports.profiles[reports.byMlbam['815888']].paragraphs[0],/right-shoulder surgery/);
 assert.match(reports.profiles[reports.byMlbam['815896']].paragraphs.join(' '),/secondary pitches.*2029/s);
 assert.match(reports.profiles[reports.byMlbam['806964']].paragraphs[0],/bat-angle adjustment/);
});
test('revised profiles render dated source links and preserve authoritative player identities',async()=>{
 const old=global.fetch;global.fetch=async path=>({ok:true,json:async()=>path.includes('transactions')?read('data/transactions.json'):reports});
 try{
  const history=await import('../profile-history.js');await history.loadProfileHistory();
  const {prospectReport}=await import('../profile-context.js');
  const id=reports.byMlbam['815896'],record=history.refinedReport({mlbamId:815896});
  assert.equal(record,reports.profiles[id]);assert.equal(history.refinedReport({playerId:'unknown',mlbamId:815896}),undefined);
  const html=prospectReport({playerId:id,mlbamId:815896,name:'Emil Morales'});
  assert.match(html,/Scouting review sources · 2026-10-18/);assert.match(html,/baseballsavant\.mlb\.com/);assert.match(html,/noopener noreferrer/);
 }finally{global.fetch=old;}
});
