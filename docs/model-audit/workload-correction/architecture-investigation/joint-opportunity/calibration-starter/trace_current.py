"""Exact current illustrative state decomposition and direct tree leaf routes."""
import importlib.util,json,hashlib,inspect
from pathlib import Path
import numpy as np,joblib
D=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('calibration_trial',D/'run.py');t=importlib.util.module_from_spec(spec);spec.loader.exec_module(t)
ids=set(t.e.read(D.parent/'targeted-repair/Protocol_Freeze.json')['reserved_excluded_known_diagnostic_ids']);assets=[a for a in t.e.read(D.parent/'targeted-repair/Repair_League.json.gz') if a['mlbam_id'] in ids];out=[];leaves=[];hist=[]
for a in assets:
 hs=t.e.v.seasons(t.e.old.players[a['id']],a['role']);z={'id':a['mlbam_id'],'year':2026,'role':a['role'],'history_override':hs,'x':t.e.base['features'](hs,a['role'],2026,a['mlbam_id']),'bounded_x':t.e.base['features'](hs,a['role'],2026,a['mlbam_id'],True)};fam='H' if a['role']=='H' else 'P';base=joblib.load(t.C/f'model-{fam}-2026.joblib');before=t.r.predict(base,z);after=t.candidate(z);sd,rd=t.s.depths(z)
 for year in range(2026,2022,-1):hist.append({'id':z['id'],'name':a['name'],**t.e.observation(z,year)})
 for variant,c in [('repaired',before),('calibrated',after)]:
  p=c['probabilities'];work=c['fitted'];cap=work['full_role_workload'];row={'id':z['id'],'name':a['name'],'role':c['role'],'variant':variant,'full_role_GS':work['slots'].get('GS'),'full_role_RA':work['slots'].get('RA'),'IP_per_start_or_PA_per_game':sd,'IP_per_relief':rd,'full_role_work':cap,'participation':c['participation'],'conditional_given_active':work['conditional_active'],'expected':work['expected'],'full_to_active_difference':work['conditional_active']-cap,'participation_difference':work['expected']-work['conditional_active']}
  for st in t.STATES:
   mean=0 if st=='absent' else cap*work['ratios'][st];row['p_'+st]=p[st];row['mean_'+st]=mean;row['contribution_'+st]=p[st]*mean
  out.append(row)
 if fam=='P':
  m=joblib.load(t.C/'direct-P-2026.joblib')['reg'];x=t.r.p.features(z);total=float(m._baseline_prediction[0,0])
  for stage,trees in enumerate(m._predictors):
   tree=trees[0];nodes=tree.nodes;node=0;path=[]
   while not nodes[node]['is_leaf']:
    n=nodes[node];j=int(n['feature_idx']);v=x[j];left=bool(n['missing_go_to_left']) if np.isnan(v) else bool(v<=n['num_threshold']);path.append({'feature':j,'value':None if np.isnan(v) else float(v),'threshold':float(n['num_threshold']),'left':left});node=int(n['left'] if left else n['right'])
   value=float(nodes[node]['value']);total+=value;leaves.append({'id':z['id'],'name':a['name'],'stage':stage,'global_intercept':float(m._baseline_prediction[0,0]),'leaf_value':value,'training_leaf_count':int(nodes[node]['count']),'age_split_on_path':any(q['feature']==13 for q in path),'route':json.dumps(path)})
  assert abs(total-float(m.predict(x[None,:])[0]))<1e-8
 t.write('Diagnostic_History.csv',hist);t.write('Diagnostic_State_Decomposition.csv',out);t.write('Direct_Pitcher_Tree_Leaves.csv',leaves)
source=[]
for name,f in [('RBI_stats_adapter',t.e.legacy.stats),('hitter_reconciliation',t.e.v.reconcile),('asof_RBI_and_workload_forecast',t.e.base['forecast']),('five_state_fit',t.s.fit),('five_state_predict',t.s.predict),('evidence_features',t.e.evidence_features),('five_state_inputs',t.s.inputs),('direct_features',t.r.p.features)]:
 try:lines,start=inspect.getsourcelines(f);file=inspect.getsourcefile(f);source.append({'name':name,'file':file,'start_line':start,'source':''.join(lines)})
 except (OSError,TypeError):source.append({'name':name,'file':'exec-loaded preserved helper; see validate_debut.py','source':str(f)})
t.put('Implemented_Code_Trace.json',source)
print('Saved exact illustration traces')
