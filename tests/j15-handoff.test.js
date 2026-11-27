import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {amateurPerformanceReportHtml} from '../amateurs.js';
const players=JSON.parse(readFileSync(new URL('../data/international/2027.json',import.meta.url))).players;
test('all twelve handoff profiles render numerical evidence with source and context',()=>{
 const rows=players.filter(p=>p.amateurPerformanceReport?.sourceFile?.endsWith('.xlsx'));
 assert.equal(rows.length,12);
 for(const p of rows){const h=amateurPerformanceReportHtml(p);assert.ok(h.includes('metricfacts'));assert.ok(h.includes(p.amateurPerformanceReport.sourceUrl.replaceAll('&','&amp;')));assert.ok(h.includes('Evidence confidence:'));}
});
test('sample boundaries and conflicting historical totals stay explicit',()=>{
 const get=id=>amateurPerformanceReportHtml(players.find(p=>p.id===id));
 assert.match(get('shoki-oda'),/not an all|excludes separate/);
 assert.match(get('cristian-oscar-lias-bieneme'),/does not exactly reconcile/);
 assert.match(get('harris-miller-jackson'),/secondary reporting/);
 assert.match(get('kosei-hiroike'),/walks \+ HBP/);
 assert.match(get('yeremy-de-leon'),/Earlier evidence/);
 assert.equal(get('miguel-grullon'),'');
});
