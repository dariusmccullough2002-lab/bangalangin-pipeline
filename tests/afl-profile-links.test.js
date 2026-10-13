import test from 'node:test';import assert from 'node:assert/strict';import fs from 'node:fs';
import {aflProfileDestination,aflProfileLink} from '../afl-profile-links.js';
const full=JSON.parse(fs.readFileSync('data/afl/full-2026.json'));
test('only independently verified ProspectRank profiles receive external links',()=>{
 const verified=JSON.parse(fs.readFileSync('docs/website/prospectrank-link-verification.json'));
 for(const p of full.players){const match=verified.find(r=>r.mlbamId===p.mlbamId);assert.equal(aflProfileDestination(p,full),match.verified?`https://www.prospect-portfolio.com/player/mlb_${p.mlbamId}`:null);}
 assert.match(aflProfileLink({mlbamId:805795},full),/ProspectRank/);assert.match(aflProfileLink({mlbamId:805795},full),/target="_blank"/);
});
test('name changes, accents and two-way eligibility cannot switch the stable player identity',()=>{
 const p=full.players.find(p=>p.mlbamId===805795);for(const name of ['José García','Jose Garcia','Same Name'])assert.equal(aflProfileDestination({...p,name,type:'TW'},full),`https://www.prospect-portfolio.com/player/mlb_${p.mlbamId}`);
});
test('missing, duplicated or unsupported profile IDs fail closed',()=>{
 assert.equal(aflProfileDestination({name:full.players[0].name},full),null);
 assert.equal(aflProfileDestination({mlbamId:999999999},full),null);
 assert.equal(aflProfileDestination(full.players[0],{...full,players:[full.players[0],full.players[0]]}),null);
 assert.match(aflProfileLink({mlbamId:999999999},full),/unavailable/);
 assert.ok(!aflProfileLink({mlbamId:999999999},full).includes('href'));
});
