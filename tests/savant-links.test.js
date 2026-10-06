import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import {prospectSavantLink} from '../profile-context.js';
test('Prospect Savant links preserve the MLBAM ID and open safely in a separate tab',()=>{
 for(const file of ['data/editions/october-2026.json','data/draft/2026.json']){
  const d=JSON.parse(fs.readFileSync(file));
  for(const p of d.rankings??d.players){
   if(!p.mlbamId)continue;
   const html=prospectSavantLink(p);
   assert.ok(html.includes(`href="https://prospectsavant.com/player/${p.mlbamId}"`));
   assert.ok(html.includes('target="_blank" rel="noopener noreferrer"'));
  }
 }
});
test('missing and invalid IDs never become external player links',()=>{
 for(const id of [null,undefined,'',0,-1,1.5,'815888/other','" onclick="alert(1)',true,Number.MAX_SAFE_INTEGER+1]){
  const html=prospectSavantLink({mlbamId:id});
  assert.ok(!html.includes('href='));assert.ok(html.includes('unavailable'));
 }
});
