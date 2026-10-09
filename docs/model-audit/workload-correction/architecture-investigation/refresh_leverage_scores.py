"""Refresh affected leverage-only scores from saved predictions; no model refits."""
import json,gzip,ast
from pathlib import Path
import numpy as np
OUT=Path(__file__).resolve().parent
s=(OUT/'opportunity_models.py').read_text();tree=ast.parse(s);fn=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='scores');env={'np':np,'METHODS':['ridge','direct_tree','hurdle','hurdle_no_capacity','hurdle_bounded2020']};exec(compile(ast.Module(body=[fn],type_ignores=[]),str(OUT/'opportunity_models.py'),'exec'),env)
def guard(z,methods):
 if z['role']=='H':return z
 baseline=z['baseline']
 for method in methods:
  if method not in z:continue
  ratio=z[method]['IP']/baseline['IP'] if baseline['IP'] else 0
  for k in ['SV','HLD']:z[method][k]=baseline.get(k,0)*min(1,ratio)
 return z
cases=json.loads(gzip.decompress((OUT/'Opportunity_Test_Cases.json.gz').read_bytes()));methods=env['METHODS']+['selected']
for z in cases:guard(z,methods)
(OUT/'Opportunity_Test_Cases.json.gz').write_bytes(gzip.compress(json.dumps(cases,separators=(',',':')).encode(),mtime=0));result=json.loads((OUT/'Opportunity_Validation.json').read_text());result['test_scores']=env['scores'](cases);result['leverage_guard']='SVG/HLD never increase; downscale with lower expected MLB workload to avoid retaining leverage without opportunity.';(OUT/'Opportunity_Validation.json').write_text(json.dumps(result,indent=2))
by={(z['mlbam_id'],z['anchor']):z for z in cases if z['role']!='H'};old=json.loads((OUT.parent/'Historical_Cases.json').read_text());frozen=[]
for z in old:
 q=by[z['mlbam_id'],z['anchor']];o=q|{'baseline':z['baseline'],'groups':z['subgroups']}
 for method in methods:
  ratio=q[method]['IP']/z['baseline']['IP'];o[method]={k:value*ratio for k,value in z['baseline'].items()}
 guard(o,methods);frozen.append(o)
(OUT/'Opportunity_Frozen94.json').write_text(json.dumps(env['scores'](frozen),indent=2))
for prefix in ['Role_Aware','Quality_Aware']:
 f=OUT/(prefix+'_Cases.json.gz');rows=json.loads(gzip.decompress(f.read_bytes()))
 for z in rows:guard(z,['role_aware','selected'])
 f.write_bytes(gzip.compress(json.dumps(rows,separators=(',',':')).encode(),mtime=0))
print('Saved prediction leverage scores refreshed; IP/K/QA3 predictions untouched')
