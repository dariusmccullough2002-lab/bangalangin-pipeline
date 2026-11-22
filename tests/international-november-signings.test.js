import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import {internationalUpdateHtml,internationalStatus,amateurRank,amateurSearchText} from '../amateurs.js';
const data=JSON.parse(fs.readFileSync(new URL('../data/international/2027.json',import.meta.url)));
const ids=['raider-sanchez-trutie','harris-miller-jackson','edenis-cruz','luis-fiallo'];
test('November signings retain source distinctions and remain outside confirmed draft eligibility',()=>{
 for(const id of ids){const rows=data.players.filter(p=>p.id===id);assert.equal(rows.length,1);const p=rows[0];assert.equal(p.classYear,2026);assert.equal(p.signingEvidence.actualSigningDate,null);assert.equal(p.signingEvidence.independentClubConfirmation,false);assert.match(p.novemberUpdate.eligibility.simulatorStatus,/Excluded/);assert.match(p.novemberUpdate.eligibility.previousFypdEligibility,/Not yet verified/);for(const sid of p.sourceIds)assert.ok(data.sources.some(s=>s.id===sid),sid);const html=internationalUpdateHtml(p,data);for(const label of ['Developmental outcomes','Strengths','Developmental concerns','Performance evidence','Signing period & fantasy eligibility'])assert.ok(html.includes(label),label);assert.ok(!html.includes('undefined'));}
 assert.equal(internationalStatus(data.players.find(p=>p.id==='edenis-cruz')).label,'Signed · reported');
 assert.equal(internationalStatus(data.players.find(p=>p.id==='harris-miller-jackson')).label,'Finalizing agreement');
});
test('Existing ranks survive and new watches do not invent ranks',()=>{assert.equal(data.players.find(p=>p.id===ids[0]).pipelineRank,15);assert.equal(data.players.find(p=>p.id===ids[2]).pipelineRank,35);for(const id of [ids[1],ids[3]])assert.equal(amateurRank(data.players.find(p=>p.id===id)),'Unranked');assert.ok(amateurSearchText(data.players.find(p=>p.id===ids[1])).includes('雷皓博'));});
