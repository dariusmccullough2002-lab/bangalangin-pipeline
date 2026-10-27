"""Build display-only hitter samples. --refresh collects official counts; default replays frozen responses."""
import argparse,concurrent.futures,datetime,json,pathlib,urllib.request
ROOT=pathlib.Path(__file__).resolve().parents[1]
D=ROOT/'docs/door-opportunity-research-20261027'
RAW=D/'Hitter_Sample_Responses.json'
args=argparse.ArgumentParser();args.add_argument('--refresh',action='store_true');refresh=args.parse_args().refresh
watch=json.loads((ROOT/'data/knocking-door-2027.json').read_text())
levels={'AAA':11,'AA':12,'A+':13,'A':14,'CPX':16,'DSL':16}
raw=json.loads(RAW.read_text()) if RAW.exists() else {'retrievedAt':None,'responses':{}}
def request(player,season,level):
 key=f"{player['mlbamId']}-{season}-{level}"
 if not refresh:
  assert key in raw['responses'],f'Missing frozen response: {key}'
  return key,raw['responses'][key]
 url=f"https://statsapi.mlb.com/api/v1/people/{player['mlbamId']}/stats?stats=season&group=hitting&season={season}&sportId={levels[level]}&gameType=R"
 with urllib.request.urlopen(url,timeout=30) as response:data=json.load(response)
 return key,{'url':url,'data':data}
def counts(response,season):
 rows=[s for g in response['data'].get('stats',[]) if g.get('group',{}).get('displayName')=='hitting' for s in g.get('splits',[]) if str(s.get('season'))==str(season) and s.get('gameType','R')=='R']
 totals=[s for s in rows if not s.get('team')]
 if totals:
  assert len(totals)==1
  rows=totals
 else:
  assert len({s.get('team',{}).get('id') for s in rows})==len(rows),'Duplicate team splits'
 if not rows:return None
 def total(key):return sum(int(s['stat'].get(key,0)) for s in rows)
 pa=total('plateAppearances');ab=total('atBats');h=total('hits');bb=total('baseOnBalls');hbp=total('hitByPitch');sf=total('sacFlies');den=ab+bb+hbp+sf
 def rate(n,d):return f'{n/d:.3f}'.removeprefix('0') if d else '—'
 return {'pa':pa,'ab':ab,'hits':h,'bb':bb,'hbp':hbp,'sf':sf,'totalBases':total('totalBases'),'k':total('strikeOuts'),'avg':rate(h,ab),'obp':rate(h+bb+hbp,den),'slg':rate(total('totalBases'),ab),'hr':total('homeRuns'),'sb':total('stolenBases')}
def collect(p):
 responses={};candidates=[];highest=None
 # Highest to lowest level, preserving the separate season identity.
 present=[level for level in levels if any(s['level']==level and s['group']=='hitting' for s in p['allLevelSplits'])]
 for level in present:
  key,response=request(p,2026,level);responses[key]=response;c=counts(response,2026)
  assert c is not None,f'Missing 2026 counts: {p["name"]} {level}'
  frozen=[s for s in p['allLevelSplits'] if s['group']=='hitting' and s['level']==level]
  for saved,field in [('pa','pa'),('k','k'),('hr','hr'),('sb','sb')]:assert sum(s.get(saved,0) for s in frozen)==c[field],f'Snapshot mismatch: {p["name"]} {level} {field}'
  line={**c,'level':level,'season':2026,'sourceUrl':response['url']}
  if level==p['level']:highest=line
  candidates.append(line)
  if c['pa']>=40:break
 display=next((c for c in candidates if c['pa']>=40),None)
 if display is None:
  for level in ['AAA','AA','A+','A','CPX']:
   key,response=request(p,2025,level);responses[key]=response;c=counts(response,2025)
   if c and c['pa']>=40:
    display={**c,'level':level,'season':2025,'sourceUrl':response['url']};break
 return p['mlbamId'],{'name':p['name'],'highest':highest,'display':display or highest,'substantial':display is not None},responses
with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
 results=list(pool.map(collect,[p for p in watch['players'] if p['type']=='H']))
for _,_,responses in results:raw['responses'].update(responses)
if refresh:raw['retrievedAt']=datetime.datetime.now(datetime.timezone.utc).isoformat();RAW.write_text(json.dumps(raw,indent=2,ensure_ascii=False)+'\n')
result={'version':1,'minimumPA':40,'retrievedAt':raw['retrievedAt'],'method':'Highest 2026 level with at least 40 PA; otherwise highest 2025 level with at least 40 PA. Rates recomputed from underlying counts, not averaged. AFL handled separately by the tile renderer.','players':{str(pid):p for pid,p,_ in results}}
(ROOT/'data/door-hitter-samples.json').write_text(json.dumps(result,indent=2,ensure_ascii=False)+'\n')
print(f'Built {len(results)} hitter tile samples')
for _,p,_ in results:
 if p['highest']['pa']<40:print(p['name'],p['display']['season'],p['display']['level'],p['display']['pa'],'PA; highest',p['highest']['pa'],'PA /',p['highest']['ab'],'AB')
