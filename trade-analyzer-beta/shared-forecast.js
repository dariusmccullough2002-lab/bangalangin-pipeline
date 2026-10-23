// One quality adjustment, shared by every strategy. Constants are disclosed policy,
// inherited from the research family weight and active rate pseudocounts.
export const RELEASE='shared-quality-forecast-20261023';
export const POLICY={qualityFamilyWeight:.10,maxContributionDeparture:.10,maxEvidenceAgeDays:45,forecastYear:2027,observedSeason:2026};
const modes=['neutral','balanced','contender','rebuild'];
const finite=x=>typeof x==='number'&&Number.isFinite(x);
const norm=s=>String(s??'').normalize('NFKD').replace(/[\u0300-\u036f]/g,'').toLowerCase().replace(/[^a-z0-9]/g,'');
const clone=x=>structuredClone(x);
const clamp=(v,lo,hi)=>Math.max(lo,Math.min(hi,v));
export function categoryScore(s,role,model){
 const r=model.category_references,d=model.category_dispersion[role==='H'?'H':'P'];let v;
 if(role==='H'){
  if(!(s.AB>0))return 0;
  const obp=(s.H+s.BB+s.HBP)/(s.AB+s.BB+s.HBP+s.SF),ops=obp+s.TB/s.AB;
  v=[s.HR,s.R,s.RBI,s.SB,s.H-r.AVG*s.AB,(ops-r.OPS)*s.AB];
 }else v=[-s.ER,s.K,3*s.SV+2*s.HLD,s.QA3,s.K-r.KBB*s.BB,r.WHIP*s.IP-s.H-s.BB];
 return v.reduce((total,x,i)=>total+x/d[i],0);
}
export function coherent(s){
 const z={...s};z.H=clamp(z.H,0,z.AB);z.HR=clamp(z.HR,0,z.H);z.TB=clamp(z.TB,z.H+3*z.HR,4*z.H);return z;
}
export function sharedQualityAdjustment(asset,evidence,model,asOf='2026-10-23'){
 const blocked=reason=>({status:'unchanged',reason});
 if(asset.audit?.kind!=='MLB'||!['H','SP','RP'].includes(asset.audit.role))return blocked('No isolated MLB production stream; prospect, hybrid and two-way paths retained.');
 const role=asset.audit.role,s=asset.audit.projection,exposure=role==='H'?'PA':'IP',mid=asset.career_profile?.identifiers?.mlbamId,k=evidence?.kodo;
 if(!s||!finite(s[exposure])||s[exposure]<=0)return blocked('Positive projected exposure unavailable.');
 if(!k?.valid||!mid||k.player_id!==mid||norm(k.name)!==norm(asset.name))return blocked('Verified matching underlying-data identity unavailable.');
 const stats=k.stats,season=POLICY.observedSeason,observed=asset.career_profile?.seasons?.filter(x=>x.year===season&&x.role===role),date=Date.parse(k.stat_date),now=Date.parse(asOf),age=(now-date)/86400000;
 if(!stats||k.season!==season||stats.season!==season||k.level!=='MLB'||stats.level!=='MLB'||!/^\d{4}-\d{2}-\d{2}$/.test(k.stat_date??'')||!finite(age)||age<0||age>POLICY.maxEvidenceAgeDays)return blocked('Underlying evidence is stale, future-dated or from a different season/level.');
 let observedExposure=stats[role==='H'?'pa':'ip'];
 if(role!=='H'&&finite(observedExposure)){const whole=Math.floor(observedExposure),outs=Math.round((observedExposure-whole)*10);observedExposure=outs>=0&&outs<=2?whole+outs/3:NaN;}
 if(observed?.length!==1||!finite(observedExposure)||observedExposure<=0||Math.abs(observed[0].stat[exposure]-observedExposure)>=1.1)return blocked('Observed exposure does not reconcile to the saved MLB season.');
 const fields=role==='H'?['AB','PA','H','HR','R','RBI','SB','BB','HBP','SF','TB']:['IP','ER','K','SV','HLD','QA3','BB','H'];
 if(fields.some(key=>!finite(s[key])||s[key]<0))return blocked('Incomplete or invalid projected counting components.');
 if(role==='H'&&(!finite(stats.xba)||stats.xba<=0||stats.xba>=1||!finite(stats.xslg)||stats.xslg<stats.xba||stats.xslg>4*stats.xba))return blocked('Coherent xBA/xSLG pair unavailable.');
 if(role!=='H'&&(!finite(stats.xera)||stats.xera<=0||stats.xera>30))return blocked('Valid expected ERA unavailable.');
 const shrink=role==='H'?100:30,requestedWeight=POLICY.qualityFamilyWeight*observedExposure/(observedExposure+shrink);
 const blend=weight=>{let p={...s};if(role==='H'){p.H=(1-weight)*s.H+weight*stats.xba*s.AB;p.TB=(1-weight)*s.TB+weight*stats.xslg*s.AB;p=coherent(p);}else p.ER=(1-weight)*s.ER+weight*stats.xera*s.IP/9;return p;};
 const floor=model.replacement_floor[role]*s[exposure]/model.reference_workload[role];
 const beforeSurplus=categoryScore(s,role,model)-floor;
 // Compact production catalogs retain annual utility paths but not full annual
 // component/state paths. Preserve that trajectory; never invent annual stat lines.
 if(!(beforeSurplus>1e-8)||!(asset.annual_expected_utility?.[0]>0))return blocked('Positive baseline contribution unavailable for the bounded trajectory bridge.');
 let weight=requestedWeight,projection=blend(weight),afterSurplus=categoryScore(projection,role,model)-floor;
 const rawFactor=Math.max(0,afterSurplus)/beforeSurplus,capped=Math.abs(rawFactor-1)>POLICY.maxContributionDeparture;
 if(capped){let lo=0,hi=weight;for(let i=0;i<50;i++){const mid=(lo+hi)/2,ratio=(categoryScore(blend(mid),role,model)-floor)/beforeSurplus;if(Math.abs(ratio-1)>POLICY.maxContributionDeparture)hi=mid;else lo=mid;}weight=lo;projection=blend(weight);afterSurplus=categoryScore(projection,role,model)-floor;}
 const factor=clamp(Math.max(0,afterSurplus)/beforeSurplus,1-POLICY.maxContributionDeparture,1+POLICY.maxContributionDeparture);
 if(!asset.annual_expected_utility?.every(x=>finite(x)&&x>=0)||asset.annual_expected_utility.length!==8||modes.some(mode=>!finite(asset.competitive_values?.[mode]?.display)))return blocked('Complete annual contribution path or strategy values unavailable.');
 return {status:'adjusted',release:RELEASE,source:'Kodo Analytics saved expected-quality snapshot',sourceUrl:`https://kodoanalytics.com/api/v1/players/${mid}`,mlbamId:mid,evidenceDate:k.stat_date,season,observedExposure,qualityWeight:weight,requestedQualityWeight:requestedWeight,contributionFactor:factor,uncappedContributionFactor:rawFactor,contributionCapApplied:capped,beforeProjection:{...s},projection,beforeSurplus,afterSurplus,method:'Modest expected-quality rate blend; one bounded proportional correction to the inherited annual utility trajectory for all strategies. Annual component/state paths are unavailable in the compact catalog; this bridge does not refit aging or outcome probabilities.',limits:'Policy sensitivity; not a chronologically validated forecasting improvement. Expected stats describe contact quality, not guaranteed future results. Undated projection benchmarks, duplicate barrel/whiff bonuses, health and new playing-time assumptions are excluded.'};
}
const scaleValue=(v,f)=>{const z={...v};for(const key of ['display','underlying','expected_before_risk_preference','outcome_dispersion','risk_preference_deduction'])if(finite(z[key]))z[key]*=f;return z;};
const scaleRange=(r,f)=>Object.fromEntries(Object.entries(r).map(([side,values])=>[side,Object.fromEntries(Object.entries(values).map(([mode,v])=>[mode,finite(v)?v*f:v]))]));
export function applySharedForecast(data,evidence,model,asOf='2026-10-23'){
 if(data.shared_forecast_release?.release===RELEASE)return data.shared_forecast_release;
 const counts={adjusted:0,unchanged:0},reasons={};
 for(const a of data.assets){
  const r=sharedQualityAdjustment(a,evidence[a.id],model,asOf);counts[r.status]++;if(r.status!=='adjusted'){reasons[r.reason]=(reasons[r.reason]??0)+1;continue;}
  const f=r.contributionFactor;
  a.forecast_research={...r,beforeCompetitiveValues:clone(a.competitive_values),beforeAnnualUtility:[...a.annual_expected_utility]};
  a.audit.projection=r.projection;
  a.audit.flags=[...(a.audit.flags??[]),'Shared bounded expected-quality correction; see forecast research for evidence and trajectory-bridge limits.'];
  a.annual_expected_utility=a.annual_expected_utility.map(v=>v*f);
  a.competitive_values=Object.fromEntries(Object.entries(a.competitive_values).map(([m,v])=>[m,scaleValue(v,f)]));
  if(a.competitive_range)a.competitive_range=scaleRange(a.competitive_range,f);
  if(a.contribution_fundamentals){const c=a.contribution_fundamentals;if(c.values)c.values=Object.fromEntries(Object.entries(c.values).map(([m,v])=>[m,scaleValue(v,f)]));if(c.range)c.range=scaleRange(c.range,f);if(c.valuation_quantities){for(const key of ['intrinsic_dynasty','transferable_fundamental'])if(finite(c.valuation_quantities[key]))c.valuation_quantities[key]*=f;if(c.valuation_quantities.competitive_fit)for(const m of modes)if(finite(c.valuation_quantities.competitive_fit[m]))c.valuation_quantities.competitive_fit[m]*=f;}}
  if(a.valuation_quantities?.competitive_fit)for(const m of modes)if(finite(a.valuation_quantities.competitive_fit[m]))a.valuation_quantities.competitive_fit[m]*=f;
  if(a.distribution_summary){const d=a.distribution_summary;if(d.neutral_outcome_quantiles)for(const q of Object.keys(d.neutral_outcome_quantiles))d.neutral_outcome_quantiles[q]*=f;delete d.first_year_above_elite_utility_probability;d.definition+=' Shared quality overlay scales saved utility states; elite exceedance is withheld because full states are unavailable.';}
 }
 // Saved trades must agree with interactive totals. Historical before-values stay
 // in forecast_research; neutral dynasty prices and their envelopes are untouched.
 const catalog=new Map(data.assets.map(a=>[a.id,a]));
 for(const t of data.trades??[])for(const [mode,m] of Object.entries(t.modes??{})){
  if(!modes.includes(mode))continue;
  const totals=t.identities.map(ids=>ids.reduce((sum,id)=>sum+(catalog.get(id)?.competitive_values?.[mode]?.display??0),0));
  m.package_values=totals;m.net_first_owner=totals[1]-totals[0];
  const bounds=t.identities.map(ids=>({low:ids.reduce((sum,id)=>sum+catalog.get(id).competitive_range.low[mode],0),high:ids.reduce((sum,id)=>sum+catalog.get(id).competitive_range.high[mode],0)}));
  m.assumption_range=[bounds[1].low-bounds[0].high,bounds[1].high-bounds[0].low];
 }
 data.shared_forecast_release={release:RELEASE,asOf,policy:POLICY,...counts,reasons,neutralPriceChanges:0,method:'One underlying-quality contribution factor per supported MLB player, used identically by all strategy views. Existing strategy time discounts retained.'};
 return data.shared_forecast_release;
}
export function renderForecastResearch(doc,asset){
 const r=asset.forecast_research;if(!r)return null;
 const section=doc.createElement('section'),make=(tag,text)=>{const el=doc.createElement(tag);el.textContent=text;return el;};
 section.append(make('h3','Underlying quality · shared forecast'),make('p',`Expected-quality evidence: ${r.evidenceDate}. Contribution adjustment: ${((r.contributionFactor-1)*100).toFixed(1)}%. The same adjustment applies to contender, balanced and rebuilding views.`));
 const s=r.projection,b=r.beforeProjection;
 if(s.AB>0){const ops=x=>(x.H+x.BB+x.HBP)/(x.AB+x.BB+x.HBP+x.SF)+x.TB/x.AB;section.append(make('p',`Projected AVG ${(b.H/b.AB).toFixed(3)} → ${(s.H/s.AB).toFixed(3)}; OPS ${ops(b).toFixed(3)} → ${ops(s).toFixed(3)}.`));}
 else section.append(make('p',`Projected ERA ${(9*b.ER/b.IP).toFixed(2)} → ${(9*s.ER/s.IP).toFixed(2)}.`));
 section.append(make('p','Small adjustment to the saved contribution trajectory; workload and dynasty price stay as saved. This method has not been validated against future seasons.','subtle'));
 return section;
}
