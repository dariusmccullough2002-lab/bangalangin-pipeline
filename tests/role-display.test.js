import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {gunzipSync} from 'node:zlib';
const source=JSON.parse(readFileSync(new URL('../data/role-display-scenarios.json',import.meta.url)));
const html=readFileSync(new URL('../trade-analyzer-beta/index.html',import.meta.url),'utf8');
const catalog=JSON.parse(gunzipSync(Buffer.from(html.match(/const packed='([^']+)'/)[1],'base64')));
const originalFetch=globalThis.fetch;globalThis.fetch=async()=>({ok:true,json:async()=>source});
const {projectionViews,hitterRatios}=await import('../trade-analyzer-beta/role-display.js');globalThis.fetch=originalFetch;
const freeze=x=>{if(x&&typeof x==='object'){Object.freeze(x);Object.values(x).forEach(freeze);}return x;};
const near=(a,b)=>assert.ok(Math.abs(a-b)<1e-10,`${a} versus ${b}`);
test('all role display lines preserve exact expected counts and every valuation field',()=>{
 const before=JSON.stringify(catalog);freeze(catalog);let hitters=0,pitchers=0;
 for(const a of catalog.assets){const v=projectionViews(a,source);if(!v)continue;assert.deepEqual(v.expected,(a.audit.MLB||a.audit).projection||null);if(!v.scenario)continue;
  const p=v.expected,l=v.scenario.line;
  if(v.kind==='H'){
   hitters++;const r=hitterRatios(p),s=hitterRatios(l);for(const k of ['AVG','OBP','SLG'])near(r[k],s[k]);
   near(l.PA,l.AB+l.BB+l.HBP+l.SF+l.otherPA);assert.ok(l.otherPA>=-1e-8);assert.ok(l.AB>=l.H&&l.H>=l.HR);assert.ok(l.TB>=l.H+3*l.HR-1e-8&&l.TB<=4*l.H+1e-8);
   near(l.RBI/l.PA,p.RBI/p.PA);assert.equal(l['2B'],null);assert.equal(l['3B'],null);
  }else{
   pitchers++;near(9*l.ER/l.IP,9*p.ER/p.IP);near((l.H+l.BB)/l.IP,(p.H+p.BB)/p.IP);near(l.K/l.IP,p.K/p.IP);
   assert.ok(l.SV===null||l.SV+l.HLD<=v.scenario.appearances+1e-8);assert.ok(l.QA3===null||l.QA3<=l.IP/5+1e-8);
   assert.equal(v.scenario.starts,0);
  }
 }
 assert.ok(hitters>600&&pitchers>400);assert.equal(JSON.stringify(catalog),before);
});
test('everyday, catcher, platoon, bench and bullpen evidence stay role-specific',()=>{
 for(const name of ['Aaron Judge','Matt Olson','Shea Langeliers','Gavin Lux','Raisel Iglesias','Matt Brash']){
  const a=catalog.assets.find(x=>x.name===name),v=projectionViews(a,source);assert.ok(v?.scenario,name);
 }
 const catcher=source.players['04o4s'];assert.equal(catcher.appearances,137);assert.ok(catcher.workload<catcher.preservedFullWorkload);
 assert.equal(source.players['041ai'].role,'platoon');assert.ok(source.players['041ai'].observations.some(x=>x.status==='verified_zero'&&x.exposure===0));
 assert.ok(Object.values(source.players).some(x=>x.supported&&x.role==='bench'));
 const rp=projectionViews(catalog.assets.find(x=>x.id==='03aqv'),source);near(rp.scenario.line.SV,rp.scenario.appearances*source.players['03aqv'].savePerAppearance);
 assert.ok(Math.abs(rp.scenario.line.SV-rp.expected.SV*rp.scenario.line.IP/rp.expected.IP)>.1);
});
test('two-way, starters and swingmen keep their existing display routes',()=>{
 for(const name of ['Shohei Ohtani','Paul Skenes','Cal Quantrill','Justin Wrobleski'])assert.equal(projectionViews(catalog.assets.find(x=>x.name===name),source),null,name);
});
test('unsupported prospect and missing rate/opportunity fields remain unavailable',()=>{
 const a={id:'fixture',audit:{kind:'prospect',role:'H',eta:2029}};
 const missing={players:{fixture:{supported:false,reason:'No observed role'}}};assert.equal(projectionViews(a,missing).scenario,null);assert.equal(a.audit.eta,2029);
 const rp={id:'fixture',audit:{kind:'MLB',role:'RP',projection:{IP:40,K:50,ER:10,H:30,BB:10}}};
 const v=projectionViews(rp,{players:{fixture:{supported:true,workload:60,appearances:65,savePerAppearance:null,holdPerAppearance:null,qa3PerAppearance:null}}});assert.equal(v.scenario.line.SV,null);assert.equal(v.scenario.line.HLD,null);assert.equal(v.scenario.line.QA3,null);
 const zero=projectionViews({...rp,audit:{...rp.audit,projection:{IP:0}}},{players:{fixture:{supported:true,workload:60}}});assert.equal(zero.scenario,null);
});
