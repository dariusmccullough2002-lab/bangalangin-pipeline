"""Rebuild the editorial debut watch from frozen, source-linked inputs. No network."""
import json,pathlib
ROOT=pathlib.Path(__file__).resolve().parents[1]
D=ROOT/'docs/door-opportunity-research-20261027'
def read(p):return json.loads(p.read_text())
edit=read(D/'Editorial_Research.json');edition=read(D/'Edition_Player_Inputs.json')
rosters=read(D/'MLB_Rosters_Condensed.json');people=read(D/'Players_Frozen.json')
byid={p['id']:p for p in people['data']['people']};teams={t['teamId']:t for t in rosters['teams']}
players=[]
for note in edit['players']:
 p=next(x for x in edition['rankings'] if x['name']==note['name'])
 assert not byid[p['mlbamId']].get('mlbDebutDate'),f"Already debuted: {p['name']}"
 assert p['level'] in ['AA','AAA']
 group='pitching' if p['type']=='P' else 'hitting';stats=next(s for s in p['seasonStats']['groups'] if s['group']==group)
 splits=[s for s in p['seasonStats']['splits'] if s['group']==group and s['level']==p['level']]
 team=teams[note['teamId']]
 incumbents=[]
 for name in note['incumbents']:
  match=next((x for x in team['players'] if x['name']==name),None)
  assert match,f"Missing incumbent: {name}"
  incumbents.append(match)
 source=p.get('scoutingGrades',{})
 players.append({**note,'playerId':p['playerId'],'mlbamId':p['mlbamId'],'mlbOrg':p['mlbOrg'],'position':p['rankingPosition'],'age':byid[p['mlbamId']]['currentAge'],'type':p['type'],'level':p['level'],'leagueRank':p['leagueRank'],'organization':p['organization'],'stats':stats,'statsDate':p['seasonStats']['retrievedDate'],'statsUrl':p['seasonStats']['sourceUrl'],'levelSplits':splits,'allLevelSplits':p['seasonStats']['splits'],'rosterUrl':team['url'],'incumbentEvidence':incumbents,'debutCheckDate':people['retrievedDate'],'mlbDebutDate':None,'sourceLabel':'FanGraphs scouting report','publishedEta':p.get('eta'),'etaContext':'Saved league profile label; not an independently calibrated debut forecast.'})
result={'version':'2026-10-27-opportunity-research-v2','asOf':edit['retrievedDate'],'selection':edit['selection'],'coverage':{'players':len(players),'researchedOrganizations':len(set(p['mlbOrg'] for p in players)),'rosterSnapshots':len(rosters['teams']),'pitchLevelMeasurements':'Not independently collected. Specific weaknesses are attributed to dated scouting reports; proposed monitors are not claimed as measurements.'},'players':players}
(ROOT/'data/knocking-door-2027.json').write_text(json.dumps(result,indent=2,ensure_ascii=False)+'\n')
print(f"Built {len(players)} researched cases across {result['coverage']['researchedOrganizations']} organizations")
