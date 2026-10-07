import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
const read=p=>JSON.parse(readFileSync(p,'utf8'));
const h=read('data/transactions.json'),edition=read('data/editions/october-2026.json'),reports=read('data/profile-reports.json');
test('live histories match stable player IDs and preserve source dates without deleted markers',()=>{
 for(const [id,p] of Object.entries(h.livePlayers)){
  assert.equal(edition.rankings.find(r=>r.fantraxId===id)?.name,p.name);
  assert.ok(p.rows.length);
  for(const row of p.rows){assert.equal(row.length,3);assert.doesNotMatch(row.join(' '),/\(\*deleted\*\)/i);assert.match(row[0],/202[0-9]$/);}
 }
 const w=h.livePlayers['06n8y'].rows;
 assert.ok(w.some(r=>r[2].includes('Ronald Acuna Jr.')&&r[2].includes('Emil Morales')));
 assert.ok(w.some(r=>r[1].startsWith('Drafted')&&r[2]==='Round 1, pick 7'));
 assert.equal(h.importAudit.exportAssetCount,217);
 assert.equal(h.trades.filter(t=>t.sourceId==='fantrax-trade-export-2026').flatMap(t=>t.assets).length,217);
});
test('missing live histories are disclosed and profile reports cover every unchanged ranking identity',async()=>{
 const module=await import('../profile-history.js');
 const oldFetch=global.fetch;global.fetch=async url=>({ok:true,json:async()=>url.includes('transactions')?h:reports});
 try{await module.loadProfileHistory();for(const p of edition.rankings){assert.equal(reports.profiles[p.playerId].name,p.name);assert.ok(reports.profiles[p.playerId].paragraphs.length>=2);}
 assert.equal(Object.keys(h.livePlayers).length,edition.rankings.length);for(const p of edition.rankings){assert.ok(h.livePlayers[p.fantraxId]);assert.doesNotMatch(module.transactionHistory(p),/\$\{esc/);assert.match(module.transactionHistory(p),/captured October [67], 2026/);assert.doesNotMatch(module.transactionHistory(p),/not yet been captured/);}
 assert.match(module.acquisitionContext(edition.rankings.find(p=>p.name==='Eli Willits')),/Ronald Acuna Jr/);assert.match(module.acquisitionContext(edition.rankings.find(p=>p.name==='Eli Willits')),/Round 1, pick 7/i);const leo=module.acquisitionContext(edition.rankings.find(p=>p.name==='Leo De Vries'));assert.match(leo,/eight minutes/);assert.match(leo,/Casey Schmitt/);assert.match(leo,/Jordan Walker/);for(const p of edition.rankings)assert.ok(module.acquisitionContext(p).length>100);
 }finally{global.fetch=oldFetch;}
});
