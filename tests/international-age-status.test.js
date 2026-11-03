import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {internationalAge,internationalStatus} from '../amateurs.js';
const data=JSON.parse(readFileSync('data/international/2027.json'));
const get=id=>data.players.find(p=>p.id===id);
test('ages respect birthdays and distinguish dated reporting from birth dates',()=>{
 assert.equal(internationalAge(get('alfredo-sena'),'2026-11-01').label,'16');
 assert.equal(internationalAge(get('alfredo-sena'),'2026-11-02').label,'17');
 assert.equal(internationalAge(get('junior-fortunato'),'2026-11-03').label,'16');
 assert.equal(internationalAge(get('enyel-gonzalez'),'2026-11-03').label,'16');
 assert.equal(internationalAge(get('anthony-calderon'),'2026-11-03').label,'17*');
 assert.equal(internationalAge(get('cristian-oscar-lias-bieneme'),'2026-11-03').label,'16*');
 assert.equal(internationalAge(get('eudi-yuten'),'2026-11-03').label,'17*');
 for(const id of ['nicolas-quintero','jesus-arteaga','dylan-rodriguez','axel-carrasco','eddy-hernandez','wilson-reyes'])assert.equal(internationalAge(get(id),'2026-11-03').label,'16*');
 for(const id of ['eudi-yuten','axel-carrasco'])assert.ok(!get(id).birthDate);
 assert.equal(internationalAge({classYear:2027,age:16},'2026-11-03').label,'—');
});
test('short table statuses retain the distinction between reported and official',()=>{
 assert.deepEqual(internationalStatus(get('marko-morua')),{label:'Reported agreement',kind:'reported'});
 assert.equal(internationalStatus(get('anthony-calderon')).label,'Physical pending');
 assert.equal(internationalStatus(get('shoki-oda')).label,'Route pending');
 assert.equal(internationalStatus(get('tatsuya-nogami')).label,'Signed');
 assert.equal(internationalStatus(get('jhonny-damon-proenza')).label,'Unsigned');
 assert.equal(internationalStatus(get('joh-sung-chul')).label,'Finalizing agreement');
 assert.ok(get('marko-morua').signingStatus.includes('Jan 2027'));
});
