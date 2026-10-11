"""Export preserved role scenarios. No fitting, expected-forecast or valuation writes.
Usage: python scripts/build-role-display.py /path/to/restored/joint-opportunity
"""
import json, gzip, csv, re, base64, sys, hashlib
from pathlib import Path
root=Path(__file__).resolve().parents[1]; research=Path(sys.argv[1])
html=(root/'trade-analyzer-beta/index.html').read_text()
catalog=json.loads(gzip.decompress(base64.b64decode(re.search("const packed='([^']+)'",html)[1])))
parents={x['id']:x['parent'] for x in json.load(gzip.open(research/'starter-severity-intercept/League_Components.json.gz','rt'))}
prior={x['id']:x for x in json.load(gzip.open(research/'targeted-repair/Repair_League.json.gz','rt'))}
old={x['id']:x for x in csv.DictReader((research/'full-workload-scenario/League_1900_Comparison.csv').open()) if x['candidate']=='fitted'}
records={}
for asset in catalog['assets']:
    evidence=asset['audit'].get('MLB',asset['audit']); role=evidence.get('role')
    if role not in ['H','RP'] or evidence.get('two_way_annual_projection'):continue
    id=asset['id']; c=parents.get(id); a=prior.get(id)
    if c and c['role']=='swingman':continue # preserve existing swingman route
    entry={'name':asset['name'],'kind':role,'role':c['role'] if c else 'unidentified','supported':False,
           'reason':'No preserved MLB-role workload with verified appearances is supported. Arrival information is unchanged.'}
    records[id]=entry
    if not c or not a:continue
    obs=a['opportunity_inputs']['observations'];f=c['fitted']; positive=[o for o in obs[:3] if o['status']=='observed_positive' and o['complete'] and o['GP'] is not None and o['GP']>0]
    entry.update(observations=obs,probabilities=c['probabilities'],participation=c['participation'],researchExpected=f['expected'],researchConditionalActive=f['conditional_active'],preservedFullWorkload=f['full_role_workload'],workloadMethod=f['fallback'])
    if not positive:entry['reason']='No complete positive MLB appearance record in the latest three observation seasons; no workload invented.';continue
    if role=='H' and c['role'] in ['everyday','platoon','bench']:
        games=f['slots']['GP'];depth=f['full_role_workload']/games if games else 0
        if depth<=0:continue
        catcher='C' in re.split(r'[,/\s]+',asset.get('position',''))
        if catcher:
            # Display sensitivity only: the preserved model pools catchers with
            # everyday hitters. Do not present that pooled 145+ GP fit as
            # verified catcher capacity. Bound by recent demonstrated total GP.
            games=min(games,max(o['GP'] for o in positive))
        entry.update(supported=True,reason=None,appearances=games,workPerAppearance=depth,workload=games*depth,
                     roleLabel=('Catcher-eligible '+c['role']+' usage proxy') if catcher else c['role'].capitalize()+' hitter',
                     method='Recent demonstrated GP ceiling × preserved PA/game; catcher/DH assignment unidentifiable' if catcher else 'GP-repaired preserved fitted role-specific high-usage GP × PA/game',
                     catcherSensitivity=catcher,hypothetical=asset['audit'].get('kind')=='prospect')
    elif role=='RP' and c['role']=='reliever' and old.get(id):
        latest=positive[0]
        if latest['GS'] is None or latest['GS']!=0:
            entry['reason']='Incidental starts or missing GS prevent a supported pure-bullpen scenario; existing route retained.';continue
        ra=f['slots']['RA'];depth=float(old[id]['work_per_relief'])
        if ra<=0 or depth<=0:continue
        seasons=asset.get('career_profile',{}).get('seasons',[]); events=[]
        for rank,o in enumerate(obs[:3]):
            if o['status']!='observed_positive' or not o['complete'] or not o['GP'] or o['GS']!=0:continue
            matches=[s for s in seasons if s['year']==o['year'] and s['role'] in ['SP','RP'] and abs(s['stat'].get('IP',-1)-o['exposure'])<1e-6]
            if len(matches)!=1:continue
            s=matches[0]; st=s['stat'];gp=s.get('skills',{}).get('gamesPlayed',st.get('GP'));gs=s.get('skills',{}).get('gamesStarted',st.get('GS'))
            if gp!=o['GP'] or gs!=0 or any(st.get(k) is None for k in ['SV','HLD']):continue
            if st['SV']+st['HLD']>gp:continue
            events.append({'year':o['year'],'weight':3-rank,'appearances':gp,'SV':st['SV'],'HLD':st['HLD'],'source':s['source']})
        den=sum(e['weight']*e['appearances'] for e in events)
        sv=sum(e['weight']*e['SV'] for e in events)/den if den else None
        hld=sum(e['weight']*e['HLD'] for e in events)/den if den else None
        label='Closer usage proxy' if sv is not None and sv>hld and sv>0 else 'Setup usage proxy' if hld is not None and hld>sv and hld>0 else 'Bullpen role'
        # Retain the existing conditional performance yield per appearance.
        # No inferred start role and no QA3/IP rescaling.
        q=a['component']['conditional']['1'];n=q['GS']+q['RA'];qa=q['QA3']/n if n else None
        entry.update(supported=True,reason=None,appearances=ra,starts=0,workPerAppearance=depth,workload=ra*depth,roleLabel=label,
                     method='Preserved fitted relief appearances × preserved relief IP/appearance; incidental-start component excluded',
                     savePerAppearance=sv,holdPerAppearance=hld,opportunityEvidence=events,qa3PerAppearance=qa,
                     hypothetical=asset['audit'].get('kind')=='prospect')
out={'schemaVersion':1,'forecastYear':2027,'researchCheckpoint':'5e00a76d83f1d0427add2132ec75beef3da6adf4 (parent components only; failed candidate excluded)',
     'expectedSource':'Unchanged website V2.3C catalog: recent-performance talent rates and inherited aging path',
     'limitation':'Annual high usage is a scheduling proxy, not medically verified full availability or a confirmed future team assignment.',
     'qa3Definition':'At least 5 IP and no more than 2 ER, OR at least 6 IP and no more than 3 ER',
     'valuationInput':False,'players':records,
     'sourceHashes':{str(p.relative_to(research)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [research/'starter-severity-intercept/League_Components.json.gz',research/'targeted-repair/Repair_League.json.gz',research/'full-workload-scenario/League_1900_Comparison.csv']}}
(root/'data/role-display-scenarios.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
print('Exported',len(records),'records;',sum(x['supported'] for x in records.values()),'supported')
