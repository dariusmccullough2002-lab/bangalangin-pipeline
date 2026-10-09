"""Read-only frozen-model diagnostic. Never calls fit or mutates model inputs."""
import sys,hashlib,csv,gzip,json,math,copy,unicodedata
from pathlib import Path
sys.dont_write_bytecode=True
D=Path(__file__).resolve().parent
sys.path.insert(0,str(D.parent/'roster-opportunity'))
from hybrid import *
import engine as eng
from talent import TalentRateForecast

def dump(name,a):
 (D/name).write_text(json.dumps(a,indent=2,default=lambda x:x.item() if isinstance(x,np.generic) else x,allow_nan=False))
def csvsave(name,rows):
 cols=list(dict.fromkeys(k for a in rows for k in a))
 with (D/name).open('w',newline='') as f:
  w=csv.DictWriter(f,cols);w.writeheader();w.writerows(rows)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
files=sorted(set([p for p in D.parent.rglob('*') if p.is_file() and D not in p.parents and p.suffix in {'.py','.joblib'}]+[HERE/'Hybrid_League.json.gz',HERE/'Integrated_P_Cases.json.gz',HERE/'Integrated_H_Cases.json.gz',Path(sys.argv[1])/'trade-preview-v22/model/career_history_cache.json',Path(sys.argv[2])]))
freeze={str(p.resolve()):sha(p) for p in files};dump('Frozen_Inputs.json',{'checkpoint':'c4d87203ea1cbf14b23a6b6c05cbe56292961740','sha256':freeze,'mode':'diagnostic only; no fit or parameter selection'})
adapter=HybridForecastEngine();league=read(HERE/'Hybrid_League.json.gz');evidence=read(HERE/'Current_Evidence.json');rows=[];histrows=[];detail=[];errs=[]
names={'Paul Skenes','Zack Wheeler','Ryan Pepiot','Jose Berrios','Jacob Misiorowski','Nolan McLean','Aaron Judge','Matt Olson','Juan Soto','Jose Ramirez','Gavin Lux','Anthony Santander'}
def norm(n):return ''.join(c for c in unicodedata.normalize('NFD',n) if unicodedata.category(c)!='Mn')
for fam in ['H','P']:
 assets=[a for a in league if a['status']=='supported_MLB' and (a['role']=='H')==(fam=='H')];zs=[]
 for a in assets:
  rr=a['role'];p=old.players[a['id']];hs=v.seasons(p,rr);zs.append({'id':a['mlbam_id'],'year':2026,'role':rr,'history_override':hs,'x':base['features'](hs,rr,2026,a['mlbam_id']),'bounded_x':base['features'](hs,rr,2026,a['mlbam_id'],True)})
 cs=eng.incumbent(2026,fam,zs);sm=adapter.strong_models[fam];ss=prior.opportunity(sm,zs,cs,adapter.strong_selection[fam]);cm=adapter.count_models[fam];X=np.stack([eng.features(z) for z in zs]);count_raw=cm['tree'].predict(X);FX=np.stack([prior.fx(z) for z in zs]);strong_raw=(sm['direct'] if fam=='H' else sm['robust_hurdle']).predict(FX)
 im=eng._incmodel(2026,fam);IX=np.stack([past.past_xrow(z,1,fam=='H') for z in zs]);rawprob=calibrated_prob(im|{'calibrator':None},IX)
 if fam=='P':
  raw_sd=im['linear']['SP'].predict(IX);raw_rd=im['linear']['RP'].predict(IX);raw_counts={s:{k:im['counts'][s,k].predict(IX) for k in ['GS','RA']} for s in [1,2]}
 fresh=predict_layer(cm,zs,cs,'tree') if fam=='H' else None
 for i,(a,z,c,s) in enumerate(zip(assets,zs,cs,ss)):
  rr=a['role'];key='PA' if fam=='H' else 'IP';p=old.players[a['id']];d=eng.decomposition(z);prob=c['probabilities'];q=1-prob['absent'];b=a['baseline'][key];final=a['hybrid'][key];healthy=c[key]/q if q else 0
  result=adapter.predict([z],evidence)[0];st=TalentRateForecast(rr,a['baseline'],z).project(result);err=st[key]-final;errs.append(abs(err))
  rf=v.recent_forecast(p,rr);pre=rf[1];au=rf[2];quality=int(np.searchsorted(v.base.CUTS[rr],r.surplus({k:x*pre for k,x in rf[0].items()},rr)/pre*r.REFERENCE[rr]));age=int(round(float(p.get('age') or 26)));agefac=v.curve(rr,age,quality)['path'][0]['workload'];prod_err=pre*agefac-b
  sr=float(strong_raw[i]);sc=float(np.clip(sr,0,sm['cap']));strong_expected=sc*q if fam=='P' else sc
  if rr=='RP':strong_expected=c[key];sr=sc=healthy
  countpre=float(np.clip(count_raw[i],0,162 if fam=='H' else 34))*d['depth'];count_expected=countpre*q
  cr=fresh[i][key] if fam=='H' else None
  blended=.5*s[key]+.5*cr if fam=='H' else c[key] if rr=='RP' else .75*c[key]+.25*s[key]
  row={'id':a['id'],'mlbam_id':z['id'],'name':a['name'],'role':rr,'workload_unit':key,'production_workload':b,'production_recent_positive_only':au['recent_workload'],'production_healthy_top2':au['healthy_observed_workload'],'production_role_prior':au['role_workload_prior'],'production_prior_weight':au['prior_weight'],'production_pre_age_workload':pre,'production_age_attrition_factor':agefac,'production_reconciliation_error':prod_err,'historical_latest_workload':z['x'][0],'historical_lag1_workload':z['x'][1],'historical_lag2_workload':z['x'][2],'historical_lag3_workload':z['x'][3],'historical_calendar_mean':z['x'][4],'historical_positive_mean':z['x'][5],'historical_max':z['x'][6],'age_feature':z['x'][13],'durability_run':z['x'][11],'cohort':cohort(z),'demonstrated_max_appearances':d['healthy_opportunity'],'observed_latest_appearances':d['latest_opportunity'],'appearance_depth':d['depth'],'counts_missing':d['counts_missing'],'participation_probability':q,'absence_probability':prob['absent'],'raw_classifier_participation':1-float(rawprob[i,0]),'incumbent_conditional_active_workload':healthy,'incumbent_after_participation':c[key],'prior_raw_model_output':sr,'prior_clipped_model_output':sc,'prior_output_quantity':'unconditional median' if fam=='H' else 'unchanged incumbent' if rr=='RP' else 'active conditional median','prior_before_participation':sc if fam=='P' and rr!='RP' else None,'prior_after_participation_or_direct':strong_expected,'previous_repair_workload':s[key],'count_raw_appearance_equivalents':float(count_raw[i]) if fam=='H' else None,'count_clipped_appearance_equivalents':float(np.clip(count_raw[i],0,162)) if fam=='H' else None,'count_conditional_opportunity':countpre if fam=='H' else None,'count_before_participation':countpre if fam=='H' else None,'count_after_participation':count_expected if fam=='H' else None,'count_after_role_reconciliation':cr,'workload_after_roster_allocation':blended,'roster_allocation_status':'not invoked; no numerical allocation','workload_after_ensemble_blending':blended,'workload_after_final_role_constraints':result[key],'final_projected_workload':final,'absolute_change':final-b,'percentage_change':100*(final/b-1) if b else None,'replay_error':err,'injury_numeric_delta':result[key]-blended,'additional_age_discount':0,'roster_numeric_delta':0}
  for k,value in prob.items():row['probability_'+k]=value
  # Ordered additive bridge: sums exactly to final-production, not unique causal attribution.
  row['bridge_conditional_model_minus_production']=healthy-b
  row['bridge_participation_discount']=c[key]-healthy
  row['bridge_replace_or_blend_incumbent']=blended-c[key]
  row['bridge_final_constraints_and_evidence']=final-blended
  row['bridge_sum_error']=sum(row[k] for k in ['bridge_conditional_model_minus_production','bridge_participation_discount','bridge_replace_or_blend_incumbent','bridge_final_constraints_and_evidence'])-(final-b)
  row['prior_constraint_delta']=s[key]-strong_expected
  if fam=='H':
   row['count_clip_delta']=(float(np.clip(count_raw[i],0,162))-float(count_raw[i]))*d['depth']*q
   row['count_participation_delta']=count_expected-countpre;row['count_role_constraint_delta']=cr-count_expected
   upper=400*prob['part_time']+754*prob['regular'];lower=400*prob['regular'];row['role_mixture_upper_PA']=upper;row['role_mixture_lower_PA']=lower
   row['weighted_prior_constraint_delta']=.5*(s[key]-strong_expected);row['weighted_count_clip_delta']=.5*row['count_clip_delta'];row['weighted_count_role_constraint_delta']=.5*(cr-count_expected)
   row['incumbent_calibration_delta']=(q-(1-float(rawprob[i,0])))*healthy
  else:
   unc_before=unc_clip=unc_cohere=0
   for state,pname in [(1,'RP'),(2,'SP')]:
    gs0=float(raw_counts[state]['GS'][i]);ra0=float(raw_counts[state]['RA'][i]);gs=float(np.clip(gs0,0,im['caps']['GS']));ra=float(np.clip(ra0,0,im['caps']['RA']));ss0=c['conditional'][str(state)]
    row[f'raw_state{state}_GS']=gs0;row[f'raw_state{state}_RA']=ra0
    for k,val in ss0.items():row[f'incumbent_state{state}_{k}']=val
    w=prob[pname];unc_before+=w*(gs0*float(raw_sd[i])+ra0*float(raw_rd[i]));unc_clip+=w*(gs*c['IP_per_start']+ra*c['IP_per_relief']);unc_cohere+=w*ss0['IP']
   row['IP_per_start']=c['IP_per_start'];row['IP_per_relief']=c['IP_per_relief'];row['raw_IP_per_start']=float(raw_sd[i]);row['raw_IP_per_relief']=float(raw_rd[i]);row['incumbent_count_and_depth_clip_delta']=unc_clip-unc_before;row['incumbent_role_count_coherence_delta']=unc_cohere-unc_clip
   row['incumbent_calibration_delta']=c[key]-sum(float(rawprob[i,state])*c['conditional'][str(state)]['IP'] for state in [1,2])
  rows.append(row)
  for h in z['history_override']:
   stat=h['stat'];yr=h['year'];info=counts(z['id'],yr) if fam=='P' and yr<2026 else p.get('pit',{}) if fam=='P' else {}
   histrows.append({'mlbam_id':z['id'],'name':a['name'],'role':rr,'season':yr,'source_role':h['role'],'GP':GP.get((z['id'],yr)) if fam=='H' else (info or {}).get('GP'),'GS':None if fam=='H' else (info or {}).get('GS'),'PA':stat.get('PA'),'IP':stat.get('IP'),'cutoff':'2026-10-08 frozen cache/export; exact statistical cutoff not verified' if yr==2026 else f'{yr} completed annual season; original acquisition timestamp unavailable','source_snapshot_date':'2026-10-08','row_missing':False,'source':h.get('source','preserved annual record')})
  for yr in range(2023,2027):
   if not any(h['year']==yr for h in z['history_override']):
    histrows.append({'mlbam_id':z['id'],'name':a['name'],'role':rr,'season':yr,'source_role':None,'GP':None,'GS':None,'PA':None,'IP':None,'cutoff':'unknown; no observed positive season row','source_snapshot_date':'2026-10-08','row_missing':True,'source':'missing row converted to exposure zero in statistical features'})
  if norm(a['name']) in names:
   detail.append({'decomposition':row,'legacy_feature_vector':z['x'].tolist(),'past_only_feature_vector':IX[i].tolist(),'new_count_feature_vector':X[i].tolist(),'prior_repair_feature_vector':FX[i].tolist(),'incumbent':c,'previous_repair':s,'new_count':fresh[i] if fam=='H' else 'not selected for pitching','final_component':result,'production_audit':au,'model_observations':d,'historical_inputs':[h for h in histrows if h['mlbam_id']==z['id']]})
 print('CURRENT',fam,len(assets),flush=True)
csvsave('Player_Workload_Decomposition.csv',rows);csvsave('Historical_Input_Seasons.csv',histrows);dump('Representative_Reconstructions.json',detail)
summary=[]
for rr in ['H','SP','RP']:
 xs=[a for a in rows if a['role']==rr];keys=['production_workload','incumbent_conditional_active_workload','incumbent_after_participation','previous_repair_workload','workload_after_ensemble_blending','final_projected_workload','absolute_change','bridge_conditional_model_minus_production','bridge_participation_discount','bridge_replace_or_blend_incumbent','bridge_final_constraints_and_evidence','prior_constraint_delta','count_clip_delta','count_role_constraint_delta','incumbent_calibration_delta','incumbent_count_and_depth_clip_delta','incumbent_role_count_coherence_delta','participation_probability']
 for k in keys:
  vals=[a[k] for a in xs if a.get(k) is not None];summary.append({'role':rr,'component':k,'n':len(vals),'sum':sum(vals),'mean':float(np.mean(vals)) if vals else None,'nonzero_n':sum(abs(t)>1e-8 for t in vals),'note':'ordered additive bridge' if k.startswith('bridge') else 'overlapping diagnostic; do not sum with bridge'})
csvsave('Population_Component_Attribution.csv',summary)
# Existing chronological cases only; no fits, tuning, or holdout reuse for selection.
validation=[];reliability=[];caseout=[]
for fam in ['P','H']:
 cases=read(HERE/f'Integrated_{fam}_Cases.json.gz');key='IP' if fam=='P' else 'PA';recordmap={(z['id'],z['year'],z['role']):z for rr,zs in records.items() for z in zs}
 for a in cases:
  c=a['components']['past_only'];hc=a['hybrid_components'];q=1-c['probabilities']['absent'];y=a['actual'].get(key,0);z=recordmap.get((a['mlbam_id'],a['anchor'],a['role']));ex=float(z['x'][0]) if z else None
  caseout.append({'mlbam_id':a['mlbam_id'],'name':a['name'],'anchor':a['anchor'],'target_season':a['anchor']+1,'role':a['role'],'groups':'|'.join(a['groups']),'anchor_workload':ex,'actual_workload':y,'actual_active':int(y>0),'participation_probability':q,'incumbent_workload':c[key],'incumbent_conditional_active':c[key]/q if q else 0,'production_reference_workload':a['baseline'].get(key,0),'previous_repair_workload':a['strong_prior'].get(key,0),'hybrid_workload':a['hybrid'].get(key,0),'hybrid_implied_active_workload':a['hybrid'].get(key,0)/q if q else 0,'standard_season':a['anchor']+1!=2020,'reconciliation_error':hc[key]-a['hybrid'][key]})
for rr in ['H','SP','RP']:
 basecases=[a for a in caseout if a['role']==rr and a['standard_season']];ranked=sorted([a for a in basecases if a['anchor_workload'] is not None],key=lambda a:a['anchor_workload'])
 for i,a in enumerate(ranked):a['historical_workload_decile']=min(10,1+i*10//len(ranked))
 groups={'all':basecases}
 for a in basecases:
  for g in a['groups'].split('|'):groups.setdefault('cohort:'+g,[]).append(a)
 for dc in range(1,11):groups['workload_decile:'+str(dc)]=[a for a in basecases if a.get('historical_workload_decile')==dc]
 for yr in sorted({a['anchor'] for a in basecases}):groups['anchor:'+str(yr)]=[a for a in basecases if a['anchor']==yr]
 for g,xs in groups.items():
  if not xs:continue
  active=[a for a in xs if a['actual_active']];row={'role':rr,'group':g,'n':len(xs),'active_n':len(active),'players':len({a['mlbam_id'] for a in xs}),'observed_participation':float(np.mean([a['actual_active'] for a in xs])),'predicted_participation':float(np.mean([a['participation_probability'] for a in xs])),'participation_Brier':float(np.mean([(a['participation_probability']-a['actual_active'])**2 for a in xs])),'actual_mean':float(np.mean([a['actual_workload'] for a in xs]))}
  for method in ['production_reference','incumbent','previous_repair','hybrid']:
   e=np.array([a[method+'_workload']-a['actual_workload'] for a in xs]);row[method+'_bias']=float(e.mean());row[method+'_MAE']=float(abs(e).mean());row[method+'_RMSE']=float(np.sqrt((e*e).mean()))
  for method in ['incumbent','hybrid_implied']:
   es=[a[method+'_active_workload' if method=='hybrid_implied' else 'incumbent_conditional_active']-a['actual_workload'] for a in active];row[method+'_conditional_active_bias']=float(np.mean(es)) if es else None
  validation.append(row)
 for bin in range(10):
  xs=[a for a in basecases if min(9,int(a['participation_probability']*10))==bin]
  if xs:reliability.append({'role':rr,'probability_bin':f'{bin/10:.1f}–{(bin+1)/10:.1f}','n':len(xs),'predicted':float(np.mean([a['participation_probability'] for a in xs])),'observed':float(np.mean([a['actual_active'] for a in xs]))})
csvsave('Chronological_Case_Diagnostics.csv',caseout);csvsave('Chronological_Calibration.csv',validation);csvsave('Participation_Reliability.csv',reliability)
missing={rr:{'n':sum(a['role']==rr for a in rows),'latest_zero_n':sum(a['role']==rr and a['historical_latest_workload']==0 for a in rows),'count_missing_n':sum(a['role']==rr and a['counts_missing'] for a in rows),'positive_latest_count_missing_n':sum(a['role']==rr and a['counts_missing'] and a['historical_latest_workload']>0 for a in rows)} for rr in ['H','SP','RP']}
changed=[p for p,s in freeze.items() if sha(Path(p))!=s]
dump('Verification.json',{'supported_players':len(rows),'max_final_replay_error':max(errs),'max_production_replay_error':max(abs(a['production_reconciliation_error']) for a in rows),'max_additive_bridge_error':max(abs(a['bridge_sum_error']) for a in rows),'max_historical_saved_reconciliation_error':max(abs(a['reconciliation_error']) for a in caseout),'changed_frozen_files':changed,'representative_players_found':len(detail),'missing_data_audit':missing,'historical_cases':len(caseout),'no_model_fit':True,'no_parameter_tuning':True,'no_deployment':True})
assert len(rows)==1900 and len(detail)==12 and max(errs)<1e-8 and not changed
print('DONE',json.dumps(read(D/'Verification.json')),flush=True)
