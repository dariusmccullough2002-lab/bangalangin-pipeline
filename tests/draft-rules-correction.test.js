import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import zlib from 'node:zlib';
import {correctText,draftRules} from '../scripts/correct-draft-rules.mjs';
const unpack=path=>JSON.parse(zlib.gunzipSync(Buffer.from(fs.readFileSync(path,'utf8').match(/const packed='([^']+)'/)[1],'base64')));
test('17-round correction retains five tradable rounds and 144 FA selections',()=>{
 assert.equal(draftRules.totalRounds,17);assert.deepEqual(draftRules.tradableRounds,[1,2,3,4,5]);assert.equal(draftRules.freeAgentSelections,12*(17-5));
 assert.equal(correctText('Rounds 6–20; R6-20; 20-round draft'),'Rounds 6–17; R6-17; 17-round draft');
 assert.equal(correctText('Rounds 6\\u201320'),'Rounds 6\\u201317');assert.equal(correctText('1999-06-20'),'1999-06-20');
});
test('built model applies corrected rules without changing assets or prices',()=>{
 const before=unpack('trade-analyzer-beta/index.html'),after=unpack('dist/trade-analyzer-beta/index.html');
 assert.deepEqual(after.draft_rules,draftRules);assert.deepEqual(after.assets.map(a=>({id:a.id,values:a.values,range:a.range})),before.assets.map(a=>({id:a.id,values:a.values,range:a.range})));
 const html=fs.readFileSync('dist/trade-analyzer-beta/index.html','utf8');
 assert.equal(/20-round|6–20|6\\\\u201320/.test(html),false,'No obsolete round references');
 assert.match(html,/6–17/);
 assert.doesNotMatch(fs.readFileSync('dist/data/access-durability.json','utf8'),/6–20/);
});
