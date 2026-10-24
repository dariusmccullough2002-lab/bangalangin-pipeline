import test from 'node:test';
import assert from 'node:assert/strict';
import {explainTrade} from '../trade-analyzer-beta/trade-explanation.js';
const asset=(id,fit,neutral=fit)=>({id,name:id,audit:{kind:'MLB',role:'H'},values:{neutral:{display:neutral}},competitive_values:{contender:{display:fit},balanced:{display:fit*.9},rebuild:{display:fit*.8}}});
const a=asset('One',34,44),b=asset('Two',35.5,33),c=asset('Three',8,13);
const explain=(incoming,outgoing,mode='contender',more={})=>{const catalog=new Map([...incoming,...outgoing].map(a=>[a.id,a]));return explainTrade({incoming,outgoing,mode,valueFor:(id,m)=>m==='neutral'?catalog.get(id).values.neutral.display:catalog.get(id).competitive_values[m]?.display??null,...more});};
test('explanation reconciles exact totals and separates dynasty price from contribution',()=>{
 const r=explain([a],[b]);assert.equal(r.net,-1.5);assert.equal(r.neutralNet,11);assert.equal(r.received,34);assert.equal(r.sent,35.5);assert.match(r.paragraphs.join(' '),/signals disagree/);assert.equal(r.rows.reduce((n,r)=>n+r.signedFit,0),r.net);
});
test('uneven packages include every signed contribution with no invented consolidation credit',()=>{
 const r=explain([a],[b,c]);assert.equal(r.net,-9.5);assert.equal(r.rows.length,3);assert.match(r.paragraphs.join(' '),/43.5/);assert.doesNotMatch(r.paragraphs.join(' '),/drop|roster need|fair trade/);
});
test('missing scores block complete verdict rather than substituting zero',()=>{
 const r=explain([a],[b], 'contender',{valueFor:(id,m)=>id==='Two'&&m==='contender'?null:10});assert.equal(r.complete,false);assert.equal(r.net,null);assert.match(r.paragraphs[0],/not counted as zero/);
});
test('published prospect scenario is used instead of withdrawn production path',()=>{
 const p={...c,audit:{kind:'prospect'},annual_expected_utility:[999999]};const r=explain([p],[a],'contender',{timingFor:()=>({source:{source:'Saved source',value:2029},regularRoleStart:2029})});assert.match(r.rows[0].notes.join(' '),/regular-role contribution starts in 2029/);assert.doesNotMatch(JSON.stringify(r),/999999/);
});
test('quality explanation uses same factor and actual strategy before/after',()=>{
 const q={...a,forecast_research:{contributionFactor:1.05,evidenceDate:'2026-10-01',beforeCompetitiveValues:{contender:{display:34/1.05},rebuild:{display:34*.8/1.05}}}};
 for(const mode of ['contender','rebuild']){const r=explain([q],[b],mode);assert.match(r.rows[0].notes.join(' '),/\+5.0% contribution adjustment, shared across all strategies/);assert.match(r.rows[0].notes.join(' '),new RegExp(mode+' fit'));}
});
test('scenario crossing and every strategy change are reflected, without modifying inputs',()=>{
 const before=structuredClone([a,b]);const r=explain([a],[b],'contender',{range:{low:-12,high:9}});assert.match(r.paragraphs.join(' '),/result can reverse/);assert.notEqual(explain([a],[b],'rebuild').net,r.net);assert.deepEqual([a,b],before);
});
test('picks use no immediate player slot and no fabricated projected stat line',()=>{
 const p={...c,audit:{kind:'pick'}};const r=explain([p],[a]);assert.match(r.rows[0].notes[0],/no immediate roster slot/);assert.doesNotMatch(r.rows[0].notes[0],/PA|IP/);
});
test('identity and values drive explanation rather than special named-trade rules',()=>{
 const r=explain([a],[b]);const renamed=explain([{...a,name:'Renamed A'}],[{...b,name:'Renamed B'}]);assert.equal(renamed.net,r.net);assert.equal(renamed.neutralNet,r.neutralNet);assert.match(renamed.paragraphs.join(' '),/Renamed A/);
});
test('compatible hitter forecasts explain categories and trajectory without claiming lineup wins',()=>{
 const projection={PA:600,AB:520,H:140,BB:65,HBP:8,SF:7,TB:230,HR:25,R:90,RBI:80,SB:20};
 const first={...a,audit:{kind:'MLB',role:'H',projection},annual_expected_utility:[5,4,3,2,1,1,1,1]};
 const second={...b,audit:{kind:'MLB',role:'H',projection:{...projection,SB:10,H:130}},annual_expected_utility:[4,3,2,1,1,1,1,1]};
 const text=explain([first],[second]).paragraphs.join(' ');assert.match(text,/\+10.0 SB/);assert.match(text,/years 1–3 totals 12.0 incoming versus 9.0 outgoing/);assert.match(text,/do not establish usable lineup production/);
});
test('an incomplete batting component suppresses package forecast comparison',()=>{
 const first={...a,audit:{kind:'MLB',role:'H',projection:{AB:500,PA:600}}};
 assert.doesNotMatch(explain([first],[first]).paragraphs.join(' '),/batting forecasts compare/);
});
test('plain summary explains the decision without score arithmetic or technical terms',()=>{
 const r=explain([a],[b],'contender',{range:{low:-12,high:9}});const text=r.summary.join(' ');
 assert.match(text,/leans toward keeping Two/);assert.match(text,/gain overall dynasty value/);assert.match(text,/isn't firm/);assert.doesNotMatch(text,/\d|utility|neutral|scenario envelope|strategy-weighted|pseudocount/);
 assert.equal(r.net,-1.5);assert.match(r.paragraphs[0],/34.0 − 35.5/);
});
test('plain summary follows changed strategy, sign and missing evidence',()=>{
 assert.match(explain([b],[a]).summary[0],/leans toward taking Two/);
 assert.match(explain([a],[b],'rebuild').summary[0],/building for the future/);
 const r=explain([a],[b],'contender',{valueFor:()=>null});assert.match(r.summary[0],/isn't enough information/);assert.doesNotMatch(r.summary[0],/leans toward/);
});
test('prospects retain a readable warning without claiming immediate lineup help',()=>{
 const p={...c,audit:{kind:'prospect'}};assert.match(explain([p],[b]).summary.join(' '),/does not mean they are ready to improve your lineup now/);
});
