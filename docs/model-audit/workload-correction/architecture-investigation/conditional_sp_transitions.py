"""Additional fixed-anchor scoring only; no selection on transition labels."""
import json,gzip,sys
from pathlib import Path
main=Path(__file__).resolve().with_name('conditional_sp_followup.py');s=main.read_text()
env={'__file__':str(main),'__name__':'transition_helpers'}
exec(compile(s.split('dev={m:[] for m in METHODS};manifest=[]')[0],str(main),'exec'),env)
OUT=main.parent;old=json.loads(gzip.decompress((OUT/'Additional_Anchor_Cases.json.gz').read_bytes()));rows=[];manifest=[]
for year in [2015,2020]:
 pooled=env['train']('SP',year)+env['train']('RP',year)
 for rr in ['SP','RP']:
  saved=[z for z in old if z['role']==rr and z['anchor']==year];ids={z['mlbam_id']:z for z in saved}
  xs=[z for z in env['records'][rr] if z['year']==year and z['id'] in ids]
  pred=env['predict'](env['fit'](env['train'](rr,year),pooled),xs,year)
  for i,z in enumerate(xs):rows.append(ids[z['id']]|{m:float(pred[m][i]) for m in env['METHODS']})
  manifest.append({'anchor':year,'role':rr,'latest_training_target':max(z['year']+1 for z in pooled),'cases':len(xs)})
def score(pairs):
 import numpy as np
 e=np.array([a-b for a,b in pairs]);return {'n':len(e),'MAE':float(np.mean(abs(e))),'bias':float(np.mean(e))}
result={'manifest':manifest,'scores':{str(y):{r:{m:score([(z[m],z['actual']) for z in rows if z['anchor']==y and z['role']==r]) for m in ['baseline_raw','baseline_bounded','primary','schedule_aware',*env['METHODS']]} for r in ['SP','RP']} for y in [2015,2020]},'scope':'Fixed additional scoring; prior outcomes exposed. 2020 is known shortened input, 2021 actual full-season outcome. No model selection.'}
(OUT/'Conditional_SP_Transitions.json').write_text(json.dumps(result,indent=2));print(json.dumps(result['scores'],indent=2))
