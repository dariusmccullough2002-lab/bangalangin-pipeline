"""Audit current player narratives and canonical redirects; retain original source dates."""
import json,re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def read(path):return json.loads((ROOT/path).read_text())
coverage=read('docs/rescout-20261018/Coverage.json');reports=read('data/profile-reports.json');repairs=read('docs/rescout-20261018/Adequacy_Repairs.json')
files={loc['file']:read(loc['file']) for p in coverage['players'].values() for loc in p['locations']}
october={p['playerId']:p for p in files['data/editions/october-2026.json']['rankings']}
def urls(obj):
 if isinstance(obj,dict):return sum((urls(v) for v in obj.values()),[])
 if isinstance(obj,list):return sum((urls(v) for v in obj),[])
 return [obj] if isinstance(obj,str) and obj.startswith('https://') else []
def locate(loc):
 d=files[loc['file']]
 return next(p for p in d.get('rankings',d.get('players')) if str(p.get('playerId',p.get('id',p.get('mlbamId'))))==str(loc['id']))
def resolve(loc):
 p=locate(loc);f=loc['file'];redirect=None
 if p.get('existingProfileId'):redirect=p['existingProfileId']
 if p.get('hasExistingProfile') and p.get('route','').startswith('#october-player/'):redirect=p['route'].split('/')[-1]
 if redirect:
  assert redirect in october,(p['name'],'broken redirect',redirect)
  p=october[redirect];f='data/editions/october-2026.json'
 if p.get('hasExistingProfile') and p.get('route','').startswith('#draft-player/'):
  target=p['route'].split('/')[-1];p=next(q for q in files['data/draft/2026.json']['players'] if q['id']==target);f='data/draft/2026.json'
 key=p.get('playerId',reports.get('byMlbam',{}).get(str(p.get('mlbamId'))));r=reports['profiles'].get(key,{}) if ('october' in f or '/afl/' in f) else {}
 paragraphs=r.get('paragraphs',p.get('projectionParagraphs',p.get('reportParagraphs',p.get('scoutingParagraphs',[]))))
 if '/dsl/' in f or 'professionals-' in f:paragraphs=[p.get('summary',''),str(p.get('performanceSummary',''))]+[q['text'] for q in p.get('reportSections',[])]
 paragraphs=[q for q in paragraphs if q]
 return p,r,paragraphs,f
errors=[];entries=0;repair_count=0;full_count=0
for key,player in coverage['players'].items():
 checks=[];statuses=[];all_urls=[]
 for loc in player['locations']:
  entries+=1;p,r,paragraphs,f=resolve(loc);text=' '.join(paragraphs)
  # Minimum catches empty/fragment-only pages; basis and development checks add substance.
  enough=len(text.split())>=55 and len(paragraphs)>=2
  unfinished=bool(re.search(r'generated:|Major risk:\s*$|\bTODO\b|building AFL sample',text,re.I))
  basis=bool(p.get('seasonStats') or p.get('regularStats') or p.get('scoutingGrades') or p.get('reportSections') or p.get('performance') or re.search(r'contact|power|fastball|slider|curve|athleti|arm|speed|defen|college|school|draft|signing|injury|surgery|strikeout|walks',text,re.I))
  development=bool(re.search(r'risk|next|need|question|depend|uncertain|remain|watch|must|if |develop|projection|path|test|limit|challeng',text,re.I))
  ids={s['id'] for s in files[f].get('sources',[]) if 'id' in s};badids=[i for i in p.get('sourceIds',[]) if i not in ids]
  relevant_urls=sorted(set(urls(r.get('sources',[]))+urls(p.get('sources',[]))+urls(p.get('researchReferences',[]))+urls(p.get('sourceUrl'))+urls(p.get('identitySource'))+urls(p.get('officialUrl'))+[u for s in files[f].get('sources',[]) if s.get('id') in p.get('sourceIds',[]) for u in urls(s)]))
  if not relevant_urls:relevant_urls=sorted(set(urls(files[f].get('sources',[]))))
  ok=enough and not unfinished and basis and development and not badids and bool(relevant_urls)
  if not ok:errors.append({'name':player['name'],'location':loc,'checks':[enough,not unfinished,basis,development,not badids,bool(relevant_urls)],'badSourceIds':badids})
  kind='individual research complete' if r.get('reviewedAsOf') and r.get('reviewType')!='adequacy repair' else 'targeted adequacy repair' if r.get('reviewType')=='adequacy repair' or p.get('id') in repairs and f=='data/draft/2026.json' else 'adequate retained'
  statuses.append(kind);all_urls+=relevant_urls
  checks.append({'location':loc,'canonicalDataset':f,'canonicalId':p.get('playerId',p.get('id',p.get('mlbamId'))),'status':kind,'wordCount':len(text.split()),'specificContext':paragraphs[0],'developmentContext':paragraphs[-1],'checksPassed':ok})
 player['status']='individual research complete' if 'individual research complete' in statuses else 'targeted adequacy repair' if 'targeted adequacy repair' in statuses else 'adequate retained'
 player['adequacyReviewedAsOf']='2026-10-18';player['adequacyChecks']=checks;player['sourceUrls']=sorted(set(all_urls))
 if player['status']=='individual research complete':full_count+=1
 if player['status']=='targeted adequacy repair':repair_count+=1
coverage.update({'reviewDate':'2026-10-18','scope':'Current-profile adequacy audit, not a claim of fresh independent scouting for every retained player. Existing source and statistical snapshot dates remain in force.','completedUniquePlayers':full_count,'pendingUniquePlayers':0,'pendingAdequacyPlayers':len({e['name'] for e in errors}),'adequacyReviewedUniquePlayers':len(coverage['players']),'adequacyReviewedProfileEntries':entries,'targetedRepairUniquePlayers':repair_count,'retainedUniquePlayers':len(coverage['players'])-full_count-repair_count,'errors':errors})
(ROOT/'docs/rescout-20261018/Coverage.json').write_text(json.dumps(coverage,ensure_ascii=False,separators=(',',':'))+'\n')
print(json.dumps({k:v for k,v in coverage.items() if k!='players'},indent=2))
if errors:raise SystemExit(1)
