"""Freeze public research inputs; GET only, no authentication or production writes."""
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import subprocess,json,hashlib,datetime,csv
ROOT=Path(__file__).resolve().parent; I=ROOT/'inputs';I.mkdir(exist_ok=True)
SOURCES=[(f'expected-{year}.csv',f'https://baseballsavant.mlb.com/leaderboard/expected_statistics?type=batter&year={year}&position=&team=&min=50&csv=true') for year in range(2015,2027)]
for year in [2010,2011,2012,*range(2015,2027)]:
 fields='stats,splits,totalSplits,player,id,stat,plateAppearances,atBats,hits,totalBases,baseOnBalls,hitByPitch,sacFlies,homeRuns,runs,rbi,stolenBases'
 SOURCES.append((f'mlb-hitting-{year}.json',f'https://statsapi.mlb.com/api/v1/stats?stats=season&group=hitting&season={year}&sportIds=1&playerPool=ALL&limit=5000&fields={fields}'))
for mid,name in [(678246,'miguel-vargas'),(647304,'josh-naylor')]:
 SOURCES.extend([(f'kodo-{mid}.json',f'https://kodoanalytics.com/api/v1/players/{mid}'),(f'savant-{mid}.html',f'https://baseballsavant.mlb.com/savant-player/{name}-{mid}')])
def fetch(item):
 name,url=item;p=I/name
 if not p.exists() or not p.stat().st_size:
  result=subprocess.run(['curl','-f','-sS','--max-time','35',url,'-o',str(p)],capture_output=True,text=True)
  if result.returncode:return {'file':name,'url':url,'status':'blocked','error':result.stderr[-500:]}
 try:
  if name.endswith('.csv'):
   with p.open(encoding='utf-8-sig') as f:rows=list(csv.DictReader(f))
   assert rows and 'player_id' in rows[0] and 'est_slg' in rows[0]
  elif name.startswith('mlb-hitting-'):
   result=json.loads(p.read_text());assert result['stats'][0]['splits'];assert len(result['stats'][0]['splits'])==result['stats'][0]['totalSplits']
  elif name.endswith('.json'):assert json.loads(p.read_text())['player']['player_id'] in [678246,647304]
  else:assert 'Statcast Batting Statistics' in p.read_text()
  return {'file':name,'url':url,'status':'frozen','bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
 except Exception as e:return {'file':name,'url':url,'status':'blocked','error':str(e)}
with ThreadPoolExecutor(max_workers=4) as pool:results=list(pool.map(fetch,SOURCES))
manifest={'retrieved_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'sources':results}
(ROOT/'Source_Manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
print(json.dumps({'frozen':sum(x['status']=='frozen' for x in results),'blocked':[r for r in results if r['status']!='frozen']},indent=2))
