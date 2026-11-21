"""Expand identity search and observed hitter panels. Never estimate missing metrics.

Sources: public MLB season registries, public Prospect Savant leaderboard JSON
used by its free UI, and the already-reviewed official Savant source snapshots.
No PS Plus export, login, private route, or paid feature is used.
"""
from pathlib import Path
from datetime import date
import csv, io, json, gzip, hashlib, urllib.request, urllib.parse, concurrent.futures, os
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'data/research'
CACHE=Path(os.environ.get('POWER_SOURCE_CACHE',str(ROOT.parent/'prospect-source-cache')));CACHE.mkdir(exist_ok=True)
ASOF='2026-11-20'
SPORTS={11:'AAA',12:'AA',13:'High-A',14:'A',16:'Rookie / DSL / complex'}
METRICS=['chase','whiff','hard_hit','barrel']
PS_LEVELS=['AAA','AA','High-A','A','Rk']
def num(v):
 try:
  n=float(v);return n if n==n and abs(n)!=float('inf') else None
 except (TypeError,ValueError):return None
def positive(v):
 n=num(v);return n if n is not None and n>0 else None
def load(url,file):
 path=CACHE/file
 if path.exists():raw=path.read_bytes()
 else:
  raw=urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'Mozilla/5.0'}),timeout=60).read();json.loads(raw);path.write_bytes(raw)
 return json.loads(raw),dict(url=url,sha256=hashlib.sha256(raw).hexdigest(),retrieved=ASOF)
def sample_status(r):
 missing=[k for k in METRICS if r.get(k) is None]
 r['complete']=not missing
 counts=[('PA',r.get('pa'),100),('swings',r.get('swings'),100),('outside-zone pitches',r.get('outsidePitches'),100),('tracked BBE / provider BIP',r.get('trackedBBE'),50)]
 short=[f'{name}: '+('not supplied' if value is None else f'{int(value)} < {minimum}') for name,value,minimum in counts if value is None or value<minimum]
 r['adequate']=not missing and not short
 r['missingMetrics']=missing
 r['status']='plot-ready' if r['adequate'] else 'partial metrics' if missing else 'sample below guard'
 r['statusReason']=('Missing '+', '.join(missing)+'. ' if missing else '')+'; '.join(short)
 return r
def normalize_ps(row,manifest):
 pid=positive(row.get('MLBAMId'));rid=positive(row.get('id'))
 if not pid or not rid or int(pid)!=int(rid):return None
 pid=int(pid);year=int(row['season']);level=row['level'];a=row.get('aball_src');rk=row.get('rk_src')
 no_impact=level in ['AA','A+'] or level=='A' and a!='fsl' or level=='Rk' and rk not in ['cpx','complex']
 # Match the UI's explicit unavailable-data masks. Backend zero placeholders
 # must never become observed zero Hard-Hit or zero Barrel measurements.
 tracking=not no_impact and positive(row.get('ev')) is not None
 label={'A+':'High-A','A':'FSL A' if a=='fsl' else 'A (Carolina / California)','Rk':'DSL (Rookie)' if rk=='dsl' else 'Complex (Rookie)'}.get(level,level)
 r=dict(id=f'ps-{pid}-{year}-{level}-{a if level=="A" else rk if level=="Rk" else "main"}',mlbamId=pid,name=row['name'],year=year,level=label,levelCode=level,pa=int(num(row.get('pa')) or 0),
  swings=int(positive(row.get('swings'))) if positive(row.get('swings')) else None,outsidePitches=int(positive(row.get('opitches'))) if positive(row.get('opitches')) else None,
  trackedBBE=int(positive(row.get('bip'))) if tracking and positive(row.get('bip')) else None,bbeLabel='provider BIP',
  chase=num(row.get('chaserate')) if positive(row.get('chaserate')) is not None or positive(row.get('opitches')) is not None else None,whiff=num(row.get('whiffrate')) if positive(row.get('whiffrate')) is not None or positive(row.get('swings')) is not None else None,
  hard_hit=num(row.get('hhrate')) if tracking else None,barrel=num(row.get('barrelbbe')) if tracking else None,
  iso=num(row.get('iso')),woba=num(row.get('woba')),xslg=num(row.get('xslg')) if tracking and level!='Rk' else None,
  k=num(row.get('krate')),bb=num(row.get('bbrate')),zoneContact=positive(row.get('zcontact')) if positive(row.get('swings')) else None,zoneSwing=positive(row.get('zswing')) if positive(row.get('pitches')) else None,
  ev=num(row.get('ev')) if tracking else None,ev90=positive(row.get('ev90')) if tracking else None,pullAir=num(row.get('pullair')),
  mlbOrg=row.get('MLB_AbbName') or row.get('team'),position=row.get('Position'),providerAge=num(row.get('age')),
  source='Prospect Savant',sourceUrl=f'https://prospectsavant.com/player/{pid}',sourceManifest=manifest['key'],retrieved=ASOF,
  trackingCoverage='partial complex-league tracking' if level=='Rk' and tracking else 'Statcast rates' if tracking else 'pitch tracking; impact unavailable',
  providerScope='Provider season-level aggregate; leagues are not pooled by this tool.',
  rawSourceFlags=dict(level=level,aball_src=a,rk_src=rk),
  sourceReportedMetrics={k:row.get(v) for k,v in [('chase','chaserate'),('whiff','whiffrate'),('hard_hit','hhrate'),('barrel','barrelbbe')]})
 for k in METRICS:
  if r[k] is not None and not 0<=r[k]<=100:raise ValueError(f'Out-of-range {k}: {pid}')
 if not positive(row.get('pitches')):
  for k in ['zoneContact','zoneSwing','pullAir']:r[k]=None
 return sample_status(r)
def official_records():
 old=json.loads((OUT/'power-translation-minor.json').read_text());sources={s['file']:s for s in old['sources']};result=[]
 for year in [2024,2025,2026]:
  for level in ['AAA','A']:
   f=f'data/research/minor-sources/{year}-{level}-all.csv';o=f'data/research/minor-sources/{year}-{level}-outside.csv'
   for name in [f,o]:assert hashlib.sha256((ROOT/name).read_bytes()).hexdigest()==sources[name]['sha256']
   allrows=list(csv.DictReader(io.StringIO((ROOT/f).read_text(encoding='utf-8-sig'))));oz={int(r['player_id']):r for r in csv.DictReader(io.StringIO((ROOT/o).read_text(encoding='utf-8-sig')))}
   for row in allrows:
    pid=int(row['player_id']);outside=oz.get(pid,{});op=positive(outside.get('pitches'));os=num(outside.get('swings'));sw=positive(row.get('swings'));wh=num(row.get('whiffs'));barrel=num(row.get('barrels_per_bbe_percent'));bars=num(row.get('barrels_total'))
    parts=row['player_name'].split(', ',1);name=parts[1]+' '+parts[0] if len(parts)==2 else parts[0]
    tracked=round(bars/(barrel/100)) if barrel and bars is not None else None
    r=dict(id=f'{pid}-{year}-{level}',mlbamId=pid,name=name,year=year,level='FSL A' if level=='A' else level,levelCode=level,pa=int(float(row['pa'])),swings=int(sw) if sw else None,outsidePitches=int(op) if op else None,trackedBBE=tracked,bbeLabel='tracked BBE',chase=100*os/op if op and os is not None else None,whiff=100*wh/sw if sw and wh is not None else None,hard_hit=num(row.get('hardhit_percent')),barrel=barrel,iso=num(row.get('iso')),woba=num(row.get('woba')),xslg=num(row.get('xslg')),k=num(row.get('k_percent')),bb=num(row.get('bb_percent')),ev=num(row.get('launch_speed')),source='Baseball Savant',sourceUrl='https://baseballsavant.mlb.com/statcast-search-minors',sourceManifest=f,trackingCoverage='official tracked source snapshot',retrieved=old['asOf'])
    result.append(sample_status(r))
 return result
def main():
 tasks=[]
 for sport in SPORTS:tasks.append(('mlb',sport,None,f'https://statsapi.mlb.com/api/v1/sports/{sport}/players?season=2026',f'mlb-2026-{sport}.json'))
 for year in [2024,2025,2026]:
  for level in PS_LEVELS:
   code='A+' if level=='High-A' else level;url=f'https://oriolebird.pythonanywhere.com/leaders/hitters/{urllib.parse.quote(code,safe="")}/{year}/1/0/99'
   tasks.append(('ps',level,year,url,f'ps-{year}-{level}.json'))
 responses=[]
 def get(t):
  d,m=load(t[3],t[4]);m['key']=t[4];m['provider']='MLB Stats API' if t[0]=='mlb' else 'Prospect Savant';m['rows']=len(d.get('people' if t[0]=='mlb' else 'data',[]));print(t[0],t[1],t[2],m['rows'],flush=True);return t,d,m
 with concurrent.futures.ThreadPoolExecutor(3) as ex:
  for value in ex.map(get,tasks):responses.append(value)
 identities={};ps=[];manifests=[]
 for task,data,manifest in responses:
  manifests.append(manifest)
  if task[0]=='mlb':
   for person in data['people']:
    pid=int(person['id']);p=identities.setdefault(pid,dict(mlbamId=pid,name=person['fullName'],aliases=[],levels=[],birthDate=person.get('birthDate'),position=person.get('primaryPosition',{}).get('abbreviation'),isPitcher=person.get('primaryPosition',{}).get('code')=='1',registry2026=True))
    if SPORTS[task[1]] not in p['levels']:p['levels'].append(SPORTS[task[1]])
    if person['fullName']!=p['name'] and person['fullName'] not in p['aliases']:p['aliases'].append(person['fullName'])
  else:
   for row in data['data']:
    assert int(row['season'])==task[2] and row['level']==('A+' if task[1]=='High-A' else task[1])
    r=normalize_ps(row,manifest)
    if r is not None:ps.append(r)
 # Direct official snapshots supersede duplicate PS measurement records in
 # the same player/year/tracking environment. Never blend component rates.
 records=official_records();keys={(r['mlbamId'],r['year'],r['level']) for r in records}
 for r in ps:
  if (r['mlbamId'],r['year'],r['level']) not in keys:records.append(r);keys.add((r['mlbamId'],r['year'],r['level']))
 board=json.loads((OUT/'power-translation-coverage.json').read_text());byboard={p['mlbamId']:p for p in board['players']}
 for r in records:
  pid=r['mlbamId'];p=identities.setdefault(pid,dict(mlbamId=pid,name=r['name'],aliases=[],levels=[],birthDate=None,position=r.get('position'),isPitcher=False,registry2026=False))
  if r['name']!=p['name'] and r['name'] not in p['aliases']:p['aliases'].append(r['name'])
  if r.get('mlbOrg'):p['mlbOrg']=r['mlbOrg']
  p['hasProspectSavant']=p.get('hasProspectSavant',False) or r['source']=='Prospect Savant'
 for r in ps:
  if r['mlbamId'] in identities:identities[r['mlbamId']]['hasProspectSavant']=True
 for pid,b in byboard.items():
  p=identities.setdefault(pid,dict(mlbamId=pid,name=b['name'],aliases=[],levels=[],birthDate=None,position=None,isPitcher=False,registry2026=False));p['boardMember']=True;p['playerId']=b['playerId'];p['organization']=b.get('organization');p['mlbOrg']=b.get('mlbOrg')
  if b['name']!=p['name'] and b['name'] not in p['aliases']:p['aliases'].append(b['name'])
 for r in records:
  p=identities[r['mlbamId']];r['boardMember']=p.get('boardMember',False);r['organization']=p.get('organization');r['playerId']=p.get('playerId');r['mlbOrg']=r.get('mlbOrg') or p.get('mlbOrg');birth=p.get('birthDate')
  if birth:
   born=date.fromisoformat(birth);r['seasonAge']=round((date(r['year'],6,30)-born).days/365.2425,1)
  else:r['seasonAge']=None
 assert len({r['id'] for r in records})==len(records)
 counts={status:sum(r['status']==status for r in records) for status in ['plot-ready','partial metrics','sample below guard']}
 directory=dict(asOf=ASOF,scope='2026 affiliated MiLB season registries across AAA, AA, High-A, A, Rookie/DSL/complex; plus source-observed 2024–2026 hitters and existing board identities. This is a dated player directory, not a prospect-eligibility judgment.',players=sorted(identities.values(),key=lambda p:p['name']),sources=manifests,ownershipSnapshot=board['ownershipSnapshot'])
 panel=dict(asOf=ASOF,records=records,counts=counts,sourcePolicy='All four components remain from one provider record. Official same-year/same-environment records take priority over PS duplicates. Partial, missing and small samples remain visible, never imputed.',availability='AA / High-A: no Statcast impact in the PS UI. Other-A and DSL: impact unavailable. Complex: partial tracking only. Backend zero placeholders are normalized to null according to the UI masks.',sampleGuard='100+ PA, 100+ swings, 100+ outside-zone pitches and 50+ tracked BBE/provider BIP, plus all four source-observed rates. Unknown denominators do not pass.',sourceFreshness='Retrieval date is not a guarantee of source completeness through that date. PS and official snapshots can differ; records are never blended.',sourceLinks=['https://prospectsavant.com/leaders','https://baseballsavant.mlb.com/statcast-search-minors'])
 for name,value in [('power-prospect-catalog',directory),('power-prospect-records',panel)]:
  (OUT/f'{name}.json.gz').write_bytes(gzip.compress(json.dumps(value,separators=(',',':'),allow_nan=False).encode(),mtime=0))
 print(json.dumps(dict(players=len(identities),records=len(records),**counts)),flush=True)
if __name__=='__main__':main()
