import test from 'node:test';
import assert from 'node:assert/strict';
import {tradeNarrative,assetKind} from '../trade-analyzer-beta/trade-narrative.js';
import {etaInfo,etaCell} from '../eta-display.js';
import {readFileSync} from 'node:fs';
const asset=(name,kind,role='H',display=20)=>({id:name,name,audit:{kind,role},values:{neutral:{display}},position:role==='H'?'SS':role});
const prospect=asset('Future Shortstop','prospect'),mlb=asset('Current Hitter','MLB'),sp=asset('Rotation Arm','MLB','SP'),pick=asset('2027 2nd — Island','pick','selection');
const context={owner:'Island',strategy:'contender',incoming:[mlb],outgoing:[prospect],fit:5,range:{low:-4,high:8},nearChange:2};
test('contender narrative separates MLB experience, projections and surrendering a prospect',()=>{
 const text=tradeNarrative(context);assert.match(text,/Current Hitter/);assert.match(text,/Future Shortstop/);assert.match(text,/recorded MLB contributions/);assert.match(text,/supports.*\(\+5.0 fit\)/);assert.match(text,/reverse the sign/);assert.match(text,/does not guarantee playing time/);assert.doesNotMatch(text,/injur|elite|scarce|guaranteed production/i);
});
test('contender receiving a prospect cannot claim immediate MLB help',()=>{
 const text=tradeNarrative({...context,incoming:[prospect],outgoing:[mlb]});assert.match(text,/future bet rather than verified immediate MLB help/);assert.match(text,/no independently dated arrival estimate/);
});
test('draft picks and uneven packages describe selection risk and capacity',()=>{
 const text=tradeNarrative({...context,strategy:'rebuild',incoming:[pick,prospect],outgoing:[mlb],fit:-8});assert.match(text,/2027 2nd/);assert.match(text,/development and arrival risk/);assert.match(text,/works against.*-8.0/);assert.match(text,/Legal roster capacity/);
 const pickOnly=tradeNarrative({...context,incoming:[pick]});assert.match(pickOnly,/selection opportunity, not an identified MLB contributor/);
});
test('consolidation does not equate quantity with an elite prospect premium',()=>{
 const text=tradeNarrative({...context,incoming:[prospect],outgoing:[mlb,pick]});assert.match(text,/consolidates 2 assets/);assert.doesNotMatch(text,/elite|market premium/);
});
test('different strategies only receive a mutual base-benefit statement when both fits are positive',()=>{
 const text=tradeNarrative({...context,otherStrategy:'rebuild',otherFit:3});assert.match(text,/positive base fit estimates for both/);
 assert.doesNotMatch(tradeNarrative({...context,otherStrategy:'rebuild',otherFit:-3}),/positive base fit estimates for both/);
 assert.doesNotMatch(tradeNarrative({...context,otherStrategy:'contender',otherFit:3}),/positive base fit estimates for both/);
});
test('missing numerical evidence never produces a gain verdict',()=>{
 const text=tradeNarrative({...context,fit:NaN,assessment:'Incomplete: missing values'});assert.match(text,/Missing valuation evidence/);assert.doesNotMatch(text,/base strategy estimate supports/);
 assert.equal(tradeNarrative({...context,incoming:[]}), 'Build both packages to explain the exchange.');
});
test('limited MLB evidence and roster labels are not established immediate production',()=>{
 const hybrid=asset('Debut Prospect','hybrid');assert.equal(assetKind(hybrid),'limited MLB');const text=tradeNarrative({...context,incoming:[hybrid]});assert.doesNotMatch(text,/toward players with recorded MLB contributions/);assert.doesNotMatch(text,/dependable|established veteran/);
});
test('starter/hitter exchange names the custom category without asserting a need',()=>{
 const text=tradeNarrative({...context,incoming:[sp],outgoing:[mlb]});assert.match(text,/QA3/);assert.match(text,/rotation need is not verified/);
});
test('veteran age and independently sourced ETA are used only when present',()=>{
 const veteran={...mlb,career_profile:{age:35}};assert.match(tradeNarrative({...context,strategy:'rebuild',incoming:[veteran]}),/35 in the saved snapshot/);
 const text=tradeNarrative({...context,incoming:[prospect],etas:{[prospect.id]:{value:'2029',source:'FanGraphs'}}});assert.match(text,/FanGraphs ETA is 2029/);
});
test('narrative generation is deterministic and never mutates the catalog or inputs',()=>{
 const original=structuredClone(context);assert.equal(tradeNarrative(context),tradeNarrative(context));assert.deepEqual(context,original);
});
test('ETA values preserve traceable source dates and make unavailable and undated data explicit',()=>{
 const records=JSON.parse(readFileSync('data/research/eta-evidence.json'));const edition=JSON.parse(readFileSync('data/editions/october-2026.json'));
 const counts={dated:0,undated:0,missing:0};for(const p of edition.rankings){const e=records[p.fantraxId];if(!e){counts.missing++;assert.equal(etaInfo(p,records).value,'TBD');continue}assert.match(String(e.value),/^20\d\d$/);if(e.date){counts.dated++;assert(e.url.startsWith('https://'));}else{counts.undated++;assert.match(etaInfo(p,records).description,/publication date unavailable/);assert.equal(e.value,p.eta);}}
 assert.deepEqual(counts,{dated:38,undated:179,missing:43});assert.match(etaCell({fantraxId:'unknown'},records),/Unavailable/);
});
