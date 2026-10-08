"""Read-only checks of cached coverage, saved predictions, identities and phase boundaries."""
import json,hashlib
from pathlib import Path
import numpy as np
p=Path(__file__).resolve().parent
v=json.load(open(p/'results/validation.json'));d=json.load(open(p/'results/diagnostics.json'));c=json.load(open(p/'results/cohort.json'))
assert v['coverage']['ranking_rows']==399 and len(c)==399
for y in [2012,2013,2017,2018]:
 r=json.load(open(p/'raw'/f'rankings-{y}.json'));assert sorted(x['rank'] for x in r)==list(range(1,101));assert len(set(x['name'] for x in r))==100
for x in v['predictions']:
 assert abs(sum(x['predicted'])-1)<1e-8 and min(x['predicted'])>=0
for x in v['probability_grid']:assert abs(sum(x['probabilities'])-1)<1e-8
assert all(d['checks'].values())
assert v['coverage']['test_counts']==[52,20,17,9,1]
for item in json.load(open(p/'sources.json')):assert hashlib.sha256((p/'raw'/item['file']).read_bytes()).hexdigest()==item['sha256']
assert json.load(open(p/'results/production-before.json'))['matches_preserved_model']
print('PASS: ranking coverage, hashes, distinct MLBAM IDs in chronological holdout, probability sums, temporal cutoff, and architecture checks. QA3, position eligibility and full outcome definitions remain unvalidated.')
