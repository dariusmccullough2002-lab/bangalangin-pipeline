import test from 'node:test';import assert from 'node:assert/strict';import {readFileSync} from 'node:fs';
const s=JSON.parse(readFileSync('data/ownership-snapshots/2026-10-06.json'));
test('October snapshot covers 12 organizations with unique ownership',()=>{assert.equal(s.teams.length,12);const ps=s.teams.flatMap(t=>t.players);assert.equal(ps.length,827);assert.equal(new Set(ps.map(p=>p.fantraxId)).size,827);assert(ps.every(p=>p.name&&p.status));assert.equal(s.scope,'league-wide')});
test('uncertain identities are not silently merged',()=>{assert.equal(s.identityReview.length,8);const blocked=new Set(s.identityReview.flatMap(x=>x.candidateFantraxIds));for(const p of s.teams.flatMap(t=>t.players)){if(blocked.has(p.fantraxId))assert.equal(p.archivePlayerId,null)}});
