import json,re,pathlib
read=lambda p:json.loads(pathlib.Path('data/'+p+'.json').read_text())
reports=read('profile-reports'); entries={}
themes=[('Health and workload',r'rehab|surgery|injur|recovery','Does competitive participation support a sustained, effective workload?','Repeated game participation and maintained effectiveness as workload grows.','Setbacks, interrupted availability or effectiveness declining as workload grows.'),('Strike throwing',r'command|control|strike.throw|walk rate','Can the pitcher locate the arsenal consistently against competitive hitters?','More competitive counts and fewer walks across multiple outings without reduced stuff.','Persistent noncompetitive misses or reduced stuff needed to find the zone.'),('Contact and approach',r'contact|secondary pitches|breaking balls|whiff|chase|strikeout','Does pitch recognition improve without sacrificing damage?','Fewer empty swings and chases across repeated looks, with extra-base impact retained.','The same pitch types repeatedly exploit the swing, or contact improves only by losing impact.'),('Arsenal and role',r'fastball|slider|splitter|velocity|arsenal|changeup','Do the reported weapons hold up in games through the intended workload?','Complementary pitches and sustained effectiveness through repeated competitive outings.','Stuff fades through outings or hitters can sit on one effective pitch.'),('Game power',r'power|damage|impact|extra.base','Does offensive potential become repeatable damage against competitive pitching?','Extra-base impact while preserving contact and approach against stronger opposition.','Damage relies on mistakes or weaker opposition, or added lift brings excessive misses.'),('Defensive opportunity',r'defens|shortstop|catcher|receiv','Does game evidence support the projected defensive home and its playing-time value?','Repeated assignments and credible defensive reports support the projected position.','A move down the defensive spectrum raises the offensive standard or reduces opportunity.')]
pools=[('october-player','editions/october-2026','rankings','playerId'),('draft-player','draft/2026','players','id'),('international-player','international/2027','players','id'),('international-pro-player','international/professionals-2026','players','id'),('afl-player','afl/full-2026','players','mlbamId'),('dsl-player','dsl/2026','players','id')]
for route,path,key,idkey in pools:
 d=read(path)
 for p in d[key]:
  review=reports['profiles'].get(p.get('playerId',reports.get('byMlbam',{}).get(str(p.get('mlbamId')))),{})
  paras=(review.get('paragraphs') or p.get('scoutingParagraphs') or p.get('reportParagraphs') or p.get('projectionParagraphs') or [p.get('summary'),p.get('performanceSummary')]+[s['text'] for s in p.get('reportSections',[])])+[p.get('outcomes',{}).get('risk',{}).get('reason'),p.get('outcomes',{}).get('defensiveOpportunity',{}).get('rationale')]
  sentences=[s for para in paras if para for s in re.split(r'(?<=[.!?])\s+',para) if len(s)>65]
  sentences.sort(key=lambda s:-(4*bool(re.search(r'next |watch |question|depends|needs|whether|must |risk|concern|uncertain|remain|improv',s,re.I))+2*bool(re.search(r'secondary pitches|breaking balls|command|rehab|surgery',s,re.I))))
  pitching=p.get('type')=='P'
  usable=lambda t: t[0] not in (['Contact and approach','Game power','Defensive opportunity'] if pitching else ['Strike throwing','Arsenal and role'])
  evidence=next((s for s in sentences if not re.search(r'not (?:been )?established|not verified|no verified|no usable|unverified|missing measurements|no reliable|not available',s,re.I) and any(usable(t) and re.search(t[1],s,re.I) for t in themes)),next(iter(sentences),None))
  theme=next((t for t in themes if re.search(t[1],evidence or '',re.I) and (t[0] not in ['Contact and approach','Game power','Defensive opportunity'] if pitching else t[0] not in ['Strike throwing','Arsenal and role'])),None)
  sources=review.get('sources',[])+p.get('scoutingSources',[])+p.get('outcomes',{}).get('sources',[])
  if isinstance(p.get('sources'),list):sources+=p['sources']
  if not sources:sources=[s for s in d.get('sources',[]) if s.get('id') in p.get('sourceIds',[])]
  if not sources:sources=[{'url':u,'label':'Profile research reference'} for u in p.get('researchReferences',[])]
  stat=p.get('seasonStats',{})
  if stat.get('sourceUrl'):sources.append({'url':stat['sourceUrl'],'label':'Saved regular-season record','retrievedDate':stat.get('retrievedDate')})
  seen=set(); sources=[s for s in sources if str(s.get('url','')).startswith('https://') and not(s['url'] in seen or seen.add(s['url']))]
  window={'afl-player':'Remaining AFL games, compared with the larger regular-season sample.','international-player':'Signing or acquisition-route confirmation, then the first verified professional game sample.','international-pro-player':'Verified posting/free-agency news and competitive games; MLB spring training if signed.','dsl-player':'Next verified DSL or stateside assignment and competitive game sample.'}.get(route,'Next verified competitive assignment or spring-training games, then the regular-season sample.')
  entries[f'{route}/{p[idkey]}']={'name':p['name'],'mlbamId':p.get('mlbamId'),'topic':theme[0] if theme else 'Establish the evidence base','question':theme[2] if theme else f'What verified competitive evidence establishes {p["name"]}’s carrying skill and likely role?','evidence':evidence,'evidenceDate':review.get('reviewedAsOf') or p.get('research',{}).get('asOf') or p.get('outcomes',{}).get('asOf') or d.get('researchAsOf') or d.get('asOf'),'positive':theme[3] if theme else 'A dated scouting report and usable game sample identify a specific carrying skill.','concern':theme[4] if theme else 'The evaluation continues to rely on pedigree, agreement news or unverified descriptions alone.','window':window,'status':'Monitoring — progress not yet verified' if theme else 'Evidence gap — research needed','sources':sources}
for p in read('dsl/2026')['players']:
 canonical=next((x for x in read('editions/october-2026')['rankings'] if x.get('mlbamId')==p.get('mlbamId')),None)
 if canonical:
  original=entries['dsl-player/'+p['id']]
  entries['dsl-player/'+p['id']]={**entries['october-player/'+canonical['playerId']],'name':p['name'],'canonicalRoute':'october-player/'+canonical['playerId']}
research=pathlib.Path('data/research/checkpoint-followup-20261022.json')
if research.exists():
 for route,override in json.loads(research.read_text())['overrides'].items():
  entries[route].update(override)
audit={'profileEntries':len(entries),'uniquePlayers':len({str(p['mlbamId']) if p['mlbamId'] else p['name'].lower() for p in entries.values()}),'evidenceGaps':sum(p['status'].startswith('Evidence gap') for p in entries.values()),'limitedScoutingEntries':sum(p['status'].startswith('Limited scouting') for p in entries.values()),'missingSources':sum(not p['sources'] for p in entries.values()),'scope':'All current prospect sections; historical August archive preserved. Automated audit of saved profile evidence, not fresh individual scouting.'}
output={'asOf':'2026-10-22','method':'Editorial monitoring prompts derived from saved profile evidence; not new scouting or verified progress.','audit':audit,'entries':entries}
pathlib.Path('data/development-checkpoints.json').write_text(json.dumps(output,ensure_ascii=False,indent=2)+'\n')
pathlib.Path('docs/development-checkpoints').mkdir(exist_ok=True)
pathlib.Path('docs/development-checkpoints/audit.json').write_text(json.dumps({'asOf':output['asOf'],**audit,'gaps':[{'route':r,'name':p['name'],'status':p['status'],'hasSources':bool(p['sources'])} for r,p in entries.items() if not p['sources'] or p['status'].startswith('Evidence gap')]},indent=2)+'\n')
print(audit)
