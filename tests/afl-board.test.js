import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import {aflSignal,indexAflStats,inningsToOuts,filterAflPlayers,aflProfileHtml} from '../afl-board.js';
import {buildProfileIndex,findProfiles} from '../home-search.js';
const read=f=>JSON.parse(fs.readFileSync(f));
const data=read('data/afl/full-2026.json'),cur=read('data/editions/october-2026.json'),archive=read('data/editions/august-2026.json'),players=read('data/players.json'),draft=read('data/draft/2026.json'),dsl=read('data/dsl/2026.json'),intl=read('data/international/2027.json'),pro=read('data/international/professionals-2026.json');
test('full official AFL roster resolves once and preserves existing profile identities',()=>{
 assert.equal(data.players.length,261);assert.equal(new Set(data.players.map(p=>p.mlbamId)).size,261);assert.equal(new Set(data.players.map(p=>p.aflTeamId)).size,6);
 assert.equal(data.players.filter(p=>p.hasExistingProfile).length,30);
 const index=buildProfileIndex(cur,archive,players,draft,intl,dsl,pro,data);
 for(const p of data.players){const matches=findProfiles(index,p.name).filter(x=>x.name===p.name);assert.equal(matches.length,1,p.name);assert.equal(matches[0].route,p.route);assert.ok(p.status);assert.match(p.sourceUrl,/statsapi\.mlb\.com/);}
 for(const id of [695722,702607]){const p=data.players.find(p=>p.mlbamId===id);assert.equal(p.hasExistingProfile,false);assert.equal(p.route,`#afl-player/${id}`);}
});
test('new AFL profiles contain sourced reports and separate regular-season and fall data',()=>{
 for(const p of data.players.filter(p=>!p.hasExistingProfile)){
  assert.ok(p.reportParagraphs.length>=4);assert.ok(p.reportParagraphs.join(' ').split(/\s+/).length>=250,p.name);
  assert.ok(p.sources.length>=3);const html=aflProfileHtml(data,p);assert.ok(html.includes(p.name.replace(/&/g,"&amp;").replace(/'/g,"&#39;")));assert.ok(html.includes('Current AFL performance'));assert.ok(html.includes('PitchIQ — AFL board'));assert.ok(html.includes('#v=afl'));assert.ok(html.includes('Performance evidence'));
  if(p.scoutingGrades){assert.ok(p.scoutingGrades.source);assert.match(p.scoutingGrades.sourceUrl,/^https:\/\//);assert.ok(p.scoutingGrades.fv);}
 }
 const boston=data.players.find(p=>p.mlbamId===695722);assert.equal(boston.regularStats.plateAppearances,493);assert.equal(boston.regularStats.homeRuns,31);assert.equal(boston.regularStats.strikeOuts,144);assert.equal(boston.regularStats.baseOnBalls,97);assert.equal(data.players.find(p=>p.mlbamId===702607).regularStats.avg,.283);
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

test('incomplete refreshes cannot erase previously reported AFL appearances',async()=>{
 const {validateAflRefresh}=await import('../afl-board.js');
 const group=(name,ids)=>({group:{displayName:name},totalSplits:ids.length,splits:ids.map(id=>({season:'2026',league:{id:119},player:{id},stat:{plateAppearances:10}}))});
 const prior={stats:[group('hitting',[1,2]),group('pitching',[3])]};
 assert.throws(()=>validateAflRefresh(prior,{stats:[group('hitting',[1]),group('pitching',[3])]}),/omitted/);
 assert.throws(()=>validateAflRefresh(prior,{stats:[group('hitting',[1,2])]}),/Incomplete/);
 const next={stats:[group('hitting',[1,2,4]),group('pitching',[3])]};assert.equal(validateAflRefresh(prior,next),next);
 const truncated={stats:[{...group('hitting',[1,2]),totalSplits:3},group('pitching',[3])]};assert.throws(()=>validateAflRefresh(prior,truncated),/Truncated/);
});

test('AFL live request includes every player rather than qualifying leaders only',async()=>{
 const {AFL_STATS_URL}=await import('../afl-board.js');const u=new URL(AFL_STATS_URL);assert.equal(u.searchParams.get('playerPool'),'ALL');assert.equal(u.searchParams.get('sportIds'),'17');assert.equal(u.searchParams.get('leagueIds'),'119');const stats=indexAflStats(data.statsSnapshot);assert.ok(stats.H.get(806988).plateAppearances>0);assert.ok(Number.isFinite(Number(stats.H.get(806988).ops)));
});
test('schedule failure cannot discard successful live AFL stats, and stats failure cannot discard the schedule',async()=>{
 const {fetchAflUpdates,AFL_STATS_URL}=await import('../afl-board.js');const schedule={dates:[]};const response=d=>({ok:true,json:async()=>d});let out=await fetchAflUpdates(data.statsSnapshot,'2026-10-13',{fetcher:async u=>u===AFL_STATS_URL?response(data.statsSnapshot):Promise.reject(Error('Schedule offline'))});assert.equal(out.stats,data.statsSnapshot);assert.equal(out.schedule,null);assert.match(out.scheduleError,/Schedule offline/);assert.equal(out.statsError,null);
 out=await fetchAflUpdates(data.statsSnapshot,'2026-10-13',{fetcher:async u=>u===AFL_STATS_URL?Promise.reject(Error('Stats offline')):response(schedule)});assert.equal(out.stats,null);assert.equal(out.schedule,schedule);assert.match(out.statsError,/Stats offline/);
});
test('invalid or truncated AFL feed still fails without blocking valid game data',async()=>{
 const {fetchAflUpdates,AFL_STATS_URL}=await import('../afl-board.js');const broken=structuredClone(data.statsSnapshot);broken.stats[0].totalSplits=broken.stats[0].splits.length+1;const schedule={dates:[]};const result=await fetchAflUpdates(data.statsSnapshot,'2026-10-13',{fetcher:async u=>({ok:true,json:async()=>u===AFL_STATS_URL?broken:schedule})});assert.equal(result.stats,null);assert.match(result.statsError,/Truncated/);assert.equal(result.schedule,schedule);
});
test('full-player feed zero-exposure rows do not count as recorded AFL appearances',async()=>{
 const {hasAflSample}=await import('../afl-board.js');assert.equal(hasAflSample({type:'H'},{plateAppearances:0}),false);assert.equal(hasAflSample({type:'P'},{inningsPitched:'0.0',battersFaced:0}),false);assert.equal(hasAflSample({type:'P'},{inningsPitched:'0.0',battersFaced:2}),true);const rows=[{mlbamId:1,type:'H',name:'Zero',status:'Active',aflTeam:'A',mlbOrg:'B'},{mlbamId:2,type:'H',name:'Played',status:'Active',aflTeam:'A',mlbOrg:'B'}];const stats={H:new Map([[1,{plateAppearances:0}],[2,{plateAppearances:1}]]),P:new Map()};assert.deepEqual(filterAflPlayers(rows,{played:true},stats).map(r=>r.mlbamId),[2]);
});

test('departed AFL participants remain searchable but are excluded from the default active roster',()=>{const stats=indexAflStats(data.statsSnapshot),puk=data.players.find(p=>p.name==='Owen Puk');assert.equal(puk.status,'Not on current official roster');assert.equal(data.players.filter(p=>p.status==='Active').length,258);assert.ok(!filterAflPlayers(data.players,{},stats).includes(puk));assert.ok(filterAflPlayers(data.players,{includeInactive:true},stats).includes(puk));const g=data.players.find(p=>p.mlbamId===695403);assert.equal(g.name,'Brock Gillis');assert.equal(g.mlbOrg,'WSH');});

test('Useche retains his canonical profile after the official Mesa reassignment',()=>{const p=data.players.find(p=>p.mlbamId===687766);assert.equal(p.name,'Miguel Useche');assert.equal(p.mlbOrg,'CHC');assert.equal(p.aflTeamId,555);assert.equal(p.aflTeam,'Mesa Solar Sox');assert.equal(p.route,'#afl-player/687766');assert.match(p.sourceUrl,/teams\/555\/roster/);});
