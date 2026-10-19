import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {draftOutcomesHtml} from '../draft-outcomes.js';
const read=p=>JSON.parse(readFileSync(p));
const draft=read('data/draft/2026.json'),evidence=read('docs/draft-outcomes-20261019/Evidence.json');
test('every draft identity has individual outcomes and traceable scouting evidence',()=>{
 assert.equal(draft.players.length,112);assert.equal(evidence.playersReviewed,112);
 assert.equal(evidence.publishedPlayerReports,103);assert.equal(evidence.alternateScoutingSources,9);
 const indexed=new Map(evidence.players.map(p=>[p.id,p]));
 for(const p of draft.players){
  const o=p.outcomes,e=indexed.get(p.id);assert.equal(e.mlbamId,p.mlbamId);assert.equal(e.name,p.name);
  assert.equal(o.asOf,'2026-10-19');
  for(const field of ['ceiling','median','floor']){assert.ok(o[field].trim().length>0,`${p.id}: ${field}`);assert.notEqual(o[field],o[field==='ceiling'?'median':'ceiling']);}
  assert.ok(['Moderate','High','Very high'].includes(o.risk.level));assert.ok(o.risk.reason.length>70);
  assert.ok(['Moderate','Limited'].includes(o.confidence.level));assert.ok(o.confidence.reason.length>70);
  assert.ok(o.sources.length>=2);assert.ok(o.sources.every(s=>new URL(s.url).protocol==='https:'&&s.coverage&&s.retrievedDate));
  assert.equal(o.sources[0].url,e.source.url);assert.match(o.context,/Pipeline interpretation/);
  const html=draftOutcomesHtml(p);for(const label of ['Ceiling','Median outcome','Floor','Risk level','Research confidence','Outcome research sources'])assert.ok(html.includes(label),p.id);
 }
 assert.equal(new Set(draft.players.map(p=>p.outcomes.ceiling)).size,112);
 assert.equal(new Set(draft.players.map(p=>p.outcomes.risk.reason)).size,112);
});
test('source limitations and medical or role distinctions survive rendering',()=>{
 const by=Object.fromEntries(draft.players.map(p=>[p.id,p]));
 assert.equal(by['will-plunkett'].outcomes.confidence.level,'Limited');assert.match(by['will-plunkett'].outcomes.sources[0].coverage,/Indexed/);
 assert.match(by['carson-wiggins'].outcomes.median,/reliever/);assert.match(by['carson-wiggins'].outcomes.risk.reason,/internal-brace/);
 assert.match(by['brody-bumila'].outcomes.risk.reason,/internal-brace.*Tommy John/);
 assert.match(by['a-j-gracia'].outcomes.risk.reason,/labrum surgery/);
 assert.match(by['carson-kerce'].outcomes.median,/Utility/);
 assert.match(draftOutcomesHtml(by['roch-cholowsky']),/qualitative central estimate/);
 assert.equal(draftOutcomesHtml({}), '');
 const safe=draftOutcomesHtml({...by['grady-emerson'],outcomes:{...by['grady-emerson'].outcomes,ceiling:'<script>alert(1)</script>'}});
 assert.ok(!safe.includes('<script>'));assert.ok(safe.includes('&lt;script&gt;'));
});
test('all 112 draft routes render the four sections and international routes remain separate',async()=>{
 const {profile}=await import('../amateurs.js');
 const app={innerHTML:'',querySelector:()=>null,querySelectorAll:()=>[]};
 for(const p of draft.players){
  profile(app,draft,'draft',p.id);
  assert.ok(app.innerHTML.includes('aria-label="Projected outcomes and risk"'),p.id);
  assert.ok(app.innerHTML.includes(p.outcomes.ceiling.replace(/&/g,'&amp;').replace(/'/g,'&#39;')));
  assert.ok(app.innerHTML.includes('Median outcome'));assert.ok(app.innerHTML.includes('Risk level'));
 }
 const intl=read('data/international/2027.json');profile(app,intl,'international',intl.players[0].id);
 assert.ok(!app.innerHTML.includes('Projected outcomes and risk'));
});
