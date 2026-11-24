import test from 'node:test';import assert from 'node:assert/strict';import fs from 'node:fs';
import {homeResearch} from '../home-research.js';import {archiveTabs,archiveShell,archiveTabForRoute,showArchive} from '../archive.js';
import {entryHistoryHtml} from '../profile-polish.js';
const read=p=>fs.readFileSync(new URL('../'+p,import.meta.url),'utf8');
test('Research showcase keeps three direct tools, a dominant featured card and the existing carousel',()=>{
 const html=homeResearch();for(const route of ['power-translation-lab','afl','winter-ball'])assert.ok(html.includes('href="#'+route+'"'));
 assert.equal((html.match(/<a class="research-card/g)??[]).length,3);
 assert.ok(html.includes('research-card-featured'));assert.ok(html.includes('CBS+'));assert.equal((html.match(/<svg/g)??[]).length,3);
 const app=read('app.js');assert.ok(app.indexOf('${homeFeature(currentEdition,homeInputs)}${homeResearch()}<section class="home-organizations">')>0);assert.ok(app.includes('homeFeatureCleanup=activateHomeFeature(app,homeInputs)'));
});
test('Explore contains exactly the seven requested entries and Archive has four accessible tabs',()=>{
 const nav=read('index.html').split('<summary>Explore</summary>')[1].split('</details>')[0];
 assert.deepEqual([...nav.matchAll(/<a[^>]*>(.*?)<\/a>/g)].map(m=>m[1]),['Knocking on the Door','Trade Analyzer (Beta)','Mock Draft Room','Arizona Fall League','Winter Ball Watch','Power Translation Lab','Archive']);
 assert.ok(!nav.includes('<details'));const shell=archiveShell();assert.equal((shell.match(/role="tab"/g)??[]).length,4);assert.equal((shell.match(/role="tabpanel"/g)??[]).length,4);
 for(const t of archiveTabs){assert.equal(archiveTabForRoute(t.legacy),t.id);assert.equal(archiveTabForRoute('archive',t.id),t.id);assert.ok(shell.includes('aria-controls="archive-panel-'+t.id+'"'));}
 assert.equal(archiveTabForRoute('archive'),'august');assert.equal(archiveTabForRoute('player','jacob-reimer'),null);
});
// Minimal DOM surface exercises panel lifetime and races without a browser dependency.
function archiveFixture(){
 const nodes=new Map(),links=[];for(const t of archiveTabs){const tab={id:'archive-tab-'+t.id,attributes:{},setAttribute(k,v){this.attributes[k]=v;},addEventListener(){}};links.push(tab);nodes.set('#'+tab.id,tab);nodes.set('#archive-panel-'+t.id,{hidden:true,innerHTML:'',attributes:{},setAttribute(k,v){this.attributes[k]=v;},removeAttribute(k){delete this.attributes[k];},querySelectorAll(){return [];}});}
 const shell={querySelector:s=>nodes.get(s),querySelectorAll:()=>links,contains:n=>[...nodes.values()].includes(n)};const app={attached:false,contains:n=>app.attached&&n===shell,querySelector:()=>shell,set innerHTML(v){app.attached=true;}};return {app,shell,nodes};
}
const settle=()=>new Promise(resolve=>setImmediate(resolve));
test('Archive switches cached panels without rebuilding roster state',async()=>{
 const {app,nodes}=archiveFixture(),calls={};const renderers=Object.fromEntries(archiveTabs.map(t=>[t.id,p=>{calls[t.id]=(calls[t.id]??0)+1;p.innerHTML=t.label;}]));
 showArchive(app,'august',renderers);await settle();showArchive(app,'rosters',renderers);await settle();const roster=nodes.get('#archive-panel-rosters');roster.innerHTML='Saved roster filter';
 showArchive(app,'farms',renderers);await settle();showArchive(app,'rosters',renderers);await settle();assert.equal(roster.innerHTML,'Saved roster filter');assert.equal(calls.rosters,1);assert.equal(roster.hidden,false);assert.equal(nodes.get('#archive-panel-farms').hidden,true);assert.equal(nodes.get('#archive-tab-rosters').attributes['aria-selected'],'true');
});
test('Leaving Archive prevents a deferred renderer from starting on another page',async()=>{
 const {app}=archiveFixture();let called=false;showArchive(app,'august',{august:()=>{called=true;}});app.attached=false;await settle();assert.equal(called,false);
});
test('Responsive layout stacks research cards and keeps tabs horizontally scrollable',()=>{
 const css=read('styles.css');assert.match(css,/@media\(max-width:750px\)\{\.research-cards\{grid-template-columns:1fr\}/);assert.match(css,/\.archive-tabs\{[^}]*overflow-x:auto;flex-wrap:nowrap/);assert.ok(css.includes('.archive-content[hidden]{display:none!important}'));
});
test('Entry cards show reported agreements and contract values without inventing completed signings',()=>{
 const entries=JSON.parse(read('data/player-entry-history.json')).entries;
 for(const [route,team]of [['international-pro-player/teruaki-sato','Chicago Cubs'],['international-pro-player/kaima-taira','Toronto Blue Jays'],['international-player/kosei-hiroike','New York Yankees']]){const row=entries[route],html=entryHistoryHtml(row);assert.equal(row.team,team);assert.ok(html.includes('Agreement reported'));assert.ok(!row.signingDate);assert.match(html,/pending|not yet verified/);assert.ok(row.sources.every(s=>s.url.startsWith('https://')));}
 assert.ok(entryHistoryHtml(entries['international-pro-player/teruaki-sato']).includes('$120,000,000'));assert.ok(entryHistoryHtml(entries['international-pro-player/kaima-taira']).includes('$80,000,000'));
});

test('Existing roster filters and farm rankings render inside Archive with their original data',async()=>{
 const {showRosters}=await import('../rosters.js'),{showOctober}=await import('../october.js');
 const originalFetch=globalThis.fetch,originalLocation=globalThis.location;
 globalThis.fetch=async path=>({ok:true,json:async()=>JSON.parse(read(String(path).replace(/^\//,'')))});
 globalThis.location={hash:'#archive/rosters'};
 try{
  const nodes=Object.fromEntries(['roster-search','roster-team','roster-status','roster-count','roster-rows'].map(id=>['#'+id,{value:'',innerHTML:'',textContent:'',handlers:{},addEventListener(k,fn){this.handlers[k]=fn;}}]));
  const panel={innerHTML:'',querySelector:s=>nodes[s]};await showRosters(panel,{isCurrent:()=>true});
  const snapshot=JSON.parse(read('data/ownership-snapshots/current.json')),team=snapshot.teams.find(t=>t.players.length);
  assert.ok(panel.innerHTML.includes('The current rosters'));nodes['#roster-team'].value=team.fantraxTeamId;nodes['#roster-team'].handlers.input();assert.equal(nodes['#roster-count'].textContent,team.players.length+' players shown');
  const name=team.players[0].name;nodes['#roster-search'].value=name;nodes['#roster-search'].handlers.input();assert.ok(nodes['#roster-rows'].innerHTML.includes(name));assert.equal(nodes['#roster-count'].textContent,team.players.filter(p=>p.name.toLowerCase().includes(name.toLowerCase())).length+' players shown');
  globalThis.location.hash='#archive/farms';const farm={innerHTML:''},organizations=JSON.parse(read('data/organizations.json'));
  await showOctober(farm,'october-farms',undefined,organizations,null,{isCurrent:()=>true});assert.ok(farm.innerHTML.includes('Farm System Power Rankings'));assert.ok(farm.innerHTML.includes('#october-farm-method'));assert.ok(farm.innerHTML.includes('class="farmtable"'));
 }finally{globalThis.fetch=originalFetch;if(originalLocation===undefined)delete globalThis.location;else globalThis.location=originalLocation;}
});
