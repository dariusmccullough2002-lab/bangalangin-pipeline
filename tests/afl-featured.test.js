import test from 'node:test';
import assert from 'node:assert/strict';
import {featuredAflTrackerPlayers} from '../afl-board.js';
import {featuredCpsHitters, sortCpsHitters} from '../afl-cps.js';
import {calculateCps, gameMatchups} from '../scripts/afl-cps.mjs';

test('two-strike pinch-hitter strikeout follows the official charged PA; a walk belongs to the substitute',()=>{
 const substitution={details:{eventType:'offensive_substitution'},count:{strikes:2},player:{id:807461},replacedPlayer:{id:815793}};
 const play=eventType=>({about:{isComplete:true},result:{eventType},matchup:{batter:{id:807461},pitcher:{id:828594}},playEvents:[substitution]});
 assert.deepEqual(gameMatchups({allPlays:[play('strikeout'),play('walk')]}),[[815793,828594,1],[807461,828594,1]]);
 const noTwoStrikes=play('strikeout');noTwoStrikes.playEvents=[{...substitution,count:{strikes:1}}];
 assert.deepEqual(gameMatchups({allPlays:[noTwoStrikes]}),[[807461,828594,1]]);
});

test('featured hitters require 35 PA and .850 OPS, then sort by CPS; pitchers keep their screen and ordering',()=>{
 const hitter=(mlbamId,pa,ops,cps)=>({mlbamId,pa,ops,cps,name:String(mlbamId)});
 const cps={hitters:[hitter(1,34,1.8,150),hitter(2,50,.849,140),hitter(3,35,.850,120),hitter(4,50,1.050,110),hitter(5,70,.950,125),hitter(6,65,.975,107)]};
 const players=[7,8,9,10].map(mlbamId=>({mlbamId,type:'P',name:String(mlbamId),status:'Active'}));
 const pitcher=(inningsPitched,battersFaced,strikeOuts,baseOnBalls,era)=>({inningsPitched,battersFaced,strikeOuts,baseOnBalls,era});
 const stats={H:new Map(),P:new Map([[7,pitcher('5.0',20,8,2,1.8)],[8,pitcher('6.2',28,10,3,2.7)],[9,pitcher('15.0',70,10,8,6)],[10,pitcher('6.1',27,12,1,0)]])};
 assert.deepEqual(featuredAflTrackerPlayers(players,stats,cps).map(p=>p.mlbamId),[5,3,4,8,10,7]);
 assert.deepEqual(featuredAflTrackerPlayers(players,stats).map(p=>p.mlbamId),[8,10,7]);
 assert.deepEqual(featuredCpsHitters(cps).map(p=>p.mlbamId),[5,3,4]);
 assert.equal(sortCpsHitters(cps.hitters,'ops')[0].mlbamId,1);
});

test('runner events are excluded and same-team hitters get different OQI from actual matchups',()=>{
 const play=(batter,pitcher,eventType,isComplete=true)=>({about:{isComplete},result:{eventType},matchup:{batter:{id:batter},pitcher:{id:pitcher}}});
 const feed={allPlays:[...Array.from({length:20},()=>play(1,10,'walk')),...Array.from({length:20},()=>play(2,11,'single')),play(1,11,'caught_stealing_2b'),play(2,10,'walk',false)]};
 const matchups=gameMatchups(feed);
 assert.deepEqual(matchups,[[1,10,20],[2,11,20]]);
 const pitch=[{pitcher_id:10,pitches:150,filth_plus:110,csw_pct:35,whiff_pct:35,chase_pct:35,k_pct:30,bb_pct:10},
  {pitcher_id:11,pitches:150,filth_plus:90,csw_pct:25,whiff_pct:25,chase_pct:25,k_pct:20,bb_pct:10}];
 const team={id:1,name:'AFL team'},hitting=[1,2].map(id=>({player:{id,fullName:String(id)},team,stat:{plateAppearances:20,ops:1}}));
 const result=calculateCps([{matchups}],pitch,hitting,[{team,stat:{ops:.85}}]);
 assert.deepEqual(result.hitters.map(p=>[p.mlbamId,p.oqi,p.cps]),[[1,110,104.5],[2,90,93.25]]);
});
