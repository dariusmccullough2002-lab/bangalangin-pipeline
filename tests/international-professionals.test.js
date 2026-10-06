import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import {filterProfessionals,professionalProfile,professionalCards} from '../international-professionals.js';
import {buildProfileIndex,findProfiles} from '../home-search.js';
import {publicAssets} from '../scripts/public-assets.js';
const read=p=>JSON.parse(fs.readFileSync(`data/${p}`,'utf8'));
const data=read('international/professionals-2026.json');
test('professional edition has sourced full profiles, unique identities and distinct availability pools',()=>{
 assert.equal(data.players.length,16);
 assert.equal(new Set(data.players.map(p=>p.id)).size,16);
 const ranked=data.players.filter(p=>p.pool==='candidates');
 assert.deepEqual(ranked.map(p=>p.pipelineRank),Array.from({length:12},(_,i)=>i+1));
 assert.equal(data.players.filter(p=>p.pool==='watchlist'&&p.pipelineRank===null).length,4);
 for(const p of data.players){
  assert.ok(p.statusDetail.length>70);
  assert.equal(p.reportSections.length,3);
  assert.ok(p.reportSections.every(s=>s.text.length>350));
  assert.ok(p.sourceIds.every(id=>data.sources.some(s=>s.id===id)));
  assert.ok(p.sourceIds.includes(p.performance.sourceId));
  assert.ok(!p.status.toLowerCase().includes('posted'));
  assert.equal(p.scoutingGrades,undefined);
  const html=professionalProfile(data,p);
  assert.ok(html.includes(p.name));
  assert.ok(html.includes('Native-league performance'));
  for(const [label,value] of Object.entries(p.performance.stats))assert.ok(html.includes(`<span>${label}</span><b>${value}</b>`));
 }
 assert.ok(publicAssets.includes('international-professionals.js'));
 assert.ok(publicAssets.includes('data/international/professionals-2026.json'));
});
test('professional filters handle name aliases, countries, leagues and watchlist',()=>{
 assert.equal(filterProfessionals(data.players,{query:'Noh Si-hwan'})[0].name,'Roh Si-hwan');
 assert.equal(filterProfessionals(data.players,{query:'Livan Moinelo'})[0].name,'Liván Moinelo');
 assert.equal(filterProfessionals(data.players,{league:'KBO'}).length,4);
 assert.equal(filterProfessionals(data.players,{query:'panama',pool:'candidates'})[0].name,'Ariel Jurado');
 assert.equal(filterProfessionals(data.players,{pool:'watchlist'}).length,4);
 assert.equal(filterProfessionals(data.players,{type:'H'}).length,4);
 assert.equal(filterProfessionals(data.players,{query:'no such player'}).length,0);
 assert.equal((professionalCards(data.players).match(/Read full scouting profile/g)||[]).length,16);
});
test('all professional profiles are discoverable in home search without replacing current identities',()=>{
 const current=read('editions/october-2026.json'),archive=read('editions/august-2026.json'),players=read('players.json'),draft=read('draft/2026.json'),intl=read('international/2027.json'),dsl=read('dsl/2026.json');
 const index=buildProfileIndex(current,archive,players,draft,intl,dsl,data);
 for(const p of data.players)assert.ok(findProfiles(index,p.name).some(row=>row.route===`#international-pro-player/${p.id}`));
 assert.ok(findProfiles(index,'Noh Si-hwan').some(row=>row.name==='Roh Si-hwan'));
 assert.ok(findProfiles(index,'Hiromi Ito').some(row=>row.name==='Hiromi Itoh'));
 assert.equal(new Set(index.map(p=>p.route)).size,index.length);
 const duplicate={...data.players[0],mlbamId:current.rankings[0].mlbamId};
 const dedup=buildProfileIndex(current,archive,players,draft,intl,dsl,{players:[duplicate]});
 assert.ok(!dedup.some(p=>p.route===`#international-pro-player/${duplicate.id}`));
});
