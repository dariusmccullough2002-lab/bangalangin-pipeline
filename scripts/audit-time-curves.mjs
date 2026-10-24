// Offline policy sensitivity. Frozen catalog and prior packages; no production writes.
import fs from 'node:fs';import {gunzipSync} from 'node:zlib';import {createHash} from 'node:crypto';
import {timingEstimate} from '../trade-analyzer-beta/prospect-timing.js';
import {rankingAnchoredCandidate} from '../docs/strategy-setting-audit-20261024/policy-candidates.mjs';
import {profiles,curveValue,smoothCurveValue,allocateNeutral} from '../docs/time-curve-audit-20261024/curve-candidate.mjs';
const root='docs/time-curve-audit-20261024';
const raw=fs.readFileSync('docs/horizon-audit-20261024/Frozen_Inputs.json.gz'),d=JSON.parse(gunzipSync(raw));
const prior=JSON.parse(gunzipSync(fs.readFileSync('docs/strategy-setting-audit-20261024/Results.json.gz')));
profiles['front-loaded-smooth']=profiles['front-loaded'];profiles['gentler-smooth']=profiles['gentler'];
const catalog=new Map(d.assets.map(a=>[a.id,a])),caps=[.1,.2],modes=['contender','rebuild'];
const price=a=>a.values?.neutral?.display??null;
const fit=(a,m)=>a.audit.kind==='prospect'?timingEstimate(a,m,d.timing)?.display??null:a.competitive_values?.[m]?.display??null;
const path=a=>a.audit.kind==='prospect'?timingEstimate(a,'balanced',d.timing)?.annualUtility??null:a.annual_expected_utility;
function value(a,profile,mode,cap){
 if(profile==='existing')return rankingAnchoredCandidate(price(a),fit(a,'balanced'),fit(a,mode),cap);
 // Picks retain their neutral asset price; zero direct player production is not a pick arrival model.
 if(a.audit.kind==='pick')return Number.isFinite(price(a))?{value:price(a),factor:1,status:'pick-neutral',reason:'Pick-specific timing not modeled by player curve'}:{value:null,status:'blocked'};
 return (profile.endsWith('-smooth')?smoothCurveValue:curveValue)(price(a),path(a),profiles[profile][mode],cap);
}
const sum=xs=>xs.every(Number.isFinite)?xs.reduce((a,b)=>a+b,0):null;
const net=(sides,f)=>{const totals=sides.map(ids=>sum(ids.map(id=>f(catalog.get(id)))));return totals.every(Number.isFinite)?totals[1]-totals[0]:null;};
let seed=20261024;const rand=n=>{seed=(1664525*seed+1013904223)>>>0;return seed%n;};
const pool=d.assets.filter(a=>!a.id.startsWith('slot-')&&price(a)>0&&profiles['front-loaded']&&modes.every(m=>Number.isFinite(value(a,'front-loaded',m,.2).value)));
const identity=JSON.parse(fs.readFileSync('docs/strategy-setting-audit-20261024/Catalog_Identity.json')).identities;
const extra=[];for(const size of [4,6]){let attempts=0;const seen=new Set();while(extra.filter(c=>c.size===size).length<200&&attempts++<100000){const outgoing=[];while(outgoing.length<size){const a=pool[rand(pool.length)];if(!outgoing.includes(a))outgoing.push(a);}const target=sum(outgoing.map(price));const options=pool.filter(a=>price(a)>=target*.9&&price(a)<=target*1.1&&!outgoing.includes(a));if(!options.length)continue;const incoming=options[rand(options.length)],all=[...outgoing,incoming];if(new Set(all.map(a=>identity[a.id]??a.id)).size!==all.length)continue;const key=outgoing.map(a=>a.id).sort().join(',')+'|'+incoming.id;if(seen.has(key))continue;seen.add(key);extra.push({id:`extra-${size}-${extra.length}`,size,sides:[outgoing.map(a=>a.id),[incoming.id]]});}}
const cases=[...prior.cases.neutralMatched,...extra];
function evaluate(c){return {id:c.id,sides:c.sides,names:c.sides.map(ids=>ids.map(id=>catalog.get(id).name)),neutral:net(c.sides,price),results:Object.fromEntries(Object.keys(profiles).map(profile=>[profile,Object.fromEntries(caps.map(cap=>[cap,Object.fromEntries(modes.map(mode=>[mode,net(c.sides,a=>value(a,profile,mode,cap).value)]))]))]))};}
const evaluated=cases.map(evaluate),named=prior.named.map(evaluate);
const q=xs=>{const a=xs.sort((a,b)=>a-b);return {median:a[Math.floor(a.length*.5)]??null,p90:a[Math.floor(a.length*.9)]??null};};
const population={};const failed=[];
for(const profile of Object.keys(profiles))for(const cap of caps)for(const mode of modes){
 const vals=d.assets.filter(a=>!a.id.startsWith('slot-')).map(a=>({a,r:value(a,profile,mode,cap)}));
 const supported=vals.filter(x=>Number.isFinite(x.r.value)),blocked=vals.filter(x=>!Number.isFinite(x.r.value));
 for(const {a,r} of supported)if(r.value<price(a)*(1-cap)-1e-8||r.value>price(a)*(1+cap)+1e-8)failed.push(`${profile}/${cap}/${mode}/${a.id}: cap violation`);
 const packages=evaluated.filter(c=>Number.isFinite(c.results[profile][cap][mode]));
 population[`${profile}/${cap}/${mode}`]={supportedAssets:supported.length,blockedAssets:blocked.length,picksHeldNeutral:supported.filter(x=>x.r.status==='pick-neutral').length,atCap:supported.filter(x=>Math.abs(Math.abs(x.r.factor-1)-cap)<1e-9).length,supportedPackages:packages.length,blockedPackages:evaluated.length-packages.length,signChangesFromNeutral:packages.filter(c=>Math.abs(c.neutral)>1e-9&&Math.sign(c.neutral)!==Math.sign(c.results[profile][cap][mode])).length,absoluteChangeFromNeutral:q(packages.map(c=>Math.abs(c.results[profile][cap][mode]-c.neutral)))};
}
for(const a of d.assets){const allocated=allocateNeutral(price(a),path(a));if(allocated&&Math.abs(sum(allocated)-price(a))>1e-8)failed.push(a.id+': area preservation');}
const curves=Object.fromEntries(Object.entries(profiles).map(([p,ms])=>[p,Object.fromEntries(Object.entries(ms).map(([m,w])=>[m,{annualMass:w,firstTwoYears:sum(w.slice(0,2)),afterSecondYear:sum(w.slice(2))}]))]));
const result={protocol:{frozenInputSha256:createHash('sha256').update(raw).digest('hex'),priorPackages:3000,newPackages:extra.length,seed:20261024,caps,selection:'New 4/6-for-1 packages matched only on neutral price within 10%; canonical duplicate assets excluded',productionChanged:false},curves,named,population,cases:evaluated,failedChecks:failed,limitations:['No historical outcome validation or empirically optimal cap selected.','Player annual contribution paths still determine timing; a Gaussian cannot repair an inaccurate path.','Picks retain neutral value under Gaussian candidates because player-production curves do not model pick conversion. Existing pick timing is tested separately in existing candidate.','Positive results for both strategies are different preferences, not new neutral value.','Cap is per asset; package net changes can exceed 10% or 20% of the original trade difference.','Does not add roster optimization, replacement value or weekly category simulation.','Eight-year truncation and curve widths are explicit policy assumptions.','No production files changed.']};
fs.writeFileSync(root+'/Results.json',JSON.stringify(result,null,2)+'\n');console.log(JSON.stringify({curves,named,population,failedChecks:failed},null,2));if(failed.length)process.exitCode=1;
