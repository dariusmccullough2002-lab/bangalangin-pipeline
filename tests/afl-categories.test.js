import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {AFL_CATEGORIES,aflCategory,filterAflPlayers,indexAflStats} from '../afl-board.js';
const data=JSON.parse(readFileSync('data/afl/full-2026.json')),stats=indexAflStats(data.statsSnapshot);
test('category tabs partition all currently filtered AFL players without changing indicator rules',()=>{
 const all=filterAflPlayers(data.players,{},stats),ids=[];
 for(const c of AFL_CATEGORIES.filter(c=>c.id!=='all')){const rows=filterAflPlayers(data.players,{category:c.id},stats);for(const p of rows){assert.equal(aflCategory(p,stats[p.type].get(p.mlbamId)),c.id);ids.push(p.mlbamId);}}
 assert.equal(ids.length,all.length);assert.equal(new Set(ids).size,all.length);
 assert.deepEqual([...ids].sort(),all.map(p=>p.mlbamId).sort());
});
test('performance category combines with team, role, search and past participant filters',()=>{
 const strong=filterAflPlayers(data.players,{category:'strong-hitting'},stats);assert.ok(strong.length>0);
 const p=strong[0];assert.ok(filterAflPlayers(data.players,{category:'strong-hitting',team:String(p.aflTeamId),type:'H',query:p.name,played:true},stats).includes(p));
 assert.deepEqual(filterAflPlayers(data.players,{category:'strong-hitting',type:'P'},stats),[]);
 assert.equal(aflCategory({type:'H'},null),'awaiting');
 assert.equal(aflCategory({type:'H'},{plateAppearances:8,ops:'1.200'}),'early');
 assert.equal(aflCategory({type:'H'},{plateAppearances:8,ops:'.500'}),'struggling-hitting');
 assert.equal(aflCategory({type:'H'},{plateAppearances:3,ops:'1.200'}),'small');
 assert.equal(aflCategory({type:'H'},{plateAppearances:30,ops:'.800'}),'mixed');
 assert.equal(aflCategory({type:'P'},{inningsPitched:'2.0',battersFaced:9,strikeOuts:1,baseOnBalls:2,era:'9.00'}),'struggling-pitching');
});
