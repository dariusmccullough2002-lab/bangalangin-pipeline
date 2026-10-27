import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import {doorHitterTileSample,doorPitcherAflSample} from '../door-tile-samples.js';
const read=p=>JSON.parse(fs.readFileSync(new URL('../'+p,import.meta.url)));
const watch=read('data/knocking-door-2027.json'),samples=read('data/door-hitter-samples.json'),afl=read('data/afl/full-2026.json');
const player=name=>watch.players.find(p=>p.name===name);
test('Walcott shows a separately dated AFL slash line, never a combined regular/fall sample',()=>{
 const s=doorHitterTileSample(player('Sebastian Walcott'),samples,afl);
 const source=afl.statsSnapshot.stats.find(g=>g.group.displayName==='hitting').splits.find(s=>s.player.id===806964).stat;
 assert.equal(s.line.level,'AFL');assert.equal(s.line.pa,source.plateAppearances);assert.deepEqual(s.metrics,[['AVG',source.avg],['OBP',source.obp],['SLG',source.slg]]);
 assert.equal(s.extras,`${source.plateAppearances} PA · ${source.homeRuns} HR · ${source.stolenBases} SB`);assert.match(s.note,/AAA sample: only 9 PA \(8 AB\)/);assert.match(s.caption,/2026 AFL only/);
 const fallback=doorHitterTileSample(player('Sebastian Walcott'),samples,null);
 assert.equal(fallback.line.level,'AA');assert.equal(fallback.line.pa,171);
});
test('brief promotions use a substantial earlier level, with honest PA and AB labels',()=>{
 const willits=doorHitterTileSample(player('Eli Willits'),samples,afl);
 assert.equal(willits.line.level,'A+');assert.equal(willits.line.pa,289);assert.deepEqual(willits.metrics,[['AVG','.230'],['OBP','.392'],['SLG','.420']]);assert.match(willits.note,/AA sample: only 17 PA \(14 AB\)/);
 const sirota=doorHitterTileSample(player('Mike Sirota'),samples,afl);assert.equal(sirota.line.level,'AA');assert.equal(sirota.line.pa,333);assert.match(sirota.note,/9 PA \(6 AB\)/);
 const miller=doorHitterTileSample(player('Aidan Miller'),samples,null);assert.equal(miller.line.season,2025);assert.match(miller.caption,/2025 AA/);assert.match(miller.note,/2026 AA sample: only 11 PA \(10 AB\)/);
});
test('40 PA is inclusive and missing denominators are not invented',()=>{
 const p={type:'H',level:'AAA',mlbamId:1,statsDate:'2026-10-06',levelSplits:[{level:'AAA',group:'hitting',pa:39,avg:'.400',slg:'.600'}],allLevelSplits:[{level:'AAA',group:'hitting',pa:39,avg:'.400',slg:'.600'},{level:'AA',group:'hitting',pa:40,avg:'.250',slg:'.500'}]};
 const s=doorHitterTileSample(p);assert.equal(s.line.level,'AA');assert.equal(s.line.pa,40);assert.equal(s.metrics[1][1],'—');assert.match(s.note,/only 39 PA/);assert.ok(!s.note.includes('AB'));
 assert.equal(doorHitterTileSample({type:'P'}),null);
});
test('all 22 hitters have attributed count-based slash lines; pitchers remain separate',()=>{
 for(const p of watch.players){const s=doorHitterTileSample(p,samples,afl);if(p.type==='P'){assert.equal(s,null);continue;}assert.ok(s.line.pa>=40,p.name);assert.ok(s.metrics.every(([label,value])=>['AVG','OBP','SLG'].includes(label)&&value!=='—'),p.name);assert.ok(!s.metrics.some(([label])=>label==='K%'));assert.ok(samples.players[String(p.mlbamId)].display.sourceUrl.startsWith('https://statsapi.mlb.com/'));}
});

test('every recorded AFL participant takes priority, including Miller, Bonemer and Susana',()=>{
 for(const p of watch.players){
  const group=p.type==='H'?'hitting':'pitching';
  const row=afl.statsSnapshot.stats.find(g=>g.group.displayName===group)?.splits.find(s=>s.player.id===p.mlbamId&&s.league.id===119);
  if(!row)continue;
  const result=p.type==='H'?doorHitterTileSample(p,samples,afl):doorPitcherAflSample(p,afl);
  assert.ok(result,p.name);assert.match(result.caption,/AFL only/,p.name);
  if(p.type==='H'){assert.equal(result.line.pa,row.stat.plateAppearances);assert.equal(result.metrics[0][1],row.stat.avg);}
  else assert.equal(result.metrics[0][1],row.stat.inningsPitched);
 }
 const p={...player('Aidan Miller'),mlbamId:123};
 const tiny={statsSnapshot:{stats:[{group:{displayName:'hitting'},splits:[{player:{id:123},season:'2026',league:{id:119},stat:{plateAppearances:2,avg:'.500',obp:'.500',slg:'.500'}}]}]}};
 assert.equal(doorHitterTileSample(p,samples,tiny).line.level,'AFL');
 assert.equal(doorPitcherAflSample({type:'P',mlbamId:123},tiny),null);
});
