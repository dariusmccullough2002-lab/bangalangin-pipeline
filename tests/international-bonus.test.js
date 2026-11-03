import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {internationalBonus,compareInternationalBonuses} from '../international-bonus.js';
const data=JSON.parse(readFileSync('data/international/2027.json'));
const get=id=>data.players.find(p=>p.id===id);
test('current reported amounts retain qualifications and avoid superseded agreements',()=>{
 assert.equal(internationalBonus(get('mairon-de-la-rosa')).amount,3800000);
 assert.equal(internationalBonus(get('junior-fortunato')).amount,3200000);
 assert.equal(internationalBonus(get('marko-morua')).label,'>$500K');
 assert.equal(internationalBonus(get('cristian-oscar-lias-bieneme')).label,'≈ $2M');
 assert.equal(internationalBonus(get('rodelvis-santiesteban')).label,'$20K');
 assert.match(internationalBonus(get('rodelvis-santiesteban')).detail,/scholarship/);
 assert.equal(internationalBonus(get('shoki-oda')).label,'TBD');
 assert.equal(internationalBonus({scoutingParagraphs:['Former agreement $70,000']}).amount,null);
 assert.equal(internationalBonus({signingBonus:250000,reportedBonusExpectation:'$300K'}).amount,250000);
 for(const value of [null,0,-1,NaN,Infinity,'250000'])assert.equal(internationalBonus({signingBonus:value}).amount,null);
});
test('both bonus sort directions keep unknowns last and use Pipeline rank for ties',()=>{
 for(const direction of ['asc','desc']){
  const sorted=[...data.players].sort((a,b)=>compareInternationalBonuses(a,b,direction));
  let unknown=false,previous=null;
  for(const p of sorted){
   const amount=internationalBonus(p).amount;
   if(amount===null){unknown=true;continue;}
   assert.equal(unknown,false);
   if(previous!==null)assert.ok(direction==='asc'?amount>=previous:amount<=previous);
   previous=amount;
  }
  assert.equal(new Set(sorted.map(p=>p.id)).size,data.players.length);
 }
 const ties=[{pipelineRank:4,reportedBonusExpectation:'$4M'},{pipelineRank:3,reportedBonusExpectation:'$4M'}];
 assert.equal(ties.sort(compareInternationalBonuses)[0].pipelineRank,3);
});
