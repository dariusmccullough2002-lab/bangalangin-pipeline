from hybrid import *
from talent import TalentRateForecast
from run_helpers import saveout,csvout
import importlib.util
s=importlib.util.spec_from_file_location('preserved_firstyear_valuation',HERE.parent/'first-year-repair'/'current.py');cur=importlib.util.module_from_spec(s);s.loader.exec_module(cur)
def run():
 adapter=HybridForecastEngine();league=read(OUT/'Past_Only_League_Impact.json.gz');evidence=read(HERE/'Current_Evidence.json');output=[];checks={'stats_coherent':0,'future_paths_frozen':0,'state_clips':0,'adapter_replays':0};names={'Paul Skenes','Aaron Judge','Jacob Misiorowski','Nolan McLean','Zack Wheeler','Juan Soto','Matt Olson','Jose Ramirez','Tarik Skubal','Logan Webb','Garrett Crochet','Cade Smith','Freddie Freeman'}
 for a in league:
  q={'id':a['id'],'name':a['name'],'role':a['role'],'status':a['status'],'baseline_values':a['baseline_values']}
  if a['status']!='supported_MLB':q['hybrid_values']=a['baseline_values'];output.append(q);continue
  rr=a['role'];p=old.players[a['id']];rows=v.seasons(p,rr);z={'id':a['mlbam_id'],'year':2026,'role':rr,'history_override':rows,'x':base['features'](rows,rr,2026,a['mlbam_id']),'bounded_x':base['features'](rows,rr,2026,a['mlbam_id'],True)};c=adapter.predict([z],evidence)[0];b=a['baseline_annual'][0];rates=TalentRateForecast(rr,b,z);st=rates.project(c)
  if rr!='RP':assert_coherent(c,st,rr,754 if rr=='H' else 251)
  else:assert st['QA3']<=st['IP']/5+1e-7
  checks['stats_coherent']+=1;paths,_=m.paths(p);_,audit=v.mlb_role_paths(p,rr);values,clips=cur.value_paths(paths,audit['outcome_state_projections'],b,c,rr);conditional,states=cur.conditional_values(paths,b,c,rr);checks['future_paths_frozen']+=1;checks['state_clips']+=clips
  q.update({'mlbam_id':z['id'],'baseline':b,'hybrid':st,'components':c,'hybrid_values':values,'conditional_value_sensitivity':conditional,'conditional_states':states,'unchanged_later_years':True,'talent_rate_evidence':rates.evidence,'rate_data_scope':'Existing preserved independent talent rates and age normalizers; no newly collected Statcast or invented features'})
  if a['name'] in names:assert adapter.predict([z],evidence)[0]==c;checks['adapter_replays']+=1
  output.append(q)
 for label in ['baseline','hybrid']:
  ranked=sorted(output,key=lambda a:-(a[label+'_values'].get('neutral') or -1e10))
  for n,a in enumerate(ranked,1):a[label+'_rank']=n
 flat=[]
 for a in output:
  x={k:a.get(k) for k in ['id','name','mlbam_id','role','status','baseline_rank','hybrid_rank']};x['rank_change']=a['baseline_rank']-a['hybrid_rank']
  for label in ['baseline','hybrid']:
   x.update({label+'_'+k:val for k,val in a[label+'_values'].items()})
   if label in a:x.update({label+'_'+k:val for k,val in a[label].items()})
  x['neutral_delta']=x['hybrid_neutral']-x['baseline_neutral'] if x['hybrid_neutral'] is not None else None
  if 'components' in a:x.update({'hybrid_method':a['components']['hybrid_method'],'role_evidence_group':a['components']['role_evidence_group'],'absence_probability':a['components']['probabilities']['absent'],'verified_injury_status':a['components']['opportunity_layer'].get('verified_injury_status','not assessed'),'mixture_constraint_residual':a['components'].get('mixture_constraint_residual',0)})
  flat.append(x)
 csvout('League_All_Assets_Before_After.csv',flat);csvout('League_Supported_MLB_Before_After.csv',[a for a in flat if a['status']=='supported_MLB']);csvout('Representative_Before_After.csv',[a for a in flat if a['name'] in names]);saveout('Hybrid_League.json.gz',output);saveout('Hybrid_Integration_Verification.json',{'assets':len(flat),'supported':checks['stats_coherent'],'checks':checks,'no_production_mutations':True,'prospect_branches_and_later_years_frozen':True,'current_evidence_records':len(evidence),'no_external_forecast_inputs':True})
 print('HYBRID INTEGRATED',checks,flush=True)
if __name__=='__main__':run()
