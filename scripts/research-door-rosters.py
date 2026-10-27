"""Freeze public MLB roster usage and debut records. Run from the repository root.
This refreshes evidence only; it does not automatically endorse or publish a watchlist.
"""
import concurrent.futures, datetime, json, pathlib, urllib.request
ROOT=pathlib.Path(__file__).resolve().parents[1]
OUT=ROOT/'docs/door-opportunity-research-20261027'
BASE='https://statsapi.mlb.com/api/v1/'
def get(url):
 with urllib.request.urlopen(url,timeout=45) as r:return json.load(r)
def condense(t):
 team_id=t['id'];url=BASE+f'teams/{team_id}/roster?rosterType=40Man&season=2026&hydrate=person(stats(group=[hitting,pitching,fielding],type=[season],season=2026))'
 raw=get(url);players=[]
 for row in raw['roster']:
  person=row['person'];stats={};field=[]
  for block in person.get('stats',[]):
   for split in block.get('splits',[]):
    if split.get('sport',{}).get('id')!=1 or split.get('team',{}).get('id')!=team_id or split.get('gameType')!='R':continue
    stat=split['stat'];group=block['group']['displayName']
    if group=='fielding':field.append({'position':split.get('position',{}).get('abbreviation'),'games':stat.get('gamesPlayed'),'starts':stat.get('gamesStarted')})
    else:
     assert group not in stats,(person['fullName'],group)
     stats[group]={k:v for k,v in stat.items() if k in ['plateAppearances','ops','gamesPlayed','gamesStarted','inningsPitched','era']}
  players.append({'id':person['id'],'name':person['fullName'],'status':row['status']['description'],'position':row['position']['abbreviation'],'fielding':field,'stats':stats})
 return {'teamId':team_id,'teamName':t['name'],'url':url,'players':players}
def main():
 OUT.mkdir(exist_ok=True);today=datetime.date.today().isoformat();teams=get(BASE+'teams?sportId=1&season=2026')['teams']
 with concurrent.futures.ThreadPoolExecutor(max_workers=6) as pool:rows=list(pool.map(condense,teams))
 assert len(rows)==30
 output={'retrievedDate':today,'season':2026,'scope':'40-man listings and hydrated full-season stats, not final 2027 depth charts','extraction':'Only sportId 1, team-matching regular-season splits; no combined totals added to team splits. Fielding games are not future depth-chart assignments.','teams':rows}
 (OUT/'MLB_Rosters_Condensed.json').write_text(json.dumps(output,indent=2,ensure_ascii=False)+'\n')
 edition=json.loads((OUT/'Edition_Player_Inputs.json').read_text());ids=','.join(str(p['mlbamId']) for p in edition['rankings']);url=BASE+'people?personIds='+ids
 (OUT/'Players_Frozen.json').write_text(json.dumps({'retrievedDate':today,'url':url,'data':get(url)},indent=2)+'\n')
 print(f'Captured {len(rows)} clubs and {len(edition["rankings"])} player checks. Review before rebuilding.')
if __name__=='__main__':main()
