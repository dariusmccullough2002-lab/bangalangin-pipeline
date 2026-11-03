import test from 'node:test';
import assert from 'node:assert/strict';
import {internationalMeasurements} from '../amateurs.js';
import {readFileSync} from 'node:fs';
const data=JSON.parse(readFileSync('data/international/2027.json'));
test('reported international measurements display feet/inches and pounds; metric conversions are approximate',()=>{
 const get=id=>internationalMeasurements(data.players.find(p=>p.id===id));
 assert.deepEqual(internationalMeasurements({measurements:{height:'186 cm',weightKg:81}}),{height:'≈ 6 ft 1 in',weight:'≈ 179 lb'});
 assert.deepEqual(get('joh-sung-chul'),{height:'≈ 6 ft 2 in',weight:'≈ 225 lb'});
 assert.deepEqual(get('alfredo-sena'),{height:'5 ft 11 in',weight:'185 lb'});
 assert.deepEqual(get('edenis-cruz'),{height:'6 ft 4 in',weight:'Not verified'});
 assert.deepEqual(get('marko-morua'),{height:'6 ft 0 in',weight:'175 lb'});
 for(const p of data.players){const m=internationalMeasurements(p);assert.ok(!/undefined|null|kg|cm/.test(m.height+' '+m.weight));}
});

test('bio research provides dated sources and preserves explicit remaining gaps',()=>{
 const get=id=>data.players.find(p=>p.id===id);
 assert.equal(data.players.length,47);
 assert.ok(data.players.every(p=>p.country));
 assert.deepEqual(internationalMeasurements(get('carlos-adrian-hernandez-cuba')),{height:'≈ 6 ft 1 in',weight:'Not verified'});
 assert.deepEqual(internationalMeasurements(get('cai-chen-long')),{height:'≈ 5 ft 10 in',weight:'≈ 176 lb'});
 assert.deepEqual(internationalMeasurements(get('luis-garcia-nicaragua-2027')),{height:'≈ 5 ft 10 in',weight:'≈ 165 lb'});
 assert.deepEqual(internationalMeasurements(get('enyel-gonzalez')),{height:'≈ 5 ft 10 in',weight:'≈ 174 lb'});
 assert.equal(get('raider-sanchez-trutie').bats,'R');
 assert.equal(get('raider-sanchez-trutie').throws,'R');
 assert.deepEqual(internationalMeasurements(get('eudi-yuten')),{height:'Not verified',weight:'Not verified'});
 for(const p of data.players)for(const e of p.bioEvidence??[]){assert.match(e.sourceUrl,/^https:\/\//);assert.equal(e.retrievedDate,'2026-11-03');assert.ok(e.note);}
});
