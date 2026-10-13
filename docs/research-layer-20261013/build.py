"""Offline DD research candidate. Never changes production or statistical forecasts."""
import json,re,gzip,base64,copy,math,csv,hashlib,collections,datetime
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[2];D=Path(__file__).resolve().parent;I=D/'inputs'
ASOF=datetime.date(2026,10,13)
def read(p):return json.loads(p.read_text())
def write(n,x):(D/n).write_text(json.dumps(x,indent=2,ensure_ascii=False))
def norm(s):
 import unicodedata
 return re.sub('[^a-z0-9]','',unicodedata.normalize('NFKD',str(s)).encode('ascii','ignore').decode().lower())
def unpack(html):return json.loads(gzip.decompress(base64.b64decode(re.search("const packed='([^']+)'",html)[1])))
html=(ROOT/'trade-analyzer-beta/index.html').read_text();current=unpack(html);candidate=copy.deepcopy(current)
E=read(ROOT/'docs/value-audit-20261012/inputs/model-evidence.json');C=read(ROOT/'docs/value-audit-20261012/Curves.json');curve=C['overall_curve'];ranks=np.array([x['rank'] for x in curve]);prices=np.array([x['value'] for x in curve]);elasticity=-float(np.polyfit(np.log(ranks),np.log(prices),1)[0]);assert elasticity>0
refs=E['category_references'];disp=E['category_dispersion'];reference=E['reference_workload']
def value(r):return float(np.interp(r,ranks,prices))
def score(s,role):
 if role=='H':
  ab=s['AB'];den=ab+s['BB']+s['HBP']+s['SF'];ops=(s['H']+s['BB']+s['HBP'])/den+s['TB']/ab
  v=[s[k] for k in ['HR','R','RBI','SB']]+[s['H']-refs['AVG']*ab,(ops-refs['OPS'])*ab]
 else:v=[-s['ER'],s['K'],3*s['SV']+2*s['HLD'],s['QA3'],s['K']-refs['KBB']*s['BB'],refs['WHIP']*s['IP']-s['H']-s['BB']]
 return float(np.sum(np.array(v)/disp['H' if role=='H' else 'P']))
def coherent(s):
 z=s.copy();parts=z['AB']+z['BB']+z['HBP']+z['SF'];f=min(1,z['PA']/parts)
 for k in z:
  if k!='PA':z[k]*=f
 z['H']=min(z['AB'],z['H']);z['HR']=min(z['HR'],z['H']);z['TB']=min(4*z['H'],max(z['H']+3*z['HR'],z['TB']));return z
fg={}
for system in ['steamer','zips']:
 for role in ['H','P']:
  rows=read(I/f'fangraphs-{system}-{"bat" if role=="H" else "pit"}.json');idx=collections.defaultdict(list)
  for row in rows:
   try:idx[int(row['xMLBAMID'])].append(row)
   except (TypeError,ValueError):pass
  fg[system,role]=idx
# Normalize retrieved facts; raw provider data never enters the web publication.
ledger={};records=[];normalized={};rowsById={}
for a in candidate['assets']:
 p=a.get('ranking_policy');role=a['audit'].get('role');identifier=a.get('career_profile',{}).get('identifiers',{});mid=identifier.get('mlbamId')
 if not p:continue
 rec={'id':a['id'],'name':a['name'],'role':role,'live_value':a['values']['neutral']['display'],'DD_rank':p['source_rank'],'DD_scope':p['source_scope'],'status':'Retained current prior: no supported MLB rate evidence','sources':[],'warnings':[],'candidate_value':a['values']['neutral']['display']};records.append(rec);rowsById[a['id']]=rec
 if a['audit']['kind']!='MLB' or role not in ['H','SP','RP'] or not mid or p['source_scope']!='overall dynasty':continue
 own=a['audit'].get('projection',{});exposure='PA' if role=='H' else 'IP'
 if not own.get(exposure):rec['warnings'].append('Missing own positive forecast exposure');continue
 # Full-role reference normalizes talent only. Expected opportunity stays independent.
 rate={k:float(v)*reference[role]/own[exposure] for k,v in own.items()};rates=[rate];sourceNames=['Pipeline rates'];rec['sources'].append({'source':'Pipeline','basis':'Frozen active projected rates; reference exposure used only for talent comparison','weight':.65})
 independent=[];quality=[]
 for system in ['steamer','zips']:
  matches=fg[system,'H' if role=='H' else 'P'].get(int(mid),[])
  if len(matches)!=1:rec['warnings'].append(system+': missing or duplicate stable ID');continue
  f=matches[0];ex=f.get(exposure)
  if norm(f.get('PlayerName'))!=norm(a['name']):rec['warnings'].append(system+': name conflict at stable ID');continue
  if not isinstance(ex,(int,float)) or ex<(50 if role=='H' else 10):rec['warnings'].append(system+': projected exposure too small for rate use');continue
  if role!='H':
   g=f.get('G',0);gs=f.get('GS',0);projectedRole='SP' if g and gs/g>=.5 else 'RP'
   if projectedRole!=role:rec['warnings'].append(system+': role conflict; numeric use blocked');continue
  fields=['AB','PA','H','HR','R','RBI','SB','BB','HBP','SF'] if role=='H' else ['IP','H','BB','ER']
  if any(not isinstance(f.get(k),(int,float)) for k in fields):rec['warnings'].append(system+': missing required components');continue
  z=rate.copy()
  for k in fields:z[k]=f[k]/ex*reference[role]
  if role=='H':z['TB']=(f.get('1B',0)+2*f.get('2B',0)+3*f.get('3B',0)+4*f['HR'])/ex*reference[role];z=coherent(z)
  else:
   z['K']=f['SO']/ex*reference[role]
   # Provider QS never substitutes for QA3. Retain own actual-definition QA3 rate.
   z['QA3']=rate['QA3'];z['SV']=rate['SV'];z['HLD']=rate['HLD']
  independent.append(z);quality.append(system);rec['sources'].append({'source':'FanGraphs '+system,'url':f'https://www.fangraphs.com/api/projections?type={system}&stats={"bat" if role=="H" else "pit"}&pos=all&team=0&players=0&lg=all','MLBAM':mid,'retrieved':'2026-10-13','publication_date':None,'projection_horizon':'Row lacks explicit season; used as weak rate benchmark, never as 2027 workload','family':'external projection ensemble','numerical_use':'rate benchmark only; freshness confidence halved'})
  normalized.setdefault(a['id'],{})[system]={k:f.get(k) for k in ['PlayerName','xMLBAMID','playerid','Team','PA','IP','G','GS','AB','H','BB','SO','ER','HR','R','RBI','SB','HBP','SF','1B','2B','3B','FIP','ERA','WHIP']}
 kodo=None;kfile=I/f'kodo-player-{mid}.json'
 if kfile.exists():
  kd=read(kfile);player=kd.get('player',{});ks=kd.get('batting_stats' if role=='H' else 'pitching_stats') or {};date=ks.get('stat_date');kid=player.get('player_id',player.get('id'));kname=player.get('full_name',player.get('name'))
  rec['sources'].append({'source':'Kodo Analytics','url':f'https://kodoanalytics.com/api/v1/players/{mid}','retrieved':'2026-10-13','stat_date':date,'family':'Statcast expected quality; not independent bonuses for xStats, barrels and whiff'})
  latest=[z for z in a.get('career_profile',{}).get('seasons',[]) if z['year']==2026 and z['role']==role]
  ownObserved=latest[0]['stat'].get(exposure) if len(latest)==1 else None
  observed=ks.get('pa' if role=='H' else 'ip')
  if role!='H' and observed is not None:
   whole=int(float(observed));frac=round((float(observed)-whole)*10)
   observed=whole+frac/3 if frac in [0,1,2] else None
  valid=kid==mid and norm(kname)==norm(a['name']) and ks.get('season')==2026 and ks.get('level')=='MLB' and date and datetime.date.fromisoformat(date)<=ASOF and (ASOF-datetime.date.fromisoformat(date)).days<=45 and ownObserved is not None and observed is not None and abs(ownObserved-observed)<1.1
  normalized.setdefault(a['id'],{})['kodo']={'player_id':kid,'name':kname,'stat_date':date,'season':ks.get('season'),'level':ks.get('level'),'stats':ks,'context':kd.get('stats_context'),'on_il':kd.get('on_il'),'valid':bool(valid)}
  if valid:
   z=rate.copy()
   if role=='H' and isinstance(ks.get('xba'),(int,float)) and isinstance(ks.get('xslg'),(int,float)):
    z['H']=ks['xba']*z['AB'];z['TB']=ks['xslg']*z['AB'];z=coherent(z);kodo=z
   elif role!='H' and isinstance(ks.get('xera'),(int,float)):
    z['ER']=ks['xera']*z['IP']/9;kodo=z
  else:rec['warnings'].append('Kodo identity/date/season/exposure validation failed; contextual only')
  rec['warnings'].append('Kodo current injury/depth/L14/remaining-season volume contextual only: cannot establish what was unknown to DD or supported 2027 availability')
 if not independent and kodo is None:continue
 # Missing providers return weight to Pipeline; the same provider family is counted once.
 blend=rate.copy()
 for key in rate:
  ext=float(np.mean([z[key] for z in independent])) if independent else rate[key]
  blend[key]=.65*rate[key]+.25*ext+.10*(kodo[key] if kodo is not None else rate[key])
 if role=='H':blend=coherent(blend)
 assert all(math.isfinite(x) for x in blend.values())
 reliability=float(a['audit'].get('MLB_evidence_reliability',.0));disagreement=abs(score(independent[0],role)-score(independent[1],role)) if len(independent)==2 else 0
 freshness=.5 if independent else 1.;confidence=reliability*(len(independent)/2 if independent else .5)*freshness/(1+disagreement)
 hist=a.get('career_profile',{}).get('seasons',[]);positiveYears=len({z['year'] for z in hist if z['role']==role and z['stat'].get(exposure,0)>0})
 if positiveYears==1:confidence*=float(a['audit']['projection_audit'].get('effective_exposure',0))/(float(a['audit']['projection_audit'].get('effective_exposure',0))+(600 if role=='H' else 170))
 rec.update(status='Bounded DD-anchored research candidate',DD_baseline=value(p['source_rank']),own_talent_score=score(rate,role),research_talent_score=score(blend,role),confidence=confidence,model_weight=.25*confidence,reference_exposure=reference[role],expected_exposure=own[exposure],projected_rate_line=blend,projection_systems=quality,kodo_numeric=kodo is not None,positive_MLB_years=positiveYears)
 ledger[a['id']]=rec
# Rank talent within role only. Map ordinal position onto that role's DD global ranks;
# this preserves hitter/SP/RP acquisition ordering and does not equalize their scale.
for role in ['H','SP','RP']:
 members=[r for r in ledger.values() if r['role']==role];dd=sorted(r['DD_rank'] for r in members);ordered=sorted(members,key=lambda r:(-r['research_talent_score'],r['DD_rank']))
 for pos,rec in enumerate(ordered):
  ties=[j for j,r in enumerate(ordered) if abs(r['research_talent_score']-rec['research_talent_score'])<1e-12];rank=float(np.interp(float(np.mean(ties)),np.arange(len(dd)),dd));w=rec['model_weight'];logmove=max(math.log(.9),min(math.log(1.1),w*math.log(rank/rec['DD_rank'])))
  # Research works in value space with a shared elasticity, so pooled flat sections
  # cannot erase a supported departure. The cap is inherited +/-10% rank-equivalent.
  new=rec['DD_baseline']*math.exp(-elasticity*logmove)
  rec.update(research_implied_rank=rank,effective_rank=rec['DD_rank']*math.exp(logmove),candidate_value=new,research_adjustment=new-rec['DD_baseline'],delta=new-rec['live_value'],global_rank_elasticity=elasticity,source_weight=1-w)
by={a['id']:a for a in candidate['assets']}
for i,rec in ledger.items():
 a=by[i];v=rec['candidate_value'];a['values']={m:{'display':v,'underlying':None,'meaning':'Offline DD baseline plus confidence-shrunk research adjustment; policy sensitivity, not market-calibrated price'} for m in a['values']};a['range']={side:{m:v*(.85 if side=='low' else 1.15) for m in a['values']} for side in ['low','high']};a['research_layer']={k:v for k,v in rec.items() if k!='projected_rate_line'};a['ranking_policy'].update(source_weight=rec['source_weight'],model_weight=rec['model_weight'],effective_overall_rank=rec['effective_rank'],meaning='Offline DD research candidate; forecasts unchanged')
 if 'valuation_quantities' in a:a['valuation_quantities']['ranking_led_trade_value']=v
for t in candidate['trades']:
 t['neutral_transfer_packages']=[sum(by[i]['values']['neutral']['display'] for i in ids) for ids in t['identities']]
 for m in t['modes'].values():m['neutral_transfer_change']=t['neutral_transfer_packages'][1]-t['neutral_transfer_packages'][0]
write('Comparison.json',records);write('Evidence.json',normalized)
summary={'baseline_commit':'26a1d75','as_of':str(ASOF),'listed':len(records),'numerically_adjusted':len(ledger),'sources':{'two_FanGraphs_systems':sum(len(r['projection_systems'])==2 for r in ledger.values()),'Kodo_numeric':sum(r['kodo_numeric'] for r in ledger.values())},'role_counts':dict(collections.Counter(r['role'] for r in ledger.values())),'elasticity':elasticity,'limits':'Candidate weight ceiling 25%; +/-10% rank-equivalent cap inherited; ordinal/value spacing is disclosed policy, not empirically validated market pricing. Projections without explicit publication date have confidence halved. Context-only health is not a numerical penalty. No external QS, no 2027 zero workloads, no duplicated injury deductions.','validation':'Implementation invariants and sensitivity; no completed chronological out-of-sample market validation of the added layer.','unchanged_production_sha256':hashlib.sha256(html.encode()).hexdigest(),'examples':[{k:r.get(k) for k in ['name','DD_rank','live_value','DD_baseline','candidate_value','delta','confidence','model_weight','research_implied_rank','kodo_numeric']} for r in records if r['name'] in ['Kyle Bradish','Carlos Rodon','Cole Carrigg','Vinnie Pasquantino','Jake Bauers','Jose Soriano','Mason Montgomery','Josue De Paula','Kaelen Culpepper']]}
write('Summary.json',summary)
with (D/'Comparison.csv').open('w',newline='') as f:
 fields=['id','name','role','DD_rank','DD_scope','live_value','DD_baseline','candidate_value','delta','confidence','model_weight','status'];w=csv.DictWriter(f,fieldnames=fields,extrasaction='ignore');w.writeheader();w.writerows(records)
packed=base64.b64encode(gzip.compress(json.dumps(candidate,separators=(',',':')).encode(),mtime=0)).decode();preview=re.sub("const packed='[^']+'","const packed='"+packed+"'",html)
preview=preview.replace('<head>','<head><base href="../../trade-analyzer-beta/">',1)
preview=preview.replace('<body>','<body><div style="padding:12px;background:#fff1bd;color:#332600">RESEARCH PREVIEW — DD baseline plus bounded projection and xStats adjustments. Not deployed or market-validated.</div>',1)
preview=preview.replace("['Source scope',a.ranking_policy.source_scope]","['Source scope',a.ranking_policy.source_scope],...(a.research_layer?[['DD baseline value',fmt(a.research_layer.DD_baseline)],['Research adjustment',fmt(a.research_layer.research_adjustment)],['Research confidence',fmt(100*a.research_layer.confidence)+'%'],['Research sources',a.research_layer.projection_systems.join(', ')+(a.research_layer.kodo_numeric?' + Kodo expected quality':'')]]:[])")
preview=preview.replace('<title>','<title>Research preview — ',1);(D/'Calculator.html').write_text(preview)
print(json.dumps(summary,indent=2))
