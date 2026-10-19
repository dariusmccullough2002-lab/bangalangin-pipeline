import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {draftOutcomesHtml,defensiveOpportunityHtml} from '../draft-outcomes.js';
const read=p=>JSON.parse(readFileSync(p));
const data=read('data/draft/2026.json'),audit=read('docs/draft-outcomes-20261019/Defense_Audit.json'),inputs=read('docs/draft-outcomes-20261019/Stat_Line_Inputs.json');
const by=new Map(data.players.map(p=>[p.id,p]));
test('defensive audit covers all 112 identities and separates role volume from batting ability',()=>{
 assert.equal(audit.players.length,112);assert.equal(new Set(audit.players.map(p=>p.id)).size,112);
 let changed=0,hitters=0,pitchers=0;
 for(const row of audit.players){
  const p=by.get(row.id);assert.equal(row.mlbamId,p.mlbamId);assert.equal(row.name,p.name);assert.ok(p.outcomes.defensiveOpportunity.rationale.length>70);
  assert.deepEqual(row.afterStatLines,p.outcomes.statLines);assert.deepEqual(row.afterInputs,inputs.players[row.id].scenarios);
  assert.deepEqual(row.beforeStatLines.ceiling,row.afterStatLines.ceiling,p.id);
  if(p.type==='P'){pitchers++;assert.deepEqual(row.beforeStatLines,row.afterStatLines);assert.equal(defensiveOpportunityHtml(p),'');continue;}
  hitters++;const d=p.outcomes.defensiveOpportunity;assert.ok(d.sources.length);assert.ok(d.sources.every(s=>s.url.startsWith('https://')));
  const differs=row.beforeInputs.median[0]!==row.afterInputs.median[0]||row.beforeInputs.floor[0]!==row.afterInputs.floor[0];assert.equal(d.changed,differs);if(differs)changed++;
  for(const key of ['ceiling','median','floor'])for(const index of [1,2,3])assert.equal(row.beforeInputs[key][index],row.afterInputs[key][index],`${p.id}: offensive rate ${key}`);
  assert.ok(draftOutcomesHtml(p).includes('Defense &amp; playing time'));assert.ok(draftOutcomesHtml(p).includes('unconditional PA guarantee'));
 }
 assert.equal(hitters,75);assert.equal(pitchers,37);assert.equal(changed,44);
});
test('elite shortstop weak-bat opportunity is distinguished from severe failure and catcher rest',()=>{
 const roch=by.get('roch-cholowsky');assert.equal(roch.outcomes.statLines.floor.pa,500);assert.equal(roch.outcomes.defensiveOpportunity.floorCase,'healthy_weak_bat_regular');
 const html=draftOutcomesHtml(roch);assert.ok(html.includes('Healthy weak-bat regular'));assert.ok(html.includes('0 MLB PA'));assert.ok(html.includes('not a guaranteed minimum'));
 assert.match(roch.outcomes.floor,/Injury.*separate severe-failure branches/);
 assert.equal(by.get('aiden-ruiz').outcomes.statLines.median.pa,500);assert.ok(by.get('aiden-ruiz').outcomes.statLines.floor.pa<500);
 assert.equal(by.get('ryder-helfrick').outcomes.statLines.median.pa,450);assert.equal(by.get('ryder-helfrick').outcomes.risk.level,'Moderate');
 for(const p of data.players.filter(p=>p.position==='C'))assert.ok(p.outcomes.statLines.median.pa<=500,p.id);
});
test('a position label, speed or first-base glove cannot create blanket premium-defense credit',()=>{
 const rose=by.get('zion-rose');assert.equal(rose.position,'CF');assert.equal(rose.outcomes.defensiveOpportunity.cushion,'Bat-dependent');assert.equal(rose.outcomes.defensiveOpportunity.changed,false);
 for(const id of ['bo-lowrance','connor-comeau','tyce-armstrong','collin-bland','myles-bailey'])assert.equal(by.get(id).outcomes.defensiveOpportunity.changed,false,id);
 const prosek=by.get('cole-prosek');assert.match(prosek.outcomes.defensiveOpportunity.defensiveHome,/3B/);assert.equal(prosek.outcomes.statLines.median.pa,330);assert.match(prosek.outcomes.ceiling,/third baseman/);assert.doesNotMatch(prosek.scoutingParagraphs[1],/second-base/);
 assert.equal(by.get('brendan-brock').outcomes.defensiveOpportunity.cushion,'Conditional');assert.equal(by.get('brendan-brock').outcomes.defensiveOpportunity.changed,false);
});
