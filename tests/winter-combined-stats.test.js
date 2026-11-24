import test from 'node:test';import assert from 'node:assert/strict';import fs from 'node:fs';
import {combinedSeasonRows,winterPerformanceEvidence} from '../winter-profiles.js';
const catalog=JSON.parse(fs.readFileSync(new URL('../data/winter/profiles-2026.json',import.meta.url)));
test('Jayson Bass combines level counts and recomputes hitting rates',()=>{
 const p=catalog.players.find(p=>p.mlbamId===814188),x=combinedSeasonRows(p.seasonStats)[0].stats;
 assert.equal(x.plateAppearances,404);assert.equal(x.atBats,355);assert.equal(x.hits,82);assert.equal(x.homeRuns,16);assert.equal(x.stolenBases,24);assert.equal(x.avg,82/355);
 const rows=p.seasonStats.map(r=>r.stats),bb=rows.reduce((s,r)=>s+r.baseOnBalls,0),hbp=rows.reduce((s,r)=>s+r.hitByPitch,0),sf=rows.reduce((s,r)=>s+r.sacFlies,0);
 assert.equal(x.obp,(82+bb+hbp)/(355+bb+hbp+sf));assert.equal(x.kPct,rows.reduce((s,r)=>s+r.strikeOuts,0)/404);
 const html=winterPerformanceEvidence(p.seasonStats),[summary,dropdown]=html.split('<details><summary>See the level and team splits</summary>');
 assert.match(summary,/Hitting · all verified levels combined/);assert.equal((summary.match(/facts metricfacts/g)??[]).length,1);assert.ok(!summary.includes('Hitting · High-A'));assert.ok(dropdown.includes('High-A'));assert.ok(dropdown.includes('Single-A'));
});
test('Pitcher totals sum outs and recompute ERA and BF-weighted rates',()=>{
 const rows=[{kind:'pitching',stats:{outs:1,battersFaced:3,earnedRuns:1,hits:1,strikeOuts:1,baseOnBalls:1,homeRuns:0}},{kind:'pitching',stats:{outs:2,battersFaced:8,earnedRuns:0,hits:2,strikeOuts:2,baseOnBalls:2,homeRuns:0}}];
 const x=combinedSeasonRows(rows)[0].stats;assert.equal(x.ip,'1.0');assert.equal(x.era,9);assert.equal(x.whip,6);assert.equal(x.kPct,3/11);assert.equal(x.bbPct,3/11);assert.equal(x.kMinusBB,0);
 const p=catalog.players.find(p=>p.position==='P'&&p.seasonStats.length>1),html=winterPerformanceEvidence(p.seasonStats);assert.match(html,/Pitching · all verified levels combined/);
});
test('Missing counts remain missing and winter leagues remain separate',()=>{
 const x=combinedSeasonRows([{kind:'hitting',stats:{plateAppearances:0,atBats:0,hits:0,baseOnBalls:0,strikeOuts:0}}])[0].stats;
 assert.equal(x.avg,null);assert.equal(x.obp,null);assert.equal(x.iso,null);assert.equal(x.totalBases,null);assert.deepEqual(combinedSeasonRows([]),[]);
 const source=JSON.parse(fs.readFileSync(new URL('../data/winter/2026.json',import.meta.url))),l=source.leagues.find(l=>l.hitters.length),row={...l.hitters[0],league:l.code,sourceUrls:l.sourceUrls,refreshedAt:l.lastSuccessfulRefresh,competitionContext:l.competitionContext};
 const html=winterPerformanceEvidence([row],true,'2026–27');assert.ok(!html.includes('all verified levels combined'));assert.ok(html.includes(l.code));
});

test('Winter prospect split tables use the same six columns as Theo Gillen',()=>{
 const headers=['LEVEL','TEAM','TYPE','SAMPLE','K / BB','AVG / SLG OR ERA'];
 for(const p of catalog.players){const html=winterPerformanceEvidence(p.seasonStats);if(!p.seasonStats.length)continue;const dropdown=html.split('<details><summary>See the level and team splits</summary>')[1];for(const h of headers)assert.ok(dropdown.includes('<th>'+h+'</th>'),p.name+': '+h);assert.ok(!dropdown.includes('wp-stats'));assert.ok(!dropdown.includes('<th>AB</th>'));}
});
