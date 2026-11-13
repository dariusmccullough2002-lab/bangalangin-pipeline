import fs from 'node:fs';import assert from 'node:assert/strict';import {createHash} from 'node:crypto';
import {calculatePitcherOqi} from './pitcher-oqi.mjs';
const raw=fs.readFileSync('data/afl/cps-matchups-2026.json'),games=JSON.parse(raw),data=JSON.parse(fs.readFileSync('data/afl/cps-2026.json'));
const full=JSON.parse(fs.readFileSync('data/afl/full-2026.json'));
const hitting=full.statsSnapshot.stats.find(g=>g.group.displayName==='hitting').splits;
const pitching=full.statsSnapshot.stats.find(g=>g.group.displayName==='pitching').splits;
const baseline=calculatePitcherOqi(games,hitting,pitching);assert.deepEqual(baseline,data.pitcherOqi);
let checked=0;
for(const row of baseline.pitchers){
 for(const event of ['strikeout','home_run']){
  const changed=games.map(g=>({...g,plateAppearances:g.plateAppearances.map(pa=>pa[1]===row.mlbamId?[pa[0],pa[1],pa[2],event]:pa)}));
  const next=calculatePitcherOqi(changed,[],pitching).pitchers.find(p=>p.mlbamId===row.mlbamId);
  assert.equal(next.oqi,row.oqi,'Self-influence: '+row.name+' '+event);checked++;
 }
}
const result={generatedAt:data.generatedAt,scope:data.scope,through:data.through,games:games.length,totalPa:baseline.totalPa,pitchers:baseline.pitchers.length,
 qualifiedPitchers:baseline.pitchers.filter(p=>!p.smallSample).length,officialHitterLinesReconciled:hitting.length,countFieldsReconciled:['PA','AB','H','TB','BB','HBP','SF','SH'],
 cacheSha256:createHash('sha256').update(raw).digest('hex'),realDataSelfInfluenceTests:checked,selfInfluenceFailures:0,
 method:baseline.method,topQualified:baseline.pitchers.filter(p=>!p.smallSample).slice(0,5)};
fs.writeFileSync('docs/website/pitcher-oqi-audit-20261112.json',JSON.stringify(result,null,2)+'\n');console.log(JSON.stringify(result,null,2));
