"""Read existing Phase1 scales without importing/rerunning its analysis."""
import json,gzip,math,datetime,collections
from pathlib import Path
import numpy as np
P=Path(__file__).resolve().parent
BASE=P.parent/'phase1-calibration'
if not BASE.exists():BASE=P.parent/'phase1-2026-10-08'
old=json.load(open(BASE/'results/validation.json'));den={k:np.array(v) for k,v in old['category_dispersion'].items()}
n=lambda s,k:float(s.get(k,0) or 0)
def ip(s):
 if 'outs' in s:return n(s,'outs')/3
 a,b=(str(s.get('inningsPitched','0.0')).split('.')+['0'])[:2];return int(a)+int(b)/3

def score(s,r):
 if r=='H':
  ab=n(s,'atBats');v=[n(s,'homeRuns'),n(s,'runs'),n(s,'rbi'),n(s,'stolenBases'),n(s,'hits')-.25*ab,(float(s.get('ops','0'))-.72)*ab]
 else:
  innings=ip(s);v=[n(s,'strikeOuts'),4.2/9*innings-n(s,'earnedRuns'),3*n(s,'saves')+2*n(s,'holds'),n(s,'strikeOuts')-3*n(s,'baseOnBalls'),1.25*innings-n(s,'hits')-n(s,'baseOnBalls')]
 return float(np.sum(np.array(v)/den['H' if r=='H' else 'P']))
def seasons():
 rows={}
 for y in range(2010,2026):
  for group in ['hitting','pitching']:
   f=BASE/'raw'/f'{group}-{y}.json'
   d=json.load(open(f)) if f.exists() else json.load(gzip.open(P/'raw'/f'mlb-{group}-{y}.json.gz','rt'))
   for ss in d['stats']:
    for a in ss['splits']:
     id=a['player']['id'];s=a['stat'];r='H' if group=='hitting' else ('SP' if n(s,'gamesStarted')>=5 else 'RP');ex=n(s,'atBats') if r=='H' else ip(s)
     if (y,id) in rows and rows[(y,id)]['ex']/(150 if rows[(y,id)]['role']=='H' else 30)>ex/(150 if r=='H' else 30):continue
     rows[y,id]={'id':id,'year':y,'name':a['player']['fullName'],'role':r,'ex':ex,'score':score(s,r),'age':n(s,'age'),'stat':s}
 return rows

def minor_features():
 out={};audit=[]
 for y in [2009,2010,2011,2012,2013,2014,2019]:
  for group in ['hitting','pitching']:
   raw=json.load(gzip.open(P/'raw'/f'milb-{group}-{y}.json.gz','rt'));per=collections.defaultdict(list);seen=set();duplicates=[]
   for ss in raw['stats']:
    for a in ss['splits']:
     key=(a['player']['id'],a.get('team',{}).get('id'),a.get('league',{}).get('id'))
     if key in seen:duplicates.append(key);continue
     seen.add(key);per[key[0]].append(a['stat'])
   audit.append(raw.get('_full_source_audit') or {'year':y,'group':group,'rows':sum(len(ss['splits']) for ss in raw['stats']),'reported_totalSplits':[ss.get('totalSplits') for ss in raw['stats']],'duplicate_player_team_league_rows':len(duplicates),'unique_ids':len(per)})
   for id,stats in per.items():
    total=lambda k:sum(n(s,k) for s in stats)
    if group=='hitting':
     pa=total('plateAppearances');ab=total('atBats');features=[total('strikeOuts')/pa if pa else 0,total('baseOnBalls')/pa if pa else 0,(total('totalBases')-total('hits'))/ab if ab else 0,math.log1p(pa)/7]
    else:
     bf=total('battersFaced');outs=sum(ip(s)*3 for s in stats);features=[total('strikeOuts')/bf if bf else 0,total('baseOnBalls')/bf if bf else 0,9*total('earnedRuns')/(outs/3) if outs else 0,math.log1p(outs/3)/6]
    out[y,id,group]=features
 return out,audit
