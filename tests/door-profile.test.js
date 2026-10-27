import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import {loadDoorWatch,showKnockingDoor,doorProfilePage,doorProfileRibbon,doorBreakdownRoute,findDoorPlayer} from '../knocking-door.js';
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
  assert.ok(html.includes('What the record tells us'),player.name);assert.ok(html.includes('What would move him closer'),player.name);assert.equal(player.research.checkpoints.length,2);assert.ok(player.research.assessment.length>180,player.name);
  if(player.sourceUpdate)assert.ok(html.includes(player.sourceUpdate.url),player.name);
 }
 assert.equal(unique.size,30);
 for(const player of edition.rankings.filter(p=>!findDoorPlayer(p))){assert.equal(doorProfilePage(player),'');assert.equal(doorProfileRibbon(player),'');}
 const archived={mlbamId:String(watch.players[0].mlbamId)};
 assert.ok(doorProfileRibbon(archived).includes(doorBreakdownRoute(watch.players[0])));
});

test('compact tiles retain every breakdown link and explain filters without the removed intro',async()=>{
 const original={fetch:globalThis.fetch,location:globalThis.location,localStorage:globalThis.localStorage};
 globalThis.fetch=async url=>({ok:true,json:async()=>JSON.parse(fs.readFileSync(new URL('../'+String(url).replace(/^\//,''),import.meta.url)))});
 globalThis.location={hash:'#knocking-on-door'};globalThis.localStorage={getItem:()=>null,setItem:()=>{}};
 const filters=Object.fromEntries(['path','org','type'].map(k=>[`#door-${k}`,{value:''}]));
 const help={},count={},deck={classList:{toggle(){}},setAttribute(){},innerHTML:''};
 const buttons=['tiles','list'].map(view=>({dataset:{doorView:view},setAttribute(){}}));
 const app={innerHTML:'',querySelector:s=>s==='.door-deck'?deck:s==='#door-count'?count:s==='#door-filter-help'?help:filters[s],querySelectorAll:s=>s==='.door-filters select'?Object.values(filters):buttons};
 try{
  await showKnockingDoor(app);
  assert.ok(!app.innerHTML.includes('door-intro'));assert.ok(!app.innerHTML.includes('An opening matters'));assert.ok(app.innerHTML.includes('What do the roster paths mean?'));
  assert.equal((deck.innerHTML.match(/class="door-card"/g)||[]).length,30);
  assert.equal((deck.innerHTML.match(/class="door-breakdown-link"/g)||[]).length,30);
  assert.ok(!deck.innerHTML.includes('door-case'));assert.ok(!deck.innerHTML.includes('door-evidence'));assert.ok(!deck.innerHTML.includes('door-research-assessment'));
  for(const key of ['rotation','lane','development']){filters['#door-path'].value=key;filters['#door-path'].onchange();assert.equal(help.hidden,false);assert.ok(help.textContent.length>80);assert.equal(count.textContent,`${watch.players.filter(p=>p.path===key).length} players`);}
  filters['#door-path'].value='';filters['#door-path'].onchange();assert.equal(help.hidden,true);
  buttons[1].onclick();assert.equal((deck.innerHTML.match(/class="door-breakdown-link"/g)||[]).length,30);
 }finally{Object.assign(globalThis,original);}
});
