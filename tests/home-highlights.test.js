import test from 'node:test';
import assert from 'node:assert/strict';
import {selectHomeAfl} from '../home-highlights.js';
test('homepage AFL rotation uses qualified active performers from both roles, with unique identities',()=>{
 const players=[{mlbamId:1,name:'Hot hitter',type:'H',status:'Active'},{mlbamId:2,name:'Hot pitcher',type:'P',status:'Active'},{mlbamId:3,name:'Second hitter',type:'H',status:'Active'},{mlbamId:4,name:'Departed hitter',type:'H',status:'Released'},{mlbamId:5,name:'Volume only',type:'H',status:'Active'}];
 const stats={H:new Map([[1,{plateAppearances:40,ops:1.2}],[3,{plateAppearances:35,ops:1.05}],[4,{plateAppearances:70,ops:1.7}],[5,{plateAppearances:100,ops:.6}]]),P:new Map([[2,{outs:21,battersFaced:27,strikeOuts:12,baseOnBalls:2,era:1.2}]])};
 assert.deepEqual(selectHomeAfl(players,stats).map(p=>p.mlbamId),[1,2,3]);
 stats.H.delete(1);assert.deepEqual(selectHomeAfl(players,stats).map(p=>p.mlbamId),[3,2]);
 assert.deepEqual(selectHomeAfl(players,{H:new Map(),P:new Map()}),[]);
});
