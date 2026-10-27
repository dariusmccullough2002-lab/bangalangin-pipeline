import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import {loadDoorWatch,doorProfilePage,doorProfileRibbon,doorBreakdownRoute,findDoorPlayer} from '../knocking-door.js';
const watch=JSON.parse(fs.readFileSync(new URL('../data/knocking-door-2027.json',import.meta.url)));
const edition=JSON.parse(fs.readFileSync(new URL('../data/editions/october-2026.json',import.meta.url)));
test('all 30 watchlist members get their own sourced profile chapter and direct ribbon URL; others get neither',async()=>{
 const original=globalThis.fetch;
 globalThis.fetch=async url=>({ok:true,json:async()=>JSON.parse(fs.readFileSync(new URL('../'+String(url).replace(/^\//,''),import.meta.url)))});
 try{await loadDoorWatch();}finally{globalThis.fetch=original;}
 assert.equal(watch.players.length,30);
 const unique=new Set();
 for(const player of watch.players){
  const profile=edition.rankings.find(p=>p.playerId===player.playerId);assert.ok(profile,player.name);
  const href=doorBreakdownRoute(player);unique.add(href);
  assert.ok(doorProfileRibbon(profile).includes(`href="${href}"`),player.name);
  const html=doorProfilePage(profile);assert.ok(html.includes('data-door-profile'),player.name);assert.ok(html.includes(player.scoutUrl),player.name);assert.ok(html.includes('The route to a call-up'),player.name);assert.ok(html.includes('What to prove'),player.name);assert.ok(!html.includes('door-monogram'));
 }
 assert.equal(unique.size,30);
 for(const player of edition.rankings.filter(p=>!findDoorPlayer(p))){assert.equal(doorProfilePage(player),'');assert.equal(doorProfileRibbon(player),'');}
 const archived={mlbamId:String(watch.players[0].mlbamId)};
 assert.ok(doorProfileRibbon(archived).includes(doorBreakdownRoute(watch.players[0])));
});
