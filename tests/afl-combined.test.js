import test from 'node:test';
import assert from 'node:assert/strict';
import {combineAflStats,fetchCombinedAflStats} from '../afl-season-stats.js';
import {includedAflGames} from '../scripts/afl-cps.mjs';
const payload=(type,stat,id=1)=>({stats:[{group:{displayName:type},totalSplits:1,splits:[{season:'2026',league:{id:119},team:{id:10},player:{id},stat}]}]});
test('combined rates are recomputed from counting stats, not averaged across unequal samples',()=>{
 const regular=payload('hitting',{age:20,plateAppearances:100,atBats:80,hits:20,totalBases:30,baseOnBalls:20,ops:'.775'});
 const postseason=payload('hitting',{age:20,plateAppearances:5,atBats:4,hits:3,totalBases:6,baseOnBalls:1,ops:'2.300'});
 const r=combineAflStats([regular,postseason]).stats[0].splits[0].stat;
 assert.equal(r.plateAppearances,105);assert.equal(r.hits,23);assert.equal(r.age,20);
 assert.equal(r.avg,(23/84).toFixed(3));assert.equal(r.ops,(44/105+36/84).toFixed(3));assert.equal(r.ops,'0.848');
});
test('pitching sums outs, never baseball-notation decimal innings',()=>{
 const r=combineAflStats([payload('pitching',{inningsPitched:'1.2',earnedRuns:1,hits:2,baseOnBalls:1}),payload('pitching',{inningsPitched:'0.2',earnedRuns:1,hits:1,baseOnBalls:0})]).stats[0].splits[0].stat;
 assert.equal(r.outs,7);assert.equal(r.inningsPitched,'2.1');assert.equal(r.era,'7.71');assert.equal(r.whip,'1.71');
});
test('all competition types except Fall Stars are fetched, postseason-only players retained, failures reject',async()=>{
 const seen=[];const fetcher=async url=>{const type=new URL(url).searchParams.get('gameType');seen.push(type);return {ok:true,json:async()=>type==='R'?payload('hitting',{plateAppearances:10,atBats:10,hits:2,totalBases:2}):type==='D'?payload('hitting',{plateAppearances:4,atBats:4,hits:1,totalBases:1},2):{stats:[]}};};
 const out=await fetchCombinedAflStats({fetcher});assert.deepEqual(seen,['R','D','L','W']);assert.equal(out.stats[0].splits.length,2);
 await assert.rejects(fetchCombinedAflStats({fetcher:async url=>new URL(url).searchParams.get('gameType')==='D'?{ok:false}:fetcher(url)}),/D stats unavailable/);
 assert.throws(()=>combineAflStats([{stats:[{group:{displayName:'hitting'},totalSplits:2,splits:[]}]}]),/Truncated/);
});
test('only completed regular and playoff games enter CBS, even when exhibitions are final',()=>{
 const game=(id,gameType,state='Final')=>({gamePk:id,gameType,status:{abstractGameState:state,detailedState:state}});
 const schedule={dates:[{date:'2026-11-12',games:[game(1,'R'),game(2,'D'),game(3,'L'),game(4,'W'),game(5,'A'),game(6,'S'),game(7,'D','Live')]}]};
 assert.deepEqual(includedAflGames(schedule).map(g=>g.id),[1,2,3,4]);
});
