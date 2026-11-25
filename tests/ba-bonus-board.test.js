import test from 'node:test';import assert from 'node:assert/strict';import fs from 'node:fs';import {execFileSync} from 'node:child_process';
import {bonusProfile,bonusRankLabel,sortBonusRows,internationalBoard} from '../ba-bonus-board.js';
import {internationalBonus} from '../international-bonus.js';import {internationalAge,internationalStatus,amateurSearchText} from '../amateurs.js';import {matchesInternationalClass} from '../international-class.js';
const d=JSON.parse(fs.readFileSync('data/international/2027.json'));const old=JSON.parse(execFileSync('git',['show','HEAD:data/international/2027.json'],{encoding:'utf8'}));
test('all 50 bonus assignments are verified once, independent talent and precise estimates retained',()=>{
 const rows=d.players.filter(p=>p.baBonusRank!=null);assert.equal(rows.length,50);assert.deepEqual(rows.map(p=>p.baBonusRank).sort((a,b)=>a-b),Array.from({length:50},(_,i)=>i+1));assert.ok(rows.every(p=>p.baBonusVerificationStatus==='verified-indexed-source'));
 for(const p of old.players){const next=d.players.find(x=>x.id===p.id);assert.ok(next);assert.equal(next.pipelineRank,p.pipelineRank);assert.equal(next.reportedBonusExpectation,p.reportedBonusExpectation);}
 assert.equal(internationalBonus(d.players.find(p=>p.id==='alfredo-sena')).amount,5800000);assert.equal(d.players.find(p=>p.baBonusRank===22).expectedOrganization,'CHW');assert.equal(d.players.find(p=>p.baBonusRank===41).expectedOrganization,'TEX');assert.equal(new Set(d.players.map(p=>p.id)).size,d.players.length);
});
test('profiles, sorting and nulls keep source order separate from talent',()=>{
 const rows=d.players.filter(p=>p.baBonusRank);const sorted=sortBonusRows(rows,'ba');assert.equal(sorted[0].id,'alfredo-sena');assert.equal(sorted.at(-1).id,'luis-advincola');for(const dir of ['asc','desc'])assert.equal(sortBonusRows(d.players,'ba',dir).at(-1).baBonusRank,null);
 const oda=d.players.find(p=>p.id==='shoki-oda');assert.equal(bonusRankLabel(oda),'—');assert.match(bonusProfile(oda),/no talent penalty/);for(const p of rows){assert.match(bonusProfile(p),/2026-11-25/);assert.ok(p.scoutingParagraphs.length>=2);assert.ok(!bonusProfile(p).includes('undefined'));}
 const yeremy=d.players.find(p=>p.id==='yeremy-de-leon');assert.equal(yeremy.mlbamId,845259);assert.equal(yeremy.signingClass,2026);assert.equal(yeremy.baBonusRank,null);
});
test('ranking selector, search and column sorting retain working clickable profiles',()=>{
 const nodes=new Map();const node=id=>{if(!nodes.has(id))nodes.set(id,{value:'',dataset:{},setAttribute(){}});return nodes.get(id);};const app={innerHTML:'',querySelector:q=>node(q.slice(1)),querySelectorAll:()=>[]};node('am-ranking').value='pipeline';internationalBoard(app,d,{age:internationalAge,status:internationalStatus,searchText:amateurSearchText,matchesClass:matchesInternationalClass});
 assert.match(app.innerHTML,/Pipeline Rankings/);assert.match(app.innerHTML,/BA Bonus Board/);assert.match(app.innerHTML,/Projected Signing Bonus/);node('am-ranking').value='ba';node('am-ranking').onchange();assert.match(node('am-count').textContent,/50 of 50/);assert.match(node('am-rows').innerHTML,/#international-player\/alfredo-sena/);node('am-search').value='Eudy Yuten';node('am-search').oninput();assert.match(node('am-count').textContent,/1 of 50/);assert.match(node('am-rows').innerHTML,/international-player\/eudi-yuten/);
});
