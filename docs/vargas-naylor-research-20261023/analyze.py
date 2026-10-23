"""Reproducible source reconciliation, category sensitivity and chronological rate test.
Python standard library only. Run fetch_sources.py first. Never edits website data.
"""
from pathlib import Path
import json,re,html,gzip,base64,csv,math,statistics,random,collections,hashlib
P=Path(__file__).resolve().parent;ROOT=P.parents[1];I=P/'inputs'
read=lambda p:json.loads(Path(p).read_text())
write=lambda name,obj:(P/name).write_text(json.dumps(obj,indent=2,allow_nan=False)+'\n')
clean=lambda s:' '.join(html.unescape(re.sub('<[^>]+>',' ',s)).split())
IDS=[678246,647304];NAMES={678246:'Miguel Vargas',647304:'Josh Naylor'}
checks=[]
def check(name,ok,detail=None):
 checks.append({'name':name,'passed':bool(ok),'detail':detail})
 if not ok:raise AssertionError((name,detail))
def tables(mid):
 s=(I/f'savant-{mid}.html').read_text();s=re.sub(r'<!--.*?-->','',s,flags=re.S);out={}
 for table in re.findall(r'<table\b[^>]*>.*?</table>',s,re.S):
  headers=[clean(x) for x in re.findall(r'<th\b[^>]*>(.*?)</th>',table,re.S)]
  kind='statcast' if 'Barrels' in headers and 'xSLG' in headers else 'discipline' if 'Chase %' in headers and 'Zone Contact %' in headers else None
  if not kind:continue
  rows=[]
  for row in re.findall(r'<tr\b[^>]*>(.*?)</tr>',table,re.S):
   cells=[clean(x) for x in re.findall(r'<td\b[^>]*>(.*?)</td>',row,re.S)]
   if not cells or not re.fullmatch(r'20\d\d',cells[0]):continue
   check(f'{mid} {kind} {cells[0]} column count',len(cells)==len(headers))
   r=dict(zip(headers,cells));rows.append({k:(float(v.replace(',','')) if re.fullmatch(r'[\d,.]+',v) else v) for k,v in r.items()})
  out[kind]=rows
 return out
profiles={str(mid):tables(mid) for mid in IDS};kodo={str(mid):read(I/f'kodo-{mid}.json') for mid in IDS}
for mid in IDS:
 k=kodo[str(mid)];s=next(r for r in profiles[str(mid)]['statcast'] if r['Season']==2026)
 check(f'{mid} Kodo identity and season',k['player']['player_id']==mid and k['batting_stats']['season']==2026 and k['batting_stats']['level']=='MLB')
 pairs={'xba':'xBA','xslg':'xSLG','xwoba':'xwOBA','ev_avg':'Exit Velocity','barrel_pct':'Barrel %','hard_hit_pct':'HardHit%','k_pct':'K%','bb_pct':'BB%'}
 for key,col in pairs.items():check(f'{mid} Savant/Kodo {key}',abs(k['batting_stats'][key]*(100 if key.endswith('_pct') else 1)-s[col])<.051)
 profiles[str(mid)]['name']=NAMES[mid];profiles[str(mid)]['kodo_date']=k['batting_stats']['stat_date'];profiles[str(mid)]['monthly_swing_path']=k.get('swing_path',[])

EXPECTED={};missing=[]
for year in range(2015,2027):
 file=I/f'expected-{year}.csv'
 if not file.exists():missing.append(year);continue
 with file.open(encoding='utf-8-sig') as f:
  for r in csv.DictReader(f):
   if not r.get('est_ba') or not r.get('est_slg'):continue
   mid=int(r['player_id']);key=(mid,year)
   check(f'expected unique {mid}/{year}',key not in EXPECTED) if key in EXPECTED else None
   assert int(r['year'])==year
   EXPECTED[key]={k:(float(r[k]) if r[k] not in ['',None] else None) for k in ['pa','bip','ba','est_ba','slg','est_slg','woba','est_woba']}
check('all expected-stat seasons frozen',not missing,missing)
for mid in IDS:
 row=EXPECTED[mid,2026];k=kodo[str(mid)]['batting_stats']
 check(f'{mid} leaderboard/profile quality agrees',abs(row['est_ba']-k['xba'])<.0011 and abs(row['est_slg']-k['xslg'])<.0011)

H={}
components={'AB':'atBats','PA':'plateAppearances','H':'hits','HR':'homeRuns','R':'runs','RBI':'rbi','SB':'stolenBases','BB':'baseOnBalls','HBP':'hitByPitch','SF':'sacFlies','TB':'totalBases'}
for year in [2010,2011,2012,*range(2015,2027)]:
 blocks=read(I/f'mlb-hitting-{year}.json')['stats'];seen=set()
 for block in blocks:
  check(f'{year} complete official hitter response',len(block['splits'])==block['totalSplits'])
  for row in block['splits']:
   mid=row['player']['id'];check(f'{year} unique official MLBAM {mid}',mid not in seen) if mid in seen else None;seen.add(mid)
   H[mid,year]={k:float(row['stat'].get(v,0)) for k,v in components.items()}
cal=[s for (mid,year),s in H.items() if year<=2012 and s.get('AB',0)>=250]
fields=['AB','PA','H','HR','R','RBI','SB','BB','HBP','SF','TB']
prior={k:sum(s.get(k,0) for s in cal)/sum(s['PA'] for s in cal) for k in fields}
def forecast(mid,latest):
 rows=[(H[mid,year],w) for year,w in zip(range(latest-3,latest+1),[.1,.2,.3,.4]) if (mid,year) in H and H[mid,year].get('PA',0)>0]
 if not rows:return None
 mass=sum(w for s,w in rows);recent=sum(s['PA']*w/mass for s,w in rows)
 rates={k:(sum(s.get(k,0)*w/mass for s,w in rows)+100*prior[k])/(recent+100) for k in fields}
 return {'AVG':rates['H']/rates['AB'],'SLG':rates['TB']/rates['AB'],'rates':rates}
weights=[0,.1,.25,.5,.75,1.];cases=[];exclusions=collections.Counter()
for (mid,latest),e in sorted(EXPECTED.items()):
 target=latest+1
 if mid in IDS or target<2019 or target>2026 or target==2020 or e['pa']<150:continue
 truth=EXPECTED.get((mid,target));s=H.get((mid,latest));f=forecast(mid,latest)
 if not truth or truth['pa']<250:exclusions['next-season missing or below 250 PA']+=1;continue
 if not s or not f:exclusions['official components/forecast unavailable']+=1;continue
 # CSV is rounded. Reject a stale or mismatched historical join before it can
 # influence the forward test. No target-year components enter the forecast.
 if abs(s['PA']-e['pa'])>1.1:exclusions['Savant/official prior-season PA mismatch']+=1;continue
 if any(abs(s[k]/s['AB']-e[x])>.002 for k,x in [('H','ba'),('TB','slg')]):exclusions['Savant/official prior-season rate mismatch']+=1;continue
 old=EXPECTED.get((mid,latest-1));group='other'
 if old and old['pa']>=200 and e['pa']>=200:
  change=e['est_slg']-old['est_slg'];group='breakout' if change>=.05-1e-12 else 'decline' if change<=-.05+1e-12 else 'other'
 predicted={}
 for alpha in weights:
  w=alpha*e['pa']/(e['pa']+100)
  predicted[str(alpha)]={'AVG':(1-w)*f['AVG']+w*e['est_ba'],'SLG':(1-w)*f['SLG']+w*e['est_slg']}
 cases.append({'id':mid,'latest':latest,'target':target,'targetPA':truth['pa'],'group':group,'actual':{'AVG':truth['ba'],'SLG':truth['slg']},'predicted':predicted})
check('chronological observations',all(c['latest']<c['target'] for c in cases))
check('named cases excluded from training/testing',all(c['id'] not in IDS for c in cases))
check('broad conditional rate sample',len(cases)>1000,len(cases))
def metrics(rows,alpha):
 if not rows:return {'n':0}
 out={'n':len(rows),'players':len(set(r['id'] for r in rows))}
 for metric in ['AVG','SLG']:
  errors=[r['predicted'][str(alpha)][metric]-r['actual'][metric] for r in rows]
  out[metric]={'MAE':statistics.mean(map(abs,errors)),'RMSE':math.sqrt(statistics.mean(x*x for x in errors)),'bias':statistics.mean(errors),'PA_weighted_MAE':sum(abs(e)*r['targetPA'] for e,r in zip(errors,rows))/sum(r['targetPA'] for r in rows)}
 return out
train=[c for c in cases if c['target']<=2023];test=[c for c in cases if c['target']>=2024];base=metrics(train,0)
train_scores={str(alpha):sum(metrics(train,alpha)[m]['MAE']/base[m]['MAE'] for m in ['AVG','SLG'])/2 for alpha in weights}
chosen=min(weights,key=lambda w:train_scores[str(w)])
def bootstrap(rows,alpha,metric):
 groups=collections.defaultdict(list)
 for c in rows:groups[c['id']].append(abs(c['predicted'][str(alpha)][metric]-c['actual'][metric])-abs(c['predicted']['0'][metric]-c['actual'][metric]))
 groups=list(groups.values());rng=random.Random(20261023);draws=[]
 for _ in range(1000):
  selected=rng.choices(groups,k=len(groups));draws.append(sum(sum(g) for g in selected)/sum(len(g) for g in selected))
 draws.sort();return {'difference_MAE_candidate_minus_baseline':statistics.mean([x for g in groups for x in g]),'player_cluster_bootstrap_95pct':[draws[24],draws[974]],'draws':1000}
backtest={'protocol':'Protocol.md','scope':'Pre-aging talent-rate estimator only; conditional on next-season >=250 PA, excluding target 2020. Not an end-to-end forecast or trade valuation backtest.','weights':weights,'training_targets':'2019–2023 excluding 2020','test_targets':'2024–2026','training_n':len(train),'test_n':len(test),'join_exclusions':dict(exclusions),'training_relative_MAE_scores':train_scores,'training_selected_weight':chosen,'all_training':{str(w):metrics(train,w) for w in weights},'all_test':{str(w):metrics(test,w) for w in weights},'by_test_year':{str(y):{str(w):metrics([c for c in test if c['target']==y],w) for w in weights} for y in [2024,2025,2026]},'groups':{g:{str(w):metrics([c for c in test if c['group']==g],w) for w in weights} for g in ['breakout','decline','other']},'selected_paired_errors':{m:bootstrap(test,chosen,m) for m in ['AVG','SLG']}}

assets={a['career_profile']['identifiers']['mlbamId']:a for a in read(I/'baseline-players.json')}
model=read(I/'model-scale.json');ref=model['category_references'];disp=model['category_dispersion']['H'];floor=model['replacement_floor']['H'];reference=model['reference_workload']['H'];scenarios=[]
def coherent(s):
 z=s.copy();z['H']=min(z['AB'],max(0,z['H']));z['HR']=min(z['HR'],z['H']);z['TB']=min(4*z['H'],max(z['H']+3*z['HR'],z['TB']));return z
def ratesline(s,pa):return {k:v*pa/s['PA'] for k,v in s.items()}
def stats(s):
 avg=s['H']/s['AB'];obp=(s['H']+s['BB']+s['HBP'])/(s['AB']+s['BB']+s['HBP']+s['SF']);slg=s['TB']/s['AB'];ops=obp+slg
 vector=[s['HR'],s['R'],s['RBI'],s['SB'],s['H']-ref['AVG']*s['AB'],(ops-ref['OPS'])*s['AB']];contrib={k:v/d for k,v,d in zip(['HR','R','RBI','SB','AVG','OPS'],vector,disp)}
 return {'AVG':avg,'OBP':obp,'SLG':slg,'OPS':ops,'category_components':contrib,'surplus':sum(contrib.values())-floor*s['PA']/reference,'counts':s}
for mid in IDS:
 a=assets[mid];s=a['audit']['projection'];k=kodo[str(mid)]['batting_stats']
 # Use the already-frozen official component row for HBP/SF/TB, avoiding rounded
 # slash-line reconstruction or a guessed component count.
 official=H[mid,2026]
 latest={key:official[key] for key in fields}
 check(f'{mid} current counts reconcile',latest['PA']==k['pa'] and latest['HR']==k['hr'] and latest['SB']==k['sb'])
 quality=latest.copy();quality['H']=k['xba']*quality['AB'];quality['TB']=k['xslg']*quality['AB'];quality=coherent(quality)
 for label,z in [('inherited_forecast',s),('2026_observed_rate_sensitivity',latest),('2026_expected_quality_sensitivity',quality)]:
  for pa_label,pa in [('equal_600_PA',600),('inherited_forecast_PA',s['PA'])]:scenarios.append({'id':mid,'name':NAMES[mid],'scenario':label,'exposure':pa_label,**stats(ratesline(z,pa))})
 for alpha in weights:
  z=s.copy();w=alpha*k['pa']/(k['pa']+100);z['H']=(1-w)*s['H']+w*k['xba']*s['AB'];z['TB']=(1-w)*s['TB']+w*k['xslg']*s['AB'];z=coherent(z)
  scenarios.append({'id':mid,'name':NAMES[mid],'scenario':'quality_weight_sensitivity','weight':alpha,'exposure':'inherited_forecast_PA',**stats(z)})
 normalized=stats(ratesline(quality,600));profiles[str(mid)]['next_season_sensitivity']=normalized
 profiles[str(mid)]['inherited_forecast']=stats(s)
 # Monthly bat-tracking samples are observations, not an injury diagnosis.
 months={r['month']:r for r in kodo[str(mid)].get('swing_path',[]) if r['season']==2026}
 profiles[str(mid)]['monthly_bat_summary']={str(m):{'swings':r.get('competitive_swings'),'bat_speed':r.get('avg_bat_speed'),'attack_angle':r.get('attack_angle')} for m,r in months.items()}

write('Profiles.json',profiles);write('Backtest.json',backtest);write('Category_Scenarios.json',scenarios);write('Backtest_Cases.json',cases)
write('Checks.json',{'checks':checks,'passed':len(checks),'failed':0,'blocked':['No 2027 actual outcomes; latest-season counterfactuals are sensitivity only.','No injury-conditioned recovery probabilities or dated historical wrist-injury cohort.','Pre-aging rate test excludes full aging/availability/category-win valuation.','Survivor sample requires next-season playing time; does not evaluate attrition.','No season-long monthly xBA/xSLG splits from current frozen player detail endpoints.'],'frozen_inputs':read(P/'Source_Manifest.json')})
print(json.dumps({'checks':len(checks),'training_selected_weight':chosen,'training_n':len(train),'test_n':len(test),'holdout_baseline':backtest['all_test']['0'],'holdout_selected':backtest['all_test'][str(chosen)],'paired':backtest['selected_paired_errors'],'groups':{g:{'baseline':v['0'],'selected':v[str(chosen)]} for g,v in backtest['groups'].items()},'equal_opportunity_cases':[s for s in scenarios if s['exposure']=='equal_600_PA']},indent=2))
