#!/usr/bin/env python3
"""Official snapshots only. Run from checkout; no browser API dependency."""
import argparse, copy, concurrent.futures as cf, datetime as dt, json, math, os, time, urllib.parse, urllib.request, unicodedata, re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]; API='https://statsapi.mlb.com/api/v1'
CONFIG={131:('LIDOM','Dominican Republic','roughly AAA-quality overall',3.5),135:('LVBP','Venezuela','roughly AA+/AAA',3),132:('LMP','Mexico','roughly AA+/AAA',3),133:('LBPRC','Puerto Rico','roughly AA+/AAA',3)}
SPORTS={1:('MLB',4),11:('AAA',3),12:('AA',2),13:('High-A',1.5),14:('Single-A',1),16:('Rookie / DSL',0)}
def get(path,**params):
 url=API+path+('?' + urllib.parse.urlencode(params) if params else '')
 for attempt in range(3):
  try:
   with urllib.request.urlopen(url,timeout=60)as f:return json.load(f)
  except Exception:
   if attempt==2:raise
   time.sleep(1+attempt)
def read(path,default=None):
 try:return json.loads((ROOT/path).read_text())
 except FileNotFoundError:return default

def stat_rows(season,group,sport,league=None):
 rows=[];offset=0
 while True:
  q=dict(stats='season',group=group,season=season,sportIds=sport,gameType='R',playerPool='ALL',limit=1000,offset=offset)
  if league:q['leagueIds']=league
  d=get('/stats',**q);blocks=d.get('stats',[])
  if len(blocks)!=1 or blocks[0].get('group',{}).get('displayName')!=group:raise ValueError('Missing/wrong stats group')
  b=blocks[0];a=b.get('splits');total=b.get('totalSplits')
  if not isinstance(a,list)or not isinstance(total,int)or total<0:raise ValueError('Malformed response')
  if any(str(r.get('season'))!=str(season)for r in a):raise ValueError('Season mismatch')
  if league and any(r.get('league',{}).get('id')!=league for r in a):raise ValueError('League mismatch')
  rows+=a;offset+=len(a)
  if offset>=total:break
  if not a:raise ValueError('Truncated pagination')
 if len(rows)!=total:raise ValueError('Truncated/duplicate pagination')
 return rows

def count(s,k,required=True):
 v=s.get(k)
 if v is None and not required:return None
 if isinstance(v,bool)or not isinstance(v,(int,float))or not math.isfinite(v)or v<0 or int(v)!=v:raise ValueError('Invalid count: '+k)
 return int(v)
def ratio(a,b):return round(a/b,6)if a is not None and b else None

def normalize_stat(s,group):
 keys=['atBats','hits','doubles','triples','homeRuns','baseOnBalls','strikeOuts']
 keys+=['plateAppearances','stolenBases','caughtStealing','hitByPitch','sacFlies','totalBases']if group=='hitting'else ['outs','battersFaced','earnedRuns']
 x={k:count(s,k)for k in keys}
 if x['hits']>x['atBats'] or x['doubles']+x['triples']+x['homeRuns']>x['hits']:raise ValueError('Impossible hit counts')
 if group=='hitting':
  pa=x['plateAppearances'];ab=x['atBats'];k=x['strikeOuts'];bb=x['baseOnBalls']
  if ab>pa or k+bb>pa:raise ValueError('Impossible PA components')
  tb=x['hits']+x['doubles']+2*x['triples']+3*x['homeRuns']
  if tb!=x['totalBases']:raise ValueError('Total bases mismatch')
  avg=ratio(x['hits'],ab);slg=ratio(tb,ab);obp=ratio(x['hits']+bb+x['hitByPitch'],ab+bb+x['hitByPitch']+x['sacFlies'])
  x.update(avg=avg,obp=obp,slg=slg,ops=round(obp+slg,6)if obp is not None and slg is not None else None,iso=round(slg-avg,6)if slg is not None else None,kPct=ratio(k,pa),bbPct=ratio(bb,pa),bbPerK=ratio(bb,k),hrPerPa=ratio(x['homeRuns'],pa),sbSuccess=ratio(x['stolenBases'],x['stolenBases']+x['caughtStealing']))
 else:
  outs=x['outs'];bf=x['battersFaced'];ip=s.get('inningsPitched')
  if not re.fullmatch(r'\d+\.[012]',str(ip))or int(str(ip).split('.')[0])*3+int(str(ip).split('.')[1])!=outs:raise ValueError('Invalid baseball innings')
  if x['strikeOuts']+x['baseOnBalls']>bf:raise ValueError('Impossible BF components')
  x.update(ip=f'{outs//3}.{outs%3}',era=ratio(x['earnedRuns']*27,outs),whip=ratio((x['hits']+x['baseOnBalls'])*3,outs),kPct=ratio(x['strikeOuts'],bf),bbPct=ratio(x['baseOnBalls'],bf),kMinusBB=ratio(x['strikeOuts']-x['baseOnBalls'],bf),kPer9=ratio(x['strikeOuts']*27,outs),bbPer9=ratio(x['baseOnBalls']*27,outs))
 for k in ['kPct','bbPct','sbSuccess']:
  if x.get(k)is not None and not 0<=x[k]<=1:raise ValueError('Impossible percentage')
 return x

def normalize_rows(rows,group,lid):
 out=[];seen=set()
 for r in rows:
  pid=r.get('player',{}).get('id')
  if not isinstance(pid,int)or pid<=0 or pid in seen:raise ValueError('Invalid/duplicate MLBAM ID')
  seen.add(pid);team=r.get('team');teams=[team]if team else []
  out.append(dict(mlbamId=pid,name=r['player']['fullName'],position=r.get('position',{}).get('abbreviation'),leagueId=lid,kind=group,teams=teams,stats=normalize_stat(r['stat'],group)))
 return out

def validate_transition(old,new,allow=False):
 for group in ['hitters','pitchers']:
  previous={p['mlbamId']:p for p in old.get(group,[])};current={p['mlbamId']:p for p in new[group]}
  if len(current)<max(1,len(previous)*.85):raise ValueError('Unexpected mass disappearance')
  if previous and len(previous.keys()-current.keys())>max(2,len(previous)*.05):raise ValueError('Previously tracked identities disappeared')
  for pid in previous.keys()&current.keys():
   fields=['plateAppearances','atBats']if group=='hitters'else ['outs','battersFaced']
   if not allow and any(current[pid]['stats'][k]<previous[pid]['stats'][k]for k in fields):raise ValueError('Counting stats regressed for '+str(pid))

def norm(s):return re.sub(r'[^a-z0-9]','',unicodedata.normalize('NFD',s).encode('ascii','ignore').decode().lower())
def pipeline_index():
 byid={};byname={};public=[]
 for path,key,prefix in [('data/editions/october-2026.json','rankings','october-player'),('data/draft/2026.json','players','draft-player'),('data/international/2027.json','players','international-player'),('data/dsl/2026.json','players','dsl-player')]:
  for p in read(path,{}).get(key,[]):
   pid=p.get('mlbamId');routeid=p.get('playerId')if prefix=='october-player'else p.get('id',pid)
   if routeid:public.append(dict(mlbamId=pid,name=p['name'],profileUrl='#'+prefix+'/'+str(routeid),position=p.get('position'),birthDate=p.get('birthDate'),mlbOrg=p.get('mlbOrg')or p.get('officialOrganization')or p.get('draftOrganization')))
 for p in read('data/players.json',[]):
  if not any(norm(x['name'])==norm(p['name'])for x in public):public.append(dict(mlbamId=p.get('mlbamId'),name=p['name'],profileUrl='#player/'+p['id'],position=p.get('position'),mlbOrg=p.get('mlbOrg')))
 for p in public:
  if p.get('mlbamId'):byid.setdefault(p['mlbamId'],p)
  byname.setdefault(norm(p['name']),[]).append(p)
 return byid,byname

def signal(p,base,competition):
 s=p['stats'];n=s.get('plateAppearances',s.get('battersFaced',0));weight=n/(n+(60 if p['kind']=='hitting'else 80));age=p.get('age');level=p.get('levelRank');jump=max(0,competition-level)if level is not None else None
 veteran=p.get('mlbDebutDate')is not None or level==4 or(age is not None and age>=26)
 perf=((s.get('ops')or 0)-base['ops'])/.18 if p['kind']=='hitting'else .7*((s.get('kMinusBB')or 0)-base['kMinusBB'])/.12+.3*(base['era']-(s.get('era')if s.get('era')is not None else base['era']))/1.5
 context=min(.9,max(0,(23-age)*.18))if age is not None else 0
 context+=min(.8,(jump or 0)*.22)
 adjusted=perf+context if perf>=-.25 else perf
 if age is not None and age<=21 and(jump or 0)>=1.5:adjusted=max(-.5,adjusted)
 value=round(weight*adjusted,4)
 if n<40:value=min(.5,value) # A tiny heater cannot lead the established strong-signal tier.
 if veteran:label='Veteran performance / limited prospect signal'
 elif not n:label='Awaiting winter appearance'
 elif age is None or level is None:label='Context incomplete — performance only'
 elif n<40:label='Encouraging small sample'if perf>.25 else 'Small sample — monitor'
 elif value>=1.1 and age<=22 and(jump or 0)>=1:label='Exceptional age/competition performance'
 elif value>=.55:label='Strong winter performance'
 elif perf>=-.25 and age<=22 and(jump or 0)>=1:label='Holding own against advanced competition'
 elif perf<-.5 and age<=21 and(jump or 0)>=1:label='Struggling, but young for competition'
 elif perf<-.5:label='Below current league baseline'
 else:label='Neutral'
 return dict(label=label,order=value,reliability=round(weight,4),sample=n,competitionGap=jump,performance=round(perf,4),contextBonus=round(context,4),prospectEligible=bool(not veteran and age is not None and age<=25 and(p.get('affiliated2026')or p.get('pipelineMatch'))and level is not None))

def fetch_league(meta,season):
 lid=meta['id'];h=normalize_rows(stat_rows(season,'hitting',17,lid),'hitting',lid);p=normalize_rows(stat_rows(season,'pitching',17,lid),'pitching',lid)
 if not h or not p:raise ValueError('Empty winter league stats')
 return dict(id=lid,code=CONFIG[lid][0],country=CONFIG[lid][1],competitionContext=CONFIG[lid][2],season=str(season),seasonLabel=f'{season}–{str(season+1)[2:]}',seasonState=meta['seasonState'],seasonDates=meta['seasonDateInfo'],scope='Regular season only; postseason and all-star games excluded',source=API+'/stats',sourceUrls=[API+f'/stats?stats=season&group={g}&season={season}&sportIds=17&leagueIds={lid}&gameType=R&playerPool=ALL&limit=1000'for g in ['hitting','pitching']],hitters=h,pitchers=p)

def refresh_leagues(meta,season,prior,stamp,allow=False):
 leagues=[];errors=[]
 with cf.ThreadPoolExecutor(max_workers=4)as ex:
  jobs={ex.submit(fetch_league,m,season):lid for lid,m in meta.items()}
  for job in cf.as_completed(jobs):
   lid=jobs[job]
   try:
    l=job.result()
    if lid in prior:validate_transition(prior[lid],l,allow)
    l.update(retrievedAt=stamp,lastSuccessfulRefresh=stamp,validationStatus='validated',stale=False);leagues.append(l)
   except Exception as e:
    errors.append(CONFIG[lid][0]+': '+str(e))
    if lid not in prior:raise RuntimeError('Initial snapshot needs all four leagues: '+str(e))
    l=copy.deepcopy(prior[lid]);l.update(stale=True,validationStatus='stale — last valid snapshot retained',lastRefreshAttempt=stamp,refreshError=str(e));leagues.append(l)
 # All-league failure preserves the entire last successful file, not a new empty publication.
 if len(errors)==4:raise RuntimeError('; '.join(errors))
 return leagues,errors

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--season',type=int,default=2026);ap.add_argument('--allow-corrections',action='store_true');a=ap.parse_args();season=a.season;now=dt.datetime.now(dt.timezone.utc);stamp=now.isoformat();outpath=ROOT/f'data/winter/{season}.json';old=read(f'data/winter/{season}.json',{})
 if old.get('status')=='archived' or now.date()>dt.date(season+1,2,8):print('Season archived / outside refresh window; no API calls.');return
 catalog=get('/leagues',sportId=17)['leagues'];meta={x['id']:x for x in catalog if x['id']in CONFIG}
 if set(meta)!=set(CONFIG)or any(str(x.get('season'))!=str(season)for x in meta.values()):raise ValueError('Expected leagues or current season absent')
 if 'pacifico'not in norm(meta[132]['name']):raise ValueError('LMP identity changed')
 prior={x['id']:x for x in old.get('leagues',[])}
 leagues,errors=refresh_leagues(meta,season,prior,stamp,a.allow_corrections)
 players={p['mlbamId']for l in leagues for group in ['hitters','pitchers']for p in l[group]};people={};aff={};teams={};context_ok=True
 try:
  teams={t['id']:t.get('abbreviation',t['name'])for t in get('/teams',sportId=1,season=season)['teams']}
  def context_stats(pair):
   sport,group=pair;return sport,stat_rows(season,group,sport)
  with cf.ThreadPoolExecutor(max_workers=6)as ex:
   for sport,rows in ex.map(context_stats,[(s,g)for s in SPORTS for g in ['hitting','pitching']]):
    for r in rows:
     pid=r['player']['id']
     if pid not in players:continue
     rank=SPORTS[sport][1]
     if rank>aff.get(pid,{}).get('levelRank',-1):aff[pid]=dict(level=SPORTS[sport][0],levelRank=rank,regularTeamId=r.get('team',{}).get('id'),regularTeam=r.get('team',{}).get('name'),affiliated2026=True)
  # Team parent organizations describe the regular-season team, not a winter team or a fantasy owner.
  team_context={}
  for sport in SPORTS:
   for t in get('/teams',sportId=sport,season=season)['teams']:team_context[t['id']]=t
  for x in aff.values():
   t=team_context.get(x['regularTeamId'],{});x['regularSeasonOrg']=teams.get(t.get('parentOrgId')or(t.get('id')if t.get('sport',{}).get('id')==1 else None))
  def people_batch(ids):return get('/people',personIds=','.join(map(str,ids)),hydrate='currentTeam')['people']
  ids=sorted(players)
  with cf.ThreadPoolExecutor(max_workers=5)as ex:
   for batch in ex.map(people_batch,[ids[i:i+75]for i in range(0,len(ids),75)]):
    for person in batch:people[person['id']]=person
  if len(people)!=len(players):raise ValueError('Incomplete official identity hydration')
  previous_aff={p['mlbamId'] for l in prior.values() for g in ['hitters','pitchers'] for p in l[g] if p.get('affiliated2026')}
  if previous_aff and len(set(aff)&previous_aff)<.8*len(previous_aff):raise ValueError('Affiliated context coverage regressed unexpectedly')
 except Exception as e:
  if not old:raise
  context_ok=False;errors.append('Context refresh: '+str(e))
 byid,byname=pipeline_index();previous={p['mlbamId']:p for l in prior.values()for group in ['hitters','pitchers']for p in l[group]}
 for l in leagues:
  if l.get('stale'):continue
  for group in ['hitters','pitchers']:
   for p in l[group]:
    pid=p['mlbamId'];person=people.get(pid,{});match=byid.get(pid);method='MLBAM ID'if match else None
    if not match:
     matches=[x for x in byname.get(norm(p['name']),[])if not x.get('mlbamId')]
     if len(matches)==1:match=matches[0];method='Unique normalized name — lower confidence'
    p['pipelineMatch']=bool(match);p['matchMethod']=method;p['profileUrl']=match.get('profileUrl')if match else None
    p.update(aff.get(pid,{}));dob=person.get('birthDate')or(match or{}).get('birthDate');p['birthDate']=dob
    p['age']=round((now.date()-dt.date.fromisoformat(dob)).days/365.2425,1)if dob else None;p['ageAsOf']=now.date().isoformat();p['position']=person.get('primaryPosition',{}).get('abbreviation')or p['position'];p['mlbDebutDate']=person.get('mlbDebutDate')
    p['mlbOrg']=teams.get(person.get('currentTeam',{}).get('parentOrgId'))or p.get('regularSeasonOrg')or(match or{}).get('mlbOrg');p['metadataAsOf']=stamp if context_ok else previous.get(pid,{}).get('metadataAsOf');p['contextStale']=not context_ok
    if not context_ok:
     for k in ['level','levelRank','regularSeasonOrg','regularTeam','affiliated2026','mlbOrg','birthDate','age','mlbDebutDate']:p[k]=previous.get(pid,{}).get(k)
   rows=l[group]
   if group=='hitters':
    sums={k:sum(p['stats'][k]for p in rows)for k in ['hits','atBats','baseOnBalls','hitByPitch','sacFlies','totalBases']};base=dict(ops=(sums['hits']+sums['baseOnBalls']+sums['hitByPitch'])/(sums['atBats']+sums['baseOnBalls']+sums['hitByPitch']+sums['sacFlies'])+sums['totalBases']/sums['atBats'])
   else:
    bf=sum(p['stats']['battersFaced']for p in rows);outs=sum(p['stats']['outs']for p in rows);base=dict(kMinusBB=sum(p['stats']['strikeOuts']-p['stats']['baseOnBalls']for p in rows)/bf,era=sum(p['stats']['earnedRuns']for p in rows)*27/outs)
   l.setdefault('baselines',{})[group]=base
   for p in rows:p['signal']=signal(p,base,CONFIG[l['id']][3])
 today=now.date().isoformat();finished=all(today>x['seasonDates']['seasonEndDate']for x in leagues);status='archived'if finished and not errors else 'partial'if errors else 'active'
 result=dict(schemaVersion=1,season=str(season),seasonLabel=f'{season}–{str(season+1)[2:]}',retrievedAt=stamp,lastSuccessfulRefresh=stamp if not errors else old.get('lastSuccessfulRefresh'),lastValidatedPublication=stamp,status=status,source='MLB Stats API — official winter league regular-season feeds',validationStatus='all leagues validated'if not errors else 'partial — stale components explicitly retained',errors=errors,contextValidation='validated'if context_ok else 'stale',leagues=sorted(leagues,key=lambda x:x['code']),signalVersion='WPS-v1',refreshPolicy='Daily 11:15 UTC October–February; stop after all league season-end dates, with February 8 hard stop. Season rollover requires explicit review.')
 outpath.parent.mkdir(parents=True,exist_ok=True);temp=outpath.with_suffix('.tmp');temp.write_text(json.dumps(result,ensure_ascii=False,separators=(',',':'))+'\n');os.replace(temp,outpath);print(json.dumps(dict(status=status,errors=errors,rows={l['code']:[len(l['hitters']),len(l['pitchers']),sum(bool(p['signal']['prospectEligible'])for p in l['hitters']+l['pitchers'])]for l in leagues}),indent=2))
if __name__=='__main__':main()
