"""Offline full-horizon league sensitivity; frozen rates, utility and existing path weights."""
from principal_followup import *
from hitter_model import predict_hitter
import csv,collections
SCENARIOS=['joint_principal','conditional_blend']
TAG='past-' if '--past-only' in sys.argv else '';RESULT='Past_Only_' if TAG else ''
if TAG:import past_only_followup
pm1=joblib.load(OUT/f'{TAG}current-pitch-one.joblib');pm8=joblib.load(OUT/f'{TAG}current-pitch-eight.joblib');hm1=joblib.load(OUT/f'{TAG}current-hitter-one.joblib');hm8=joblib.load(OUT/f'{TAG}current-hitter-eight.joblib')
source={};unchanged={};batches={rr:[] for rr in ['H','SP','RP']};assets={a['id']:a for a in catalog['assets']}
for a in catalog['assets']:
 p=old.players.get(a['id']);au=a.get('audit',{});ident=v.cf.IDS.get(a['id'],p.get('mlbamId') if p else None)
 if not p or not ident or not au.get('MLB',au).get('projection'):
  unchanged[a['id']]='Pick/prospect/unresolved or no modeled MLB projection';continue
 if au.get('role')=='H+SP' or au.get('MLB',{}).get('role')=='H+SP':unchanged[a['id']]='Two-way combined overlap/distribution kept frozen';continue
 rr=v.role(p);rows=v.seasons(p,rr);f=base['features'](rows,rr,2026,ident);fb=base['features'](rows,rr,2026,ident,True)
 if f is None:unchanged[a['id']]='No supported MLB features';continue
 z={'id':ident,'asset_id':a['id'],'year':2026,'role':rr,'x':f,'bounded_x':fb,'history_override':rows};batches[rr].append(z);source[a['id']]=z
predictions={}
for rr,xs in batches.items():
 predictions[rr]={s:[] for s in SCENARIOS}
 for h in range(1,9):
  for scenario in SCENARIOS:
   pred=predict_hitter(hm1 if h==1 else hm8,xs,h) if rr=='H' else predict_augmented(pm1 if h==1 else pm8,xs,h,scenario=='conditional_blend');predictions[rr][scenario].append(pred)
 print('Batched current predictions',rr,len(xs),flush=True)
priorP={z['id']:z for z in read(PARENT/'Conditional_SP_Current_Impact.json.gz')};priorHmethod=read(PARENT/'Opportunity_Validation.json')['selected_by_development']['H'];priorHmodel=base['fit'](base['training']('H',2026),priorHmethod);priorHp=base['predict'](priorHmodel,batches['H'],priorHmethod,base['cap_at']('H',2026))[0];priorH={z['asset_id']:float(p) for z,p in zip(batches['H'],priorHp)}
rows=[];csvrows=[];maxbaseline=0;leverage_checks=0;coherence_checks=0
positions={z['asset_id']:i for rr,xs in batches.items() for i,z in enumerate(xs)}
for a in catalog['assets']:
 ident=a['id'];baselinefit=a.get('competitive_values',a.get('values',{}));bvals={mode:baselinefit.get(mode,{}).get('display') for mode in r.MODES};out={'id':ident,'name':a['name'],'role':a.get('audit',{}).get('role'),'owner':a.get('owner'),'baseline_values':bvals,'status':unchanged.get(ident,'supported_MLB'),'variants':{}}
 if ident not in source:
  for s in SCENARIOS:out['variants'][s]={'values':bvals}
  rows.append(out);continue
 z=source[ident];rr=z['role'];i=positions[ident];p=old.players[ident];paths,audit=m.paths(p);_,ma=v.mlb_role_paths(p,rr);means=ma['annual_projection'];states=ma['outcome_state_projections'];out['baseline_annual']=means;out['age']=float(p.get('age') or 26);out['role']=rr;key='PA' if rr=='H' else 'IP';out['mlbam_id']=z['id'];out['capacity_feature']=feature(z)[38];out['baseline_values']={mode:m.competitive(paths,mode)['display'] for mode in r.MODES};maxbaseline=max(maxbaseline,abs(out['baseline_values']['neutral']-a['values']['neutral']['display']))
 for scenario in SCENARIOS:
  new=[(prob,list(path)) for prob,path in paths];annual=[];components=[]
  for t in range(8):
   pred=predictions[rr][scenario][t][i];components.append(pred);b=means[t];ratio=pred[key]/b[key] if b[key]>0 else 0;stats={k:val*ratio for k,val in b.items()}
   if b[key]==0:
    initial=ma['projection_audit']['talent_rates'];stats={k:val*pred[key] for k,val in initial.items()}
   if rr=='H':stats=v.reconcile(stats)
   else:
    stats['QA3']=pred['QA3']
    for k in ['SV','HLD']:stats[k]=b.get(k,0)*min(1,ratio)
   annual.append(stats)
   for j in range(3):
    factor=states[j][t][key]/b[key] if b[key]>0 else [states[j][0][key]/means[0][key] for j in range(3)][j];st={k:val*factor for k,val in stats.items()}
    if rr=='H':
     st=v.reconcile(st);assert st['HR']<=st['H']<=st['AB']<=st['PA']+1e-8;assert st['AB']+st['BB']+st['HBP']+st['SF']<=st['PA']+1e-7;assert st['H']+3*st['HR']<=st['TB']+1e-7 and st['TB']<=4*st['H']+1e-7;coherence_checks+=1
    else:
     assert st['QA3']<=st['IP']/5+1e-8
     for k in ['SV','HLD']:assert st[k]<=states[j][t].get(k,0)+1e-8;leverage_checks+=1
    new[j][1][t]=r.utility(r.surplus(st,rr))
  assert [x[0] for x in paths]==[x[0] for x in new] and paths[3:]==new[3:]
  fits={mode:m.competitive(new,mode) for mode in r.MODES};out['variants'][scenario]={'values':{mode:f['display'] for mode,f in fits.items()},'annual':annual,'components':components,'annual_expected_utility':[sum(prob*pa[t] for prob,pa in new) for t in range(8)],'uncertainty':'Inherited three MLB contribution states and prospect mixture; new absent/SP/RP mixture collapsed into annual mean. Not calibrated joint path uncertainty.'}
 # Reconstruct strongest previous first-year-only values without re-running old historical tests.
 prior=[(prob,list(path)) for prob,path in paths];priorwork=priorH[ident] if rr=='H' else priorP[ident]['variants']['linear_SP']['stats']['IP'];f=priorwork/means[0][key]
 out['prior_comparison_method']=priorHmethod if rr=='H' else 'linear_SP sensitivity (not the previous development-selected future_role_caps)'
 if rr!='H':out['prior_development_first_year_workload']=priorP[ident]['variants'][priorP[ident]['selected']]['stats']['IP']
 for j in range(3):
  st={k:val*f for k,val in states[j][0].items()}
  if rr=='H':st=v.reconcile(st)
  else:
   for k in ['SV','HLD']:st[k]=states[j][0].get(k,0)*min(1,f)
  prior[j][1][0]=r.utility(r.surplus(st,rr))
 out['prior_first_year_values']={mode:m.competitive(prior,mode)['display'] for mode in r.MODES};out['prior_first_year_workload']=priorwork
 rows.append(out)
for s in ['baseline',*SCENARIOS]:
 ranked=sorted([z for z in rows if (z['baseline_values'] if s=='baseline' else z['variants'][s]['values']).get('neutral') is not None],key=lambda z:-(z['baseline_values'] if s=='baseline' else z['variants'][s]['values'])['neutral'])
 for rank,z in enumerate(ranked,1):z.setdefault('neutral_ranks',{})[s]=rank
for z in rows:
 a=assets[z['id']];out={'id':z['id'],'name':z['name'],'role':z['role'],'status':z['status'],'age':z.get('age'),'baseline_rank':z.get('neutral_ranks',{}).get('baseline')}
 for mode,val in z['baseline_values'].items():out['baseline_'+mode]=val
 if 'baseline_annual' in z:
  key='PA' if z['role']=='H' else 'IP';out['baseline_first_workload']=z['baseline_annual'][0][key];out['baseline_eight_workload']=sum(a[key] for a in z['baseline_annual']);out['prior_first_workload']=z['prior_first_year_workload'];out['prior_first_neutral']=z['prior_first_year_values']['neutral']
 for s in SCENARIOS:
  va=z['variants'][s]
  for mode,val in va['values'].items():out[s+'_'+mode]=val;out[s+'_delta_'+mode]=val-z['baseline_values'][mode] if val is not None and z['baseline_values'][mode] is not None else None
  out[s+'_rank']=z.get('neutral_ranks',{}).get(s);out[s+'_rank_change']=out['baseline_rank']-out[s+'_rank'] if out['baseline_rank'] and out[s+'_rank'] else None
  if 'annual' in va:
   out[s+'_first_workload']=va['annual'][0][key];out[s+'_eight_workload']=sum(a[key] for a in va['annual'])
 csvrows.append(out)
cols=list(dict.fromkeys(k for z in csvrows for k in z));f=(OUT/(RESULT+'League_Impact.csv')).open('w',newline='');w=csv.DictWriter(f,cols);w.writeheader();w.writerows(csvrows);f.close()
summary={'assets':len(rows),'supported':len(source),'supported_by_role':{k:len(vv) for k,vv in batches.items()},'unchanged_by_reason':dict(collections.Counter(unchanged.values())),'max_baseline_value_difference':maxbaseline,'coherent_hitter_state_checks':coherence_checks,'leverage_state_checks':leverage_checks,'scope':'Full eight-year offline sensitivity. First year separate selected architecture, horizons2-8 pooled extrapolation. No numerical deployment; prospects/picks and unresolved/two-way remain frozen. Numerical changes replace workload, never multiply original workload attrition again. Talent-rate aging remains frozen.','category_policy':'Retain baseline per-opportunity MLB rates and rate aging; exact-QA3 regression separate; SV/HLD never grow from increased workload.','ranking_policy':'All catalog assets with modeled neutral value included, stable catalog tie order.','joint_path_gate':'Role state histories/probabilities and correlated uncertainty not propagated into valuation path atoms. Current mean sensitivity is not production-ready.'}
for s in SCENARIOS:
 supported=[z for z in rows if z['id'] in source];delta=np.array([z['variants'][s]['values']['neutral']-z['baseline_values']['neutral'] for z in supported]);summary[s]={'median_neutral_change':float(np.median(delta)),'mean_neutral_change':float(np.mean(delta)),'max_absolute_neutral_change':float(max(abs(delta))),'count_abs_delta_over1':int(sum(abs(delta)>1))}
summary['feature_chronology']='Past-only ability priors and H-stream debut flag' if TAG else 'Inherited frozen full-history ability priors; see past-only correction'
save(RESULT+'League_Impact.json.gz',rows);save(RESULT+'League_Impact_Summary.json',summary);print('League impacts saved',summary,flush=True)
