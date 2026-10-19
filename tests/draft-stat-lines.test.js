import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {draftOutcomesHtml,draftStatLineHtml} from '../draft-outcomes.js';
const draft=JSON.parse(readFileSync('data/draft/2026.json'));
const rounded=(n,d=3)=>Math.round((n+Number.EPSILON)*10**d)/10**d;
test('all 336 numerical seasons have coherent counts and league-category math',()=>{
 let count=0;
 for(const p of draft.players){
  assert.deepEqual(Object.keys(p.outcomes.statLines).sort(),['ceiling','floor','median']);
  for(const [key,s]of Object.entries(p.outcomes.statLines)){
   count++;assert.equal(s.type,p.type);assert.ok(Object.values(s).every(v=>typeof v!=='number'||Number.isFinite(v)));
   if(s.type==='H'){
    for(const k of ['pa','ab','hits','singles','doubles','triples','homeRuns','runs','rbi','stolenBases','walks','hitByPitch','sacFlies','totalBases'])assert.ok(Number.isInteger(s[k])&&s[k]>=0,`${p.id} ${key} ${k}`);
    assert.equal(s.pa,s.ab+s.walks+s.hitByPitch+s.sacFlies);
    assert.equal(s.hits,s.singles+s.doubles+s.triples+s.homeRuns);
    assert.equal(s.totalBases,s.singles+2*s.doubles+3*s.triples+4*s.homeRuns);
    assert.equal(s.avg,rounded(s.hits/s.ab));assert.equal(s.obp,rounded((s.hits+s.walks+s.hitByPitch)/s.pa));assert.equal(s.slg,rounded(s.totalBases/s.ab));assert.equal(s.ops,rounded(s.obp+s.slg));
    assert.ok(s.avg<=s.obp&&s.avg<=s.slg);assert.ok(s.runs>=s.homeRuns&&s.rbi>=s.homeRuns);
   }else{
    for(const k of ['outs','gamesStarted','earnedRuns','strikeOuts','walks','hitsAllowed','qa3','saves','holds','svh7'])assert.ok(Number.isInteger(s[k])&&s[k]>=0);
    const [whole,part]=s.ip.split('.').map(Number);assert.ok(part<3);assert.equal(s.outs,whole*3+part);
    assert.equal(s.era,rounded(s.earnedRuns*27/s.outs,2));assert.equal(s.whip,rounded((s.hitsAllowed+s.walks)*3/s.outs,2));assert.equal(s.kPerWalk,rounded(s.strikeOuts/s.walks,2));
    assert.equal(s.svh7,s.saves*3+s.holds*2);assert.ok(s.qa3<=s.gamesStarted);assert.ok(s.qa3*15<=s.outs);
    if(s.gamesStarted===0)assert.equal(s.qa3,0);
   }
  }
  const s=p.outcomes.statLines,c=s.ceiling,m=s.median,f=s.floor;
  assert.ok((p.type==='H'?c.pa:c.outs)>=(p.type==='H'?m.pa:m.outs));assert.ok((p.type==='H'?m.pa:m.outs)>=(p.type==='H'?f.pa:f.outs));
  assert.ok(!p.outcomes.statLineBasis.includes('expected 2027'));
 }
 assert.equal(count,336);
});
test('each outcome renders its numbers and preserves the zero-MLB downside distinction',()=>{
 for(const p of draft.players){
  const html=draftOutcomesHtml(p);
  assert.equal((html.match(/scenario stat line/g)||[]).length,3,p.id);
  assert.ok(html.includes('not a 2027 forecast'));assert.ok(html.includes('Complete-bust alternative'));
  if(p.type==='H'){assert.ok(html.includes('0 MLB PA'));assert.ok(html.includes('AVG / OPS —'));assert.ok(html.includes('RBI'));assert.ok(html.includes('SB'));}
  else{assert.ok(html.includes('0 MLB IP'));assert.ok(html.includes('ERA / WHIP / K/BB —'));assert.ok(html.includes('SVH7'));assert.ok(html.includes('QA3'));}
 }
 const w=draft.players.find(p=>p.id==='carson-wiggins');assert.equal(w.outcomes.statLines.ceiling.gamesStarted,30);assert.equal(w.outcomes.statLines.median.gamesStarted,0);assert.equal(w.outcomes.statLines.median.qa3,0);assert.ok(w.outcomes.statLines.median.svh7>0);
 const catcher=draft.players.find(p=>p.id==='vahn-lackey');assert.ok(catcher.outcomes.statLines.ceiling.pa<600);
 const speed=draft.players.find(p=>p.id==='lucas-moore'),power=draft.players.find(p=>p.id==='collin-bland');assert.ok(speed.outcomes.statLines.ceiling.stolenBases>power.outcomes.statLines.ceiling.stolenBases);assert.ok(power.outcomes.statLines.ceiling.homeRuns>speed.outcomes.statLines.ceiling.homeRuns);
 assert.equal(draftStatLineHtml({outcomes:{}},'ceiling'),'');
});
