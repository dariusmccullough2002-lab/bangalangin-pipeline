import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import {aflInlineStats,aflParticipant,aflCard,aflResources,loadAfl} from '../afl.js';
const data=JSON.parse(fs.readFileSync('data/afl/2026.json'));
const october=JSON.parse(fs.readFileSync('data/editions/october-2026.json')).rankings;
const draft=JSON.parse(fs.readFileSync('data/draft/2026.json')).players;
test('reviewed AFL participants match unique existing identities and organizations',()=>{
 assert.equal(data.players.length,30);
 assert.equal(new Set(data.players.map(p=>p.mlbamId)).size,30);
 assert.equal(october.filter(p=>aflParticipant(p,data)).length,29);
 assert.equal(draft.filter(p=>aflParticipant(p,data)).length,1);
 for(const row of data.players){
  const p=[...october,...draft].find(p=>p.mlbamId===row.mlbamId);
  assert.equal(aflParticipant(p,data),row);
  assert.match(row.sourceUrl,/^https:\/\/statsapi\.mlb\.com\/api\/v1\/teams\/\d+\/roster\?rosterType=fullRoster&season=2026&hydrate=person$/);
  if(row.prospectRankUrl)assert.equal(Number(new URL(row.prospectRankUrl).pathname.split('mlb_')[1]),row.mlbamId);
 }
});
test('ambiguous names, missing IDs and mismatched identities never receive AFL cards',()=>{
 const p=october.find(p=>p.mlbamId===806964);
 for(const change of [{mlbamId:null},{mlbamId:'806964'},{mlbamId:-1},{name:'Sebastian Walcot'},{mlbOrg:'SEA'},{type:'P'}])assert.equal(aflCard({...p,...change},data),'');
 assert.equal(aflCard(p,{...data,season:2025}),'');
 assert.equal(aflCard({name:p.name,mlbOrg:p.mlbOrg,type:p.type},data),'');
 assert.equal(aflCard(october.find(p=>!data.players.some(r=>r.mlbamId===p.mlbamId)),data),'');
});
test('cards distinguish verified player stats from the pitcher board fallback',()=>{
 const hitter=aflCard(october.find(p=>p.mlbamId===806964),data);
 const pitcher=aflCard(october.find(p=>p.mlbamId===703186),data);
 assert.ok(hitter.includes('Surprise Saguaros'));
 assert.ok(hitter.includes('https://www.prospect-portfolio.com/player/mlb_806964'));
 assert.ok(hitter.includes('Checked 2026-10-08'));
 assert.ok(hitter.includes('Underlying AFL data · Search Sebastian Walcott'));
 assert.ok(hitter.includes('https://pitchiq.prospecttilt.com/#v=afl'));
 assert.ok(pitcher.includes('Hitter tracker; no verified pitcher-specific AFL page'));
 assert.ok(pitcher.includes('href="https://www.prospect-portfolio.com/afl"'));
 for(const html of [hitter,pitcher,aflResources()]){
  for(const a of html.matchAll(/<a\b[^>]*>/g))if(a[0].includes('href="https://'))assert.ok(a[0].includes('target="_blank" rel="noopener noreferrer"'));
 }
});
test('AFL source failure does not reject profile loading',async()=>{
 const original=globalThis.fetch;
 try{globalThis.fetch=async()=>{throw Error('Unavailable')};await assert.doesNotReject(loadAfl());}
 finally{globalThis.fetch=original;}
});

test('inline AFL statistics distinguish hitters, pitchers and missing samples',()=>{
 const h=aflInlineStats({type:'H'},{plateAppearances:12,avg:'.700',obp:'.750',slg:'1.200',homeRuns:1,stolenBases:1,strikeOuts:2,baseOnBalls:2,ops:'1.950'});
 assert.ok(h.includes('12 PA'));assert.ok(h.includes('16.7%'));assert.ok(h.includes('Early hot start · small sample'));
 const p=aflInlineStats({type:'P'},{inningsPitched:'2.1',era:'0.00',strikeOuts:4,baseOnBalls:0,battersFaced:8});assert.ok(p.includes('2.1 IP'));assert.ok(p.includes('50.0%'));
 assert.ok(aflInlineStats({type:'H'},null).includes('No recorded AFL sample'));
 assert.ok(aflCard(october.find(p=>p.mlbamId===806964),data).includes('data-afl-id="806964"'));
});
