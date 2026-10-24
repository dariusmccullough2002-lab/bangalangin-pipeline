// Run after npm run build to freeze; subsequent runs replay frozen inputs only.
// node scripts/audit-contribution-horizons.mjs --freeze '/path/to/export.json'
// node scripts/audit-contribution-horizons.mjs
import fs from 'node:fs';import {gzipSync,gunzipSync} from 'node:zlib';import {createHash} from 'node:crypto';
import {unpackCatalog} from './integrate-shared-forecast.mjs';
import {timingEstimate} from '../trade-analyzer-beta/prospect-timing.js';
import {compareHorizons} from '../trade-analyzer-beta/contribution-horizon.js';
import {explainTrade} from '../trade-analyzer-beta/trade-explanation.js';
const dir='docs/horizon-audit-20261024',input=dir+'/Frozen_Inputs.json.gz';fs.mkdirSync(dir,{recursive:true});
const hash=x=>createHash('sha256').update(x).digest('hex');
if(process.argv.includes('--freeze')){
 const html=fs.readFileSync('dist/trade-analyzer-beta/index.html'),d=unpackCatalog(html.toString()),timing=JSON.parse(fs.readFileSync('data/prospect-timing-audit.json')),exportPath=process.argv[process.argv.indexOf('--freeze')+1],raw=fs.readFileSync(exportPath),trade=JSON.parse(raw);
 const compactValues=values=>values?Object.fromEntries(Object.entries(values).map(([m,v])=>[m,{display:v?.display??null}])):null;
 const assets=d.assets.map(a=>({id:a.id,name:a.name,position:a.position,audit:{kind:a.audit.kind,role:a.audit.role,projection:a.audit.projection,MLB:a.audit.MLB?{projection:a.audit.MLB.projection}:undefined},annual_expected_utility:a.annual_expected_utility,competitive_values:compactValues(a.competitive_values),values:compactValues(a.values),ranking_policy:a.ranking_policy?{source_rank:a.ranking_policy.source_rank,source_scope:a.ranking_policy.source_scope}:undefined,forecast_research:a.forecast_research?{contributionFactor:a.forecast_research.contributionFactor,evidenceDate:a.forecast_research.evidenceDate,beforeCompetitiveValues:compactValues(a.forecast_research.beforeCompetitiveValues)}:undefined,active_forecast_inputs:a.active_forecast_inputs?{estimator:a.active_forecast_inputs.estimator}:undefined}));
 fs.writeFileSync(input,gzipSync(JSON.stringify({assets,timing,trades:d.trades,uploadedTrade:trade,hashes:{publishedHtml:hash(html),uploadedTrade:hash(raw)},displayMultiplier:2.6501808805798475}),{mtime:0}));
}
const raw=fs.readFileSync(input),d=JSON.parse(gunzipSync(raw)),catalog=new Map(d.assets.map(a=>[a.id,a]));
const valueFor=(id,m)=>{const a=catalog.get(id);return m==='neutral'?a?.values?.neutral?.display??null:a?.audit?.kind==='prospect'?timingEstimate(a,m,d.timing)?.display??null:a?.competitive_values?.[m]?.display??null;},timingFor=(a,m)=>timingEstimate(a,m,d.timing);
const caseResult=(id,sides)=>{
 const assets=sides.map(ids=>ids.map(id=>catalog.get(id)));
 if(assets.flat().some(a=>!a))return {id,status:'blocked',reason:'Missing catalog identity',sides};
 const teams=['contender','rebuild'].map((mode,side)=>explainTrade({incoming:assets[1-side],outgoing:assets[side],mode,valueFor,timingFor}));
 const near=teams.map(e=>e.horizon.nextSeason.net);
 return {id,sides,names:assets.map(rows=>rows.map(a=>a.name)),status:teams.every(e=>e.horizon.complete)?'complete':'blocked',baselineEightYear:teams.map(e=>e.net),neutralChange:teams.map(e=>e.neutralNet),nextSeason:near,firstThreeYears:teams.map(e=>e.horizon.firstThreeYears.net),laterYears:teams.map(e=>e.horizon.laterYears.net),nextSeasonAndContenderDisagree:near[0]!==null&&teams[0].net!==null&&near[0]*teams[0].net<0,summary:teams.map(e=>e.summary)};
};
const named=[caseResult('uploaded-export',d.uploadedTrade.sides),caseResult('screenshot-Holliday',[['05y9r','062cx'],['02w7p']]),caseResult('Vargas-Naylor',[['03pjd'],['04ru7']])];
const saved=(d.trades??[]).map((t,i)=>caseResult('saved-'+(t.id??i),t.identities));
const groups=['H','SP','RP','prospect','pick'].map(role=>d.assets.filter(a=>(['prospect','pick'].includes(role)?a.audit.kind===role:a.audit.kind==='MLB'&&a.audit.role===role)&&Number.isFinite(valueFor(a.id,'contender'))&&a.values.neutral.display>0).sort((a,b)=>a.id.localeCompare(b.id)));
let seed=20261024;const random=n=>{seed=(1664525*seed+1013904223)>>>0;return seed%n;};const hypotheticals=[];
for(const size of [1,2,3])for(let n=0;n<100;n++){
 const ids=new Set(),sides=[[],[]];for(let side=0;side<2;side++)for(let j=0;j<(side===0?size:1);j++){
  const group=groups[(n+j+side)%groups.length];let a;do{a=group[random(group.length)];}while(ids.has(a.id));ids.add(a.id);sides[side].push(a.id);
 }
 hypotheticals.push(caseResult(`${size}-for-1-${n+1}`,sides));
}
const failures=[];for(const c of [...named,...saved,...hypotheticals])if(c.status==='complete'&&Math.abs(c.nextSeason[0]+c.nextSeason[1])>1e-10)failures.push(c.id+' next-season sides not symmetric');
// Reconcile the saved eight-year algorithm without changing any coefficient.
const annualFit=(path,m)=>{const discount={contender:.75,balanced:.88,rebuild:.94}[m],mass=Array.from({length:8},(_,t)=>.88**t).reduce((a,b)=>a+b,0),w=Array.from({length:8},(_,t)=>discount**t),normalize=mass/w.reduce((a,b)=>a+b,0);return path.reduce((n,x,t)=>n+x*w[t]*normalize*d.displayMultiplier,0);};
let reconciled=0,maxResidual=0;for(const a of d.assets.filter(a=>['MLB','hybrid'].includes(a.audit.kind)))for(const m of ['contender','balanced','rebuild'])if(a.annual_expected_utility?.length===8&&Number.isFinite(valueFor(a.id,m))){const residual=Math.abs(annualFit(a.annual_expected_utility,m)-valueFor(a.id,m));maxResidual=Math.max(maxResidual,residual);if(residual>1e-8)failures.push(`${a.id} ${m} annual fit residual ${residual}`);reconciled++;}
const decomposition=['02w7p','05y9r'].map(id=>{const a=catalog.get(id),p=a.annual_expected_utility;return {id,name:a.name,role:a.audit.role,displayPosition:a.position,projection:a.audit.projection,nextSeason:p[0],contenderFirstSeason:annualFit(p.map((x,i)=>i===0?x:0),'contender'),contenderLaterSeasons:annualFit(p.map((x,i)=>i>0?x:0),'contender'),contenderTotal:valueFor(id,'contender')};});
const result={inputSha256:hash(raw),sourceHashes:d.hashes,coverage:{assets:d.assets.length,savedTrades:saved.length,hypotheticals:hypotheticals.length,byPackageSize:{oneForOne:100,twoForOne:100,threeForOne:100},blockedHypotheticals:hypotheticals.filter(c=>c.status!=='complete').length,firstSeasonDisagreesWithEightYear:hypotheticals.filter(c=>c.nextSeasonAndContenderDisagree).length,reconciledAssetModes:reconciled,maxScoreResidual:maxResidual},named,decomposition,savedTrades:saved,hypotheticals,failedChecks:failures,blockedChecks:['No new external playing-time, injury or role forecast: saved assumptions retained.','Cross-position replacement scale remains provisional; no newly fitted replacement floors or price weights.','Next-season contribution is before actual lineup displacement; daily schedules and weekly category wins are not modeled.','Prospect calendar paths are conditional published-ETA scenarios, not calibrated probabilities.','No forward-season observed outcomes are available for forecast accuracy validation.']};
fs.writeFileSync(dir+'/Results.json',JSON.stringify(result,null,2)+'\n');console.log(JSON.stringify({coverage:result.coverage,named:result.named.map(({id,names,baselineEightYear,nextSeason,neutralChange})=>({id,names,baselineEightYear,nextSeason,neutralChange})),decomposition,failedChecks:failures},null,2));if(failures.length)process.exitCode=1;
