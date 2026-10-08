"""Official MLB weekly pitching totals, including holds absent from Retrosheet CSV."""
import urllib.request,json,concurrent.futures,datetime,hashlib,gzip
from pathlib import Path
P=Path(__file__).resolve().parent;R=P/'raw'
def get(task):
 y,start=task;end=start+datetime.timedelta(days=6);f=R/f'week-{start.isoformat()}.json.gz'
 if f.exists():
  try:json.loads(gzip.decompress(f.read_bytes()));return start.isoformat()
  except (OSError,EOFError,ValueError):pass
 u=f'https://statsapi.mlb.com/api/v1/stats?stats=byDateRange&group=pitching&startDate={start}&endDate={end}&sportIds=1&limit=10000&playerPool=ALL&gameType=R'
 for i in range(3):
  try:d=json.load(urllib.request.urlopen(u,timeout=35));break
  except Exception:
   if i==2:raise
 ss=d.get('stats',[{}])[0].get('splits',[])
 assert len(ss)==d.get('stats',[{}])[0].get('totalSplits',0)
 # A traded player may have team split rows: sum only after inspect/cross-check.
 tmp=f.with_suffix('.tmp');tmp.write_bytes(gzip.compress(json.dumps({'url':u,'data':d},separators=(',',':')).encode()));tmp.replace(f)
 return start.isoformat()
if __name__=='__main__':
 tasks=[]
 for y in [2010,2011,2012,2018,2023,2024]:
  d=datetime.date(y,4,1);d-=datetime.timedelta(days=d.weekday())
  while d<=datetime.date(y,9,30):tasks.append((y,d));d+=datetime.timedelta(days=7)
 with concurrent.futures.ThreadPoolExecutor(max_workers=8) as pool:
  for s in pool.map(get,tasks):print(s,flush=True)
