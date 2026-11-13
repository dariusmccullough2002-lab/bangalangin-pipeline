import fs from 'node:fs';import assert from 'node:assert/strict';
import {calculateCpi} from './pitcher-cpi.mjs';
const read=p=>JSON.parse(fs.readFileSync(p));
const data=read('data/afl/cps-2026.json'),input=read('data/afl/cpi-pitch-inputs-2026.json'),full=read('data/afl/full-2026.json');
const official=full.statsSnapshot.stats.find(g=>g.group.displayName==='pitching').splits;
const base=calculateCpi(input.pitchers,official,data.pitcherOqi);assert.deepEqual(base,data.pitcherCpi);
let checks=0;
for(const p of base.pitchers.filter(p=>p.cpi!=null)){
 for(const key of ['strikeOuts','earnedRuns']){
  const updated=official.map(row=>row.player.id===p.mlbamId?{...row,stat:{...row.stat,[key]:key==='strikeOuts'?row.stat[key]+5:Math.max(0,row.stat[key]-1)}}:row);
  if(key==='earnedRuns'&&p.earnedRuns===0)continue;
  const next=calculateCpi(input.pitchers,updated,data.pitcherOqi).pitchers.find(r=>r.mlbamId===p.mlbamId);
  assert.equal(next.oqi,p.oqi);assert.equal(next.components.opposition,p.components.opposition);
  assert.ok(next.cpi>=p.cpi,'Improved result lowered CPI+: '+p.name+' '+key);checks++;
 }
}
const qualified=base.pitchers.filter(p=>p.cpiRank);
const out={generatedAt:data.generatedAt,through:data.through,pitchSourceGeneratedAt:input.generatedAt,scoredPitchers:base.pitchers.filter(p=>p.cpi!=null).length,qualifiedPitchers:qualified.length,
 performanceDirectionChecks:checks,failures:0,qualifiedMean:qualified.reduce((sum,p)=>sum+p.cpi,0)/qualified.length,
 weights:base.weights,shapeWeights:base.shapeWeights,top5:qualified.slice(0,5).map(p=>({name:p.name,cpi:p.cpi,filthPlus:p.filthPlus,kMinusBB:p.kMinusBB,era:p.era,batterQuality:p.oqi,contextPoints:p.components.opposition}))};
fs.writeFileSync('docs/website/cpi-audit-20261112.json',JSON.stringify(out,null,2)+'\n');console.log(JSON.stringify(out,null,2));
