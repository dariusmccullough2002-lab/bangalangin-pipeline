#!/usr/bin/env python3
"""Create performance-led profiles only for verified affiliated winter prospects."""
import concurrent.futures as cf,datetime as dt,importlib.util,json,os,copy
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('winter',ROOT/'scripts/winter-ball.py');w=importlib.util.module_from_spec(spec);spec.loader.exec_module(w)

def existing_index():
 byid,byname=w.pipeline_index(include_winter=False)
 byid={pid:p for pid,p in byid.items()if not p['profileUrl'].startswith('#winter-player/')}
 byname={k:[p for p in v if not p['profileUrl'].startswith('#winter-player/')]for k,v in byname.items()}
 for p in w.read('data/afl/full-2026.json',{}).get('players',[]):
  pid=p.get('mlbamId')
  if pid and pid not in byid:
   row=dict(mlbamId=pid,name=p['name'],profileUrl=p.get('route')or'#afl-player/'+str(pid),mlbOrg=p.get('mlbOrg'),birthDate=p.get('birthDate'));byid[pid]=row;byname.setdefault(w.norm(p['name']),[]).append(row)
 # New winter profiles are never used to decide whether an independent profile already existed.
 byid={pid:p for pid,p in byid.items()if not p['profileUrl'].startswith('#winter-player/')}
 byname={k:[p for p in v if not p['profileUrl'].startswith('#winter-player/')]for k,v in byname.items()}
 return byid,byname

def merge_match(pid,name,org,dob,byid,byname):
 if pid in byid:return byid[pid],'MLBAM ID'
 candidates=[p for p in byname.get(w.norm(name),[])if not p.get('mlbamId')and p.get('mlbOrg')==org and(not p.get('birthDate')or not dob or p['birthDate']==dob)]
 routes={p['profileUrl']:p for p in candidates}
 return (next(iter(routes.values())),'Unique normalized name + organization — lower confidence')if len(routes)==1 else(None,None)

def summarize(s,kind):
 x=w.normalize_stat(s,kind)
 x.update({k:s[k]for k in ['gamesPlayed','gamesStarted','wins','losses','saves','holds']if k in s});return x

def main():
 path=ROOT/'data/winter/profiles-2026.json';old=w.read('data/winter/profiles-2026.json',{});snapshot=w.read('data/winter/2026.json');stamp=dt.datetime.now(dt.timezone.utc).isoformat();season=int(snapshot['season']);allrows=[p for l in snapshot['leagues']for g in ['hitters','pitchers']for p in l[g]]
 candidates={p['mlbamId']:p for p in allrows if p.get('age')is not None and p['age']<26 and p.get('levelRank')!=4 and not p.get('mlbDebutDate')}
 # Include still-young previously profiled players in affiliation audits; pages persist after winter participation stops.
 prior={p['mlbamId']:p for p in old.get('players',[])};ids=set(candidates)|set(prior)
 teams=w.get('/teams',sportId=1,season=season)['teams'];orgmap={t['id']:t['abbreviation']for t in teams}
 def roster(t):
  data=w.get(f"/teams/{t['id']}/roster",rosterType='fullRoster');rows=data.get('roster')
  if not isinstance(rows,list)or len(rows)<60:raise ValueError('Truncated organization roster: '+t['name'])
  return t,rows
 memberships={};rosterEvidence=[]
 with cf.ThreadPoolExecutor(max_workers=5)as ex:
  for team,rows in ex.map(roster,teams):
   rosterEvidence.append(dict(teamId=team['id'],organization=team['abbreviation'],players=len(rows),url=w.API+f"/teams/{team['id']}/roster?rosterType=fullRoster",retrievedAt=stamp))
   for row in rows:
    pid=row['person']['id'];status=row.get('status',{}).get('description','')
    if pid in ids and not any(x in status.lower()for x in ['released','free agent','retired']):memberships.setdefault(pid,[]).append(dict(organization=team['abbreviation'],organizationId=team['id'],status=status))
 transaction_reviews={}
 def transactions(pid):
  url=w.API+f'/transactions?playerId={pid}&startDate={season}-09-01&endDate={stamp[:10]}'
  data=w.get('/transactions',playerId=pid,startDate=f'{season}-09-01',endDate=stamp[:10]);rows=data.get('transactions')
  if not isinstance(rows,list)or any(t.get('person',{}).get('id')!=pid for t in rows):raise ValueError('Invalid transaction response')
  return pid,url,sorted(rows,key=lambda t:(t.get('date',''),t.get('id',0)))
 with cf.ThreadPoolExecutor(max_workers=5)as ex:
  for pid,url,rows in ex.map(transactions,[pid for pid in ids if len(memberships.get(pid,[]))!=1]):
   relevant=[t for t in rows if t.get('toTeam',{}).get('id')in orgmap or any(x in t.get('description','').lower()for x in ['elected free agency','released','retired'])]
   transaction_reviews[pid]=dict(url=url,retrievedAt=stamp,events=[dict(date=t.get('date'),description=t.get('description'),toTeam=t.get('toTeam'),typeCode=t.get('typeCode'))for t in relevant])
   if relevant:
    last=relevant[-1];dest=last.get('toTeam',{}).get('id');text=last.get('description','').lower()
    if dest in orgmap and any(x in text for x in ['signed','invited non-roster','claimed','traded','selected']):memberships[pid]=[dict(organization=orgmap[dest],organizationId=dest,status=last['description'],verificationMethod='Official MLB transaction; current roster membership not independently confirmed',sourceUrl=url)]
 people={}
 def person_batch(a):return w.get('/people',personIds=','.join(map(str,a)))['people']
 ids=sorted(ids)
 with cf.ThreadPoolExecutor(max_workers=4)as ex:
  for batch in ex.map(person_batch,[ids[i:i+75]for i in range(0,len(ids),75)]):
   for p in batch:people[p['id']]=p
 if len(people)!=len(ids):raise ValueError('Incomplete player identity response')
 byid,byname=existing_index();records=[];excluded=[];newids={pid for pid in candidates if len(memberships.get(pid,[]))==1 and not people[pid].get('mlbDebutDate')}-set(prior);seasonstats={}
 if newids:
  def stats(pair):sport,kind=pair;return sport,kind,w.stat_rows(season,kind,sport)
  with cf.ThreadPoolExecutor(max_workers=5)as ex:
   for sport,kind,rows in ex.map(stats,[(s,g)for s in w.SPORTS for g in ['hitting','pitching']]):
    for row in rows:
     pid=row['player']['id']
     if pid not in newids:continue
     stat=summarize(row['stat'],kind)
     if not stat.get('plateAppearances',stat.get('battersFaced')):continue
     seasonstats.setdefault(pid,[]).append(dict(season=str(season),kind=kind,level=w.SPORTS[sport][0],levelRank=w.SPORTS[sport][1],team=row.get('team',{}).get('name'),stats=stat,source=w.API+f'/stats?stats=season&group={kind}&season={season}&sportIds={sport}&playerPool=ALL&gameType=R',retrievedAt=stamp))
 for pid in ids:
  person=people[pid];member=memberships.get(pid,[]);verified=len(member)==1;org=member[0]['organization']if verified else None;dob=person.get('birthDate');age=round((dt.datetime.now(dt.timezone.utc).date()-dt.date.fromisoformat(dob)).days/365.2425,1)if dob else None
  eligible=verified and not person.get('mlbDebutDate')and age is not None and age<26
  if not eligible and pid not in prior:
   excluded.append(dict(mlbamId=pid,name=person['fullName'],reason='Current MLB affiliation unverified or ambiguous'if not verified else 'MLB debut / age outside current prospect screen',transactionReview=transaction_reviews.get(pid)));continue
  match,method=merge_match(pid,person['fullName'],org,dob,byid,byname)
  records.append(dict(mlbamId=pid,name=person['fullName'],birthDate=dob,age=age,ageAsOf=stamp[:10],position=person.get('primaryPosition',{}).get('abbreviation'),mlbOrg=org,recentTransactions=transaction_reviews.get(pid),affiliationVerified=verified,affiliation=member,prospectEligible=eligible,existingProfile=match['profileUrl']if match else None,profileUrl=match['profileUrl']if match else '#winter-player/'+str(pid),matchMethod=method if match else 'MLBAM ID — winter prospect profile',profileType='Existing Pipeline profile'if match else 'Performance-led prospect profile',bio=dict(height=person.get('height'),weightLb=person.get('weight'),bats=person.get('batSide',{}).get('code'),throws=person.get('pitchHand',{}).get('code'),birthCountry=person.get('birthCountry'),draftYear=person.get('draftYear'),mlbDebutDate=person.get('mlbDebutDate')),seasonStats=seasonstats.get(pid,prior.get(pid,{}).get('seasonStats',[])),regularSeasonRetrievedAt=stamp if pid in newids else prior.get(pid,{}).get('regularSeasonRetrievedAt'),metadataAsOf=stamp,sources=[dict(label='Official MLB player identity',url=w.API+'/people/'+str(pid),retrievedAt=stamp),dict(label='Official MLB organization evidence',url=member[0].get('sourceUrl')or w.API+f"/teams/{member[0]['organizationId']}/roster?rosterType=fullRoster",retrievedAt=stamp)]if verified else[dict(label='Official MLB player identity',url=w.API+'/people/'+str(pid),retrievedAt=stamp)]))
 index={p['mlbamId']:p for p in records};changedorg=[]
 for row in allrows:
  record=index.get(row['mlbamId'])
  if record and record['prospectEligible']:
   if row.get('mlbOrg')!=record['mlbOrg']:changedorg.append(dict(name=row['name'],previous=row.get('mlbOrg'),current=record['mlbOrg']))
   row.update(mlbOrg=record['mlbOrg'],pipelineMatch=True,profileUrl=record['profileUrl'],matchMethod=record['matchMethod'],affiliationVerified=True,affiliationAsOf=stamp)
  elif row['mlbamId']in candidates:
   row['signal']['prospectEligible']=False;row['affiliationVerified']=False;row['mlbOrg']=None;row['signal']['label']='Current prospect affiliation not verified'
 result=dict(schemaVersion=1,asOf=stamp,season=str(season),scope='Winter prospect profile coverage: under 26, no verified MLB debut, and independently verified MLB organization association. Unknown 2026 level does not imply a poor tool or fabricated assignment. The performance-signal cohort remains separate. Other winter players receive no new prospect profile.',players=sorted(records,key=lambda p:p['name']),audit=dict(candidateIds=len(candidates),verifiedProspects=sum(p['prospectEligible']for p in records),newProfiles=sum(not p['existingProfile']for p in records),reusedProfiles=sum(bool(p['existingProfile'])for p in records),excluded=excluded,organizationChanges=changedorg,rosterEvidence=rosterEvidence))
 for target,data in [(path,result),(ROOT/'data/winter/2026.json',snapshot)]:
  temp=target.with_suffix('.tmp');temp.write_text(json.dumps(data,ensure_ascii=False,separators=(',',':'))+'\n');os.replace(temp,target)
 print(json.dumps({k:v for k,v in result['audit'].items()if k!='rosterEvidence'},ensure_ascii=False,indent=2))
if __name__=='__main__':main()
