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
 assert.deepEqual(get('marko-morua'),{height:'Not verified',weight:'Not verified'});
 for(const p of data.players){const m=internationalMeasurements(p);assert.ok(!/undefined|null|kg|cm/.test(m.height+' '+m.weight));}
});
