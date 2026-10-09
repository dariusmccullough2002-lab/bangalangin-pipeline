from run_helpers import *
selection=read(HERE/"Selection_Freeze.json")["selected"]
# Current integration: all supported MLB; RP remains the preserved expert.
league=read(OUT/'Past_Only_League_Impact.json.gz');mods={f:joblib.load(HERE/f'current-{f}.joblib') for f in ['P','H']}
for f,mod in mods.items():checkpoint(mod,HERE/f'current-{f}.joblib')
current=[]
for a in league:
 if a['status']!='supported_MLB':continue
 rr=a['role'];p=old.players[a['id']];rows=v.seasons(p,rr);z={'id':a['mlbam_id'],'year':2026,'role':rr,'name':a['name'],'history_override':rows,'x':base['features'](rows,rr,2026,a['mlbam_id']),'bounded_x':base['features'](rows,rr,2026,a['mlbam_id'],True)};fam='H' if rr=='H' else 'P';c=incumbent(2026,fam,[z])[0];key='PA' if rr=='H' else 'IP'
 preds={} if rr=='RP' else {s:predict_layer(mods[fam],[z],[c],s)[0] for s in VAR};chosen=c if rr=='RP' or selection[fam]=='incumbent' else preds[selection[fam]];b=a['baseline_annual'][0];st=stats(b,chosen,rr,z)
 if rr!='RP' and selection[fam]!='incumbent':assert_coherent(chosen,st,rr,754 if rr=='H' else 251)
 d=decomposition(z);current.append({'id':a['id'],'mlbam_id':z['id'],'name':a['name'],'role':rr,'selected':selection[fam] if rr!='RP' else 'preserved_RP','baseline_workload':b[key],'incumbent_workload':c[key],'selected_workload':chosen[key],'healthy_role_appearances':d['healthy_opportunity'],'depth':d['depth'],'latest_appearances':d['latest_opportunity'],'counts_missing':d['counts_missing'],**{s:q[key] for s,q in preds.items()},**{'selected_'+k:val for k,val in st.items()}})
csvout('Current_Player_Comparisons.csv',current);saveout('Current.json.gz',current);saveout('Integration.json',{'supported':len(current),'selected':selection,'production_changed':False,'medical_evidence_missing_not_healthy':True,'roster_depth_not_fabricated':True,'all_current_stats_coherent':True,'GP_preserved_rows':len(GP)})
print('COMPLETE',selection,flush=True)
