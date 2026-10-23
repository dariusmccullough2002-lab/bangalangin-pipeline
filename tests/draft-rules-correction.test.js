import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import zlib from 'node:zlib';
import os from 'node:os';
import path from 'node:path';
import {correctText,draftRules,correctDraftRules} from '../scripts/correct-draft-rules.mjs';
const unpack=path=>JSON.parse(zlib.gunzipSync(Buffer.from(fs.readFileSync(path,'utf8').match(/const packed='([^']+)'/)[1],'base64')));
test('17-round correction retains five tradable rounds and 144 FA selections',()=>{
 assert.equal(draftRules.totalRounds,17);assert.deepEqual(draftRules.tradableRounds,[1,2,3,4,5]);assert.equal(draftRules.freeAgentSelections,12*(17-5));
 assert.equal(correctText('Rounds 6–20; R6-20; 20-round draft'),'Rounds 6–17; R6-17; 17-round draft');
 assert.equal(correctText('Rounds 6\\u201320'),'Rounds 6\\u201317');assert.equal(correctText('1999-06-20'),'1999-06-20');
});
test('publication correction preserves numeric assets and dates',()=>{
 const dir=fs.mkdtempSync(path.join(os.tmpdir(),'draft-rules-'));
 try{
  fs.mkdirSync(path.join(dir,'trade-analyzer-beta'));
  const before={assets:[{id:'player',birthDate:'1999-06-20',values:{neutral:{display:13.1}}},{id:'pick',round:5,audit:{flags:['No standalone tradable assets in rounds6–20']}}]};
  const file=path.join(dir,'trade-analyzer-beta/index.html');
  fs.writeFileSync(file,"const packed='"+zlib.gzipSync(JSON.stringify(before)).toString('base64')+"'; Rounds 6–20");
  correctDraftRules(dir);const after=unpack(file);
  assert.deepEqual(after.draft_rules,draftRules);
  assert.deepEqual(after.assets[0],before.assets[0]);assert.equal(after.assets[1].round,5);
  assert.equal(after.assets[1].audit.flags[0],'No standalone tradable assets in rounds6–17');
  assert.match(fs.readFileSync(file,'utf8'),/Rounds 6–17/);
 }finally{fs.rmSync(dir,{recursive:true,force:true});}
});
