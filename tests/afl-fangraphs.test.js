import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import {aflFanGraphsGrades} from '../afl-fangraphs-grades.js';
import {aflProfileHtml} from '../afl-board.js';
const afl=JSON.parse(fs.readFileSync(new URL('../data/afl/full-2026.json',import.meta.url)));

test('published AFL tool grades resolve to reviewed MLBAM identities and valid scouting values',()=>{
 for(const [id,g] of Object.entries(aflFanGraphsGrades)){
  const matches=afl.players.filter(p=>String(p.mlbamId)===id);
  assert.equal(matches.length,1);
  assert.equal(g.verifiedName,matches[0].name);
  assert.equal(String(g.verifiedMlbamId),id);
  assert.match(g.fv,/^\d{2}\+?$/);
  assert.ok(Object.keys(g.tools).length>0);
  for(const value of Object.values(g.tools)){
   assert.match(value,/^\d{2}(\/\d{2})?$/);
   assert.ok(value.split('/').every(n=>Number(n)>=20&&Number(n)<=80));
  }
  assert.match(g.sourceUrl,/^https:\/\/(blogs|www)\.fangraphs\.com\//);
 }
});

test('new hitter and pitcher grade tables appear above the AFL roster with their report dates',()=>{
 for(const name of ['Dakota Jordan','Patrick Forbes']){
  const p=afl.players.find(p=>p.name===name),g=aflFanGraphsGrades[p.mlbamId];
  const html=aflProfileHtml(afl,p);
  assert.ok(html.indexOf('FUTURE VALUE')<html.indexOf('AFL ROSTER / 2026'));
  assert.ok(html.includes(g.sourceDate));
  assert.ok(html.includes(g.sourceUrl));
  for(const value of Object.values(g.tools))assert.ok(html.includes(value));
 }
});
