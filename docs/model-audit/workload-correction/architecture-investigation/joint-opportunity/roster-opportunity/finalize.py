from pathlib import Path
import json,hashlib,csv
HERE=Path(__file__).resolve().parent
read=lambda name:json.loads((HERE/name).read_text())
d=read('Integrated_Validation.json');g=read('Hybrid_Release_Gates.json');g['gates']=[a for a in g['gates'] if not a['gate'].startswith('additional_')]
for name,pool,group,key,limit in [('expandedSP','P_expanded','SP','IP',47.376),('youngSP','P_expanded','young_SP','IP',43.4103),('stableSP_vs_strong','P_expanded','stable_rotation','IP',51.3123),('durableH_vs_strong','H_standard','durable_four_years','PA',89.1316)]:
 a=d[pool][group];value=a['metrics'][key]['hybrid']['MAE'];g['gates'].append({'gate':'additional_'+name,'n':a['n'],'value':value,'limit':limit,'pass':value<=limit,'paired_vs_strong':a['paired']})
for pool,key in [('P_expanded','IP'),('H_standard','PA')]:
 for group,a in d[pool].items():
  if not group.startswith('anchor_') or a['n']<30:continue
  old=a['metrics'][key]['strong_prior']['MAE'];new=a['metrics'][key]['hybrid']['MAE'];bad=new>1.1*old and a['paired']['player_cluster95'][0]>0
  g['gates'].append({'gate':'additional_'+pool+'_'+group+'_stability','pass':not bad,'prior':old,'hybrid':new,'paired':a['paired']})
g['all_gates_pass']=all(a['pass'] for a in g['gates']);g['ready_for_release_review']=False;(HERE/'Hybrid_Release_Gates.json').write_text(json.dumps(g,indent=2))
source=read('Simple_Selection_Freeze.json');assert source['source_sha256']==hashlib.sha256((HERE/'simple_select.py').read_bytes()).hexdigest();(HERE/'PROTOCOL_at_Final_Selection.md').write_bytes((HERE/'PROTOCOL.md').read_bytes())
(HERE/'Input_Provenance.json').write_text(json.dumps({'preserved_files':[{'path':str(p),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in [Path('recovered/beta-unpacked.json'),Path('recovered/model/trade-preview-v22/model/career_history_cache.json'),Path('recovered/model/trade-preview-v22/model/inputs/baseline.json.gz'),Path('recovered/model/trade-preview-v22/model/inputs/game-inputs.json.gz')]],'new_raw_statistical_collection':False,'future_feature_rows_filtered_by_anchor':True,'historical_GP_coverage_not_random':True,'active_H_targets_use_complete_PA_outcomes_instead_of_GP_coverage_selection':True,'known_prior_empty_artifact':'parent past-hitter-2019.joblib remains unchanged; historical integrated replay uses preserved components, not that unreadable file','validation_scope':'Chronological retrospective cohorts already exposed, not fresh untouched holdout'},indent=2))
print('Final gates',[(a['gate'],a['pass']) for a in g['gates'] if not a['pass']])
