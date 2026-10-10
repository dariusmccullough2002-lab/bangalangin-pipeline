"""Bounded official current-season verification, no projection-source collection."""
import urllib.request,json,gzip,hashlib,datetime,time
from pathlib import Path
D=Path(__file__).resolve().parent
(D/'verified').mkdir(exist_ok=True)
def get(tag,url):
 p=D/'verified'/f'{tag}.json.gz'
 if p.exists():return json.loads(gzip.decompress(p.read_bytes()))
 for attempt in range(3):
  try:
   with urllib.request.urlopen(url,timeout=45) as r:data=r.read();date=r.headers.get('Date')
   a=json.loads(data);p.write_bytes(gzip.compress(data,mtime=0));meta={'url':url,'retrieved_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'http_date':date,'sha256':hashlib.sha256(data).hexdigest(),'statistical_window':'regular season only; completed2026 regular season; not postseason or future2027','restricted_data':False};(D/'verified'/f'{tag}.provenance.json').write_text(json.dumps(meta,indent=2));print(tag,len(data),flush=True);return a
  except Exception:
   if attempt==2:raise
teams=get('teams2026','https://statsapi.mlb.com/api/v1/teams?sportId=1&season=2026')['teams']
for season in [2025,2026]:
 for group in ['hitting','pitching']:
  a=get(f'{group}{season}',f'https://statsapi.mlb.com/api/v1/stats?stats=season&group={group}&season={season}&sportIds=1&gameType=R&playerPool=ALL&limit=5000')
  assert a['stats'] and len(a['stats'][0]['splits'])<5000
for t in teams:get(f"roster-{t['id']}",f"https://statsapi.mlb.com/api/v1/teams/{t['id']}/roster?rosterType=40Man&season=2026")
for group in ['hitting','pitching']:
 get(f'team-{group}2026',f'https://statsapi.mlb.com/api/v1/teams/stats?stats=season&group={group}&season=2026&sportIds=1&gameType=R&limit=100')
get('toronto-schedule2027','https://statsapi.mlb.com/api/v1/schedule?sportId=1&teamId=141&season=2027&gameType=R')
