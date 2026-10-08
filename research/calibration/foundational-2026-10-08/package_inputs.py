"""Package selected exact replay inputs, without changing collected raw files."""
import json,gzip,zipfile,hashlib,re,unicodedata,ast,datetime
from pathlib import Path
P=Path(__file__).resolve().parent;R=P/'raw';O=P/'results';BASE=P.parent/'phase1-calibration';rows=json.load(open(O/'resolved-rankings.json'));old=json.load(open(BASE/'results/cohort.json'));ids={r['mlbamId'] for r in rows+old};manifest=[];entries={}
def add(name,b,notes=''):
 entries['raw/'+name]=b;manifest.append({'archive_path':'raw/'+name,'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest(),'notes':notes})
def comp(x):return gzip.compress(json.dumps(x,separators=(',',':')).encode(),mtime=0)
# Complete original new MLB season responses and compact prior-year MiLB rows needed for every analyzed identity.
audits={(r['year'],r['group']):r for r in json.load(open(O/'prospect-calibration.json'))['minor_feature_source_audit']}
for f in sorted(R.glob('mlb-*.json.gz')):add(f.name,f.read_bytes(),'Complete MLB source response; not filtered')
for f in sorted(R.glob('milb-*.json.gz')):
 x=json.loads(gzip.decompress(f.read_bytes()));_,group,year=f.name.replace('.json.gz','').split('-');x['_full_source_audit']=audits[int(year),group];x['_full_source_sha256']=hashlib.sha256(f.read_bytes()).hexdigest();x['_selected_identity_filter']=sorted(ids)
 for s in x['stats']:s['splits']=[r for r in s['splits'] if r['player']['id'] in ids]
 add(f.name,comp(x),'Exact original rows for all cohort identities; full-source coverage/counts/hash recorded; unrelated players omitted')
x=json.loads(gzip.decompress((R/'game-inputs.json.gz').read_bytes()));x['weekly']={w:v for w,v in x['weekly'].items() if w.startswith(('2018','2024'))};x['positions']={y:v for y,v in x['positions'].items() if y in ['2017','2023']};x['bios']={id:v for id,v in x['bios'].items() if int(id) in ids};x['_replay_scope']='AnnualQA3 all2010-2025; H/P weeks2018/2024; prior-position games2017/2023; cohort biographies only. Source-reconciliation result saved, full raw archives optional.'
add('game-inputs.json.gz',comp(x),'Lossless selected context replay; full generated input snapshot hash retained in source inventory')
# Stable identity rows include ambiguous matching candidates, not only chosen winners.
norm=lambda s:re.sub('[^a-z]','',unicodedata.normalize('NFKD',re.sub(r'\b(Jr\.?|III|II)\b','',s,flags=re.I)).encode('ascii','ignore').decode().lower())
module=ast.parse((P/'identities.py').read_text());aliases=next(ast.literal_eval(n.value) for n in module.body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='aliases' for t in n.targets));wanted={norm(r['name']) for r in rows};wanted|={aliases.get(w,w) for w in list(wanted)}
blocks=json.loads(gzip.decompress((R/'identity-register.json.gz').read_bytes()));selected=[]
for block in blocks:
 z=[r for r in block['rows'] if r['key_mlbam'] and (int(r['key_mlbam']) in ids or any(norm(a+' '+r['name_last']+' '+r.get('name_suffix','')) in wanted for a in [r['name_first'],r['name_given'],r.get('name_nick','')] if a))];selected.append({k:v for k,v in block.items() if k!='rows'}|{'rows':z})
add('identity-register.json.gz',comp(selected),'Stable selected rows plus all name-matching ambiguous candidates; current register status fields not modeling features')
for name in ['fg-rankings.json','identity-overrides.json']:add(name,(R/name).read_bytes(),'Factual ordinal/name/grade extraction or explicit identity override')
for f in sorted(R.glob('fg-web-*.json')):
 x=json.load(open(f));facts=[]
 for line in x['lines']:
  prefix,s=line.split(': ',1) if ': ' in line else ('',line);plain=re.sub(r'【\d+†([^†】]+)(?:†[^】]+)?】',r'\1',s);keep=False
  if re.match(r'(?:> )?\d+\. ',plain):
   # Keep factual name/position/org; omit scouting paragraph after org colon.
   s=s.split(':',1)[0];keep=True
  elif 'FV:' in plain and re.search(r'\d+/\d+',plain):keep=True
  elif re.match(r'(Hit|Fastball)\s*\|',plain):keep=True
  elif '/' in plain and '|' in plain and all(re.match(r'^[0-9+./ −–-]*$',v) for v in plain.split('|')):keep=True
  elif len(plain.split('|'))==8 and plain.split('|')[0].strip().isdigit():keep=True
  elif re.match(r'(January|February|March) \d+, (2010|2011|2014|2015|2019|2020)$',plain):keep=True
  if keep:facts.append(prefix+': '+s)
 x['lines']=facts;x['extraction_scope']='Factual rank/name/position/org/grades and publication header only; expressive scouting prose omitted';add(f.name,json.dumps(x,indent=2).encode(),'Filtered factual replay of original retrieved lines; no scouting paragraphs')
with zipfile.ZipFile(P/'replay-inputs.zip','w',zipfile.ZIP_DEFLATED) as z:
 for name,b in entries.items():z.writestr(name,b)
source=[]
for f in sorted(R.iterdir()):
 if f.is_file() and (f.suffix=='.zip' or f.name.endswith('.json.gz')):source.append({'file':f.name,'bytes':f.stat().st_size,'sha256':hashlib.sha256(f.read_bytes()).hexdigest(),'url':f'https://www.retrosheet.org/downloads/{f.name[11:15]}/{f.name[11:15]}csvs.zip' if f.name.startswith('retrosheet-') else 'See collected response/source collector for exact endpoint'})
(P/'input-source-manifest.json').write_text(json.dumps({'created_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'archive_sha256':hashlib.sha256((P/'replay-inputs.zip').read_bytes()).hexdigest(),'replay_entries':manifest,'full_source_inventory':source,'original_Phase1_inputs':'Unchanged sibling phase1-2026-10-08/raw-data.zip','scope':'Selected exact inputs reproduce analysis; source audits quote full source inventories, not filtered counts. Full public ZIPs not duplicated in Git.'},indent=2))
print('replay zip bytes',(P/'replay-inputs.zip').stat().st_size,'entries',len(entries),'selected IDs',len(ids))
