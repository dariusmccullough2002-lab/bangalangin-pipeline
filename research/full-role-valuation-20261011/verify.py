"""Check experiment identities, arithmetic, chronology and publication isolation."""
import json,gzip,csv,math,hashlib,subprocess,sys
from pathlib import Path
D=Path(__file__).resolve().parent;ROOT=D.parents[1]
read=lambda p:json.loads(gzip.decompress(p.read_bytes()) if p.suffix=='.gz' else p.read_text())
manifest=read(D/'Reproduction_Manifest.json');checks={}
for p,sha in manifest['files'].items():assert hashlib.sha256(Path(p).read_bytes()).hexdigest()==sha,p
checks['source_hashes']=len(manifest['files'])
near=lambda a,b:math.isclose(a,b,rel_tol=1e-9,abs_tol=1e-8)
for name in ['Current_Lines.json.gz','Historical_Lines.json.gz']:
 rows=read(D/name);n=0
 for row in rows:
  b=row['lines']['production'];rr=row['role'];key='PA' if rr=='H' else 'IP'
  for method in ['full_role','expected_benchmark']:
   s=row['lines'].get(method)
   if not s:continue
   factor=s[key]/b[key]
   for k in (['PA','AB','H','HR','R','RBI','SB','BB','HBP','SF','TB'] if rr=='H' else ['IP','K','ER','H','BB']):assert near(s[k],b[k]*factor),(row.get('name',row.get('id')),method,k)
   if rr=='H':
    assert s['H']<=s['AB']+1e-8 and s['HR']<=s['H']+1e-8
    assert s['H']+3*s['HR']<=s['TB']+1e-8<=4*s['H']+2e-8
    assert s['AB']+s['BB']+s['HBP']+s['SF']<=s['PA']+1e-8
   elif s.get('QA3') is not None:assert 0<=s['QA3']<=s['IP']/5+1e-8
   n+=1
 checks[name+'_fixed_rate_lines']=n
# Replay production mean exposures must match archived chronological workloads.
hs=list(csv.DictReader((D/'Historical_Player_Comparisons.csv').open()))
for row in hs:
 if row['category_supported']=='True':
  key='PA' if row['role']=='H' else 'IP'
  assert near(float(row['production_'+key]),float(row['production_workload'])),(row['name'],row['anchor'])
checks['historical_baseline_workloads_match']=sum(a['category_supported']=='True' for a in hs)
P=Path(manifest['arguments'][1]);original=read(P/'targeted-repair/Chronological_Cases.json.gz')
for row in original:
 for obs in row['component']['opportunity_layer']['observations']:assert obs['year']<=row['anchor']
checks['historical_observation_cutoffs']=len(original)
# Verify saved full-role models, without fitting or changing their probabilities.
import joblib
models=[]
for path in (P/'historical-coverage-retrain').glob('model-*-*.joblib'):
 m=joblib.load(path);z=m['manifest'];assert z['latest_target']<=min(m['asof'],2025)
 models.append({'file':path.name,'asof':m['asof'],'latest_target':z['latest_target'],'rows':z['rows']})
checks['chronological_full_role_models']=models
changed=subprocess.check_output(['git','diff','--name-only',manifest['production_base'],'--',':(exclude)research/full-role-valuation-20261011'],cwd=ROOT,text=True).splitlines()
assert not changed,changed
checks['publication_files_changed']=changed;checks['production_adoption']=False
(D/'Verification.json').write_text(json.dumps(checks,indent=2))
print(json.dumps({k:v for k,v in checks.items() if k!='chronological_full_role_models'}))
