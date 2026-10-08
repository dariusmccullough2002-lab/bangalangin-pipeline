"""Cached collection of primary MLB rankings and regular-season aggregate statistics."""
import json,urllib.request,time,concurrent.futures,re,html,hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parent;RAW=ROOT/'raw'
def fetch(url,path):
 if path.exists():return path.read_bytes()
 for attempt in range(3):
  try:
   with urllib.request.urlopen(url,timeout=40) as r:b=r.read()
   path.write_bytes(b);return b
  except Exception:
   if attempt==2:raise
   time.sleep(1)
pages={2012:'301610610',2013:'301609842',2017:'301608460',2018:'301606192'}
def job(task):
 year,group=task
 url=f'https://statsapi.mlb.com/api/v1/stats?stats=season&group={group}&season={year}&sportIds=1&limit=10000&playerPool=ALL&gameType=R'
 p=RAW/f'{group}-{year}.json';d=json.loads(fetch(url,p));splits=d['stats'][0]['splits'];assert len(splits)==d['stats'][0]['totalSplits'],(year,group,len(splits),d['stats'][0]['totalSplits'])
 return {'url':url,'file':p.name,'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'rows':len(splits)}
if __name__=='__main__':
 provenance=[]
 for year,id in pages.items():
  url=f'https://www.mlb.com/news/{year}-top-100-mlb-prospects-list-c{id}';p=RAW/f'rankings-{year}.html';s=fetch(url,p).decode()
  # Retain numeric tables, not prose scouting passages.
  s=re.sub(r'<(script|style)\b.*?</\1>','',s,flags=re.S)
  text=html.unescape(re.sub('<[^>]+>','\n',s));rows=[]
  text=text.replace('43. Mike Olt, 3B TEX','43. Mike Olt, 3B, TEX')
  if year==2017:text=text.replace('32. José De León, RHP, TB','33. José De León, RHP, TB') # Archive duplicates #32; sequence correction logged in report.
  for rank,name,pos,org in re.findall(r'(\d{1,3})\.\s*([^\n<>]+?),\s*([^,\n]+),\s*([A-Z0-9/]{1,7})',text):
   if len(name)>60:continue
   if pos in ['HOU','BOS']:pos,org=org,pos
   if 1<=int(rank)<=100 and int(rank) not in {x['rank'] for x in rows}:rows.append({'year':year,'rank':int(rank),'name':name.strip(),'position':pos,'organization':org})
  if year==2018:
   rows=[]
   for item in re.findall(r'<li\b[^>]*>(.*?)</li>',s,flags=re.S):
    plain=html.unescape(re.sub('<[^>]+>','',item)).strip()
    m=re.fullmatch(r'(.+?),\s*([A-Z0-9/]+),\s*([A-Z]{2,3})',plain)
    if m:rows.append({'year':year,'rank':len(rows)+1,'name':m[1].strip(),'position':m[2],'organization':m[3]})
  assert len(rows)==100,(year,len(rows))
  (RAW/f'rankings-{year}.json').write_text(json.dumps(rows,indent=2));provenance.append({'url':url,'file':p.name,'rows':len(rows),'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'archive_republication':'2018-12-08; historical preseason list, not contemporaneous timestamp'})
 with concurrent.futures.ThreadPoolExecutor(max_workers=6) as pool:
  for result in pool.map(job,[(y,g) for y in range(2010,2024) for g in ['hitting','pitching']]):provenance.append(result);print(result['file'],result['rows'],flush=True)
 (ROOT/'sources.json').write_text(json.dumps(provenance,indent=2))
