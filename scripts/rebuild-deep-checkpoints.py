"""Rebuild reviewed plans from per-player editorial decisions and a provenance manifest.
Research snapshots stay outside the public repository; this importer never invents a plan.
"""
import json,pathlib,collections
root=pathlib.Path(__file__).resolve().parents[1]
read=lambda p:json.loads((root/p).read_text())
decisions={}
for n,line in enumerate((root/'checkpoint-editorial/decisions.txt').read_text().splitlines(),1):
 if not line.strip():continue
 bits=line.split('|')
 if len(bits)!=5:raise ValueError(f'Invalid editorial row {n}')
 ident,topic,question,positive,concern=bits
 if ident in decisions:raise ValueError('Duplicate reviewed identity '+ident)
 decisions[ident]=dict(topic=topic,question=question,positive=positive,concern=concern)
manifest=read('checkpoint-editorial/research-manifest.json');previous=read('data/development-checkpoints.json')
pools=[('october-player','editions/october-2026','rankings','playerId'),('draft-player','draft/2026','players','id'),('international-player','international/2027','players','id'),('international-pro-player','international/professionals-2026','players','id'),('afl-player','afl/full-2026','players','mlbamId'),('dsl-player','dsl/2026','players','id')]
identities={};routes={}
for route,path,key,idkey in pools:
 for p in read('data/'+path+'.json')[key]:
  ident=str(p.get('mlbamId') or p['name']);identities.setdefault(ident,[]).append((route,p));routes[f'{route}/{p[idkey]}']=ident
if set(identities)!=set(decisions):raise ValueError('Editorial coverage mismatch')
def baseline(records):
 for route,p in records:
  for g in p.get('seasonStats',{}).get('groups',[]):
   when=p['seasonStats'].get('retrievedDate','date unavailable');level=p.get('level','checked levels')
   if g['group']=='hitting':return f"2026 regular season, {level}: {g.get('pa')} PA; {g.get('kPercent')}% K, {g.get('bbPercent')}% BB, {g.get('iso')} ISO; {g.get('homeRuns')} HR. Snapshot retrieved {when}. Combined-level rates must be checked against the level splits."
   if g['group']=='pitching':return f"2026 regular season, {level}: {g.get('ip')} IP; {g.get('strikeOuts')} K, {g.get('walks')} BB; {g.get('kPercent')}% K, {g.get('bbPercent')}% BB. Snapshot retrieved {when}. Baseball innings notation is retained."
 for route,p in records:
  s=p.get('regularStats')
  if s:
   if p.get('type')=='H':return f"Saved 2026 regular-season record (profile snapshot {read('data/afl/full-2026.json')['asOf']}): {s.get('plateAppearances')} PA, {s.get('homeRuns')} HR, {s.get('strikeOuts')} K, {s.get('baseOnBalls')} BB. Regular-season data remain separate from AFL results."
   return f"Saved 2026 regular-season record (profile snapshot {read('data/afl/full-2026.json')['asOf']}): {s.get('inningsPitched')} IP, {s.get('strikeOuts')} K, {s.get('baseOnBalls')} BB; {s.get('gamesStarted')} starts in {s.get('gamesPlayed')} games. These counts describe usage and outcomes, not pitch grades."
 for route,p in records:
  if p.get('performance',{}).get('stats'):return 'Native-league snapshot (not an MLB projection): '+ '; '.join(f'{k}: {v}' for k,v in p['performance']['stats'].items())+'. See the native-league source date on this profile.'
 if any(route=='international-player' for route,p in records):return 'Amateur/reported-agreement evidence; no verified professional performance baseline is assigned. Signing status and acquisition route remain separate from talent.'
 return 'No usable current regular-season baseline is stored. Establish game participation and a documented competitive sample before inferring present stuff, health or role.'
def sources_for(ident,records):
 sources=[]
 for route,p in records:
  for old in previous['entries'].values():
   if old.get('mlbamId') and str(old['mlbamId'])==ident:sources+=old.get('sources',[])
  if not p.get('mlbamId'):
   for old in previous['entries'].values():
    if old['name']==p['name']:sources+=old.get('sources',[])
 m=manifest['players'][ident]
 sources=m['retrievedSources']+sources;seen=set();return [s for s in sources if s.get('url','').startswith('https://') and not(s['url'] in seen or seen.add(s['url']))]
plans={}
limited={'Luis García','Enyel González','Eudi Yuten','Sebastián Pérez Acuña','801842','694761','695403','836586'}
for ident,records in identities.items():
 m=manifest['players'][ident];primary=records[0][1];plan=decisions[ident];source_kind=m['basis'];hasnew=bool(m['retrievedSources'])
 if ident in limited:status='Limited evidence — targeted verification needed'
 elif hasnew:status='Individual source review — progress not yet verified'
 else:status='Individual review of saved evidence — new scouting limited'
 earlier=next((previous['entries'][r] for r,i in routes.items() if i==ident),{})
 evidence=f"Individually reviewed focus: {plan['topic']}. "
 if source_kind=='published_player_report':evidence+=f"The {m['reportYear']} MLB Pipeline scouting report was retrieved October 22, 2026 and checked against the saved profile. The checkpoint is Pipeline interpretation of that report, not a new tool grade."
 elif source_kind=='published_afl_overview':evidence+='MLB’s 2026 team AFL overview was retrieved October 22, 2026 and checked for this player’s role, health context and repertoire or hitting issues. The proposed signal is editorial interpretation, not reported progress.'
 else:evidence+='The saved player-specific scouting, outcome and performance material was re-read for this review. Public detail remains limited in places; the checkpoint does not assert unseen pitch shapes or an unreported mechanical diagnosis.'
 plans[ident]={**plan,'name':primary['name'],'mlbamId':primary.get('mlbamId'),'evidence':evidence,'baseline':baseline(records),'evidenceDate':m.get('reportYear') or earlier.get('evidenceDate'),'reviewedAsOf':'2026-10-22','window':earlier.get('window','Next verified competitive games and assignment.'),'status':status,'sources':sources_for(ident,records),'researchBasis':source_kind,'individualEditorialReview':True}
entries={route:{**plans[ident],**({'canonicalRoute':previous['entries'][route]['canonicalRoute']} if previous['entries'].get(route,{}).get('canonicalRoute') else {}),'name':next(p['name'] for r,p in identities[ident] if route==f"{r}/{p.get('playerId') if r=='october-player' else p.get('mlbamId') if r=='afl-player' else p.get('id')}")} for route,ident in routes.items()}
questions=collections.Counter(p['question'] for p in plans.values())
audit={'profileEntries':len(entries),'uniquePlayers':len(plans),'individualEditorialPlans':len(decisions),'publishedPlayerReportsRetrieved':sum(m['basis']=='published_player_report' for m in manifest['players'].values()),'additionalAflOverviewsUsed':sum(m['basis']=='published_afl_overview' for m in manifest['players'].values()),'savedEvidenceReviews':sum(m['basis']=='saved_player_evidence' for m in manifest['players'].values()),'limitedEvidencePlayers':sum(p['status'].startswith('Limited evidence') for p in plans.values()),'missingSources':sum(not p['sources'] for p in entries.values()),'duplicateQuestionsAcrossDistinctPlayers':sum(v-1 for v in questions.values() if v>1),'scope':'All current prospect sections reviewed by player identity. Individual questions, positive signals and concerns are editorially authored, never selected from keyword templates. Historical August archive unchanged.'}
output={'asOf':'2026-10-22','method':'Individually written development plans informed by retrieved published scouting and dated player evidence. Signals describe what to verify, not changes already achieved. No automatic ranking/projection update.','audit':audit,'entries':entries}
(root/'data/development-checkpoints.json').write_text(json.dumps(output,ensure_ascii=False,indent=2)+'\n')
(root/'docs/development-checkpoints/deep-audit-20261022.json').write_text(json.dumps({'asOf':output['asOf'],**audit,'players':[{'identity':i,'name':p['name'],'topic':p['topic'],'question':p['question'],'basis':p['researchBasis'],'status':p['status'],'sourceUrls':[s['url'] for s in p['sources']]} for i,p in plans.items()]},ensure_ascii=False,indent=2)+'\n')
print(json.dumps(audit,indent=2))
