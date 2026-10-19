import test from 'node:test';
import assert from 'node:assert/strict';
import {featuredAflPlayers} from '../afl-board.js';
test('featured AFL cards balance hitter production with exposure among strong results and reject volume without quality',()=>{
 const players=[],stats={H:new Map(),P:new Map()};
 const add=(id,type,s)=>{players.push({mlbamId:id,type,name:String(id)});stats[type].set(id,s);};
 add(1,'H',{plateAppearances:8,ops:'1.800'});
 add(2,'H',{plateAppearances:20,ops:'.950'});
 add(3,'H',{plateAppearances:30,ops:'.910'});
 add(4,'H',{plateAppearances:60,ops:'.650'});
 add(5,'H',{plateAppearances:30,ops:'1.100'});
 add(6,'P',{inningsPitched:'2.0',battersFaced:7,strikeOuts:6,baseOnBalls:0,era:'0.00'});
 add(7,'P',{inningsPitched:'5.0',battersFaced:20,strikeOuts:8,baseOnBalls:2,era:'1.80'});
 add(8,'P',{inningsPitched:'6.2',battersFaced:28,strikeOuts:10,baseOnBalls:3,era:'2.70'});
 add(9,'P',{inningsPitched:'15.0',battersFaced:70,strikeOuts:10,baseOnBalls:8,era:'6.00'});
 add(10,'P',{inningsPitched:'6.1',battersFaced:27,strikeOuts:12,baseOnBalls:1,era:'0.00'});
 assert.deepEqual(featuredAflPlayers(players,stats).map(p=>p.mlbamId),[1,5,3,8,10,7]);
 assert.deepEqual(featuredAflPlayers(players,stats,10).filter(p=>p.type==='H').map(p=>p.mlbamId),[1,5,3,2]);
 assert.deepEqual(featuredAflPlayers([],stats),[]);
 assert.equal(players[0].mlbamId,1);
});

test('exceptional 32-PA production outranks larger ordinary hot samples without featuring a tiny fluke',()=>{
 const players=[1,2,3,4,5].map(mlbamId=>({mlbamId,type:'H',name:String(mlbamId)}));
 const stats={H:new Map([[1,{plateAppearances:32,ops:'1.650',avg:'.615'}],[2,{plateAppearances:50,ops:'1.000'}],[3,{plateAppearances:45,ops:'1.050'}],[4,{plateAppearances:8,ops:'1.200'}],[5,{plateAppearances:70,ops:'.650'}]]),P:new Map()};
 assert.deepEqual(featuredAflPlayers(players,stats).map(p=>p.mlbamId),[1,3,2]);
});
