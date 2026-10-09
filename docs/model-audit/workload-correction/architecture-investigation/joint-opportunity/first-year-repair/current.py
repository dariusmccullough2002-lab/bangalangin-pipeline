"""All supported2027 forecasts; first-year-only dynasty sensitivity."""
from engine import *
from collections import Counter

def value_paths(paths,states,base_stats,c,rr):
 # Primary sensitivity: retain frozen contribution-state weights and years2–8.
 # Bounded state workload, followed by coherent category reconciliation.
 result=[(prob,list(path)) for prob,path in paths];key='PA' if rr=='H' else 'IP';factor=c[key]/base_stats[key] if base_stats[key] else 0;clips=0
 for j in range(3):
  state_ratio=states[j][0][key]/base_stats[key] if base_stats[key] else 0
  state_c=c|{key:states[j][0][key]*factor}
  if rr!='H':state_c.update({k:c[k]*state_ratio for k in ['QA3','GS','RA']})
  st=stats(states[j][0],state_c,rr,mixture_leverage=False)
  ceiling=754 if rr=='H' else 251
  if st[key]>ceiling:
   ratio=ceiling/st[key];st={k:val*ratio for k,val in st.items()};clips+=1
  if rr=='H':st=v.reconcile(st)
  else:
   st['QA3']=min(st['QA3'],st['IP']/5)
   for k in ['SV','HLD']:st[k]=states[j][0].get(k,0)*min(1,factor)
  result[j][1][0]=r.utility(r.surplus(st,rr))
 assert [prob for prob,path in result]==[prob for prob,path in paths]
 assert all(path[1:]==b[1:] for (_,path),(_,b) in zip(result,paths)) and result[3:]==paths[3:]
 return {mode:m.competitive(result,mode)['display'] for mode in r.MODES},clips

def conditional_values(paths,b,c,rr):
 """Exact first-year opportunity-state mean utility, frozen later path rewards.
 No multi-year joint uncertainty or dispersion claim. Current-role floor remains
 primary; future-role replacement is a separate sensitivity.
 """
 expected=0;role_expected=0;parts=[];key='PA' if rr=='H' else 'IP'
 for label,prob in c['probabilities'].items():
  if label=='absent':st={k:0 for k in b};role=rr
  elif rr=='H':st=stats(b,c|{'PA':c['conditional_part_PA'] if label=='part_time' else c['conditional_regular_PA']},rr);role=rr
  else:
   part=c['conditional']['1' if label=='RP' else '2'];st=stats(b,c|part,rr,mixture_leverage=False);role=label
  utility=r.utility(r.surplus(st,rr));futureutility=r.utility(r.surplus(st,role));expected+=prob*utility;role_expected+=prob*futureutility;parts.append({'state':label,'probability':prob,'role':role,'stats':st,'utility_current_role_floor':utility,'utility_future_role_floor':futureutility})
 vals={}
 for name,reward in [('conditional_mean',expected),('future_role_floor',role_expected)]:
  new=[(prob,list(path)) for prob,path in paths]
  for j in range(3):new[j][1][0]=reward
  assert all(a[1:]==b[1:] for (_,a),(_,b) in zip(new,paths))
  vals[name]={mode:m.competitive(new,mode)['display'] for mode in r.MODES}
 return vals,parts

def run():
 selected=read(HERE/'Selection_Freeze.json')['selected'];models={f:fit(2026,f) for f in ['P','H']}
 for f,mod in models.items():checkpoint(mod,HERE/f'current-{f}.joblib',compress=3)
 league=read(OUT/'Past_Only_League_Impact.json.gz');source={};batches={'H':[],'P':[]}
 for row in league:
  if row['status']!='supported_MLB':continue
  rr=row['role'];p=old.players[row['id']];ident=row['mlbam_id'];rows=v.seasons(p,rr);z={'id':ident,'asset_id':row['id'],'year':2026,'role':rr,'x':base['features'](rows,rr,2026,ident),'bounded_x':base['features'](rows,rr,2026,ident,True),'history_override':rows};source[row['id']]=z;batches['H' if rr=='H' else 'P'].append(z)
 predictions={};incpred={}
 for fam,zs in batches.items():
  inc=incumbent(2026,fam,zs);new=inc if selected[fam]=='incumbent' else opportunity(models[fam],zs,inc,selected[fam]);predictions.update({z['asset_id']:p for z,p in zip(zs,new)});incpred.update({z['asset_id']:p for z,p in zip(zs,inc)})
  print('Current batch',fam,len(zs),flush=True)
 output=[];flat=[];checks={'stat_coherence':0,'future_paths_frozen':0,'bounded_inherited_state_clips':0,'adapter_replays':0};adapter=FirstYearForecastEngine();replay_names={'Paul Skenes','Jacob Misiorowski','Nolan McLean','Zack Wheeler','Aaron Judge','Juan Soto','Matt Olson','José Ramírez'}
 for row in league:
  q={'id':row['id'],'name':row['name'],'role':row['role'],'status':row['status'],'baseline_values':row['baseline_values']}
  if row['id'] not in source:
   q['revised_values']=row['baseline_values'];output.append(q);continue
  z=source[row['id']];rr=z['role'];fam='H' if rr=='H' else 'P';b=row['baseline_annual'][0];c=predictions[row['id']];inc=incpred[row['id']];s=stats(b,c,rr,z);key='PA' if rr=='H' else 'IP';p=old.players[row['id']];paths,_=m.paths(p);_,ma=v.mlb_role_paths(p,rr)
  if rr!='RP':assert_coherent(c,s,rr,models[fam]['cap']);checks['stat_coherence']+=1
  values,clips=value_paths(paths,ma['outcome_state_projections'],b,c,rr);oldjoint,_=value_paths(paths,ma['outcome_state_projections'],b,inc,rr);conditional,states=conditional_values(paths,b,c,rr);checks['future_paths_frozen']+=1;checks['bounded_inherited_state_clips']+=clips
  q.update(mlbam_id=z['id'],age=float(z['x'][13]),cohort=cohort(z),baseline=b,prior_joint=stats(b,inc,rr,z,mixture_leverage=False),revised=s,components=c,conditional_states=states,revised_values=values,prior_joint_first_year_values=oldjoint,conditional_value_sensitivity=conditional,feature_evidence={'latest_MLB_exposure':float(z['x'][0]),'previous_MLB_exposure':float(z['x'][1]),'current_GP':float(z['x'][15]),'current_GS':float(z['x'][16]),'debut_MLB_exposure':float(z['x'][19]),'verified_debut_MiLB_exposure':float(z['x'][20]),'debut_capacity':float(z['x'][21]),'current_MiLB_exposure':float(z['x'][24]),'current_combined_capacity':float(z['x'][25]),'capacity_missing':bool(z['x'][23]),'durability_run':float(z['x'][11]),'years_since_debut':float(z['x'][14])})
  if row['name'] in replay_names:
   replay=adapter.predict([z])[0];assert abs(replay[key]-c[key])<1e-8;checks['adapter_replays']+=1
  output.append(q)
 for method in ['baseline','revised','prior_joint']:
  key={'baseline':'baseline_values','revised':'revised_values','prior_joint':'prior_joint_first_year_values'}[method]
  ranked=sorted([z for z in output if z.get(key,z['baseline_values']).get('neutral') is not None],key=lambda z:-z.get(key,z['baseline_values'])['neutral'])
  for rank,q in enumerate(ranked,1):q.setdefault('ranks',{})[method]=rank
 for q in output:
  a={k:q.get(k) for k in ['id','name','mlbam_id','role','status','age','cohort']};a.update({k+'_rank':val for k,val in q['ranks'].items()})
  for method,key in [('baseline','baseline_values'),('revised','revised_values'),('prior_joint','prior_joint_first_year_values')]:
   for mode,val in q.get(key,q['baseline_values']).items():a[method+'_'+mode]=val
  a['neutral_delta']=a['revised_neutral']-a['baseline_neutral'] if a['revised_neutral'] is not None else None;a['neutral_rank_change']=a['baseline_rank']-a['revised_rank'];a['review_large_change']=bool(a['neutral_delta'] is not None and (abs(a['neutral_delta'])>10 or abs(a['neutral_rank_change'])>50))
  if 'revised' in q:
   for method in ['baseline','prior_joint','revised']:
    for k,val in q[method].items():a[method+'_'+k]=val
   c=q['components'];a.update({'absence_probability':c['probabilities']['absent'],'expert_unconstrained_workload':c.get('expert_unconstrained_workload'),'mixture_constraint_residual':c.get('mixture_constraint_residual')});a.update(q['feature_evidence'])
   for mode,val in q['conditional_value_sensitivity']['conditional_mean'].items():a['conditional_'+mode]=val
  flat.append(a)
 writecsv('First_Year_All_Assets.csv',flat);writecsv('First_Year_Supported_MLB.csv',[a for a in flat if a['status']=='supported_MLB']);writecsv('Representative_Forecasts.csv',[a for a in flat if a['name'] in replay_names|{'Freddie Freeman','Cade Smith','Tarik Skubal','Garrett Crochet','Logan Webb'}]);put('Current_League.json.gz',output)
 summary={'assets':len(output),'supported':len(source),'roles':dict(Counter(a['role'] for a in flat if a['status']=='supported_MLB')),'unchanged':len(output)-len(source),'selected':selected,'checks':checks,'large_change_flags':sum(a['review_large_change'] for a in flat),'median_neutral_delta':float(np.median([a['neutral_delta'] for a in flat if a['status']=='supported_MLB'])),'mean_neutral_delta':float(np.mean([a['neutral_delta'] for a in flat if a['status']=='supported_MLB'])),'max_abs_neutral_delta':float(max(abs(a['neutral_delta']) for a in flat if a['status']=='supported_MLB')),'scope':'First-year-only sensitivity; all later utility-path rewards, probabilities and prospect branches frozen. Primary values scale inherited contribution-state workload with physical bounds; separate exact first-year opportunity-state expected utility and future-role floor sensitivity supplied. No new eight-year uncertainty fit or release certification.','training_manifest':{f:mod['manifest'] for f,mod in models.items()}}
 put('Current_Summary.json',summary);print('Current complete',json.dumps(summary),flush=True)
if __name__=='__main__':run()
