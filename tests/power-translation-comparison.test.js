import test from 'node:test';import assert from 'node:assert/strict';import {readFileSync} from 'node:fs';
import {modelCoordinates,probability} from '../power-translation-math.js';
import {comparisonBenchmarks,frontierDetails} from '../power-translation-comparison.js';
const d=JSON.parse(readFileSync(new URL('../data/research/power-translation-v1.json',import.meta.url))),m=d.model;
test('combined axes exactly reconstruct the fitted four-metric MLB relationship',()=>{
 for(const p of d.seasons){const c=modelCoordinates(p,m),direct=m.intercept+m.features.reduce((s,k,i)=>s+m.coefficients[i]*p[k],0);assert.ok(Math.abs(c.logit-direct)<1e-12);assert.ok(Math.abs(c.baseline+c.y-c.x-direct)<1e-12);const onLine={...p,qualified:true,supported:true};assert.ok(Math.abs(probability(onLine,m)-1/(1+Math.exp(-c.logit)))<1e-12);}
 assert.equal(modelCoordinates({...d.seasons[0],barrel:null},m),null);
});
test('MLB reference view caps points, retains landmarks and labels earlier qualified seasons',()=>{
 for(const y of [2015,2024,2025,2026]){
  const {points,landmarks,pool}=comparisonBenchmarks(d.seasons,y,m);
  assert.ok(points.length<=25&&points.length>=20);assert.equal(new Set(points.map(p=>p.id)).size,points.length);assert.ok(points.every(p=>p.qualified&&p.year<=y));
  assert.ok(landmarks.every(p=>points.some(r=>r.id===p.id)));assert.ok(points.every(p=>p.year===y||landmarks.some(r=>r.id===p.id)));
  const chosen=pool.at(-1);assert.ok(comparisonBenchmarks(d.seasons,y,m,chosen.id).points.some(p=>p.id===chosen.id));
 }
 const b=comparisonBenchmarks(d.seasons,2026,m);assert.ok(b.landmarks.some(p=>p.playerId===592450&&p.year<2026));
});
test('raw prospect placement changes no stored record and supplies no translated probability',()=>{
 const minor=JSON.parse(readFileSync(new URL('../data/research/power-translation-minor.json',import.meta.url))),before=JSON.stringify(minor);
 for(const p of minor.records.filter(p=>p.adequate)){const c=modelCoordinates(p,m);assert.ok(Number.isFinite(c.x)&&Number.isFinite(c.y));assert.equal('probability' in c,false);assert.equal('endpoint' in c,false);assert.equal('score' in p,false);}
 assert.equal(JSON.stringify(minor),before);
});
test('raw frontier distance is exact geometry and attribution preserves coefficient signs',()=>{
 for(const p of d.seasons){const f=frontierDetails(p,m),c=modelCoordinates(p,m);assert.ok(Math.abs(f.distance-(c.y-c.x+c.baseline)/Math.SQRT2)<1e-12);assert.equal(f.side,c.logit>=0?'Above':'Below');assert.ok(Math.abs(f.terms.reduce((s,t)=>s+t.value,0)+c.baseline-c.logit)<1e-12);if(f.positive)assert.ok(f.positive.value>0);if(f.negative)assert.ok(f.negative.value<0);assert.equal('probability' in f,false);}
 assert.equal(frontierDetails({...d.seasons[0],whiff:null},m),null);
});
