import test from 'node:test';import assert from 'node:assert/strict';import fs from 'node:fs';
import {winterRouteIndex} from '../winter-profile-integration.js';
import {renderWinterProfile,winterProfileContext,winterPerformanceEvidence} from '../winter-profiles.js';
const read=p=>JSON.parse(fs.readFileSync(new URL('../data/'+p,import.meta.url))),catalog=read('winter/profiles-2026.json'),winter=read('winter/2026.json'),archive=read('players.json');
test('current, winter and archive links resolve to one verified winter identity',()=>{
 const index=winterRouteIndex(catalog,winter,archive);
 assert.equal(index.get('#october-player/fantrax-06ibv').mlbamId,815908);
 assert.equal(index.get('#player/jacob-reimer').mlbamId,702544);
 assert.equal(index.get('#player/jesus-made').mlbamId,815908);
 for(const p of catalog.players)assert.equal(index.get(p.profileUrl).mlbamId,p.mlbamId);
 const conflicting=winterRouteIndex(catalog,winter,[{id:'wrong-id',name:'Jacob Reimer',mlbOrg:'NYM',mlbamId:1}]);assert.ok(!conflicting.has('#player/wrong-id'));
});
test('existing profiles receive actual saved winter samples and update dates',()=>{
 for(const id of [815908,702544]){
  const p=catalog.players.find(p=>p.mlbamId===id),rows=winterProfileContext(p,winter),html=winterPerformanceEvidence(rows,true,winter.seasonLabel);
  assert.ok(rows.length);for(const row of rows){assert.ok(html.includes(row.league));assert.ok(html.includes(String(row.stats.plateAppearances??row.stats.battersFaced)));assert.ok(html.includes(row.refreshedAt));}
 }
});
test('winter players have sourced entry cards and a visible scouting-grade section',()=>{
 for(const p of catalog.players){assert.ok(p.proEntry,p.name);assert.equal(p.proEntry.mlbamId,p.mlbamId);assert.ok(p.proEntry.sources.length);const html=renderWinterProfile(p,winter);assert.ok(html.includes('Entry into pro baseball'));assert.ok(html.includes('aria-label="Scouting grades"'));}
 const reimer=catalog.players.find(p=>p.mlbamId===702544);assert.equal(reimer.proEntry.overallPick,119);assert.equal(reimer.proEntry.signingBonusUsd,775000);assert.equal(reimer.scoutingGrades.fv,50);assert.ok(reimer.scoutingReport.paragraphs.length>=2);
});
