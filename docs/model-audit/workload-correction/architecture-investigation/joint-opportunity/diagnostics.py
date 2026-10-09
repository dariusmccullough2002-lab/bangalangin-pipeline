"""Diagnostics on saved predictions only: calibration, COVID, cohorts and uncertainty."""
import json,gzip,pathlib,numpy as np
P=pathlib.Path(__file__).resolve().parent
read=lambda p:json.loads(gzip.decompress(p.read_bytes()) if p.suffix=='.gz' else p.read_text())
def metric(pairs):
 d=np.array([p-a for p,a in pairs]);return dict(n=len(d),MAE=float(np.mean(abs(d))),bias=float(np.mean(d)),RMSE=float(np.sqrt(np.mean(d*d))))
def cluster_delta(xs,a,b,k,seed=2309):
 rng=np.random.default_rng(seed);ids=sorted({z['mlbam_id'] for z in xs});rows={i:[abs(z[b][k]-z['actual'].get(k,0))-abs(z[a][k]-z['actual'].get(k,0)) for z in xs if z['mlbam_id']==i] for i in ids};s=np.array([sum(rows[i]) for i in ids]);n=np.array([len(rows[i]) for i in ids]);draw=rng.integers(len(ids),size=(2000,len(ids)));v=s[draw].sum(axis=1)/n[draw].sum(axis=1)
 return {'comparison':f'{b} minus {a} MAE','players':len(ids),'cases':len(xs),'delta':float(s.sum()/n.sum()),'cluster_bootstrap_95_interval':np.quantile(v,[.025,.975]).tolist(),'caution':'Exploratory exposed labels; repeated model development and cohort multiplicity not corrected.'}
xs=read(P/'Past_Only_Pitch_Cases.json.gz');hs=read(P/'Past_Only_Hitter_Cases.json.gz');he=read(P/'Past_Only_Hitter_Additional.json.gz');out={'probability':{},'transitions':{},'bootstrap':{},'COVID':{},'season':{}}
for variant in ['joint_raw','joint_calibrated','joint_calendar','past_only']:
 data=[]
 for z in xs:
  state=0 if z['actual_absent'] else 2 if z['future_role_observed_for_scoring_only']=='SP' else 1
  pp=z['components'][variant]['probabilities'];p=np.array([pp['absent'],pp['RP'],pp['SP']]);y=np.eye(3)[state];data.append((z,p,state,float(sum((p-y)**2)),float(-np.log(max(p[state],1e-12)))))
 out['probability'][variant]={'multiclass_Brier':float(np.mean([z[3] for z in data])),'logloss':float(np.mean([z[4] for z in data])),'bins':{}}
 for state,name in enumerate(['absent','RP','SP']):
  bins=[]
  for lo,hi in [(0,.2),(.2,.4),(.4,.6),(.6,.8),(.8,1.00001)]:
   rows=[a for a in data if lo<=a[1][state]<hi]
   if rows:bins.append({'low':lo,'high':min(1,hi),'n':len(rows),'mean_prediction':float(np.mean([a[1][state] for a in rows])),'observed':float(np.mean([a[2]==state for a in rows])),'IP_bias':metric([(a[0]['joint_selected']['IP'],a[0]['actual'].get('IP',0)) for a in rows])['bias']})
  out['probability'][variant]['bins'][name]=bins
for rr in ['SP','RP']:
 for future in ['SP','RP','absent']:
  zs=[z for z in xs if z['role']==rr and ('absent' if z['actual_absent'] else z['future_role_observed_for_scoring_only'])==future]
  if zs:out['transitions'][f'{rr}_to_{future}']={k:{m:metric([(z[m][k],z['actual'].get(k,0)) for z in zs]) for m in ['baseline','linear_SP','principal_QA3','conditional_blend','past_only']} for k in ['IP','K','QA3']}
for rr in ['all','SP','RP','first_MLB_season','second_MLB_season']:
 zs=xs if rr=='all' else [z for z in xs if rr in z['groups']]
 out['bootstrap'][f'P_{rr}']=cluster_delta(zs,'linear_SP','principal_QA3','IP')
 out['bootstrap'][f'P_past_only_{rr}']=cluster_delta(zs,'linear_SP','past_only','IP')
for group in ['all','durable_four_years','aging_33plus']:
 zs=hs if group=='all' else [z for z in hs if group in z['groups']]
 out['bootstrap'][f'H_{group}']=cluster_delta(zs,'selected','hitter_selected','PA')
 out['bootstrap'][f'H_past_only_{group}']=cluster_delta(zs,'selected','past_only','PA')
for anchor in [2019,2020]:
 zs=[z for z in he if z['anchor']==anchor and 'returning_after_missed_season' not in z['groups']]
 out['COVID'][f'H_anchor_{anchor}']={k:{m:metric([(z[m].get(k,0),z['actual'].get(k,0)) for z in zs]) for m in ['baseline','selected','hitter_selected','calendar_mix_tree','calendar_mix_linear','past_only']} for k in ['PA','HR','R','RBI','SB']}
zs=[z for z in read(P/'Principal_Additional_Cases.json.gz') if z['anchor']==2020 and 'returning_after_missed_season' not in z['groups']]
out['COVID']['P_anchor_2020']={k:{m:metric([(z[m].get(k,0),z['actual'].get(k,0)) for z in zs]) for m in ['baseline','joint_selected','joint_calendar','principal_QA3','conditional_blend']} for k in ['IP','K','QA3']}
for year in sorted({z['anchor'] for z in xs}):
 zs=[z for z in xs if z['anchor']==year];out['season'][str(year)]={k:{m:metric([(z[m][k],z['actual'].get(k,0)) for z in zs]) for m in ['baseline','linear_SP','principal_QA3','conditional_blend','past_only']} for k in ['IP','QA3']}
(P/'Diagnostics.json').write_text(json.dumps(out,allow_nan=False));print('Saved diagnostics',len(xs),len(hs))
