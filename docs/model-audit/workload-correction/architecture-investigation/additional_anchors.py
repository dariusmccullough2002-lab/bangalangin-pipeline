"""Additional cold-start2015 and known-shortened-season2020 forecasts; past-only."""
import sys,json,gzip,copy
from pathlib import Path
import numpy as np
OUT=Path(__file__).resolve().parent;main=OUT/'opportunity_models.py';s=main.read_text();env={'__file__':str(main),'__name__':'extra_helpers'}
exec(compile(s.split('devscores={};test=[];selected={};training_manifest=[]')[0],str(main),'exec'),env)
selected=json.loads((OUT/'Opportunity_Validation.json').read_text())['selected_by_development'];rows=[];manifest=[]
for rr in ['H','SP','RP']:
 for year in [2015,2020]:
  train=env['training'](rr,year);xs=[z for z in env['records'][rr] if z['year']==year and z['id']%5==0 and z['positive_anchor']]
  if not xs:continue
  methods={'primary':selected[rr],'schedule_aware':'hurdle_bounded2020'};preds={}
  for label,method in methods.items():preds[label]=env['predict'](env['fit'](train,method),xs,method,env['cap_at'](rr,year))[0]
  manifest.append({'role':rr,'anchor':year,'latest_training_target':max(z['year']+1 for z in train),'training_rows':len(train),'cases':len(xs)})
  for j,z in enumerate(xs):
   history=env['hist'][z['id'],'H' if rr=='H' else 'P'];f=env['forecast'](history,rr,year,z['id'],strict=True);fb=env['forecast'](history,rr,year,z['id'],strict=True,pandemic='bounded_capacity')
   if not f:continue
   baseline=env['project'](f,rr,z['x'][13],year,True);bounded=env['project'](fb,rr,z['x'][13],year,True);key='PA' if rr=='H' else 'IP'
   rows.append({'name':z['name'],'mlbam_id':z['id'],'anchor':year,'role':rr,'groups':z['groups'],'actual':z['target'],'baseline_raw':baseline[key],'baseline_bounded':bounded[key],**{label:float(ps[j]) for label,ps in preds.items()}})
score={}
for year in [2015,2020]:
 score[str(year)]={}
 for rr in ['H','SP','RP']:
  xs=[z for z in rows if z['anchor']==year and z['role']==rr]
  if xs:score[str(year)][rr]={'n':len(xs),'metrics':{method:{'MAE':float(np.mean([abs(z[method]-z['actual']) for z in xs])),'bias':float(np.mean([z[method]-z['actual'] for z in xs]))} for method in ['baseline_raw','baseline_bounded','primary','schedule_aware']}}
(OUT/'Additional_Anchor_Validation.json').write_text(json.dumps({'scores':score,'training_manifest':manifest,'note':'2015 tests limited-history cold-start;2020->2021 tests a known shortened input season against an actual full-length target. Future2020 length is never assumed at a2019 prediction date. No new model selection on these cases.'},indent=2));(OUT/'Additional_Anchor_Cases.json.gz').write_bytes(gzip.compress(json.dumps(rows).encode(),mtime=0));print('Additional anchors',score,flush=True)
