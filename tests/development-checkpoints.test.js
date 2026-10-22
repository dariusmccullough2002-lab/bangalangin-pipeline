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
