import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import vm from 'node:vm';
import {mkdtemp,cp,rm} from 'node:fs/promises';
import {tmpdir} from 'node:os';
import {join} from 'node:path';
import {unpackCatalog,sharedForecastInputs,integrateSharedForecast} from '../scripts/integrate-shared-forecast.mjs';
import {applySharedForecast,sharedQualityAdjustment,categoryScore,POLICY} from '../trade-analyzer-beta/shared-forecast.js';
const html=fs.readFileSync('trade-analyzer-beta/index.html','utf8'),baseline=unpackCatalog(html),{evidence,model}=sharedForecastInputs(),data=structuredClone(baseline),release=applySharedForecast(data,evidence,model),by=new Map(baseline.assets.map(a=>[a.id,a]));
const changed=data.assets.filter(a=>a.forecast_research),close=(a,b)=>assert.ok(Math.abs(a-b)<1e-8,`${a} != ${b}`),modes=['neutral','balanced','contender','rebuild'];
test('catalog preserves dynasty prices, rankings, eligibility and identities; unsupported paths remain intact',()=>{
 assert.ok(changed.length>300);assert.equal(release.neutralPriceChanges,0);
 for(const a of data.assets){const old=by.get(a.id);for(const key of ['values','range','ranking_policy','market','position','group','owner','playerIdentity'])assert.deepEqual(a[key],old[key]);if(!a.forecast_research)assert.deepEqual(a,old);}
});
test('all strategy views use exactly the same bounded correction and the same annual path',()=>{
 for(const a of changed){const b=by.get(a.id),f=a.forecast_research.contributionFactor;assert.ok(f>=.9-1e-12&&f<=1.1+1e-12);
  a.annual_expected_utility.forEach((u,t)=>close(u,b.annual_expected_utility[t]*f));
  for(const mode of modes){close(a.competitive_values[mode].display,b.competitive_values[mode].display*f);assert.equal(a.competitive_values[mode].annual_time_discount,b.competitive_values[mode].annual_time_discount);const discount=a.competitive_values[mode].annual_time_discount,mass=Array.from({length:8},(_,t)=>.88**t).reduce((s,v)=>s+v,0),w=Array.from({length:8},(_,t)=>discount**t),sum=w.reduce((s,v)=>s+v,0);close(a.competitive_values[mode].display,model.display_multiplier*a.annual_expected_utility.reduce((s,u,t)=>s+u*w[t]*mass/sum,0));}
 }
});
test('adjusted statistics remain coherent and retain workload, steals, home runs and league-specific pitching counts',()=>{
 for(const a of changed){const s=a.audit.projection,b=by.get(a.id).audit.projection,r=a.forecast_research;close(r.afterSurplus/r.beforeSurplus,r.contributionFactor);
  if(a.audit.role==='H'){assert.ok(s.H<=s.AB&&s.HR<=s.H&&s.TB>=s.H+3*s.HR-1e-9&&s.TB<=4*s.H+1e-9);assert.ok(s.AB+s.BB+s.HBP+s.SF<=s.PA+1e-8);for(const k of ['PA','AB','HR','R','RBI','SB','BB','HBP','SF'])assert.equal(s[k],b[k]);}
  else for(const k of ['IP','K','SV','HLD','QA3','BB','H'])assert.equal(s[k],b[k]);
  assert.ok(r.qualityWeight<=POLICY.qualityFamilyWeight&&r.qualityWeight>0);
 }
});
test('identity, age, season, level and exposure checks reject invalid evidence',()=>{
 const a=baseline.assets.find(a=>evidence[a.id]?.kodo?.valid&&a.audit.kind==='MLB'&&a.audit.role==='H');
 for(const mutate of [e=>e.kodo.player_id++,e=>e.kodo.name='Wrong player',e=>e.kodo.stat_date='2026-10-24',e=>e.kodo.stat_date='2026-01-01',e=>e.kodo.stats.season=2025,e=>e.kodo.level='AAA',e=>e.kodo.stats.pa+=50,e=>e.kodo.stats.xba=null,e=>e.kodo.stats.xslg=NaN]){const e=structuredClone(evidence[a.id]);mutate(e);assert.equal(sharedQualityAdjustment(a,e,model).status,'unchanged');}
});
test('equal quality is a no-op; stronger and weaker evidence moves every strategy in the same direction',()=>{
 const a=baseline.assets.find(a=>a.name==='Miguel Vargas'),e=structuredClone(evidence[a.id]),s=a.audit.projection;
 e.kodo.stats.xba=s.H/s.AB;e.kodo.stats.xslg=s.TB/s.AB;close(sharedQualityAdjustment(a,e,model).contributionFactor,1);
 const up=structuredClone(e),down=structuredClone(e);up.kodo.stats.xba*=1.05;up.kodo.stats.xslg*=1.05;down.kodo.stats.xba*=.95;down.kodo.stats.xslg*=.95;
 assert.ok(sharedQualityAdjustment(a,up,model).contributionFactor>1);assert.ok(sharedQualityAdjustment(a,down,model).contributionFactor<1);
 const context=structuredClone(e);context.kodo.stats.barrel_pct=.99;context.kodo.stats.whiff_pct=.01;close(sharedQualityAdjustment(a,context,model).contributionFactor,1);
});
test('saved-package totals and ranges use adjusted assets and reverse symmetrically',()=>{
 const index=new Map(data.assets.map(a=>[a.id,a]));for(const t of data.trades)for(const [mode,m] of Object.entries(t.modes)){
  const totals=t.identities.map(ids=>ids.reduce((s,id)=>s+index.get(id).competitive_values[mode].display,0));assert.deepEqual(m.package_values,totals);close(m.net_first_owner,totals[1]-totals[0]);close(-m.net_first_owner,totals[0]-totals[1]);assert.ok(m.assumption_range[0]<=m.net_first_owner&&m.net_first_owner<=m.assumption_range[1]);
 }
});
test('evidence inputs are immutable and release cannot be applied twice',()=>{
 const e=JSON.stringify(evidence),m=JSON.stringify(model),before=JSON.stringify(data);applySharedForecast(data,evidence,model);assert.equal(JSON.stringify(data),before);assert.equal(JSON.stringify(evidence),e);assert.equal(JSON.stringify(model),m);
});
test('published integration compiles and withholds unsupported elite probabilities without NaN display',async()=>{
 const dir=await mkdtemp(join(tmpdir(),'shared-forecast-test-')),path=join(dir,'index.html');try{await cp('trade-analyzer-beta/index.html',path);const release=integrateSharedForecast(path),served=fs.readFileSync(path,'utf8'),catalog=unpackCatalog(served),code=JSON.parse(served.match(/script\.textContent\s*=\s*("(?:[^"\\]|\\.)*")/)[1]);new vm.Script(code);assert.ok(code.includes('Unavailable after quality adjustment'));assert.equal(catalog.shared_forecast_release.adjusted,release.adjusted);assert.ok(catalog.assets.find(a=>a.forecast_research).forecast_research.sourceUrl);}finally{await rm(dir,{recursive:true,force:true});}
});
