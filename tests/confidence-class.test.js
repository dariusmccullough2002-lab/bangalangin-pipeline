import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {internationalClass,matchesInternationalClass} from '../international-class.js';
import {scoutingConfidence} from '../scouting-confidence.js';
const board=JSON.parse(readFileSync('data/international/2027.json')).players;
test('class filters partition the board without silently assigning unresolved classes',()=>{
 const groups=['2027','2026','other'].map(c=>board.filter(p=>matchesInternationalClass(p,c)));
 assert.equal(groups.flat().length,board.length);
 assert.equal(new Set(groups.flat().map(p=>p.id)).size,board.length);
 assert.ok(board.every(p=>matchesInternationalClass(p,'')));
 assert.equal(internationalClass(board.find(p=>p.id==='shoki-oda')),'2027');
 assert.equal(internationalClass(board.find(p=>p.id==='carlos-adrian-hernandez-cuba')),'other');
 assert.equal(internationalClass(board.find(p=>p.id==='alayn-daniel-blanco')),'other');
 assert.equal(internationalClass({classYear:2026,classLabel:'2027 outdated label'}),'2026');
 const subset=board.filter(p=>matchesInternationalClass(p,'2027')&&p.expectedOrganization==='SEA'&&p.type==='H');
 assert.ok(subset.some(p=>p.id==='eudi-yuten'));
 assert.ok(subset.every(p=>p.classYear===2027));
});
test('confidence notes use recorded judgments without inventing ratings',()=>{
 assert.match(scoutingConfidence(board[0],'international'),/Moderate confidence/);
 assert.match(scoutingConfidence({},'international'),/public scouting/);
 assert.doesNotMatch(scoutingConfidence({},'draft'),/High confidence|Moderate confidence/);
 assert.match(scoutingConfidence({},'dsl'),/uneven competition/);
 assert.match(scoutingConfidence({},'afl'),/short season/);
 assert.match(scoutingConfidence({ranking:{confidence:'<bad>'}},'international'),/&lt;bad&gt;/);
 for(const kind of ['international','draft','dsl','afl','professional','archive','prospect'])assert.match(scoutingConfidence({},kind),/not talent rank/);
});
