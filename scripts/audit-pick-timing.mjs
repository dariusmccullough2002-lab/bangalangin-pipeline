// Offline pick conversion timing scenario: never credit a pick as direct lineup production.
import fs from 'node:fs';import {gunzipSync} from 'node:zlib';import {profiles,smoothCurveValue} from '../docs/time-curve-audit-20261024/curve-candidate.mjs';
const root='docs/valuation-priorities-20261024',d=JSON.parse(gunzipSync(fs.readFileSync(root+'/Frozen_Inputs.json.gz'))),rows=[];
for(const a of d.assets.filter(a=>a.audit.kind==='pick')){
 const path=a.annual_expected_utility,year=a.audit.year;
 const valid=Array.isArray(path)&&path.length===8&&path.every(x=>Number.isFinite(x)&&x>=0)&&path.every((x,i)=>2027+i>=year||x===0);
 rows.push({id:a.id,name:a.name,year,round:a.audit.round,status:valid?'conditional selection-path scenario':'blocked',neutral:a.values.neutral.display,firstModeledProductionYear:valid?2027+path.findIndex(x=>x>0):null,proxyClass:year>2027,immediatePlayerSlots:0,directLineupProduction:0,candidate:valid?Object.fromEntries([.1,.2].map(cap=>[cap,Object.fromEntries(['contender','rebuild'].map(mode=>[mode,smoothCurveValue(a.values.neutral.display,path,profiles['front-loaded'][mode],cap).value]))])):null});
}
const result={policy:'Value timing of future selected-player conversion using the saved selection-model annual path; distinguish from immediate lineup production. Do not add both ledgers.',rows,limitations:['2028/2029 classes use the saved uncertain 2026 proxy, not actual future-class forecasts.','Lottery/selection quality and time to productive MLB role remain uncertain.','No empirical market-price validation. Deployment remains gated by unresolved neutral-value coverage and price-scale policy.'],blocked:rows.filter(r=>r.status==='blocked').length};
fs.writeFileSync(root+'/Pick_Timing_Scenarios.json',JSON.stringify(result,null,2)+'\n');console.log(JSON.stringify({picks:rows.length,blocked:result.blocked,byYear:Object.fromEntries([2027,2028,2029].map(y=>[y,rows.filter(r=>r.year===y).slice(0,1)]))},null,2));
