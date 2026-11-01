import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {j15Country,j15FlagArtwork,homeFeature} from '../home-highlights.js';
const data=JSON.parse(readFileSync('data/international/2027.json'));
const by=id=>data.players.find(p=>p.id===id);
test('all 27 talents share a unique contiguous rank, with sourced insertions and original period distinctions',()=>{
 assert.equal(data.players.length,27);
 assert.deepEqual(data.players.map(p=>p.pipelineRank),Array.from({length:27},(_,i)=>i+1));
 for(const [id,rank] of Object.entries({'joh-sung-chul':9,'raider-sanchez-trutie':12,'anthony-calderon':16,'marko-morua':17,'edenis-cruz':22,'yonewrys-garcia':24,'alayn-daniel-blanco':27})){
  const p=by(id);assert.equal(p.pipelineRank,rank);assert.ok(p.ranking.rationale.length>200);assert.equal(p.ranking.asOf,'2026-11-01');assert.equal(p.officialOrganization,null);
  for(const sid of p.ranking.sourceIds)assert.ok(data.sources.some(s=>s.id===sid));
 }
 assert.equal(by('anthony-calderon').classYear,2026);assert.equal(by('edenis-cruz').classYear,2026);assert.equal(by('joh-sung-chul').classYear,2027);assert.equal(by('alayn-daniel-blanco').classYear,null);
 assert.equal(by('shoki-oda').ranking.conditional,true);assert.equal(by('shoki-oda').classYear,null);
 assert.equal(by('yonewrys-garcia').country,undefined);assert.equal(by('yonewrys-garcia').throws,undefined);
});
test('all seven countries have artwork; featured jerseys keep flags without a separate strip',()=>{
 const countries=[...new Set(data.players.map(j15Country).filter(Boolean))];
 assert.deepEqual([...countries].sort(),['Cuba','Dominican Republic','Hungary','Japan','Nicaragua','South Korea','Venezuela']);
 for(const c of countries){assert.match(j15FlagArtwork(c),/<(rect|path)/);}
 assert.equal(j15FlagArtwork('Unverified'),'');
 const edition=JSON.parse(readFileSync('data/editions/october-2026.json'));const markup=homeFeature(edition,{international:data});
 assert.ok(!markup.includes('j15-country-index'));
 assert.ok(markup.includes('Joh Sung-chul'));assert.ok(markup.includes('j15-country-flag'));
});
