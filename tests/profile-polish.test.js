import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import {entryHistoryHtml} from '../profile-polish.js';
const history=JSON.parse(fs.readFileSync(new URL('../data/player-entry-history.json',import.meta.url)));
const checkpoints=JSON.parse(fs.readFileSync(new URL('../data/development-checkpoints.json',import.meta.url)));
test('every existing player route has a sourced original-entry record or explicit unsigned/overseas status',()=>{
 for(const [route,p] of Object.entries(checkpoints.entries)){
  const entry=history.entries[route];assert.ok(entry,route);assert.equal(entry.name,p.name,route);
  assert.ok(entry.summary);assert.ok(entry.sources.length,route);
  assert.ok(['draft','signing','independent','unsigned','overseas'].includes(entry.kind),route);
  if(entry.kind==='draft'){assert.ok(entry.year);assert.ok(entry.team);}
  if(entry.signingDate)assert.ok(Number.isFinite(Date.parse(entry.signingDate)));
 }
});
test('entry histories keep original affiliations, school and independent acquisitions distinct',()=>{
 const rows=Object.values(history.entries);
 const riley=rows.find(p=>p.name==='Riley Thompson');assert.equal(riley.team,'Chicago Cubs');assert.equal(riley.year,'2018');assert.equal(riley.school,'Louisville');
 const walcott=rows.find(p=>p.name==='Sebastian Walcott');assert.equal(walcott.team,'Texas Rangers');assert.equal(walcott.signingDate,'2023-01-15');
 const gillis=rows.find(p=>p.name==='Brock Gillis');assert.equal(gillis.kind,'independent');assert.match(gillis.detail,/Yuba-Sutter/);
 const oda=rows.find(p=>p.name==='Shoki Oda');assert.equal(oda.kind,'unsigned');
 const nogami=rows.find(p=>p.name==='Tatsuya Nogami');assert.equal(nogami.signingDate,'2026-10-15');
});
test('sidebar entry renderer escapes record text and retains sources',()=>{
 const html=entryHistoryHtml({summary:'<script>bad</script>',detail:'A & B',sources:[{url:'https://example.com/',label:'Official record'}]});
 assert.ok(!html.includes('<script>'));assert.match(html,/A &amp; B/);assert.match(html,/Entry into pro baseball/);assert.match(html,/noopener noreferrer/);
});
