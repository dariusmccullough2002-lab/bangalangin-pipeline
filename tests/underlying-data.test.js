import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import {underlyingDataSection} from '../profile-context.js';
const full=JSON.parse(fs.readFileSync('data/afl/full-2026.json'));
test('all matched profile identities receive one safe Savant destination in the shared section',()=>{
 for(const file of ['editions/october-2026','draft/2026','dsl/2026','afl/full-2026','international/2027','international/professionals-2026']){
  const d=JSON.parse(fs.readFileSync('data/'+file+'.json'));
  for(const p of d.rankings??d.players){
   const html=underlyingDataSection(p);
   assert.equal((html.match(/aria-label="Underlying Data"/g)??[]).length,1);
   if(p.mlbamId)assert.equal((html.match(new RegExp('https://prospectsavant.com/player/'+p.mlbamId,'g'))??[]).length,1,p.name);
   else {assert.match(html,/Prospect Savant link unavailable/);assert.ok(!html.includes('prospectsavant.com/player/'));}
   for(const a of html.matchAll(/<a\b[^>]*>/g))assert.match(a[0],/target="_blank" rel="noopener noreferrer"/);
  }
 }
});
test('AFL research follows general data and retains only verified player-profile URLs',()=>{
 for(const p of full.players){
  const html=underlyingDataSection(p,{aflRoster:full,aflPlayer:p});
  assert.ok(html.indexOf('Prospect Savant data')<html.indexOf('Underlying AFL Data'));
  assert.match(html,/https:\/\/pitchiq.prospecttilt.com\/#v=afl/);
  assert.ok(html.includes('prospect-portfolio.com/player/mlb_'+p.mlbamId)||html.includes('ProspectRank player profile unavailable'));
 }
 const p=full.players[0];
 assert.ok(!underlyingDataSection(p,{aflRoster:{...full,players:[p,p]},aflPlayer:p}).includes('Underlying AFL Data'));
 assert.ok(!underlyingDataSection(p).includes('Underlying AFL Data'));
});
test('every profile renderer uses the shared section and contextual help stays in place',()=>{
 for(const file of ['app.js','october.js','amateurs.js'])assert.match(fs.readFileSync(file,'utf8'),/\$\{profileUnderlyingData\(/);
 for(const file of ['dsl.js','afl-board.js','international-professionals.js'])assert.match(fs.readFileSync(file,'utf8'),/\$\{underlyingDataSection\(/);
 assert.match(fs.readFileSync('profile-polish.js','utf8'),/keepInPlace='\.profile-underlying-data/);
});
