import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import {buildProfileIndex,findProfiles} from '../home-search.js';
const read=p=>JSON.parse(fs.readFileSync(`data/${p}`,'utf8'));
const current=read('editions/october-2026.json'),archive=read('editions/august-2026.json'),players=read('players.json'),draft=read('draft/2026.json'),international=read('international/2027.json');
const index=buildProfileIndex(current,archive,players,draft,international);
test('homepage search routes only to available profiles and prefers current MLBAM identities',()=>{
 assert.equal(index.filter(p=>p.route.startsWith('#october-player/')).length,current.rankings.length);
 assert.equal(new Set(index.map(p=>p.route)).size,index.length);
 for(const row of index){
  const [kind,id]=row.route.slice(1).split('/');
  if(kind==='october-player')assert.ok(current.rankings.some(p=>p.playerId===id));
  else if(kind==='draft-player')assert.ok(draft.players.some(p=>p.id===id));
  else if(kind==='international-player')assert.ok(international.players.some(p=>p.id===id));
  else {assert.equal(kind,'player');assert.ok(archive.rankings.some(p=>p.playerId===id&&p.organizationId==='shea-stadiums'));}
 }
 for(const p of draft.players.filter(p=>current.rankings.some(r=>r.mlbamId&&r.mlbamId===p.mlbamId)))assert.ok(!index.some(r=>r.route===`#draft-player/${p.id}`));
});
test('search handles accents, partial names, token order, empty queries and no matches',()=>{
 const sample=[{name:'Elian Peña',route:'#a'},{name:'A.J. Ewing',route:'#b'}];
 assert.equal(findProfiles(sample,'pena elian')[0].route,'#a');
 assert.equal(findProfiles(sample,'ewi')[0].route,'#b');
 assert.equal(findProfiles(sample,'a.j.')[0].route,'#b');
 assert.deepEqual(findProfiles(sample,'   '),[]);
 assert.deepEqual(findProfiles(sample,'no such player'),[]);
 assert.ok(findProfiles(index,'Walcott').some(p=>p.route.startsWith('#october-player/')));
 assert.ok(findProfiles(index,'Alfredo Sena').some(p=>p.route.startsWith('#international-player/')));
});

test('international additions are searchable by accents, aliases and Japanese identity',()=>{
 for(const q of ['Sebastian Perez Acuna','Sebastián Pérez','Sebastian Acuna'])assert.ok(findProfiles(index,q).some(p=>p.route==='#international-player/sebastian-perez-acuna'));
 for(const q of ['Shoki Oda','Oda Shoki','織田翔希'])assert.ok(findProfiles(index,q).some(p=>p.route==='#international-player/shoki-oda'));
});
