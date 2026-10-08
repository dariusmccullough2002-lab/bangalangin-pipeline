"""Primary Chadwick Bureau register for MLBAM/Retrosheet identities and stable births."""
import urllib.request,concurrent.futures,csv,io,json,gzip,hashlib
from pathlib import Path
P=Path(__file__).resolve().parent;R=P/'raw'
def get(k):
 f=R/f'register-{k}.csv.gz';u=f'https://raw.githubusercontent.com/chadwickbureau/register/master/data/people-{k}.csv'
 if not f.exists():
  b=urllib.request.urlopen(u,timeout=45).read()
  with gzip.open(f,'wb') as g:g.write(b)
 with gzip.open(f,'rt') as g:rows=list(csv.DictReader(g))
 return {'url':u,'file':f.name,'rows':[r for r in rows if r.get('key_mlbam') or r.get('key_retro')],'sha256':hashlib.sha256(f.read_bytes()).hexdigest()}
if __name__=='__main__':
 with concurrent.futures.ThreadPoolExecutor(max_workers=6) as pool:rows=list(pool.map(get,'0123456789abcdef'))
 with gzip.open(R/'identity-register.json.gz','wt') as g:json.dump(rows,g,separators=(',',':'))
 print('register records',sum(len(r['rows']) for r in rows))
