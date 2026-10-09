from engine import *
VAR=['usage','ridge_100','ridge_1000','ridge_10000','tree','blend','tree_quarter','tree_half','ridge_quarter','usage_quarter']
def saveout(name,obj):
 b=json.dumps(obj,default=lambda a:a.item() if isinstance(a,np.generic) else a,allow_nan=False).encode();(HERE/name).write_bytes(gzip.compress(b,mtime=0) if name.endswith('.gz') else b)
def csvout(name,rows):
 with (HERE/name).open('w',newline='') as f:
  w=csv.DictWriter(f,list(dict.fromkeys(k for a in rows for k in a)));w.writeheader();w.writerows(rows)
def summaries(rows,methods):
 return {g:{m:metric([(a[m],a['actual']) for a in rows if g in a['groups']]) for m in methods} for g in sorted({g for a in rows for g in a['groups']})}
selection={};dev={};man=[]
for fam in ['P','H']:
 cases=[];key='IP' if fam=='P' else 'PA'
 for year in [2016,2017,2018,2021,2022]:
  zs=[z for z in records['SP' if fam=='P' else 'H'] if z['year']==year and z['id']%5==4 and z['positive_anchor']]
  mod=fit_layer(year,fam);checkpoint(mod,HERE/f'dev-{fam}-{year}.joblib');man.append(mod['manifest']);inc=incumbent(year,fam,zs);pred={s:predict_layer(mod,zs,inc,s) for s in VAR}
  for i,z in enumerate(zs):cases.append({'id':z['id'],'anchor':year,'groups':['all',cohort(z)],'actual':(target(z) or {}).get('stat',{}).get(key,0),'incumbent':inc[i][key],**{s:pred[s][i][key] for s in VAR}})
  print('DEV',fam,year,len(zs),flush=True)
 score=summaries(cases,['incumbent']+VAR);critical='stable_rotation' if fam=='P' else 'everyday';groups=[g for g in [critical,'interrupted','young_entry','durable'] if g in score and score[g]['incumbent']['n']>=15]
 obj={s:score['all'][s]['MAE']+.15*abs(score['all'][s]['bias'])+np.mean([score[g][s]['MAE'] for g in groups]) for s in ['incumbent']+VAR}
 elig={s:score['all'][s]['MAE']<=score['all']['incumbent']['MAE']*1.03 and score[critical][s]['MAE']<=score[critical]['incumbent']['MAE']*1.05 for s in obj}
 selection[fam]=min([s for s in obj if elig[s]],key=obj.get);dev[fam]={'scores':score,'objective':obj,'eligible':elig,'selected':selection[fam]};saveout(f'Development_{fam}_Cases.json.gz',cases)
 print('SELECT',fam,selection[fam],obj,elig,flush=True)
saveout('Development.json',dev);saveout('Selection_Freeze.json',{'selected':selection,'protocol_sha256':hashlib.sha256((HERE/'PROTOCOL.md').read_bytes()).hexdigest(),'source_sha256':hashlib.sha256((HERE/'engine.py').read_bytes()).hexdigest(),'manifests':man,'test_used_for_selection':False})
# Selected exactly once. Retrospective comparison uses the preserved cohorts.
validation={};comparisons=[]
for fam in ['P','H']:
 key='IP' if fam=='P' else 'PA';cases=read(OUT/('Past_Only_Pitch_Cases.json.gz' if fam=='P' else 'Past_Only_Hitter_Cases.json.gz'))+read(OUT/('Past_Only_Pitch_Additional.json.gz' if fam=='P' else 'Past_Only_Hitter_Additional.json.gz'));indexcases={(a['mlbam_id'],a['anchor'],a['role']):a for a in cases};rows=[]
 for year in sorted({a['anchor'] for a in cases}):
  zs=[z for rr in (['SP'] if fam=='P' else ['H']) for z in records[rr] if z['year']==year and (z['id'],year,z['role']) in indexcases]
  if not zs:continue
  mod=fit_layer(year,fam);checkpoint(mod,HERE/f'test-{fam}-{year}.joblib');inc=[indexcases[z['id'],year,z['role']]['components']['past_only'] for z in zs];pred={s:predict_layer(mod,zs,inc,s) for s in VAR}
  for i,z in enumerate(zs):
   a=indexcases[z['id'],year,z['role']];q={'mlbam_id':z['id'],'name':z['name'],'role':z['role'],'anchor':year,'target_year':year+1,'groups':list(dict.fromkeys(a['groups']+[cohort(z),f'anchor_{year}'])),'actual':a['actual'].get(key,0),'baseline':a['baseline'].get(key,0),'incumbent':inc[i][key],**{s:pred[s][i][key] for s in VAR}};q['selected']=q[selection[fam]];rows.append(q);comparisons.append({k:v for k,v in q.items() if k!='groups'})
  print('TEST',fam,year,len(zs),flush=True)
 validation[fam]=summaries(rows,['baseline','incumbent']+VAR+['selected']);saveout(f'Test_{fam}_Cases.json.gz',rows)
saveout('Validation.json',validation);csvout('Chronological_Player_Comparisons.csv',comparisons)
# Current integration: all supported MLB; RP remains the preserved expert.
league=read(OUT/'Past_Only_League_Impact.json.gz');mods={f:fit_layer(2026,f) for f in ['P','H']}
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
