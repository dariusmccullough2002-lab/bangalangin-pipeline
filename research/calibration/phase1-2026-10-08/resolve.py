import json,urllib.request,urllib.parse,concurrent.futures
from pathlib import Path
ROOT=Path(__file__).resolve().parent
aliases={'Christopher Guerrieri':'Taylor Guerrieri','Carl Webster':'Allen Webster','Christopher Austin':'Tyler Austin','Mike Soroka':'Michael Soroka','Luis Robert':'Luis Robert Jr.'}
def job(name):
 url='https://statsapi.mlb.com/api/v1/people/search?names='+urllib.parse.quote(aliases.get(name,name))
 with urllib.request.urlopen(url,timeout=30) as r:d=json.load(r)
 return name,{'url':url,'people':d.get('people',[])}
names=sorted({p['name'] for p in json.load(open(ROOT/'results/identity-unresolved.json'))})
with concurrent.futures.ThreadPoolExecutor(max_workers=5) as pool:out=dict(pool.map(job,names))
(ROOT/'raw/identity-search.json').write_text(json.dumps(out,indent=2))
for k,v in out.items():print(k,[(p['id'],p['fullName'],p.get('birthDate'),p.get('primaryPosition',{}).get('abbreviation')) for p in v['people']])
