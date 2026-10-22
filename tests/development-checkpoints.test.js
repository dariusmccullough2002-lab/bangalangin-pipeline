import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {checkpointHtml} from '../development-checkpoints.js';
import {publicAssets} from '../scripts/public-assets.js';
const data=JSON.parse(readFileSync(new URL('../data/development-checkpoints.json',import.meta.url)));
test('all current profile routes have checkpoints and evidence gaps remain explicit',()=>{
 const pools=[['october-player','editions/october-2026','rankings','playerId'],['draft-player','draft/2026','players','id'],['international-player','international/2027','players','id'],['international-pro-player','international/professionals-2026','players','id'],['afl-player','afl/full-2026','players','mlbamId'],['dsl-player','dsl/2026','players','id']];
 let count=0;for(const [route,path,key,id] of pools){const pool=JSON.parse(readFileSync(new URL(`../data/${path}.json`,import.meta.url)));for(const p of pool[key]){count++;const c=data.entries[`${route}/${p[id]}`];assert.equal(c.name,p.name);for(const field of ['question','positive','concern','window','status'])assert.ok(c[field]?.length>15);assert.ok(c.evidence||c.status.startsWith('Evidence gap'));assert.ok(!c.status.includes('verified improvement'));}}
 assert.equal(count,Object.keys(data.entries).length);assert.equal(count,data.audit.profileEntries);
});
test('safe rendering, no source hallucination, deployment includes both assets',()=>{
 const html=checkpointHtml({name:'x',topic:'<script>',question:'<img>',status:'Monitoring',evidence:null,positive:'x',concern:'x',window:'x',sources:[]});assert.ok(!html.includes('<script>'));assert.match(html,/verification remains pending/);assert.equal(checkpointHtml(null),'');
 for(const p of Object.values(data.entries))for(const s of p.sources)assert.match(s.url,/^https:\/\//);
 for(const p of ['development-checkpoints.js','data/development-checkpoints.json'])assert.ok(publicAssets.includes(p));
});
test('specific plans distinguish contact, opportunity, rehab and role changes',()=>{
 const e=data.entries;
 assert.match(e['october-player/fantrax-067yc'].question,/surgery|shoulder|labrum/i);
 assert.equal(e['dsl-player/837864'].question,e['october-player/fantrax-0769m'].question);
 assert.match(e['international-player/luis-garcia-nicaragua-2027'].status,/Limited evidence/);
 assert.match(e['international-player/erick-gonzalez-nicaragua-2027'].question,/90.plus|slider|changeup/);
 assert.match(e['afl-player/692284'].question,/hip|left.hand/i);
 assert.match(e['draft-player/roch-cholowsky'].question,/wood.bat|glove/i);
 assert.match(e['afl-player/805800'].question,/shorten|bullpen/i);
 assert.match(e['october-player/fantrax-06ibv'].question,/airborne|both sides/i);
});
test('every distinct player has an authored plan and old template questions cannot return',()=>{
 const byIdentity=new Map();
 for(const p of Object.values(data.entries)){
  const id=p.mlbamId?String(p.mlbamId):p.name;
  assert.equal(p.individualEditorialReview,true);assert.ok(p.baseline.length>35);
  assert.doesNotMatch(p.question,/Does pitch recognition improve without sacrificing damage|Do the reported weapons hold up in games|Can the pitcher locate the arsenal consistently/i);
  if(byIdentity.has(id))assert.equal(p.question,byIdentity.get(id));else byIdentity.set(id,p.question);
  assert.equal((checkpointHtml(p).match(/scope="row"/g)||[]).length,5);
 }
 assert.equal(new Set(byIdentity.values()).size,byIdentity.size);
 assert.equal(data.audit.uniquePlayers,byIdentity.size);
 assert.equal(data.audit.duplicateQuestionsAcrossDistinctPlayers,0);
});
