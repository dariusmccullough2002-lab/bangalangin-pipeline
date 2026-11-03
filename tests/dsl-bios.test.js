import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {dslAge} from '../dsl.js';
const data=JSON.parse(readFileSync('data/dsl/2026.json'));
const get=name=>data.players.find(p=>p.name===name);
test('DSL ages advance on birthdays rather than using a stale season age',()=>{
 assert.equal(dslAge(get('Yostin Peña'),'2026-10-18'),'18');
 assert.equal(dslAge(get('Yostin Peña'),'2026-10-19'),'19');
 assert.equal(dslAge(get('Angeibel Gomez'),'2026-11-03'),'17');
 assert.equal(dslAge(get('Angeibel Gomez'),'2026-12-12'),'18');
 assert.equal(dslAge({},'2026-11-03'),'—');
});
test('all 35 DSL nations come from matched MLB identity records',()=>{
 assert.equal(data.players.length,35);
 assert.equal(get('Angeibel Gomez').identity.birthCountry,'Venezuela');
 assert.equal(get('Joniel Hernandez').identity.birthCountry,'Cuba');
 assert.equal(get('Luis Garces').identity.birthCountry,'Colombia');
 for(const p of data.players){assert.ok(p.identity.birthCountry);assert.ok(p.identity.birthDate);assert.ok(p.identity.bioSource.sourceUrl.endsWith('/'+p.mlbamId));}
});
