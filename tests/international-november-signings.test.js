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
test('Ranked additions preserve relative board order and have actionable checkpoints',()=>{const h=data.players.find(p=>p.id===ids[1]),f=data.players.find(p=>p.id===ids[3]);assert.equal(h.pipelineRank,35);assert.equal(f.pipelineRank,64);assert.equal(new Set(data.players.filter(p=>p.pipelineRank!=null).map(p=>p.pipelineRank)).size,data.players.filter(p=>p.pipelineRank!=null).length);assert.ok(amateurSearchText(h).includes('雷皓博'));for(const p of [h,f]){assert.equal(amateurRank(p),'#'+p.pipelineRank);for(const key of ['question','baseline','positive','concern','window'])assert.ok(p.developmentCheckpoint[key]);assert.ok(p.developmentCheckpoint.sources.length);assert.match(p.ranking.basis,/scouting/);}});
