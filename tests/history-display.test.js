import test from 'node:test';
import assert from 'node:assert/strict';
import {historyTables} from '../trade-analyzer-beta/history-display.js';
import fs from 'node:fs';
import zlib from 'node:zlib';
const html=fs.readFileSync(new URL('../trade-analyzer-beta/index.html',import.meta.url),'utf8');
const data=JSON.parse(zlib.gunzipSync(Buffer.from(html.match(/const packed='([^']+)'/)[1],'base64')));
test('Misiorowski preserved 2026 MLB strikeouts and HR allowed remain separate',()=>{
 const row=data.assets.find(a=>a.name==='Jacob Misiorowski').career_profile.seasons.find(r=>r.year===2026);
 assert.equal(row.id,694819);assert.equal(row.stat.K,252);assert.equal(row.stat.HR,14);
 const [headers,values]=historyTables([row])[0];assert.equal(values[headers.indexOf('K')],'252.0');assert.equal(values[headers.indexOf('HR allowed')],'14.0');assert.equal(values[headers.indexOf('ER')],'35.0');assert.equal(headers.length,values.length);
});
test('missing K never falls back to HR and genuine zeros remain zero',()=>{
 const [headers,...rows]=historyTables([{year:2026,role:'RP',stat:{HR:14}},{year:2025,role:'SP',stat:{K:0,HR:2}},{year:2024,role:'SP',stat:{},skills:{strikeOuts:87,homeRuns:8}}])[0];
 assert.equal(rows[0][headers.indexOf('K')],'unavailable');assert.equal(rows[1][headers.indexOf('K')],'0.0');assert.equal(rows[2][headers.indexOf('K')],'87.0');
});
test('all existing history rows have aligned columns and explicit pitching mapping',()=>{
 for(const asset of data.assets){const seasons=asset.career_profile?.seasons??[];for(const [headers,...rows] of historyTables(seasons)){for(const row of rows) assert.equal(row.length,headers.length);}for(const season of seasons.filter(r=>r.role!=='H')){const [headers,row]=historyTables([season])[0];const k=season.stat.K??season.skills?.strikeOuts;assert.equal(row[headers.indexOf('K')],k==null?'unavailable':Number(k).toFixed(1));}}
});
test('MLB histories contain no duplicate player-season-level pitching totals',()=>{
 for(const asset of data.assets){const keys=(asset.career_profile?.seasons??[]).filter(r=>r.role!=='H').map(r=>`${r.id}:${r.year}:${r.level??'MLB'}`);assert.equal(new Set(keys).size,keys.length,asset.name);}
});
test('cached minor-league aggregate K matches distinct team/level splits',()=>{
 const profiles=JSON.parse(fs.readFileSync(new URL('../data/research/october-2026-evidence.json',import.meta.url),'utf8'));
 let checked=0;for(const p of profiles){const s=p.seasonStats;for(const g of s?.groups??[]){if(g.group!=='pitching')continue;const splits=s.splits.filter(r=>r.group==='pitching');assert.equal(g.strikeOuts,splits.reduce((n,r)=>n+r.k,0));const keys=splits.map(r=>`${r.level}:${r.team}:${r.group}`);assert.equal(new Set(keys).size,keys.length);checked++;}}assert.equal(checked,80);
});
