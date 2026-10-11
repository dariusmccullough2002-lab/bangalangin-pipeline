import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {gunzipSync} from 'node:zlib';
const source=JSON.parse(readFileSync(new URL('../data/starter-display-scenarios.json',import.meta.url)));
const html=readFileSync(new URL('../trade-analyzer-beta/index.html',import.meta.url),'utf8');
const catalog=JSON.parse(gunzipSync(Buffer.from(html.match(/const packed='([^']+)'/)[1],'base64')));
const originalFetch=globalThis.fetch;globalThis.fetch=async()=>({ok:true,json:async()=>source});
const {projectionViews,qa3Eligible}=await import('../trade-analyzer-beta/starter-display.js');globalThis.fetch=originalFetch;
const deepFreeze=x=>{if(x&&typeof x==='object'){Object.freeze(x);Object.values(x).forEach(deepFreeze);}return x;};
test('display-only scenario adapter preserves all catalog valuations, workload inputs, and future paths',()=>{
 const before=JSON.stringify(catalog);deepFreeze(catalog);let supported=0;
 for(const a of catalog.assets){const v=projectionViews(a,source);if(!v?.scenario)continue;supported++;
  const s=v.scenario,p=v.expected;assert.equal(p.IP,(a.audit.MLB||a.audit).projection.IP);
  assert.ok(Math.abs(9*s.line.ER/s.line.IP-9*p.ER/p.IP)<1e-12);
  assert.ok(Math.abs((s.line.H+s.line.BB)/s.line.IP-(p.H+p.BB)/p.IP)<1e-12);
  assert.ok(s.line.QA3<=s.starts+s.reliefAppearances+1e-8);assert.ok(s.line.QA3<=s.line.IP/5+1e-8);
  assert.ok(s.line.SV+s.line.HLD<=s.reliefAppearances+1e-8);
  assert.ok(Object.values(s.line).every(x=>Number.isFinite(x)&&x>=0));
 }
 assert.ok(supported>=200);assert.equal(JSON.stringify(catalog),before);
});
test('established, interrupted, young and prospect routes preserve evidence and fallbacks',()=>{
 for(const name of ['Zack Wheeler','Paul Skenes','Kyle Bradish','Jacob Misiorowski']){
  const a=catalog.assets.find(a=>a.name===name);assert.ok(a,name);const v=projectionViews(a,source);assert.ok(v?.scenario,name);
 }
 const prospect=catalog.assets.find(a=>a.name==='Jamie Arnold');const v=projectionViews(prospect,source);
 assert.equal(v.scenario,null);assert.match(v.unsupported,/unknown/);assert.ok(prospect.audit.eta);
});
test('hitter, reliever, swingman and two-way displays do not route into starter scenarios',()=>{
 for(const a of catalog.assets){const evidence=a.audit.MLB||a.audit;
  if(evidence.role==='H'||evidence.role==='RP'||evidence.two_way_annual_projection)assert.equal(projectionViews(a,source),null);
 }
 assert.equal(projectionViews({id:'unmodeled-swingman',audit:{kind:'MLB',role:'SP',projection:{IP:40}}},source),null);
});
test('QA3 uses the actual inclusive league definition, not conventional QS',()=>{
 for(const [outs,er,expected] of [[14,0,false],[15,2,true],[15,3,false],[17,3,false],[18,3,true],[18,4,false],[21,2,true]])assert.equal(qa3Eligible(outs,er),expected);
 const skenes=projectionViews(catalog.assets.find(a=>a.name==='Paul Skenes'),source);
 assert.ok(Math.abs(skenes.scenario.line.QA3-21.272221211233074)<1e-8);
 assert.ok(Math.abs(skenes.scenario.line.QA3-skenes.expected.QA3*skenes.scenario.line.IP/skenes.expected.IP)>.01);
});
