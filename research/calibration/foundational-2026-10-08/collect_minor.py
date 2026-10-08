"""Cache evaluation-date prior-year MiLB features and new MLB outcomes; no fitting."""
import urllib.request,json,concurrent.futures,gzip
from pathlib import Path
P=Path(__file__).resolve().parent;R=P/'raw'
def job(t):
 year,g,minor=t;f=R/f'{"milb" if minor else "mlb"}-{g}-{year}.json.gz'
 if f.exists():
  try:json.loads(gzip.decompress(f.read_bytes()));return f.name
  except (OSError,EOFError,ValueError):pass
 old=R/f'milb-{g}-{year}.json'
 if old.exists():d=json.load(open(old))
 else:
  u=f'https://statsapi.mlb.com/api/v1/stats?stats=season&group={g}&season={year}&sportIds={"11,12,13,14,15,16" if minor else "1"}&limit=100000&playerPool=ALL&gameType=R';d=json.load(urllib.request.urlopen(u,timeout=45));d['_source_url']=u
 tmp=f.with_suffix('.tmp');tmp.write_bytes(gzip.compress(json.dumps(d,separators=(',',':')).encode()));tmp.replace(f)
 print(f.name,sum(len(x['splits']) for x in d['stats']),flush=True);return f.name
if __name__=='__main__':
 tasks=[(y,g,True) for y in [2009,2010,2011,2012,2013,2014,2019] for g in ['hitting','pitching']]+[(y,g,False) for y in [2024,2025] for g in ['hitting','pitching']]
 with concurrent.futures.ThreadPoolExecutor(max_workers=6) as pool:list(pool.map(job,tasks))
