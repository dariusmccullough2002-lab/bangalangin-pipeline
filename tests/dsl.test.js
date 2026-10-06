import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import {resolveDslProfile} from '../dsl-profiles.js';
import {buildProfileIndex,findProfiles} from '../home-search.js';
const read=p=>JSON.parse(fs.readFileSync(`data/${p}`,'utf8'));
const dsl=read('dsl/2026.json'),current=read('editions/october-2026.json'),orgs=read('organizations.json'),snapshot=read('ownership-snapshots/2026-10-06.json');
const index=buildProfileIndex(current,read('editions/august-2026.json'),read('players.json'),read('draft/2026.json'),read('international/2027.json'),dsl);
test('all 35 DSL identities resolve once in homepage search, preserving existing profiles',()=>{
 assert.equal(dsl.players.length,35);
 assert.equal(new Set(dsl.players.map(p=>p.mlbamId)).size,35);
 assert.equal(dsl.players.filter(p=>resolveDslProfile(p,current).current).length,15);
 for(const p of dsl.players){
  const resolved=resolveDslProfile(p,current,orgs);
  const found=index.filter(r=>r.route===resolved.route);
  assert.equal(found.length,1,p.name);
  assert.ok(findProfiles(index,p.name.split(' ')[0]).some(r=>r.route===resolved.route),p.name);
  if(p.existingProfileId)assert.equal(resolved.current.playerId,p.existingProfileId);
  else assert.equal(resolved.owner,'BangaLangin free agent');
 }
 assert.equal(index.filter(r=>r.route.startsWith('#dsl-player/')).length,20);
 // The Cardinals catcher and Milwaukee shortstop have several namesakes.
 assert.equal(dsl.players.find(p=>p.name==='Sebastian Rojas').mlbamId,837943);
 assert.equal(dsl.players.find(p=>p.name==='Jose Rodriguez').mlbamId,836624);
});
test('claimed ownership comes from unique reviewed identities, never fuzzy names',()=>{
 for(const p of dsl.players.filter(p=>p.existingProfileId)){
  const resolved=resolveDslProfile(p,current,orgs);
  assert.notEqual(resolved.owner,'BangaLangin free agent');
  assert.ok(snapshot.teams.some(t=>t.players.some(r=>`fantrax-${r.fantraxId}`===resolved.current.playerId)));
 }
 const p=dsl.players[0];
 assert.equal(resolveDslProfile(p,{rankings:[{name:p.name,mlbamId:12345,playerId:'wrong'}]}).current,null);
 assert.equal(resolveDslProfile(p,{rankings:[{mlbamId:p.mlbamId},{mlbamId:p.mlbamId}]}).current,null);
 assert.equal(resolveDslProfile({...p,fantasyOrganizationId:'epskenes-island'},null,orgs).owner,'Island');
});
test('every new profile has individual scouting, risks, outlook, counts and evidence',()=>{
 const text=new Set();
 for(const p of dsl.players.filter(p=>!p.existingProfileId)){
  assert.equal(p.reportSections.length,3,p.name);
  assert.ok(p.reportSections.map(s=>s.text).join(' ').split(/\s+/).length>=150,p.name);
  assert.ok(p.scoutingSources.length);
  assert.ok(p.performanceSummary);
  assert.ok(p.seasonStats.groups.length);
  assert.ok(p.seasonStats.splits.length);
  assert.ok(p.identity.birthDate);
  assert.ok(!text.has(p.reportSections[0].text));text.add(p.reportSections[0].text);
  for(const g of p.seasonStats.groups){
   const denominator=g.group==='hitting'?g.pa:g.battersFaced;
   assert.equal(g.kPercent,Math.round(g.strikeOuts/denominator*1000)/10);
   assert.equal(g.bbPercent,Math.round(g.walks/denominator*1000)/10);
  }
 }
 assert.equal(dsl.players.find(p=>p.baRank===32).name,'Angel Salio');
 assert.equal(dsl.players.find(p=>p.baRank===33).name,'Carlos Vielma');
});
test('all 20 unclaimed routes render complete profiles with verified Savant identities',async()=>{
 const fetchBefore=globalThis.fetch;
 globalThis.fetch=async()=>({ok:true,json:async()=>dsl});
 try{
  const {showDsl}=await import('../dsl.js');
  for(const p of dsl.players.filter(p=>!p.existingProfileId)){
   const app={innerHTML:''};await showDsl(app,'dsl-player',p.id,[],current,orgs);
   assert.ok(app.innerHTML.includes(p.name));
   assert.ok(app.innerHTML.includes('Dynasty outlook'));
   assert.ok(app.innerHTML.includes('Performance evidence'));
   assert.ok(app.innerHTML.includes(`https://prospectsavant.com/player/${p.mlbamId}`));
   assert.ok(app.innerHTML.includes('BangaLangin free agent'));
   assert.ok(!app.innerHTML.includes('href="https://www.baseballamerica.com'));
  }
 }finally{globalThis.fetch=fetchBefore;}
});
