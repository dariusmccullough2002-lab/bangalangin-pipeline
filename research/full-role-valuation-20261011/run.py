"""Offline first-year replay. Inputs: recovered model root, preserved joint-opportunity root.
Uses saved predictions only; does not fit models, collect data or modify publication files.
"""
import sys,json,gzip,csv,re,base64,hashlib,math,statistics,subprocess
from pathlib import Path
from collections import Counter,defaultdict
ROOT=Path(__file__).resolve().parents[2];OUT=Path(__file__).resolve().parent
MODEL=Path(sys.argv[1]).resolve();P=Path(sys.argv[2]).resolve()
sys.path.insert(0,str(MODEL/'trade-preview-v23c-evidence-guard'))
import model_asset_fit as engine
r=engine.r;old=engine.old
def read(p):return json.loads(gzip.decompress(p.read_bytes()) if p.suffix=='.gz' else p.read_text())
def write(name,x):
 b=json.dumps(x,indent=2,allow_nan=False).encode();(OUT/name).write_bytes(gzip.compress(b,mtime=0) if name.endswith('.gz') else b)
def csvwrite(name,rows):
 cols=list(dict.fromkeys(k for a in rows for k in a))
 with (OUT/name).open('w',newline='') as f:
  w=csv.DictWriter(f,cols);w.writeheader();w.writerows(rows)
def metric(xs):
 d=[a-b for a,b in xs if a is not None and b is not None]
 return {'n':len(d),'MAE':sum(abs(a) for a in d)/len(d) if d else None,'RMSE':math.sqrt(sum(a*a for a in d)/len(d)) if d else None,'bias':sum(d)/len(d) if d else None}
def ratios(s,rr):
 if rr=='H':
  ab=s.get('AB',0);den=ab+sum(s.get(k,0) for k in ['BB','HBP','SF'])
  return {'AVG':s.get('H',0)/ab if ab else None,'OBP':sum(s.get(k,0) for k in ['H','BB','HBP'])/den if den else None,'SLG':s.get('TB',0)/ab if ab else None,'OPS':(sum(s.get(k,0) for k in ['H','BB','HBP'])/den+s.get('TB',0)/ab) if ab and den else None}
 ip=s.get('IP',0);bb=s.get('BB',0)
 return {'ERA':9*s.get('ER',0)/ip if ip else None,'WHIP':(s.get('H',0)+bb)/ip if ip else None,'KBB':s.get('K',0)/bb if bb else None}
def contribution(s,rr):
 if any(s.get(k) is None for k in old.fields[rr]):return None
 ex=s.get('PA' if rr=='H' else 'IP',0);score=r.score(s,rr);replacement=r.floor[rr]*ex/r.REFERENCE[rr];surplus=r.surplus(s,rr)
 assert abs(score-replacement-surplus)<1e-9
 return {'signed_category_contribution':score,'replacement_charge':replacement,'replacement_surplus':surplus,'utility':r.utility(surplus)}
def scale(line,rr,work):
 key='PA' if rr=='H' else 'IP';f=work/line[key]
 keys=old.fields[rr] if rr=='H' else ['IP','K','ER','H','BB']
 return {k:line[k]*f for k in keys}
def current_scenario(a,roles,starters):
 e=a['audit'].get('MLB',a['audit']);rr=e.get('role');b=e.get('projection')
 if not b or rr not in ['H','SP','RP'] or e.get('two_way_annual_projection'):return None,'unsupported/two-way'
 # Do not reroute hybrids/prospects even when a hypothetical MLB display exists.
 if a['audit']['kind']!='MLB':return None,'prospect/hybrid route retained'
 key='PA' if rr=='H' else 'IP'
 if not b.get(key):return None,'no positive fixed rate line'
 if a['id'] in starters and rr=='SP':
  s=starters[a['id']];return (s['line'].copy(),'starter',s['starts']+s['reliefAppearances']),None
 s=roles.get(a['id'])
 if not s or not s.get('supported'):return None,(s or {}).get('reason','unsupported/swingman')
 z=scale(b,rr,s['workload'])
 if rr=='RP':
  for k,rate in [('SV','savePerAppearance'),('HLD','holdPerAppearance')]:z[k]=s['appearances']*s[rate] if s.get(rate) is not None else None
  z['QA3']=min(z['IP']/5,s['appearances'],s['appearances']*s['qa3PerAppearance']) if s.get('qa3PerAppearance') is not None else None
 return (z,'catcher' if s.get('catcherSensitivity') else s['role'],s['appearances']),None
def flatten(a,lines,rr):
 for method,line in lines.items():
  for k,v in line.items():a[method+'_'+k]=v
  for k,v in ratios(line,rr).items():a[method+'_'+k]=v
  value=contribution(line,rr)
  if value:
   for k,v in value.items():a[method+'_'+k]=v
 return a
catalog=json.loads(gzip.decompress(base64.b64decode(re.search("const packed='([^']+)'",(ROOT/'trade-analyzer-beta/index.html').read_text())[1])))
roles=read(ROOT/'data/role-display-scenarios.json')['players'];starters=read(ROOT/'data/starter-display-scenarios.json')['players']
league={a['id']:a for a in csv.DictReader((P/'historical-coverage-retrain/League_1900_Comparison.csv').open())}
rows=[];unsupported=[];details=[]
for a in catalog['assets']:
 full,reason=current_scenario(a,roles,starters)
 if not full:unsupported.append({'id':a['id'],'name':a['name'],'kind':a['audit']['kind'],'reason':reason});continue
 b=a['audit']['projection'];rr=a['audit']['role'];key='PA' if rr=='H' else 'IP';line,group,n=full
 bm=league.get(a['id']);work=min(754 if rr=='H' else 251,float(bm['preserved_strong_benchmark'])) if bm else None
 lines={'production':b.copy(),'full_role':line}
 if work is not None:
  z=scale(b,rr,work)
  if rr!='H':
   # Keep opportunity assumptions separate from IP. Benchmark supplies expected
   # workload only; retained-role expected appearances = W / saved depth.
   fac=work/line[key]
   for k in ['SV','HLD','QA3']:z[k]=line[k]*fac if line.get(k) is not None else None
  lines['expected_benchmark']=z
 row={'id':a['id'],'name':a['name'],'role':rr,'cohort':group,'full_role_appearances':n,'expected_workload_ratio':work/line[key] if work is not None else None,'production_dynasty_display_CONTEXT_ONLY':a['values']['neutral']['display'],'production_first_year_expected_utility_CONTEXT_ONLY':a['annual_expected_utility'][0]}
 flatten(row,lines,rr)
 if rr!='H' and contribution(line,rr):
  fixed=scale(b,rr,line[key]);fixed.update({k:b.get(k) for k in ['SV','HLD','QA3']})
  if contribution(fixed,rr):
   row['full_role_workload_only_delta_surplus']=contribution(fixed,rr)['replacement_surplus']-contribution(b,rr)['replacement_surplus']
   row['full_role_opportunity_delta_surplus']=contribution(line,rr)['replacement_surplus']-contribution(fixed,rr)['replacement_surplus']
 for method in ['full_role','expected_benchmark']:
  for k in ['signed_category_contribution','replacement_surplus','utility']:
   if method+'_'+k in row:row[method+'_delta_'+k]=row[method+'_'+k]-row['production_'+k]
 rows.append(row);details.append({'id':a['id'],'name':a['name'],'role':rr,'cohort':group,'lines':lines})
ranked_universe=[a for a in rows if all(method+'_utility' in a for method in ['production','full_role','expected_benchmark'])]
for method in ['production','full_role','expected_benchmark']:
 for rank,a in enumerate(sorted(ranked_universe,key=lambda a:(-a[method+'_utility'],a['id'])),1):a[method+'_first_year_rank']=rank
for a in rows:
 for method in ['full_role','expected_benchmark']:
  if method+'_first_year_rank' in a:a[method+'_rank_gain']=a['production_first_year_rank']-a[method+'_first_year_rank']
csvwrite('Current_Comparison.csv',rows);write('Current_Lines.json.gz',details);csvwrite('Unsupported_Current.csv',unsupported)
names={'Aaron Judge','Matt Olson','Gavin Lux','Shea Langeliers','Paul Skenes','Zack Wheeler','Raisel Iglesias','Matt Brash'}
csvwrite('Representative_Examples.csv',[a for a in rows if a['name'] in names]);csvwrite('Largest_Changes.csv',sorted(rows,key=lambda a:-abs(a.get('full_role_delta_utility',0)))[:50])
# Historical replay: saved chronological predictions, never current sidecars.
components={(a['id'],a['anchor']):a['component'] for a in read(P/'historical-coverage-retrain/Repaired_Components.json.gz')}
basecases=read(P/'targeted-repair/Chronological_Cases.json.gz');rawfull={(a['mlbam_id'],a['anchor']):a for a in read(P/'full-workload-scenario/Chronological_Cases.json.gz')}
catcases={(a['mlbam_id'],a['anchor']):a for fam in ['H','P'] for a in read(P/f'roster-opportunity/Integrated_{fam}_Cases.json.gz')}
AN={(a['id'],a['year'],'H' if a['role']=='H' else 'P'):a for a in old.AN}
appear={(a['mlbamId'],a['year']):a for a in read(MODEL/'trade-preview-v23c-evidence-guard/Recovery_Appearances.json')['rows']}
hGP={}
for entry in read(P/'historical-coverage-retrain/Source_Coverage.json'):
 if entry['status']=='verified_complete':
  for s in read(P/'historical-coverage-retrain'/entry['source'])['stats'][0]['splits']:hGP[s['player']['id'],entry['year']]=float(s['stat']['gamesPlayed'])
hist=[];excluded=[];hdetails=[]
for a in basecases:
 ident,year=a['mlbam_id'],a['anchor'];key=ident,year;comp=components.get(key);rr=a['role'];exkey='PA' if rr=='H' else 'IP'
 if not comp or comp['role'] not in ['everyday','platoon','bench','starter','reliever']:
  excluded.append({'id':ident,'anchor':year,'reason':'unidentified/swingman full role'});continue
 obs=a['component']['opportunity_layer']['observations'];good=[o for o in obs[:3] if o['complete'] and o['exposure'] and o['GP'] and o['exposure']>0]
 if rr=='H':
  good=[o for o in obs[:3] if o['complete'] and o['exposure'] and hGP.get((ident,o['year']))]
 if not good:excluded.append({'id':ident,'anchor':year,'reason':'missing positive appearance evidence'});continue
 if comp['role']=='reliever' and good[0]['GS']!=0:
  excluded.append({'id':ident,'anchor':year,'reason':'incidental starts/missing GS'});continue
 F=comp['fitted']['full_role_workload'];slots=comp['fitted']['slots'];n=slots.get('GP',slots.get('GS',0)+slots.get('RA',0));opps={}
 if comp['role']=='reliever':
  # Same saved smoothed pure-relief depth estimator; eliminate incidental GS.
  obsrel=[(o,3-i) for i,o in enumerate(obs[:3]) if o['exposure'] and o['GP'] and o['GS']==0]
  rd=max(.25,min(3,(sum(o['exposure']*w for o,w in obsrel)+10)/(sum(o['GP']*w for o,w in obsrel)+10)))
  n=slots['RA'];F=n*rd;events=[]
  for i,o in enumerate(obs[:3]):
   if o['year']>year:raise AssertionError('future input')
   z=AN.get((ident,o['year'],'P'));cnt=appear.get((ident,o['year']))
   if not z or not cnt or not o['GP'] or o['GS']!=0 or cnt['GP']!=o['GP'] or cnt['GS']!=0:continue
   st=z['stat']
   if not all(k in st for k in ['SV','HLD']) or st['SV']+st['HLD']>o['GP']:continue
   events.append((o,st,3-i))
  den=sum(o['GP']*w for o,st,w in events)
  for k in ['SV','HLD']:opps[k]=n*sum(st[k]*w for o,st,w in events)/den if den else None
  q=a['component']['conditional']['1'];qn=q['GS']+q['RA'];opps['QA3']=min(F/5,n,n*q['QA3']/qn) if qn else None
 record={'mlbam_id':ident,'name':a['name'],'anchor':year,'target_season':a['target_season'],'role':rr,'cohort':comp['role'],'actual_workload':a['actual'],'production_workload':a['production'],'full_role_workload':F,'expected_benchmark_workload':min(754 if rr=='H' else 251,a['strong_prior']),'expected_workload_ratio':a['strong_prior']/F,'evaluation':'exposed chronological replay','category_supported':False}
 # Conditional retained-high-usage proxy eligibility for evaluation only.
 raw=rawfull.get(key,{});targetrole=raw.get('target_role');targetGP=hGP.get((ident,a['target_season'])) if rr=='H' else appear.get((ident,a['target_season']),{}).get('GP');targetGS=appear.get((ident,a['target_season']),{}).get('GS') if rr!='H' else None
 record['high_usage_proxy']=bool(targetGP and ((rr=='H' and targetGP>={'everyday':145,'platoon':100,'bench':70}.get(comp['role'],999) and (a['actual']/targetGP>=3.8 if comp['role']=='everyday' else 2.8<=a['actual']/targetGP<3.8 if comp['role']=='platoon' else a['actual']/targetGP<2.8)) or (comp['role']=='starter' and targetGS is not None and targetGS>=30 and targetGS/targetGP>=.8) or (comp['role']=='reliever' and targetGS==0 and targetGP>=60)))
 c=catcases.get(key)
 if c and a['target_season']<=2025 and c['baseline'].get(exkey,0)>0:
  b=c['baseline'];lines={'production':b.copy(),'actual':c['actual'].copy()}
  full=scale(b,rr,F)
  if rr!='H':
   if comp['role']=='reliever':full.update(opps)
   else:
    for k in ['SV','HLD']:full[k]=b.get(k,0) # no leverage inflation from IP
    joint=c['components'].get('joint_raw',{});qs=joint.get('QA3_per_start');qr=joint.get('QA3_per_relief')
    full['QA3']=min(F/5,slots.get('GS',0)+slots.get('RA',0),slots.get('GS',0)*qs+slots.get('RA',0)*qr) if qs is not None and qr is not None else None
  expected=scale(b,rr,record['expected_benchmark_workload'])
  if rr!='H':
   fac=record['expected_benchmark_workload']/F
   for k in ['SV','HLD','QA3']:expected[k]=full[k]*fac if full.get(k) is not None else None
  lines.update(full_role=full,expected_benchmark=expected,preserved_benchmark=c['strong_prior'])
  # Require matched complete source lines for category/utility scoring.
  if all(contribution(v,rr) is not None for v in lines.values()):
   record['category_supported']=True;flatten(record,lines,rr);hdetails.append({'id':ident,'anchor':year,'role':rr,'lines':lines})
 hist.append(record)
csvwrite('Historical_Player_Comparisons.csv',hist);csvwrite('Historical_Unsupported.csv',excluded);write('Historical_Lines.json.gz',hdetails)
metrics=[];aggregates=[]
for window in ['all_exposed','pre2026_exposed','2026_workload_only']:
 ys=[a for a in hist if window=='all_exposed' or (a['target_season']==2026)==(window=='2026_workload_only')]
 for group in ['all','H','P','everyday','platoon','bench','starter','reliever','catcher']:
  xs=[a for a in ys if group=='all' or group=='H' and a['role']=='H' or group=='P' and a['role']!='H' or a['cohort']==group]
  for mode in ['expected_all','conditional_high_usage_proxy']:
   zs=xs if mode=='expected_all' else [a for a in xs if a['high_usage_proxy']]
   for method in ['production','full_role','expected_benchmark']:
    if group!='all':metrics.append({'window':window,'group':group,'evaluation':mode,'method':method,'metric':'PA' if group in ['H','everyday','platoon','bench','catcher'] else 'IP',**metric([(a[method+'_workload'],a['actual_workload']) for a in zs])})
   cats=[a for a in zs if a['category_supported']]
   for method in ['production','full_role','expected_benchmark','preserved_benchmark']:
    for k in ['HR','R','RBI','SB','K','ER','SV','HLD','QA3','signed_category_contribution','replacement_surplus','utility']:
     pairs=[(a.get(method+'_'+k),a.get('actual_'+k)) for a in cats if method+'_'+k in a and 'actual_'+k in a]
     if pairs:metrics.append({'window':window,'group':group,'evaluation':mode,'method':method,'metric':k,**metric(pairs)})
   if mode=='expected_all':
    for family in ['H','P']:
     selected=[d for d in hdetails if any(a['mlbam_id']==d['id'] and a['anchor']==d['anchor'] for a in cats) and (d['role']=='H')==(family=='H')]
     for method in ['production','full_role','expected_benchmark','preserved_benchmark','actual']:
      sums=defaultdict(float)
      for d in selected:
       for k,v in d['lines'][method].items():
        if v is not None:sums[k]+=v
      aggregates.append({'window':window,'group':group,'family':family,'method':method,'n':len(selected),**ratios(sums,'H' if family=='H' else 'SP')})
csvwrite('Historical_Metrics.csv',metrics);csvwrite('Aggregate_Ratios.csv',aggregates)
gates=[]
for group in ['H','P','everyday','platoon','bench','starter','reliever']:
 pair={m['method']:m for m in metrics if m['window']=='all_exposed' and m['group']==group and m['evaluation']=='expected_all' and m['metric'] in ['PA','IP']}
 if not pair or not pair['production']['n']:continue
 tolerance=1 if group in ['H','P'] else 1.05
 gates.append({'group':group,'n':pair['production']['n'],'MAE_pass':pair['expected_benchmark']['MAE']<=pair['production']['MAE']*tolerance,'RMSE_pass':pair['expected_benchmark']['RMSE']<=pair['production']['RMSE']*tolerance})
write('Release_Gates.json',{'gates':gates,'all_pass':all(g['MAE_pass'] and g['RMSE_pass'] for g in gates),'independent_validation':False,'production_adoption':False})
write('Frozen_Category_Parameters.json',{'refs':old.refs,'dens':{k:v.tolist() for k,v in old.dens.items()},'floor':r.floor,'reference':r.REFERENCE,'utility_threshold':r.T,'utility_curve':.1,'display_multiplier_CONTEXT_ONLY':r.DISPLAY,'QA3':'5 IP <=2 ER OR 6 IP <=3 ER','weekly_gate':'35 IP team eligibility not modeled by annual asset replay'})
write('Coverage.json',{'catalog_assets':len(catalog['assets']),'current_supported':len(rows),'current_cohorts':dict(Counter(a['cohort'] for a in rows)),'current_complete_contribution':sum('full_role_utility' in a for a in rows),'current_preserved':len(unsupported),'historical_saved_cases':len(basecases),'historical_supported_workload':len(hist),'historical_cohorts':dict(Counter(a['cohort'] for a in hist)),'historical_complete_category':len(hdetails),'historical_catcher':'Unavailable: no dated catcher/DH positional history; current eligibility never used to classify past roles','category_target2026':'Excluded: workload GP/PA/IP verified but matching complete category census not part of this replay','expected_method':'reexpression of preserved benchmark; no new fit','independent_holdout':False})
sources=[ROOT/'trade-analyzer-beta/index.html',ROOT/'data/role-display-scenarios.json',ROOT/'data/starter-display-scenarios.json',OUT/'Protocol_Freeze.json',P/'historical-coverage-retrain/Repaired_Components.json.gz',P/'targeted-repair/Chronological_Cases.json.gz',P/'full-workload-scenario/Chronological_Cases.json.gz',P/'roster-opportunity/Integrated_H_Cases.json.gz',P/'roster-opportunity/Integrated_P_Cases.json.gz',P/'historical-coverage-retrain/League_1900_Comparison.csv',MODEL/'trade-preview-v22/model/revised.py',MODEL/'trade-preview-v22/model/prototype.py',MODEL/'trade-preview-v23/model_v23.py',MODEL/'trade-preview-v23c-evidence-guard/model_asset_fit.py']
write('Reproduction_Manifest.json',{'protocol_commit':'1984a3c','production_base':'ce326ae24cd0e6d016b1ff0fefb23ffd54903ba9','research_checkpoint':'5e00a76d83f1d0427add2132ec75beef3da6adf4','files':{str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in sources},'python':sys.version,'arguments':[str(MODEL),str(P)],'no_new_fit':True,'production_tree_changed_files':subprocess.check_output(['git','diff','--name-only','ce326ae24cd0e6d016b1ff0fefb23ffd54903ba9','--',':(exclude)research/full-role-valuation-20261011'],cwd=ROOT,text=True).splitlines()})
print(json.dumps(read(OUT/'Coverage.json')));print(json.dumps(read(OUT/'Release_Gates.json')))
