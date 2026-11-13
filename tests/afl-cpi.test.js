import test from 'node:test';import assert from 'node:assert/strict';
import {calculateCpi} from '../scripts/pitcher-cpi.mjs';
import {aflPitcherCpiTile,renderPitcherCpi,sortPitcherCpi} from '../afl-pitcher-cpi.js';
const inputs=()=>({pitch:[1,2,3].map((id,i)=>({pitcher_id:id,pitches:300,filth_plus:98+2*i,whiff_pct:25+5*i,csw_pct:28+2*i,chase_pct:24+4*i,k_pct:10,bb_pct:5})),
 official:[1,2,3].map((id,i)=>({player:{id},stat:{battersFaced:100,outs:90,earnedRuns:8+2*i,strikeOuts:20+2*i,baseOnBalls:10}})),
 opponents:{pitchers:[1,2,3].map(id=>({mlbamId:id,name:'Arm '+id,team:'A',bf:100,oqi:100,ip:'30.0',smallSample:false}))}});
const calc=x=>calculateCpi(x.pitch,x.official,x.opponents);
const target=(x,id=2)=>calc(x).pitchers.find(r=>r.mlbamId===id);
test('CPI+ responds to better pitch quality, K-BB and ERA while independent opponent quality stays fixed',()=>{
 const base=target(inputs());
 for(const change of [x=>x.pitch[1].filth_plus+=10,x=>x.official[1].stat.strikeOuts+=15,x=>x.official[1].stat.baseOnBalls-=8,x=>x.official[1].stat.earnedRuns=0]){
  const x=inputs();change(x);const after=target(x);assert.ok(after.cpi>base.cpi);assert.equal(after.oqi,base.oqi);assert.equal(after.components.opposition,base.components.opposition);
 }
});
test('K-BB enters once explicitly from official results; provider K/BB/ERA cannot be counted again',()=>{
 const x=inputs(),base=calc(x);x.pitch.forEach(p=>{p.k_pct=99;p.bb_pct=0;p.era=0;p.stuff_plus=180;});assert.deepEqual(calc(x),base);
 assert.equal(base.weights.pitchQuality,.65);assert.equal(base.weights.kMinusBB,.25);assert.equal(base.weights.era,.10);assert.ok(!Object.hasOwn(base.shapeWeights,'kMinusBB'));
});
test('opposition is a bounded supporting adjustment, never the main score',()=>{
 const base=target(inputs()),x=inputs();x.opponents.pitchers[1].oqi=1000;const after=target(x);
 assert.equal(after.components.opposition,Number((3*100/140).toFixed(3)));assert.ok(after.cpi>base.cpi);assert.ok(after.cpi-base.cpi<3);
});
test('small samples regress to neutral; qualified mean is 100 and incomplete inputs get a dash',()=>{
 const x=inputs(),out=calc(x);assert.ok(Math.abs(out.pitchers.reduce((a,p)=>a+p.cpi,0)/3-100)<.001);
 const large=out.pitchers.find(p=>p.mlbamId===3);x.pitch[2].pitches=10;x.official[2].stat={...x.official[2].stat,battersFaced:10,outs:9,strikeOuts:2.4,baseOnBalls:1,earnedRuns:1.2};x.opponents.pitchers[2].bf=10;
 const small=target(x,3);assert.ok(small.smallSample);assert.ok(Math.abs(small.components.pitchQuality)<Math.abs(large.components.pitchQuality));assert.ok(Math.abs(small.components.kMinusBB)<Math.abs(large.components.kMinusBB));
 const missing=inputs();delete missing.pitch[1].filth_plus;const row=target(missing);assert.equal(row.cpi,null);assert.ok(row.missingInputs);assert.match(aflPitcherCpiTile({pitcherCpi:{pitchers:[row]}},{type:'P',mlbamId:2}),/—/);
});
test('CPI+ UI sorts the performance score first and retains filters and explicit input labels',()=>{
 const x=inputs(),data={generatedAt:'2026-11-13T01:00:00Z',through:'2026-11-12',pitcherCpi:calc(x)};
 const nodes=new Map(),app={innerHTML:'',querySelector(id){if(!nodes.has(id))nodes.set(id,{value:id==='#cpi-sort'?'cpi':'',checked:false,innerHTML:'',textContent:''});return nodes.get(id);}};
 renderPitcherCpi(app,data);assert.match(app.innerHTML,/CPI\+ Pitcher Leaderboard/);assert.match(app.innerHTML,/65% pitch quality/);assert.match(app.querySelector('#cpi-rows').innerHTML,/Arm 3/);
 app.querySelector('#cpi-search').value='Arm 1';app.querySelector('#cpi-search').oninput();assert.doesNotMatch(app.querySelector('#cpi-rows').innerHTML,/Arm 3/);
 assert.equal(sortPitcherCpi([{name:'Missing',cpi:null,bf:100},{name:'Scored',cpi:90,bf:100}])[0].name,'Scored');
 assert.equal(aflPitcherCpiTile(data,{type:'H',mlbamId:1}),'');
});
