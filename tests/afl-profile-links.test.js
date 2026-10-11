import test from 'node:test';import assert from 'node:assert/strict';import fs from 'node:fs';
import {aflProfileDestination,aflProfileLink} from '../afl-profile-links.js';
const full=JSON.parse(fs.readFileSync('data/afl/full-2026.json'));
test('every published AFL profile has its own stable ID destination, including pitchers',()=>{
 assert.equal(full.players.length,251);for(const p of full.players)assert.equal(aflProfileDestination(p,full),`#afl-player/${p.mlbamId}`);
 const pitcher=full.players.find(p=>p.mlbamId===703186);assert.equal(pitcher.type,'P');assert.equal(aflProfileDestination(pitcher,full),'#afl-player/703186');
});
test('name changes, accents and two-way eligibility cannot switch the stable player identity',()=>{
 const p=full.players[0];for(const name of ['José García','Jose Garcia','Same Name'])assert.equal(aflProfileDestination({...p,name,type:'TW'},full),`#afl-player/${p.mlbamId}`);
});
test('missing, duplicated or unsupported profile IDs fail closed',()=>{
 assert.equal(aflProfileDestination({name:full.players[0].name},full),null);
 assert.equal(aflProfileDestination({mlbamId:999999999},full),null);
 assert.equal(aflProfileDestination(full.players[0],{...full,players:[full.players[0],full.players[0]]}),null);
 assert.match(aflProfileLink({mlbamId:999999999},full),/unavailable/);
 assert.ok(!aflProfileLink({mlbamId:999999999},full).includes('href'));
});
