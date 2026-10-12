"""Build the integration registry and trade-scale examples from scored comparisons."""
from pathlib import Path
import json,csv,hashlib,gzip,base64,re
D=Path(__file__).resolve().parent;ROOT=D.parents[1]
rows=list(csv.DictReader((D/'Current_Comparison.csv').read_text().splitlines()))
verification=json.loads((D/'Verification.json').read_text());sourcehash=verification['source_sha256'];curvehash=hashlib.sha256((D/'Rank_Value_Curve.json').read_bytes()).hexdigest()
registry={'schema':1,'quantity':'Ranking-led dynasty policy value; contribution fundamentals remain separate','source_snapshot_sha256':sourcehash,'source_publication_date':'unknown','source_received':'2026-10-12','curve_sha256':curvehash,'curve_refit_policy':'Explicit versioned research/calibration update only; never on firstPA/IP or eligibility metadata changes','reference_strengths':{'H':600,'SP':170,'RP':170},'production_adoption':False,'players':{}}
for a in rows:
 if not a.get('reference_value'):continue
 registry['players'][a['id']]={'name':a['name'],'source_rank':int(a['source_rank']),'source_tier':int(a['source_tier']),'source_ETA':a['source_ETA'],'minimum_adjusted_rank':int(a['minimum_adjusted_rank']),'maximum_adjusted_rank':int(a['maximum_adjusted_rank']),'archived_policy_value':float(a['reference_value']),'baseline_fundamental_value':float(a['production']),'source_weight':float(a['reference_source_weight']),'evidence_exposure':float(a['career_exposure']),'role':a['role'],'debut_status_does_not_remove_membership':True,'confirmed_graduation':False,'status':a['status']}
(D/'Ranking_Policy_Registry.json').write_text(json.dumps(registry,indent=2)+'\n')
cat=json.loads(gzip.decompress(base64.b64decode(re.search("const packed='([^']+)'",(ROOT/'trade-analyzer-beta/index.html').read_text())[1])));assets={a['name']:a['values']['neutral']['display'] for a in cat['assets']};examples=[]
for prospect,mlb in [('Josue De Paula','Zack Wheeler'),('Kaelen Culpepper','Matt Olson'),('Walker Jenkins','Shea Langeliers'),('Kade Anderson','Matt Brash')]:
 a=next(a for a in rows if a['name']==prospect);examples.append({'prospect':prospect,'established_player':mlb,'established_value_unchanged':assets[mlb],'production_prospect_value':float(a['production']),'reference_policy_prospect_value':float(a['reference_value']),'production_prospect_minus_established':float(a['production'])-assets[mlb],'reference_prospect_minus_established':float(a['reference_value'])-assets[mlb]})
with (D/'Trade_Scale_Examples.csv').open('w',newline='') as f:
 w=csv.DictWriter(f,list(examples[0]));w.writeheader();w.writerows(examples)
print('Wrote registry',len(registry['players']),'and',len(examples),'trade-scale comparisons')
