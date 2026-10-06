import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {createHash} from 'node:crypto';
import {rankEquivalent} from '../scripts/ranking-model.js';
import {scoreFarms,farmWeights} from '../scripts/farm-model.js';
const read=p=>JSON.parse(readFileSync(`data/${p}`));
const edition=read('editions/october-2026.json');
const ownership=read('ownership-snapshots/2026-10-06.json');
const owned=new Map(ownership.teams.flatMap(t=>t.players.map(p=>[p.fantraxId,{...p,team:t.name}])));
const candidates=[...edition.rankings,...edition.reviewQueue];
test('every current roster identity is audited once and assigned to its latest owner',()=>{
  const all=[...candidates,...edition.excluded];
  assert.equal(all.length,827); assert.equal(new Set(all.map(p=>p.fantraxId)).size,827);
  for(const p of all) assert(owned.has(p.fantraxId));
  for(const p of candidates){assert.equal(p.organization,owned.get(p.fantraxId).team);assert.equal(p.status,owned.get(p.fantraxId).status)}
});
test('ranked prospects have no MLB debut and pass recorded eligibility thresholds',()=>{
  for(const p of candidates){assert.equal(p.eligibility,'eligible');assert.equal(p.mlbDebutDate,null);assert(p.careerMLBAB==null||p.careerMLBAB<=130);assert(p.careerMLBOuts==null||p.careerMLBOuts<=150);assert(p.activeMLBDays==null||p.activeMLBDays<=45);assert(Number.isInteger(p.mlbamId))}
  for(const name of ['Zac Veen','Jonah Tong','Angel Genao','Kendry Rojas']) assert(edition.excluded.some(p=>p.name===name&&p.ddRank));
  for(const name of ['Walker Jenkins','Kaelen Culpepper','Josue De Paula'])assert(edition.excluded.some(p=>p.name===name&&p.mlbDebutDate));
  assert(candidates.some(p=>p.name==='Ricki Moneys'&&p.status==='RESERVE'));
  assert(candidates.some(p=>p.name==='Brady Smith'&&p.status==='RESERVE'));
});
test('rank order reproduces the documented model and DD controls missing evidence',()=>{
  assert.equal(rankEquivalent({dd:100,pl:null,fg:null,jb:null,ba:null}),100);
  assert.equal(rankEquivalent({dd:null,pl:null,fg:null,jb:null,ba:null}),null);
  assert(rankEquivalent({dd:100,pl:1,fg:1,jb:1,ba:1})>=100/2**.4-1e-5);
  for(const p of edition.rankings){
    if(p.editorialPlacement){assert.equal(p.modelRankEquivalent,null);assert.equal(p.orderingScore,p.editorialPlacement.score);assert(Object.values(p.sourceRanks).every(v=>v===null));}
    else {assert.equal(rankEquivalent(p.sourceRanks),p.modelRankEquivalent);assert.equal(p.orderingScore,p.modelRankEquivalent);}
  }
  assert.deepEqual(edition.rankings.map(p=>p.leagueRank),Array.from({length:edition.rankings.length},(_,i)=>i+1));
  for(let i=1;i<edition.rankings.length;i++)assert(edition.rankings[i].orderingScore>=edition.rankings[i-1].orderingScore);
});
test('October cannot rewrite August or assign misleading cross-team movement',()=>{
  const hash=createHash('sha256').update(readFileSync('data/editions/august-2026.json')).digest('hex');
  assert.equal(hash,edition.inputHashes.archive);
  for(const p of edition.rankings)if(p.previousOrganizationId!==p.organizationId)assert.equal(p.movement,null);
});
test('research gaps stay visible and never become invented source ranks',()=>{
  assert.equal(edition.summary.rankedPlayers,edition.rankings.length);
  assert.equal(edition.summary.eligibleAwaitingResearch,edition.reviewQueue.length);
  for(const p of edition.reviewQueue)assert(Object.values(p.sourceRanks).every(v=>v===null));
  assert.equal(edition.sources.find(s=>s.id==='ba').coverage,36);
});
test('all 45 research gaps receive disclosed placements without invented publication ranks',()=>{
  const supplement=read('research/october-2026-supplement.json');
  assert.equal(supplement.length,45);assert.equal(edition.reviewQueue.length,0);assert.equal(edition.rankings.length,260);
  for(const s of supplement){const p=edition.rankings.find(p=>p.fantraxId===s.fantraxId);assert(p);assert.equal(p.orderingScore,s.score);assert.equal(p.editorialPlacement.reason,s.reason);assert(edition.rankings.some(p=>p.name===s.comparisonPeer));}
  assert.equal(edition.rankings.filter(p=>p.organizationId==='shea-stadiums').length,26);
  const dd=edition.rankings.filter(p=>!p.editorialPlacement);
  for(let i=1;i<dd.length;i++)assert(dd[i].modelRankEquivalent>=dd[i-1].modelRankEquivalent);
});
test('all profiles contain projections and sourced grades; season splits are not doubled',()=>{
  const outs=ip=>{const [a,b='0']=String(ip).split('.');return Number(a)*3+Number(b)};
  assert.equal(edition.rankings.filter(p=>p.scoutingGrades).length,edition.summary.profilesWithPublishedGrades);
  for(const p of edition.rankings){
    assert.equal(p.projectionParagraphs.length,2);assert(p.projectionParagraphs.every(s=>s.length>=100));
    if(p.scoutingGrades){assert(p.scoutingGrades.sourceUrl.startsWith('https://'));assert(p.scoutingGrades.retrievedDate);for(const v of Object.values(p.scoutingGrades.tools))assert(/^\d+(\/\d+)?$/.test(v));}
    for(const g of p.seasonStats.groups){const splits=p.seasonStats.splits.filter(s=>s.group===g.group);assert.equal(splits.reduce((s,x)=>s+x.k,0),g.strikeOuts);assert.equal(splits.reduce((s,x)=>s+x.bb,0),g.walks);
      if(g.group==='hitting')assert.equal(splits.reduce((s,x)=>s+x.pa,0),g.pa);
      else assert.equal(splits.reduce((s,x)=>s+outs(x.ip),0),g.outs);
    }
  }
  assert.equal(edition.rankings.find(p=>p.name==='Shotaro Morii').type,'B');
  assert.equal(edition.rankings.find(p=>p.name==='Jonathon Long').seasonStats.groups[0].pa,598);
});
test('farm indices reproduce the transparent model and exclude MLB players',()=>{
  assert(Math.abs(Object.values(farmWeights).reduce((a,b)=>a+b,0)-1)<1e-9);
  assert.deepEqual(scoreFarms(edition.rankings,read('organizations.json')),edition.farms);
  assert.equal(edition.farms.length,12);assert.equal(edition.farms[0].index,100);
  assert.equal(edition.farms.reduce((n,f)=>n+f.eligibleCount,0),260);
  for(const f of edition.farms){assert.equal(f.gap,Number((100-f.index).toFixed(1)));for(const v of Object.values(f.components))assert(v>=0&&v<=100+1e-9);}
});
