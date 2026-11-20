"""Source snapshots for level-separated experimental MiLB component views.
No MLB coefficients or success thresholds are applied to minor-league records.
"""
from pathlib import Path
import csv, io, json, hashlib, urllib.request, urllib.parse, concurrent.futures
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'data/research';RAW=OUT/'minor-sources';RAW.mkdir(exist_ok=True)
coverage=json.loads((OUT/'power-translation-coverage.json').read_text())
players={int(p['mlbamId']):p for p in coverage['players'] if p.get('mlbamId')}
BASE='https://baseballsavant.mlb.com/statcast-search-minors/csv?'
def download(task):
 year,level,outside=task
 params=dict(all='true',player_type='batter',hfSea=f'{year}|',hfGT='R|',hfLevel=f'{level}|',group_by='name',min_pas='0' if outside else '100',min_pitches='0',min_results='0',minors='true',chk_stats_pa='on',chk_stats_hardhit_percent='on',chk_stats_barrels_per_bbe_percent='on',chk_stats_swing_miss_percent='on')
 if level=='A':params['hfLeague']='123|'
 if outside:params['hfZ']='11|12|13|14|'
 url=BASE+urllib.parse.urlencode(params);file=RAW/f'{year}-{level}-{"outside" if outside else "all"}.csv'
 if file.exists():raw=file.read_bytes()
 else:
  raw=urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'Mozilla/5.0'}),timeout=55).read()
  assert raw.startswith(b'\xef\xbb\xbf"pitches"') or raw.startswith(b'"pitches"'), 'Unexpected export format'
  file.write_bytes(raw)
 rows=list(csv.DictReader(io.StringIO(raw.decode('utf-8-sig'))))
 assert all('player_id' in r and 'swings' in r for r in rows)
 print(year,level,outside,len(rows),flush=True)
 return task,rows,dict(year=year,level='FSL A' if level=='A' else level,outsideZoneOnly=outside,url=url,file=str(file.relative_to(ROOT)),sha256=hashlib.sha256(raw).hexdigest(),rows=len(rows),retrieved='2026-11-20')
tasks=[(y,l,o) for y in [2024,2025,2026] for l in ['AAA','A'] for o in [False,True]]
responses={};sources=[];errors=[]
with concurrent.futures.ThreadPoolExecutor(4) as ex:
 future={ex.submit(download,t):t for t in tasks}
 for f in concurrent.futures.as_completed(future):
  try:t,rows,manifest=f.result();responses[t]=rows;sources.append(manifest)
  except Exception as e:errors.append(dict(task=future[f],error=str(e)))
def number(r,k):
 try:return float(r[k])
 except (KeyError,ValueError,TypeError):return None
panel=[]
for year,level,outside in tasks:
 if outside:continue
 allrows=responses.get((year,level,False),[]);oz={int(r['player_id']):r for r in responses.get((year,level,True),[]) if r.get('player_id')}
 for r in allrows:
  pid=int(r['player_id']);p=players.get(pid)
  if not p:continue
  o=oz.get(pid);op=number(o or {},'pitches');os=number(o or {},'swings')
  chase=100*os/op if op and os is not None else None
  hh=number(r,'hardhit_percent');barrel=number(r,'barrels_per_bbe_percent');swings=number(r,'swings');whiffs=number(r,'whiffs');whiff=100*whiffs/swings if swings and whiffs is not None else None
  pa=number(r,'pa');bip=number(r,'bip');barrels=number(r,'barrels_total');tracked=round(barrels/(barrel/100)) if barrel and barrels is not None else None
  vals=[chase,whiff,hh,barrel]
  assert all(v is None or 0<=v<=100 for v in vals)
  assert o is None or number(o,'pitches')<=number(r,'pitches'), 'O-zone denominator exceeds all pitches'
  complete=all(v is not None for v in vals)
  adequate=bool(complete and pa>=100 and swings>=100 and op>=100 and tracked is not None and tracked>=50)
  panel.append(dict(id=f'{pid}-{year}-{level}',playerId=p['playerId'],mlbamId=pid,name=p['name'],year=year,level='FSL A' if level=='A' else level,organization=p.get('organization'),mlbOrg=p.get('mlbOrg'),pa=int(pa),swings=int(swings or 0),outsidePitches=int(op or 0),trackedBBE=tracked,bip=int(bip or 0),chase=chase,whiff=whiff,hard_hit=hh,barrel=barrel,iso=number(r,'iso'),woba=number(r,'woba'),xslg=number(r,'xslg'),hr=number(r,'hrs'),k=number(r,'k_percent'),bb=number(r,'bb_percent'),complete=complete,adequate=adequate))
# Peer reference uses all source hitters in that year/level, not only the fantasy board.
peers=[]
for year,level in [(y,l) for y in [2024,2025,2026] for l in ['AAA','A']]:
 allrows=responses.get((year,level,False),[]);oz={int(r['player_id']):r for r in responses.get((year,level,True),[]) if r.get('player_id')}
 values=[]
 for r in allrows:
  o=oz.get(int(r['player_id']),{});op=number(o,'pitches');os=number(o,'swings');hh=number(r,'hardhit_percent')
  if op and os is not None and hh is not None:values.append((100*os/op,hh))
 if values:
  import statistics
  peers.append(dict(year=year,level='FSL A' if level=='A' else level,n=len(values),medianChase=statistics.median(v[0] for v in values),medianHardHit=statistics.median(v[1] for v in values)))
out=dict(asOf='2026-11-20',scope='Fantrax league-board hitters only; level-separated 2024–2026 AAA and tracked FSL A snapshots.',status='Raw observed components; no MiLB-to-MLB scoring',records=panel,peers=peers,sources=sources,errors=errors,guard='100+ source PA, 100+ swings, 100+ classified outside-zone pitches, and 50+ inferred tracked BBE; all four components observed. Exploratory sample guard, not validated reliability.',definitions={'chase':'100 × swings / pitches for Savant zones 11–14; unclassified locations are excluded. Same year, level and regular-season query as the main panel.','whiff':'100 × whiffs / swings in the all-pitch aggregate.','hard_hit':'Savant hardhit_percent: tracked batted balls at 95+ mph.','barrel':'Savant barrels_per_bbe_percent; never Barrel/PA.','trackedBBE':'Rounded barrels_total divided by Barrel/BBE fraction when barrels >0; unavailable for zero-barrel samples.','coverage':'All AAA parks since 2023; FSL A tracking since 2021. Other levels/parks are not implied covered.'},limitations=['No future MLB outcome labels, probabilities, frontier or prospect classifications.','Tracking and location gaps can affect denominators. Selected peers are same year and level, not park-adjusted.','Age shown on the league board is a snapshot and is not treated as age in a historical season.','Different levels/seasons are never pooled for rates. Missing data is never imputed.','Leaderboard limited to the 178-player November board audit, not every Fantrax minor leaguer.'])
(OUT/'power-translation-minor.json').write_text(json.dumps(out,separators=(',',':'),allow_nan=False))
print(json.dumps(dict(records=len(panel),complete=sum(r['complete'] for r in panel),adequate=sum(r['adequate'] for r in panel),errors=errors)),flush=True)
