"""Past-only debut-conditioned contribution paths. No production writes."""
import sys,json,gzip,csv,collections,functools,datetime,math
from pathlib import Path
import numpy as np
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
D=Path(__file__).resolve().parent;MODEL=Path(sys.argv[1]).resolve()
sys.path.insert(0,str(MODEL/'trade-preview-v23c-evidence-guard'));import model_asset_fit as m
r=m.r;old=m.old
read=lambda p:json.loads(p.read_text())
scr=read(MODEL/'trade-preview-v23b-stabilized/Debut_Scrutiny.json')['records'];saved=read(MODEL/'trade-preview-v23b-stabilized/Prior_Validation.json')['records']
rankinfo={(z['id'],z['origin']):z for z in saved}
# Expanded scrutiny includes additional very short debuts omitted from the old >=250PA sample.
for z in scr:
 key=z['id'],z['origin']
 if key in rankinfo:continue
 matches=[a for a in old.CO if a['mlbamId']==z['id'] and a['year']==z['prior_year'] and not a['pitcher']]
 if matches:
  a=matches[0];age=(datetime.date(a['year'],2,12)-datetime.date.fromisoformat(a['birthDate'])).days/365.2425
  rankinfo[key]={'prior_rank':a['rank'],'prior_age':age,'prior_year':a['year']}
TEST_IDS={z['id'] for z in scr}
H={(a['id'],a['year']):a for a in old.AN if a['role']=='H'}
FIRST={}
for ident,year in H:
 if H[ident,year]['stat'].get('PA',0)>0:FIRST[ident]=min(FIRST.get(ident,9999),year)

def ranking_age(a):return (datetime.date(a['year'],2,12)-datetime.date.fromisoformat(a['birthDate'])).days/365.2425
@functools.lru_cache(None)
def training(year):
 rows=[a for a in old.CO if a['year']+5<=year and a['mlbamId'] not in TEST_IDS]
 if len({a['five_year_label'] for a in rows})<5:return None
 classifier=make_pipeline(StandardScaler(),LogisticRegression(C=.3,max_iter=2000)).fit([[math.log(min(100,a['rank'])),ranking_age(a),a['pitcher']] for a in rows],[a['five_year_label'] for a in rows])
 # One earliest eligible independent dated hitter prior per identity.
 cohort={}
 for a in sorted(rows,key=lambda a:a['year']):
  ident=a['mlbamId'];first=FIRST.get(ident)
  if a['pitcher'] or ident in cohort or (first is not None and first<a['year']) or first==2010:continue
  cohort[ident]=a
 return classifier,list(cohort.values())

def prior(rank,age,rank_year,first,origin,horizon=8):
 train=training(origin)
 if not train:return None,'Missing past-completed class support'
 clf,cohort=train;pr=np.zeros(5)
 for c,p in zip(clf[-1].classes_,clf.predict_proba([[math.log(min(100,rank)),age,0]])[0]):pr[int(c)]=p
 lag=max(0,origin-rank_year);offset=origin-first
 adjusted=[];values={};counts={};debut_counts={}
 for c in range(5):
  group=[a for a in cohort if a['five_year_label']==c];success=[a for a in group if FIRST.get(a['mlbamId'],9999)<=a['year']+lag]
  counts[c]=len(group);debut_counts[c]=len(success)
  if not group:return None,'No independent past hitter class '+str(c)
  adjusted.append(pr[c]*(len(success)+.5)/(len(group)+1))
  values[c]=[]
  for t in range(horizon):
   xs=[]
   for a in success:
    y=FIRST[a['mlbamId']]+offset+t+1
    if y>origin:continue # Right-censoring cannot become a zero.
    stat=H.get((a['mlbamId'],y),{}).get('stat',{})
    xs.append(r.utility(r.surplus(stat,'H')))
   if not xs:return None,'No completed debut-aligned class '+str(c)+' horizon '+str(t+1)
   values[c].append(float(np.mean(xs)))
 adjusted=np.array(adjusted);adjusted/=sum(adjusted)
 return [(float(adjusted[c]),values[c]) for c in range(5)],{'class_counts':counts,'observed_debut_counts':debut_counts,'probabilities':adjusted.tolist(),'latest_training_target':origin,'offset_since_debut':offset,'rank_year':rank_year}

rows=[];unsupported=[]
for z in scr:
 key=z['id'],z['origin'];src=rankinfo.get(key)
 if not src:unsupported.append({'id':z['id'],'name':z['name'],'origin':z['origin'],'reason':'Dated rank absent from recovered inputs'});continue
 ps,info=prior(src['prior_rank'],src['prior_age'],src['prior_year'],z['first_MLB_year'],z['origin'],1)
 if not ps:unsupported.append({'id':z['id'],'name':z['name'],'origin':z['origin'],'reason':info});continue
 pm=sum(pr*path[0] for pr,path in ps);w=z['career_PA']/(z['career_PA']+600);candidate=w*z['baseline_mean']+(1-w)*pm
 rows.append({'id':z['id'],'name':z['name'],'origin':z['origin'],'stage':z['stage'],'career_PA':z['career_PA'],'baseline':z['baseline_mean'],'candidate':candidate,'actual':z['actual'],'debut_conditioned_prior':pm,'MLB_weight':w,'baseline_error':z['baseline_mean']-z['actual'],'candidate_error':candidate-z['actual']})

def summarize(xs):
 out={'n':len(xs),'players':len({z['id'] for z in xs})}
 for method in ['baseline','candidate']:
  err=[z[method+'_error'] for z in xs];out[method]={'MAE':float(np.mean(np.abs(err))) if err else None,'bias':float(np.mean(err)) if err else None}
 return out
scores={stage:{band:summarize([z for z in rows if z['stage']==stage and lo<=z['career_PA']<hi]) for band,lo,hi in [('all',0,float('inf')),('under250',0,250),('under50',0,50),('50to100',50,100),('100to250',100,250),('250to600',250,600)]} for stage in ['development','later']}
xs=[z for z in rows if z['stage']=='later' and z['career_PA']<250];groups=collections.defaultdict(list)
for z in xs:groups[z['id']].append(abs(z['candidate_error'])-abs(z['baseline_error']))
boot=[];rng=np.random.default_rng(2312);vals=list(groups.values())
if vals:
 for _ in range(2000):
  sample=[vals[i] for i in rng.integers(0,len(vals),len(vals))];boot.append(sum(map(sum,sample))/sum(map(len,sample)))
gate=all(scores['later'][band]['n'] and scores['later'][band]['candidate']['MAE']<scores['later'][band]['baseline']['MAE'] for band in ['all','under250'])
result={'scores':scores,'release_gate_pass':bool(gate),'unsupported':len(unsupported),'total_scrutiny_cases':len(scr),'under250_paired_MAE_interval':list(np.quantile(boot,[.025,.975])) if boot else None,'scope':'Exposed chronological first-year utility test only; no new independent eight-year holdout'}
(D/'Debut_Validation.json').write_text(json.dumps(result,indent=2)+'\n')
for name,data in [('Debut_Comparisons.csv',rows),('Debut_Unsupported.csv',unsupported)]:
 with (D/name).open('w',newline='') as f:
  w=csv.DictWriter(f,list(dict.fromkeys(k for z in data for k in z)));w.writeheader();w.writerows(data)
# Current named diagnostics require all eight independently completed path offsets.
current=[]
for name in ['Josue De Paula','Kaelen Culpepper']:
 p=next(p for p in old.players.values() if p['name']==name);original,audit=m.paths(p);src=m.MATCHED[p['id']]
 ps,info=prior(src['rank'],src['age'],2026,2026,2026,8)
 entry={'id':p['id'],'name':name,'production':m.competitive(original,'neutral')['display'],'supported':bool(ps),'audit':info}
 if ps:
  mlb,unused=m.v.mlb_paths(p);e=p['bat']['PA'];w=e/(e+600);mix=[(prob*w,path) for prob,path in mlb]+[(prob*(1-w),path) for prob,path in ps]
  entry.update(candidate=m.competitive(mix,'neutral')['display'],MLB_weight=w,release_gate_pass=bool(gate))
 current.append(entry)
(D/'Debut_Current_Diagnostics.json').write_text(json.dumps(current,indent=2)+'\n')
print(json.dumps(result,indent=2));print(json.dumps(current,indent=2))
