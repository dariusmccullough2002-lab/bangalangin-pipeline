"""Resumable official MiLB workload intake. Two workers; paced globally;429/5xx backoff."""
import sys,json,time,threading,urllib.request,urllib.error,hashlib,gzip,datetime,concurrent.futures
from pathlib import Path
OUT=Path(__file__).resolve().parent;RAW=OUT/'source-cache';RAW.mkdir(exist_ok=True)
lock=threading.Lock();last=[0.]
def fetch(job):
 y,s=job;name=f'{y}-{s}';dest=RAW/(name+'.json.gz');meta=RAW/(name+'.meta.json')
 if dest.exists() and meta.exists():return name,'cached'
 url=f'https://statsapi.mlb.com/api/v1/stats?stats=season&group=pitching&season={y}&sportId={s}&playerPool=ALL&limit=10000'
 for attempt in range(5):
  with lock:
   wait=max(0,.75-(time.monotonic()-last[0]));time.sleep(wait);last[0]=time.monotonic()
  try:
   req=urllib.request.Request(url,headers={'User-Agent':'BangaLangin-workload-review/1.0'})
   with urllib.request.urlopen(req,timeout=40) as resp:b=resp.read()
   x=json.loads(b);groups=x.get('stats',[])
   if len(groups)!=1:raise ValueError('Missing or ambiguous stat group')
   g=groups[0];n=len(g['splits']);total=g.get('totalSplits')
   if n!=total:raise ValueError(f'Truncated or tied response: {n}/{total}')
   if any(z.get('sport',{}).get('id')!=s or int(z['season'])!=y for z in g['splits']):raise ValueError('Wrong sport/season')
   dest.write_bytes(gzip.compress(b,mtime=0));meta.write_text(json.dumps({'url':url,'retrieved_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'sha256_uncompressed':hashlib.sha256(b).hexdigest(),'split_count':n,'totalSplits':total,'status':200},indent=2))
   return name,'saved'
  except Exception as e:
   if attempt==4:return name,'ERROR '+str(e)
   delay=min(30,2**attempt)
   if isinstance(e,urllib.error.HTTPError) and e.code==429:
    try:delay=min(60,float(e.headers.get('Retry-After',delay)))
    except ValueError:pass
   time.sleep(delay)
 return name,'ERROR'
years=list(range(2015,2027));jobs=[(y,s) for y in years for s in range(11,17)]
with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
 for i,(name,status) in enumerate(pool.map(fetch,jobs),1):print(f'{i}/{len(jobs)} {name} {status}',flush=True)
