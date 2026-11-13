import test from 'node:test';
import assert from 'node:assert/strict';
import {calculatePitcherOqi,eventOffense} from '../scripts/pitcher-oqi.mjs';
import {aflPitcherOqiTile,renderPitcherOqi} from '../afl-pitcher-oqi.js';
import {gamePaEvents,gameMatchups} from '../scripts/afl-cps.mjs';
const games=entries=>[{id:1,plateAppearances:entries}];
const pa=(b,p,t,e,n=1)=>Array.from({length:n},()=>[b,p,t,e]);
const fixture=[...pa(1,10,100,'strikeout',12),...pa(2,10,200,'single',8),...pa(1,20,100,'home_run',10),...pa(1,20,100,'field_out',30),...pa(2,20,200,'single',10),...pa(2,20,200,'field_out',30),...pa(3,30,100,'double',8),...pa(3,30,100,'field_out',32),...pa(4,30,200,'walk',8),...pa(4,30,200,'field_out',32)];
const score=(entries,id)=>calculatePitcherOqi(games(entries),[]).pitchers.find(r=>r.mlbamId===id);
test('own strikeouts, hits and walks cannot change OQI, including through team or league references',()=>{
 const original=score(fixture,10);
 for(const event of ['home_run','walk','strikeout','hit_by_pitch','sac_fly']){
  const changed=fixture.map(row=>row[1]===10?[row[0],row[1],row[2],event]:row);
  assert.equal(score(changed,10).oqi,original.oqi,event);
 }
 const changed=fixture.map(row=>row[1]===10?[row[0],row[1],row[2],'home_run']:row);
 assert.notEqual(score(changed,20).oqi,score(fixture,20).oqi,'other pitchers may learn from the changed independent evidence');
});
test('no independent offense is neutral, never a penalty for facing hitters the pitcher shut down',()=>{
 const r=score(pa(1,10,100,'strikeout',25),10);assert.equal(r.oqi,100);assert.equal(r.neutralBf,25);assert.equal(r.independentBf,0);
});
test('independent low-sample estimates are shrunk; stronger outside hitters make opposition harder',()=>{
 const own=pa(1,10,100,'strikeout',20),outside=[...pa(1,20,100,'home_run',2),...pa(1,20,100,'field_out',8),...pa(2,20,100,'field_out',10)];
 const small=score([...own,...outside],10),large=score([...own,...Array.from({length:10},()=>outside).flat()],10);
 assert.ok(small.oqi>100);assert.ok(large.oqi>small.oqi);assert.equal(small.bf,20);
});
test('count extraction respects walks, sacrifices and catcher interference, then fails closed on official discrepancies',()=>{
 assert.equal(eventOffense('walk').ab,0);assert.equal(eventOffense('sac_fly').sf,1);assert.equal(eventOffense('catcher_interf').pa,1);assert.equal(eventOffense('catcher_interf').ab,0);assert.equal(eventOffense('home_run').tb,4);
 assert.throws(()=>calculatePitcherOqi(games(pa(1,10,100,'single')), [{player:{id:1,fullName:'Test'},stat:{plateAppearances:1,atBats:1,hits:0,totalBases:0}}]),/counting-stat mismatch/);
 assert.throws(()=>calculatePitcherOqi([{matchups:[]}],[]),/outcome-level/);
});
test('defensive-shift awards are PA without an AB, while an ordinary fielding error is an AB',()=>{
 const play=violation=>({about:{isComplete:true,isTopInning:true},matchup:{batter:{id:1},pitcher:{id:10}},result:{eventType:'field_error'},playEvents:[{details:violation?{violation:{type:'defensive_shift'}}:{}}]});
 const feed={allPlays:[play(true),play(false)]};const rows=gamePaEvents(feed,{away:{team:{id:100}}});
 assert.deepEqual(rows.map(r=>eventOffense(r[3]).ab),[0,1]);assert.deepEqual(gameMatchups(feed),[[1,10,2]]);
});
test('all pitchers receive profiles while the default leaderboard protects against tiny BF samples',()=>{
 const data={generatedAt:'2026-11-13T00:00:00Z',through:'2026-11-12',pitcherOqi:{pitchers:[{mlbamId:1,name:'Qualified arm',team:'A',bf:20,independentBf:20,neutralBf:0,oqi:105,rank:1,smallSample:false},{mlbamId:2,name:'Tiny arm',team:'B',bf:1,independentBf:0,neutralBf:1,oqi:100,rank:null,smallSample:true}]}};
 assert.match(aflPitcherOqiTile(data,{type:'P',mlbamId:2}),/100.0/);assert.match(aflPitcherOqiTile(data,{type:'P',mlbamId:2}),/small sample/);assert.equal(aflPitcherOqiTile(data,{type:'H',mlbamId:1}),'');
 const nodes=new Map();const app={innerHTML:'',querySelector(id){if(!nodes.has(id))nodes.set(id,{value:id==='#poq-sort'?'oqi':'',checked:false,innerHTML:'',textContent:''});return nodes.get(id);}};
 renderPitcherOqi(app,data);assert.match(app.querySelector('#poq-rows').innerHTML,/Qualified arm/);assert.doesNotMatch(app.querySelector('#poq-rows').innerHTML,/Tiny arm/);
 app.querySelector('#poq-small').checked=true;app.querySelector('#poq-small').onchange();assert.match(app.querySelector('#poq-rows').innerHTML,/Tiny arm/);
 app.querySelector('#poq-search').value='tiny';app.querySelector('#poq-search').oninput();assert.doesNotMatch(app.querySelector('#poq-rows').innerHTML,/Qualified arm/);
 assert.match(app.innerHTML,/Every OPS in that expression excludes A/);
});
