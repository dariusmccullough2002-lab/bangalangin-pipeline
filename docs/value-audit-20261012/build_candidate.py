"""Reproducible, offline ranking-policy candidates; production stays byte-identical.
Run from repository root: python docs/value-audit-20261012/build_candidate.py
Dependencies: numpy, scipy, scikit-learn. Input ranks are separate scopes.
"""
import json,csv,re,gzip,base64,copy,math,hashlib,collections,subprocess
from pathlib import Path
import numpy as np
from sklearn.isotonic import IsotonicRegression
D=Path(__file__).resolve().parent;ROOT=D.parents[1]
def read(p):return json.loads(p.read_text())
def save(name,obj):(D/name).write_text(json.dumps(obj,indent=2,ensure_ascii=False))
def csvout(name,rows):
 if not rows:return
 with (D/name).open('w',newline='') as f:
  w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
html=subprocess.check_output(['git','show','4607c16:trade-analyzer-beta/index.html'],cwd=ROOT,text=True);packed=re.search("const packed='([^']+)'",html)[1];data=json.loads(gzip.decompress(base64.b64decode(packed)));assets={a['id']:a for a in data['assets']}
protected=['trade-analyzer-beta/index.html','data/starter-display-scenarios.json','data/role-display-scenarios.json','afl-profile-links.js','trade-analyzer-beta/history-display.js','trade-analyzer-beta/role-display.js','trade-analyzer-beta/starter-display.js']
hashes={p:sha(ROOT/p) for p in protected}
prospectcurve=read(D/'inputs/prospect-curve.json');oldcurve=prospectcurve['curve'] if 'curve' in prospectcurve else prospectcurve['points']
comparison=list(csv.DictReader((D/'inputs/prospect-comparison.csv').open()));comparisons={x['id']:x for x in comparison}
overall=list(csv.DictReader((D/'inputs/overall.tsv').open(),delimiter='\t'));prospect=list(csv.DictReader((D/'inputs/prospects.tsv').open(),delimiter='\t'))
for rows in [overall,prospect]:
 for x in rows:x.update(id=x['Player ID'].strip('*'),rank=int(x['Ranking']),tier=int(x['Tier']))
 assert len(rows)==500 and len({x['id'] for x in rows})==500 and sorted(x['rank'] for x in rows)==list(range(1,501))
ov={x['id']:x for x in overall};pr={x['id']:x for x in prospect}
def interpolate(curve,r):return float(np.interp(r,[x['rank'] for x in curve],[x['value'] for x in curve]))
def spaced(points,weight=.1):
 # A fitted positive decreasing power curve gives a modest ordinal-distance prior.
 # Blend with pooled estimates, rather than injecting player-specific epsilons.
 ranks=np.array([x['rank'] for x in points]);values=np.array([x['value'] for x in points]);positive=values>0
 slope,intercept=np.polyfit(np.log(ranks[positive]),np.log(values[positive]),1)
 if slope>=0:raise ValueError('No supported decreasing spacing prior')
 trend=np.exp(intercept)*ranks**slope
 # Normalize mean to the original curve: avoid changing aggregate rank-curve scale.
 trend*=values.mean()/trend.mean()
 curve=[{'rank':int(r),'value':float((1-weight)*v+weight*t)} for r,v,t in zip(ranks,values,trend)]
 return curve,{'trend_exponent':float(slope),'trend_coefficient':float(trend[0]),'trend_weight':weight,'mean_preserved':float(np.mean([x['value'] for x in curve])-values.mean()),'policy':'10% fitted positive power spacing prior, 90% pooled internal-scale estimate. Ordinal distance is a policy assumption, not empirical market pricing. No player-specific coefficients.'}
curve,spacing=spaced(oldcurve)
correction=copy.deepcopy(data);corrected={a['id']:a for a in correction['assets']}
def fundamental(a):return a.get('contribution_fundamentals',a)['values']['neutral']['display']
def setvalue(a,value,policy):
 if 'contribution_fundamentals' not in a:a['contribution_fundamentals']={k:copy.deepcopy(a[k]) for k in ['values','range','valuation_quantities'] if k in a}
 a['values']={mode:{'display':value,'underlying':None,'meaning':'Ranking-led trade-value policy, not expected category contribution or calibrated transaction price'} for mode in a['values']}
 # Policy ranges are assumption envelopes; fundamentals retain original ranges.
 a['range']={side:{mode:value*(.85 if side=='low' else 1.15) for mode in a['values']} for side in ['low','high']};a['ranking_policy']=policy
 if 'valuation_quantities' in a:a['valuation_quantities']['ranking_led_trade_value']=value
rows=[]
for a in correction['assets']:
 if not a.get('ranking_policy'):continue
 r=a['ranking_policy']['effective_rank'];v=interpolate(curve,r);policy=a['ranking_policy']|{'curve_version':'spacing-20261012','source_scope':'prospect-only','source_tab':'supplied prospects table','source_received':'2026-10-12','source_publication_date':'unknown','stable_id':a['id'],'spacing_policy':spacing,'contribution_value':fundamental(a)}
 setvalue(a,v,policy);rows.append({'id':a['id'],'name':a['name'],'source_rank':policy['source_rank'],'source_tier':policy['source_tier'],'effective_rank':r,'before':assets[a['id']]['values']['neutral']['display'],'after_spacing':v,'delta':v-assets[a['id']]['values']['neutral']['display'],'rounded_before':round(assets[a['id']]['values']['neutral']['display'],1),'rounded_after':round(v,1)})
assert len(rows)==265
# Overall source-fit always uses fundamentals, never prospect-policy values.
fit=[{'id':x['id'],'rank':x['rank'],'value':fundamental(assets[x['id']])} for x in overall if x['id'] in assets and fundamental(assets[x['id']]) is not None]
iso=IsotonicRegression(increasing=False,out_of_bounds='clip').fit([x['rank'] for x in fit],[x['value'] for x in fit]);pooled=[{'rank':i,'value':float(iso.predict([i])[0])} for i in range(1,501)];overallcurve,overallspacing=spaced(pooled)
# Map prospect-only rank to overall rank from shared stable IDs. This is a scope bridge,
# not a second value anchor; the final value curve is the overall curve only.
pairs=[{'id':x['id'],'prospect_rank':x['rank'],'overall_rank':ov[x['id']]['rank']} for x in prospect if x['id'] in ov]
bridge=IsotonicRegression(increasing=True,out_of_bounds='clip').fit([x['prospect_rank'] for x in pairs],[x['overall_rank'] for x in pairs]);bridgepoints=[{'rank':i,'overall_rank':float(bridge.predict([i])[0])} for i in range(1,501)]
# A flat scope bridge conveys insufficient ordering evidence. Spread using a 10%
# positive fitted log-rank trend, preserving source dominance and displayed scope.
bx=np.array([x['rank'] for x in bridgepoints]);by=np.array([x['overall_rank'] for x in bridgepoints]);bsl,bint=np.polyfit(np.log(bx),np.log(by),1);bt=np.exp(bint)*bx**bsl;bt*=by.mean()/bt.mean();by=np.clip(.9*by+.1*bt,1,500)
for x,v in zip(bridgepoints,by):x['overall_rank']=float(v)
def mapped(r):return float(np.interp(r,bx,by))
extension=copy.deepcopy(correction);extended={a['id']:a for a in extension['assets']};population=[];registry={};unsupported=[]
for x in overall:
 if x['id'] not in assets:unsupported.append({'id':x['id'],'name':x['Player'],'rank':x['rank'],'reason':'Not in production catalog; no invented asset/value'})
for a in extension['assets']:
 i=a['id'];base=assets[i];src=ov.get(i);ispros=i in pr and base.get('ranking_policy') is not None
 if src:
  scope='overall dynasty';rank=src['rank'];tier=src['tier'];source_date='2026-10-08';source_tab='Dynasty_Dugout_Overall.tsv';sourceweight=1.;eff=float(rank);bound=.1*rank
  # A bounded contribution disagreement, not an unconstrained rank substitution.
  anchor=interpolate(overallcurve,rank);f=fundamental(base);au=base['audit'];rr=au.get('role');supported=au.get('kind')=='MLB' and rr in ['H','SP','RP']
  exposure=sum(z['stat'].get('PA' if rr=='H' else 'IP',0) for z in base.get('career_profile',{}).get('seasons',[]) if z['role']==rr)
  if rr!='H':
   prof=base.get('career_profile',{}).get('seasons',[]);latest=max(prof,key=lambda z:z['year']) if prof else {};skills=latest.get('skills',{});gp=skills.get('GP',skills.get('gamesPlayed',0));gs=skills.get('GS',skills.get('gamesStarted',0));supported &= gp>=10 and (gs/gp>=.8 if rr=='SP' else gs==0)
  w=.25*exposure/(exposure+(600 if rr=='H' else 170)) if supported else 0.;sourceweight=1-w
  # Determine model-implied rank on the fixed common curve; bound rank departure ±10%.
  mr=float(np.interp(max(0,f or 0),[z['value'] for z in overallcurve][::-1],[z['rank'] for z in overallcurve][::-1]));eff=math.exp(sourceweight*math.log(rank)+w*math.log(mr));eff=max(1,rank-bound,min(500,rank+bound,eff));status='bounded contribution deviation' if supported else 'source only; role/sample or forecast support insufficient'
  # Existing prospect deviations use talent rates rather than damaged short workload.
  if ispros:
   c=base['ranking_policy'];eff=max(1,rank-bound,min(500,rank+bound,rank*mapped(c['effective_rank'])/mapped(pr[i]['rank'])));sourceweight=c['source_weight'];status='bounded retained prospect talent deviation'
 elif ispros:
  src=pr[i];scope='prospect-only mapped to overall domain';rank=src['rank'];tier=src['tier'];source_date='2026-10-12';source_tab='Supplied_Rankings.tsv';eff=mapped(base['ranking_policy']['effective_rank']);sourceweight=base['ranking_policy']['source_weight'];status='one overall curve via disclosed stable-ID scope bridge';bound=None
 else:continue
 v=interpolate(overallcurve,eff);policy={'source_rank':rank,'source_tier':tier,'source_scope':scope,'source_tab':source_tab,'source_received':source_date,'source_publication_date':'not independently established','stable_id':i,'mlbam_id':base.get('career_profile',{}).get('identifiers',{}).get('mlbamId'),'source_weight':sourceweight,'model_weight':1-sourceweight,'effective_overall_rank':eff,'maximum_rank_departure':bound,'curve_version':'overall-spacing-20261012','contribution_value':fundamental(base),'archived_policy_value':v,'graduation_policy':'Retain last supported policy value at confirmed graduation; blend toward supported fundamentals only with additional observed exposure delta/(delta+K), with delta0 retaining the exact prior value. No eligibility-triggered cliff.','status':status,'no_anchor_stacking':True,'debut_status_does_not_remove_membership':True,'meaning':'Ranking-led dynasty trade-value policy; forecasts unchanged'}
 setvalue(a,v,policy);registry[i]=policy
 population.append({'id':i,'name':a['name'],'role':a['audit'].get('role'),'source_scope':scope,'source_rank':rank,'source_tier':tier,'effective_overall_rank':eff,'source_weight':sourceweight,'before':base['values']['neutral']['display'],'after_spacing':corrected[i]['values']['neutral']['display'],'after_extension':v,'delta_spacing':corrected[i]['values']['neutral']['display']-base['values']['neutral']['display'],'delta_extension':v-corrected[i]['values']['neutral']['display'],'fundamental':fundamental(base)})
def packages(cat):
 by={a['id']:a for a in cat['assets']}
 for t in cat['trades']:
  sums=[sum(by[i]['values']['neutral']['display'] for i in ids) for ids in t['identities']];t['neutral_transfer_packages']=sums
  for mode in t['modes'].values():mode['neutral_transfer_change']=sums[1]-sums[0]
for cat in [correction,extension]:packages(cat)
def ties(values):
 exact=collections.defaultdict(list);rounded=collections.defaultdict(list)
 for i,n,v in values:exact[v].append({'id':i,'name':n});rounded[round(v,1)].append({'id':i,'name':n,'exact_value':v})
 return {'exact_groups':[{'value':v,'members':m} for v,m in exact.items() if len(m)>1],'rounded_groups':[{'display_value':v,'members':m,'distinct_exact_values':len({z['exact_value'] for z in m})} for v,m in rounded.items() if len(m)>1]}
exact=ties([(x['id'],x['name'],x['before']) for x in rows]);after=ties([(x['id'],x['name'],x['after_spacing']) for x in rows]);extties=ties([(x['id'],x['name'],x['after_extension']) for x in population]);save('Tie_Diagnostics.json',{'before_prospects':exact,'after_spacing_prospects':after,'after_extension_listed':extties})
csvout('Prospects_All_265.csv',rows);csvout('Population_Comparison.csv',population);csvout('Overall_Unsupported.csv',unsupported);csvout('Overall_Fit_Points.csv',fit);csvout('Scope_Bridge_Pairs.csv',pairs)
save('Curves.json',{'prospect_spacing':curve,'prospect_policy':spacing,'overall_curve':overallcurve,'overall_policy':overallspacing,'scope_bridge':bridgepoints,'bridge_pair_count':len(pairs)})
save('Source_Registry.json',registry)
trade=[]
for old,c,e in zip(data['trades'],correction['trades'],extension['trades']):trade.append({'label':old.get('label',old.get('name','saved trade')),'identities':old['identities'],'before':old['neutral_transfer_packages'],'after_spacing':c['neutral_transfer_packages'],'after_extension':e['neutral_transfer_packages']})
save('Saved_Trade_Comparisons.json',trade)
# Separately review example packages; no player-specific parameter fitting.
examples=[(['Kyle Bradish'],['Colt Keith']),(['Jose Soriano'],['Colt Keith']),(['Ramon Marquez','Taitn Gray','Franklin Primera'],['Emmanuel Rodriguez','Ethan Holliday']),(['Kyle Bradish','Jose Soriano'],['Eury Perez'])]
ex=[]
for left,right in examples:
 ids=[[next(a['id'] for a in data['assets'] if a['name']==n) for n in side] for side in [left,right]]
 ex.append({'sides':[left,right],**{label:[sum(by[i]['values']['neutral']['display'] for i in side) for side in ids] for label,by in [('before',assets),('spacing',corrected),('extension',extended)]}})
save('Representative_Trades.json',ex)
# Freeze forecast/interface identity and invariants.
for cat in [correction,extension]:
 for a in cat['assets']:
  b=assets[a['id']]
  for k in ['audit','annual_expected_utility','competitive_values','competitive_range','career_profile','availability_status']:
   assert a.get(k)==b.get(k),(a['name'],k)
for points in [curve,overallcurve]:assert all(b['value']<a['value'] for a,b in zip(points,points[1:]));assert all(x['value']>0 for x in points)
assert all(x['source_weight']>.5 for x in registry.values())
assert all(sha(ROOT/p)==h for p,h in hashes.items())
for cat in [correction,extension]:
 for a in cat['assets']:
  pa=a.get('audit',{}).get('projection_audit',{})
  if pa.get('estimator','').startswith('V2.3 recent-performance'):
   a['active_forecast_inputs']={'rate_pseudocount':100 if 'H' in a['audit']['role'] else 30,'recent_season_weights':{'2023':.1,'2024':.2,'2025':.3,'2026':.4},'healthy_workload_weight':.3,'recent_workload_weight':.7,'prior_weight':pa.get('prior_weight'),'cohort_attrition_applied_once':True,'additional_injury_penalty':0,'note':'Inherited career_diagnostic is a separate diagnostic estimator; it does not set the active forecast.'}
# Preview candidates reuse the deployed calculator shell/logic and all scenario scripts.
for label,cat in [('spacing',correction),('overall',extension)]:
 cat['version']=f'REVIEW ONLY — {label} ranking-policy candidate';cat['ranking_policy_release']={'candidate':label,'base_commit':'4607c16','production_deployed':False,'scope':'prospect-only' if label=='spacing' else 'overall dynasty plus mapped prospect-only ranks','forecast_changes':0};cat['warnings'].append('Unvalidated valuation policy preview; production unchanged. Rankings are ordinal expert judgments, not observed market prices. Source publication date unknown.')
 packed2=base64.b64encode(gzip.compress(json.dumps(cat,separators=(',',':'),ensure_ascii=False).encode(),mtime=0)).decode();preview=html.replace("const packed='"+packed+"'","const packed='"+packed2+"'")
 preview=preview.replace('<body>','<body><div style="padding:12px;background:#ffe08a;color:#182223;font:600 15px Arial">REVIEW ONLY: '+label+' policy candidate. Production valuations remain unchanged.</div>',1)
 # Update only preview explanations: do not call an overall rank a prospect rank.
 start=preview.index('script.textContent=');end=preview.index(';document.body.append(script)',start)
 raw=preview[start+len('script.textContent='):end];code=json.loads(raw)
 code=code.replace("['Source prospect rank',a.ranking_policy.source_rank]", "[(a.ranking_policy.source_scope==='overall dynasty'?'Source overall dynasty rank':'Source prospect-only rank'),a.ranking_policy.source_rank],['Source scope',a.ranking_policy.source_scope],['Effective overall rank',a.ranking_policy.effective_overall_rank??'Not applicable: prospect-only spacing policy']")
 marker="body.append(el('h3','','Transferable fundamentals and acquisition evidence')"
 insert="if(a.active_forecast_inputs)body.append(el('h3','','Active forecast inputs'),tableRows([['Active rate pseudocount',a.active_forecast_inputs.rate_pseudocount+(a.audit.role.includes('H')?' PA':' IP')],['Season weights','2023 .1 · 2024 .2 · 2025 .3 · 2026 .4'],['Career diagnostic','Separate inherited estimator; not active forecast parameters'],['Additional injury penalty','None']])); "
 code=code.replace(marker,insert+marker)
 preview=preview[:start+len('script.textContent=')]+json.dumps(code,ensure_ascii=False)+preview[end:]
 target=ROOT/f'value-audit-preview/{label}/index.html';target.parent.mkdir(parents=True,exist_ok=True);target.write_text(preview)
 # Numeric metadata correction is explicit and separate from valuation.
# A stale copied career field says100/half-life while the active estimator uses30/.1-.4.
metadata=[]
for a in data['assets']:
 au=a.get('audit',{});pa=au.get('projection_audit',{})
 if pa.get('estimator','').startswith('V2.3 recent-performance'):
  metadata.append({'id':a['id'],'name':a['name'],'role':au['role'],'stale_rate_prior_strength':pa.get('rate_prior_strength'),'active_rate_prior_strength':100 if 'H' in au['role'] else 30,'actual_recent_weights':{'2023':.1,'2024':.2,'2025':.3,'2026':.4},'action':'Expose active inputs separately from inherited career diagnostics; no forecast/value change'})
save('Confirmed_Metadata_Correction.json',metadata)
sensitivity=[]
for w in [.1,.2,.3]:
 c,_=spaced(oldcurve,w);v=[interpolate(c,x['effective_rank']) for x in rows];sensitivity.append({'weight':w,'sum_before':sum(x['before'] for x in rows),'sum_after':sum(v),'largest_absolute_delta':max(abs(a-x['before']) for a,x in zip(v,rows))})
save('Spacing_Sensitivity.json',sensitivity)
summary={'base_commit':'4607c1619458be18aa884a106eb1be2ac7bd13ee','catalog_assets':len(assets),'prospect_affected':len(rows),'overall_rows':len(overall),'overall_supported':len(fit),'overall_missing_catalog':len(unsupported),'extension_covered':len(population),'prospect_bridge_pairs':len(pairs),'overall_direct_covered':sum(x['source_scope']=='overall dynasty' for x in population),'prospect_bridge_covered':sum(x['source_scope']!='overall dynasty' for x in population),'unlisted_retained':len(assets)-len(population),'exact_tie_groups_before':len(exact['exact_groups']),'exact_tie_groups_after_spacing':len(after['exact_groups']),'rounded_tie_groups_before':len(exact['rounded_groups']),'rounded_tie_groups_after_spacing':len(after['rounded_groups']),'extension_exact_tie_groups':len(extties['exact_groups']),'prospect_total_before':sum(x['before'] for x in rows),'prospect_total_after_spacing':sum(x['after_spacing'] for x in rows),'largest_spacing_changes':sorted(rows,key=lambda x:-abs(x['delta']))[:20],'largest_extension_changes':sorted(population,key=lambda x:-abs(x['delta_extension']))[:20],'production_hashes':hashes,'source_hashes':{str(p.relative_to(D)):sha(p) for p in (D/'inputs').iterdir()},'forecast_changes':0,'confirmed_valuation_calculation_defects':0,'confirmed_metadata_defects':len(metadata),'production_changed':False,'policy_validation':'Algebra, continuity, scope and isolation checked. No historical market-price validation claimed.'}
boundaries=[]
for scope,source,prior,new in [('prospects',prospect,oldcurve,curve),('overall',overall,pooled,overallcurve)]:
 for left,right in zip(source,source[1:]):
  if left['tier']!=right['tier']:
   boundaries.append({'scope':scope,'left_rank':left['rank'],'right_rank':right['rank'],'left_tier':left['tier'],'right_tier':right['tier'],'old_left':interpolate(prior,left['rank']),'old_right':interpolate(prior,right['rank']),'new_left':interpolate(new,left['rank']),'new_right':interpolate(new,right['rank']),'new_step':interpolate(new,left['rank'])-interpolate(new,right['rank']),'policy':'One continuous rank curve, no tier-triggered step or bonus; existing prospect deviation bounds retained'})
csvout('Tier_Boundaries.csv',boundaries)
save('Summary.json',summary);print(json.dumps({k:v for k,v in summary.items() if not isinstance(v,(list,dict))},indent=2))
