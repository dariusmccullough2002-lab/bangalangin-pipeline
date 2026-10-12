"""Verify the actual-model candidate against every original catalog asset."""
import json,gzip,base64,re,sys,hashlib
from pathlib import Path
D=Path(__file__).resolve().parent;ROOT=D.parents[1]
old=json.loads(gzip.decompress(base64.b64decode(re.search("const packed='([^']+)'",(ROOT/'trade-analyzer-beta/index.html').read_text())[1])))
new=json.loads(gzip.decompress((D/'Candidate_Catalog.json.gz').read_bytes()));byid={a['id']:a for a in new['assets']};n=0
for a in old['assets']:
 b=byid[a['id']]
 if 'relief_opportunity_repair' not in b.get('audit',{}):assert b==a;continue
 n+=1;assert a['audit']['kind']=='MLB' and a['audit']['role']=='RP'
 assert b['annual_expected_utility'][1:]==a['annual_expected_utility'][1:]
 for field,value in a['audit']['projection'].items():
  if field not in ['SV','HLD']:assert b['audit']['projection'][field]==value
 assert b['values']['neutral']['display']==b['competitive_values']['neutral']['display']
 assert all(v==b['values']['neutral'] for v in b['values'].values())
 for scenario in ['low','high']:
  assert all(v==b['competitive_range'][scenario]['neutral'] for v in b['range'][scenario].values())
 for k,v in b['audit']['projection'].items():
  average=sum(pr*st[0][k] for pr,st in zip([.25,.5,.25],b['audit']['outcome_state_projections']))
  assert abs(average-v)<1e-8
 for mode in b['values']:
  assert b['competitive_range']['low'][mode]<=b['competitive_values'][mode]['display']<=b['competitive_range']['high'][mode]
for trade in new['trades']:
 for mode,t in trade['modes'].items():
  sums=[sum(byid[i]['competitive_values'][mode]['display'] for i in ids) for ids in trade['identities']]
  assert sums==t['package_values']
result={'assets':len(old['assets']),'changed_relief_assets':n,'unchanged_assets':len(old['assets'])-n,'all_future_utility_rewards_unchanged':True,'nonleverage_counts_unchanged':True,'uncertainty_state_means_consistent':True,'strategy_invariant_transfer_values':True,'trade_package_sums_consistent':True,'production_html_sha256':hashlib.sha256((ROOT/'trade-analyzer-beta/index.html').read_bytes()).hexdigest()}
(D/'Catalog_Verification.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
