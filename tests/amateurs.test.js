import test from 'node:test';
import assert from 'node:assert/strict';
import {readFile,mkdtemp,readdir,rm} from 'node:fs/promises';
import {tmpdir} from 'node:os';
import {join} from 'node:path';
import {execFileSync} from 'node:child_process';
import {publicAssets} from '../scripts/public-assets.js';
const draft=JSON.parse(await readFile('data/draft/2026.json','utf8'));
const intl=JSON.parse(await readFile('data/international/2027.json','utf8'));
test('domestic class separates public-input ranks, actual MLB picks and missing league picks',()=>{
 assert.equal(draft.players.length,112);assert.equal(new Set(draft.players.map(p=>p.id)).size,112);
 const ranked=draft.players.filter(p=>p.pipelineRank!=null);assert.equal(ranked.length,110);
 assert.deepEqual(ranked.map(p=>p.pipelineRank),Array.from({length:110},(_,i)=>i+1));
 let previous=-Infinity;
 for(const p of ranked){const score=.7*Math.log2(p.sourceRanks.ddClass??99)+.3*Math.log2(p.sourceRanks.baFypd??101);assert.ok(Math.abs(score-p.consensusScore)<1e-7);assert.ok(score>=previous);previous=score;assert.equal(p.pipelineRank,p.consensusRank);}
 for(const p of draft.players){assert.equal(p.draftYear,2026);assert.ok(p.mlbamId>0);assert.ok(p.mlbDraftPick>0);assert.equal(p.actualFypdPick,null);assert.equal(p.scoutingParagraphs.length,2);assert.equal(p.seasonStats.sourceUrls.length,5);}
 assert.equal(draft.players.find(p=>p.name==='Roch Cholowsky').mlbDraftPick,1);
 assert.equal(draft.players.find(p=>p.name==='Grady Emerson').signingBonus,9750000);
 assert.equal(draft.players.find(p=>p.name==='Anthony Potestio').pipelineRank,null);
});
test('international profiles preserve uncertainty and never convert expected agreements to signings',()=>{
 assert.equal(intl.players.length,13);assert.equal(new Set(intl.players.map(p=>p.id)).size,13);
 for(const [i,p]of intl.players.slice(0,11).entries()){assert.equal(p.pipelineRank,i+1);assert.equal(p.classYear,2027);assert.equal(p.officialOrganization,null);assert.ok(p.expectedOrganization);assert.match(p.signingStatus,/not official/);assert.equal(p.consensusRank,null);assert.equal(p.actualFypdPick,null);assert.equal(p.scoutingParagraphs.length,4);assert.equal(p.research.asOf,intl.researchAsOf);assert.ok(p.research.coverage);assert.ok(p.research.verifiedContext);assert.ok(p.research.limitations);for(const id of p.research.sourceIds)assert.ok(p.sourceIds.includes(id));assert.ok(!('seasonStats'in p));}
 assert.equal(intl.players[0].name,'Alfredo Sena');
});
test('new publication datasets have no strategy fields or private notes',()=>{
 const forbiddenKey=/personal|bpa|availability|waitRisk|manager|tendenc|target|preference|strategy|simulat|pickRange|portfolio/i;
 function inspect(v){if(Array.isArray(v))v.forEach(inspect);else if(v&&typeof v==='object')for(const[k,x]of Object.entries(v)){assert.ok(!forbiddenKey.test(k),`Private field ${k}`);inspect(x);}}
 for(const data of [draft,intl]){inspect(data);assert.doesNotMatch(JSON.stringify(data),/Shea|Darius|smash value|wait.?risk|portfolio|manager tendencies|MP_DEFAULT|FYPD_MASTER_CONTEXT|2027-fypd-simulator/i);const ids=new Set(data.sources.map(s=>s.id));for(const p of data.players)for(const id of p.sourceIds)assert.ok(ids.has(id));}
});
test('built client assets exactly match the explicit publication allowlist',async()=>{
 const output=await mkdtemp(join(tmpdir(),'pipeline-public-'));
 try{execFileSync(process.execPath,['scripts/build.js',output]);async function walk(dir,prefix=''){const out=[];for(const entry of await readdir(dir,{withFileTypes:true})){const path=prefix+entry.name;if(entry.isDirectory())out.push(...await walk(join(dir,entry.name),path+'/'));else out.push(path);}return out;}
 assert.deepEqual((await walk(output)).sort(),[...publicAssets].sort());assert.ok(!publicAssets.some(p=>/simulator|project_sources|private|handoff|\.csv$|\.txt$/i.test(p)));const app=await readFile(join(output,'app.js'),'utf8');assert.match(app,/showAmateurs/);assert.match(app,/showOctober/);
 }finally{await rm(output,{recursive:true,force:true});}
});
