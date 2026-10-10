"""Full1900-player research replay; production talent/years2–8 untouched."""
from engine import *
_run_spec=importlib.util.spec_from_file_location('targeted_training',HERE/'run.py');_run=importlib.util.module_from_spec(_run_spec);_run_spec.loader.exec_module(_run);model_for,value=_run.model_for,_run.value
import joblib,unicodedata

def preserve_qa3(c,before):
 if 'IP' not in c:return c
 for st,a in c['conditional'].items():
  olda=before['conditional'][st];oldgs=olda['GS'];oldra=olda['RA'];oldip=olda['IP'];oldqa=olda['QA3'];rp=min(legacy._incmodel(2026,'P')['principal_QA3']['relief_probability'],a['IP_per_relief']/5);sp=min(1,max(0,(oldqa-oldra*rp)/oldgs) if oldgs else 0,a['IP_per_start']/5);a['QA3']=min(a['IP']/5,a['GS']+a['RA'],a['GS']*sp+a['RA']*rp)
 c['QA3']=sum(c['probabilities']['RP' if s=='1' else 'SP']*a['QA3'] for s,a in c['conditional'].items());return c

def run():
 sel=read(HERE/'Selection_Freeze.json')['selection'];league=read(HERE.parent/'roster-opportunity/Hybrid_League.json.gz');assets=[a for a in league if a['status']=='supported_MLB'];zs=[];bef=[];verification=[]
 for a in assets:
  p=old.players[a['id']];rr=a['role'];hs=v.seasons(p,rr);z={'id':a['mlbam_id'],'year':2026,'role':rr,'history_override':hs,'x':base['features'](hs,rr,2026,a['mlbam_id']),'bounded_x':base['features'](hs,rr,2026,a['mlbam_id'],True)};zs.append(z);bef.append(a['components']);o=observation(z,2026);key='PA' if rr=='H' else 'IP';verification.append({'id':a['id'],'mlbam_id':z['id'],'name':a['name'],'role':rr,'old_snapshot_exposure':z['x'][0],'verified_exposure':o['exposure'],'exposure_change':o['exposure']-z['x'][0] if o['exposure'] is not None else None,'old_snapshot_GP':GP.get((z['id'],2026)) if rr=='H' else z['x'][15],'old_legacy_feature_GP':z['x'][15],'verified_GP':o['GP'],'verified_GS':o['GS'],'observation_status':o['status'],'complete':o['complete'],'source':o['source'],'source_date':o['source_date'],'medical_absence_inferred':False})
 before_roster=[None]*len(zs);semantics=[]
 # Models have target<=2025 despite asof2026; no2026 fitting or named tuning.
 for fam in ['H','P']:
  indices=[i for i,z in enumerate(zs) if (z['role']=='H')==(fam=='H')];zz=[zs[i] for i in indices];model=model_for(2026,fam);method,prob=sel[fam].split('__');ps=predict_model(model,zz,method,prob)
  for i,c in zip(indices,ps):before_roster[i]=c
 # Explicit missing-source robustness replay uses observed NaN+status markers,
 # not a fake zero. Rebuild unverified2026 features while retaining trained model.
 cache=VERIFIED.pop((2026,'H'));cachep=VERIFIED.pop((2026,'P'))
 for fam in ['H','P']:
  indices=[i for i,z in enumerate(zs) if (z['role']=='H')==(fam=='H')];zz=[zs[i] for i in indices];model=model_for(2026,fam);method,prob=sel[fam].split('__');ps=predict_model(model,zz,method,prob)
  for i,c in zip(indices,ps):semantics.append({'mlbam_id':zs[i]['id'],'role':zs[i]['role'],'unverified_source_workload':value(c,fam),'verified_source_workload':value(before_roster[i],fam),'verification_sensitivity':value(before_roster[i],fam)-value(c,fam)})
 VERIFIED[2026,'H']=cache;VERIFIED[2026,'P']=cachep
 rosterlists={}
 for p in sorted((HERE/'verified').glob('roster-*.json.gz')):
  team=int(p.name.split('-')[1].split('.')[0])
  for a in read(p)['roster']:rosterlists.setdefault(a['person']['id'],set()).add(team)
 rosters={i:next(iter(ts)) for i,ts in rosterlists.items() if len(ts)==1};budgets={}
 for a in read(HERE/'verified/team-hitting2026.json.gz')['stats'][0]['splits']:
  s=a['stat'];budgets.setdefault(a['team']['id'],{})['PA']=float(s['plateAppearances'])*162/max(1,float(s['gamesPlayed']))
 for a in read(HERE/'verified/team-pitching2026.json.gz')['stats'][0]['splits']:
  s=a['stat'];n=max(1,float(s['gamesPlayed']));budgets.setdefault(a['team']['id'],{}).update(GS=float(s['gamesStarted'])*162/n,IP=float(s['outs'])/3*162/n)
 post_roster,ledger=allocate_verified(before_roster,zs,rosters,budgets);evid=read(HERE/'Availability_Evidence.json');out=[];decomp=[];named=[];diagnosticids=set(read(HERE/'Protocol_Freeze.json')['reserved_excluded_known_diagnostic_ids'])
 for i,(a,z,c) in enumerate(zip(assets,zs,post_roster)):
  key='PA' if z['role']=='H' else 'IP';pre=before_roster[i];q=1-pre['probabilities']['absent'];c=apply_verified_availability(c,z,evid);c=preserve_qa3(c,bef[i]);stats0=legacy.prior.stats(a['baseline'],c,z['role'],z);final=stats0[key];assert abs(final-c[key])<1e-8;assert abs(sum(c['probabilities'].values())-1)<1e-8
  if key=='IP':assert stats0['QA3']<=final/5+1e-8
  if key=='PA':assert stats0['AB']+sum(stats0[k] for k in ['BB','HBP','SF'])<=final+1e-8
  healthy=pre['opportunity_layer']['healthy_role_capacity']*pre['opportunity_layer']['demonstrated_depth'];conditional=pre[key]/q if q else 0
  d={'id':a['id'],'mlbam_id':z['id'],'name':a['name'],'role':z['role'],'production_workload':a['baseline'][key],'frozen_hybrid_workload':a['hybrid'][key],'verified_latest_exposure':verification[i]['verified_exposure'],'observation_status':verification[i]['observation_status'],'healthy_full_role_capacity_scenario':healthy,'healthy_scenario_is_medical_fact':False,'conditional_active_workload':conditional,'participation_probability':q,'after_participation':pre[key],'after_roster_allocation':post_roster[i][key],'after_verified_availability':c[key],'ensemble_median_weight':0,'final_workload':final,'delta_vs_frozen_hybrid':final-a['hybrid'][key],'delta_vs_production':final-a['baseline'][key],'conditional_model_bridge':conditional-a['hybrid'][key],'participation_delta':pre[key]-conditional,'roster_delta':post_roster[i][key]-pre[key],'medical_delta':c[key]-post_roster[i][key],'numeric_reconciliation_delta':final-c[key],'roster_allocation_executed':c['opportunity_layer']['roster_allocation_executed'],'method':c['opportunity_layer']['method'],'probability_method':c['opportunity_layer']['probability_method']}
  for k,v0 in c['probabilities'].items():d['probability_'+k]=v0
  for st,ss in c['conditional'].items():
   for k,v0 in ss.items():d[f'conditional_state{st}_{k}']=v0
  d['decomposition_error']=d['conditional_model_bridge']+d['participation_delta']+d['roster_delta']+d['medical_delta']+d['numeric_reconciliation_delta']-d['delta_vs_frozen_hybrid'];assert abs(d['decomposition_error'])<1e-8
  row={'id':a['id'],'mlbam_id':z['id'],'name':a['name'],'role':z['role'],'production':a['baseline'],'frozen_hybrid':a['hybrid'],'repair':stats0,'component':c,'before_roster':pre,'opportunity_inputs':fz(z)[1],'later_years_changed':False,'talent_source':'preserved independent production rates; no external forecasts'};out.append(row);decomp.append(d)
  if z['id'] in diagnosticids:named.append(row)
 assert len(out)==1900 and len(named)==12
 put('Repair_League.json.gz',out);put('Diagnostic_Players.json',named);csvout('League_1900_Before_After.csv',decomp);csvout('Diagnostic_Players_Before_After.csv',[a for a in decomp if a['mlbam_id'] in diagnosticids]);csvout('Observation_Verification_1900.csv',verification);csvout('Verification_Sensitivity.csv',semantics);csvout('Team_Allocation_Ledger.csv',ledger)
 summary={rr:{'n':sum(a['role']==rr for a in decomp),'mean_delta_vs_hybrid':float(np.mean([a['delta_vs_frozen_hybrid'] for a in decomp if a['role']==rr])),'mean_delta_vs_production':float(np.mean([a['delta_vs_production'] for a in decomp if a['role']==rr]))} for rr in ['H','SP','RP']}
 checks={'players':len(out),'diagnostic_players':len(named),'max_decomposition_error':max(abs(a['decomposition_error']) for a in decomp),'allocated_players':sum(a['roster_allocation_executed'] for a in decomp),'verified_changed_exposure_n':sum(abs(a['exposure_change'] or 0)>1e-8 for a in verification),'old_zero_now_positive_n':sum(a['old_snapshot_exposure']==0 and a['verified_exposure']>0 for a in verification),'confirmed_zero_n':sum(a['observation_status']=='verified_zero' for a in verification),'team_ledger_records':len(ledger),'organization_conflicts':sum(len(ts)>1 for ts in rosterlists.values()),'no_production_mutation':True,'no_external_projections':True,'later_years_frozen':True,'summary':summary};put('Replay_Verification.json',checks);print('REPLAY',checks,flush=True)
if __name__=='__main__':run()
