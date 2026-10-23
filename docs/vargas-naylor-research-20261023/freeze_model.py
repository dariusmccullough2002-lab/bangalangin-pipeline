"""Extract the two frozen baseline player rows and category constants once."""
from pathlib import Path
import re,json,gzip,base64,hashlib
P=Path(__file__).resolve().parent;ROOT=P.parents[1];I=P/'inputs'
baseline=ROOT/'trade-analyzer-beta/index.html';scale=ROOT/'docs/value-audit-20261012/inputs/model-evidence.json'
if not (I/'baseline-players.json').exists():
 source=baseline.read_text();data=json.loads(gzip.decompress(base64.b64decode(re.search(r"const packed='([^']+)'",source)[1])))
 assets=[a for a in data['assets'] if a.get('career_profile',{}).get('identifiers',{}).get('mlbamId') in [678246,647304]]
 assert len(assets)==2
 (I/'baseline-players.json').write_text(json.dumps(assets,indent=2)+'\n')
 model=json.loads(scale.read_text());(I/'model-scale.json').write_text(json.dumps({k:v for k,v in model.items() if k not in ['players','source_hashes']},indent=2)+'\n')
 (P/'Model_Manifest.json').write_text(json.dumps({'sourceFiles':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [baseline,scale]},'meaning':'Unmodified saved baseline before the shared quality overlay; live overlay values are documented separately in Checkpoint.md.'},indent=2)+'\n')
print('Frozen baseline player rows and league category scale available.')
