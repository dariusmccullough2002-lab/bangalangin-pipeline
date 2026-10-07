import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import {aflSignal,indexAflStats,inningsToOuts,filterAflPlayers,aflProfileHtml} from '../afl-board.js';
import {buildProfileIndex,findProfiles} from '../home-search.js';
const read=f=>JSON.parse(fs.readFileSync(f));
const data=read('data/afl/full-2026.json'),cur=read('data/editions/october-2026.json'),archive=read('data/editions/august-2026.json'),players=read('data/players.json'),draft=read('data/draft/2026.json'),dsl=read('data/dsl/2026.json'),intl=read('data/international/2027.json'),pro=read('data/international/professionals-2026.json');
test('full official AFL roster resolves once and preserves existing profile identities',()=>{
 assert.equal(data.players.length,251);assert.equal(new Set(data.players.map(p=>p.mlbamId)).size,251);assert.equal(new Set(data.players.map(p=>p.aflTeamId)).size,6);
 assert.equal(data.players.filter(p=>p.hasExistingProfile).length,30);
 const index=buildProfileIndex(cur,archive,players,draft,intl,dsl,pro,data);
 for(const p of data.players){const matches=findProfiles(index,p.name).filter(x=>x.name===p.name);assert.equal(matches.length,1,p.name);assert.equal(matches[0].route,p.route);assert.ok(p.status);assert.match(p.sourceUrl,/statsapi\.mlb\.com/);}
 for(const id of [695722,702607]){const p=data.players.find(p=>p.mlbamId===id);assert.equal(p.hasExistingProfile,false);assert.equal(p.route,`#afl-player/${id}`);}
});
test('new AFL profiles contain sourced reports and separate regular-season and fall data',()=>{
 for(const p of data.players.filter(p=>!p.hasExistingProfile)){
  assert.ok(p.reportParagraphs.length>=4);assert.ok(p.reportParagraphs.join(' ').split(/\s+/).length>=250,p.name);
  assert.ok(p.sources.length>=3);const html=aflProfileHtml(data,p);assert.ok(html.includes(p.name.replace(/&/g,"&amp;").replace(/'/g,"&#39;")));assert.ok(html.includes('Current AFL performance'));assert.ok(html.includes('PitchIQ — AFL board'));assert.ok(html.includes('#v=afl'));assert.ok(html.includes('Performance evidence'));
  if(p.scoutingGrades){assert.equal(p.scoutingGrades.source,'MLB Pipeline / Baseball Savant');assert.ok(p.scoutingGrades.sourceUrl.endsWith(String(p.mlbamId)));}
 }
 const boston=data.players.find(p=>p.mlbamId===695722);assert.equal(boston.regularStats.plateAppearances,493);assert.equal(boston.regularStats.homeRuns,31);assert.equal(boston.regularStats.strikeOuts,144);assert.equal(boston.regularStats.baseOnBalls,97);
});
test('AFL indicators never turn missing or tiny samples into established strong performance',()=>{
 assert.equal(inningsToOuts('1.2'),5);assert.equal(inningsToOuts('2.0'),6);assert.equal(inningsToOuts('2.8'),null);
 assert.equal(aflSignal({type:'H'},{plateAppearances:7,ops:'2.000'}).hot,false);
 assert.equal(aflSignal({type:'H'},{plateAppearances:8,ops:'1.000'}).label,'Early hot start · small sample');
 assert.equal(aflSignal({type:'H'},{plateAppearances:20,ops:'.950'}).label,'Strong AFL production');
 assert.equal(aflSignal({type:'P'},{inningsPitched:'1.2',battersFaced:7,strikeOuts:5,baseOnBalls:0,era:'0.00'}).hot,false);
 assert.equal(aflSignal({type:'P'},{inningsPitched:'2.0',battersFaced:7,strikeOuts:4,baseOnBalls:0,era:'0.00'}).hot,true);
 assert.equal(aflSignal({type:'P'},{inningsPitched:'2.0',battersFaced:0,strikeOuts:4,baseOnBalls:0,era:'0.00'}).hot,false);
 assert.equal(aflSignal({type:'P'},{inningsPitched:'2.0',battersFaced:7,strikeOuts:4,baseOnBalls:0,era:null}).hot,false);
 assert.equal(aflSignal({type:'H'},null).hot,false);
});
test('only 2026 AFL stats are indexed and filters preserve official roster membership',()=>{
 const stats=indexAflStats(data.statsSnapshot);assert.ok(stats.H.size>0&&stats.P.size>0);
 const fake={stats:[{group:{displayName:'hitting'},splits:[{season:'2025',league:{id:119},player:{id:1},stat:{}},{season:'2026',league:{id:103},player:{id:2},stat:{}}]}]};assert.equal(indexAflStats(fake).H.size,0);
 assert.equal(filterAflPlayers(data.players,{query:'dakota jordan'},stats)[0].mlbamId,702607);
 const noSample=data.players.find(p=>!stats[p.type].has(p.mlbamId));assert.ok(noSample);assert.ok(filterAflPlayers(data.players,{},stats).includes(noSample));assert.ok(!filterAflPlayers(data.players,{played:true},stats).includes(noSample));
});
