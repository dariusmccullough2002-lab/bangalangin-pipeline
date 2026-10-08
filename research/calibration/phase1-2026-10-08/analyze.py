"""First historical calibration checkpoint; reduced-category surrogate, not deployment code."""
import json,math,unicodedata,re,statistics,hashlib,importlib.util,sys,gzip
from pathlib import Path
import numpy as np
from sklearn.linear_model import LogisticRegression,Ridge
from sklearn.metrics import log_loss
ROOT=Path(__file__).resolve().parent;RAW=ROOT/'raw';OUT=ROOT/'results';OUT.mkdir(exist_ok=True)
def norm(s):return re.sub('[^a-z]','',unicodedata.normalize('NFKD',s).encode('ascii','ignore').decode().lower())
def load(y,g):return json.load(open(RAW/f'{g}-{y}.json'))['stats'][0]['splits']
def n(s,k):return float(s.get(k,0) or 0)
def ip(s):return n(s,'outs')/3 if 'outs' in s else int(float(s.get('inningsPitched',0)))+round(float(s.get('inningsPitched',0))%1*10)/3
def vec(s,r):
 if r=='H':
  ab=n(s,'atBats');return np.array([n(s,'homeRuns'),n(s,'runs'),n(s,'rbi'),n(s,'stolenBases'),n(s,'hits')-.25*ab,(float(s.get('ops','0'))-.72)*ab])
 innings=ip(s);return np.array([n(s,'strikeOuts'),4.2/9*innings-n(s,'earnedRuns'),3*n(s,'saves')+2*n(s,'holds'),n(s,'strikeOuts')-3*n(s,'baseOnBalls'),1.25*innings-n(s,'hits')-n(s,'baseOnBalls')])
rows={};names={};ids={};groups={}
for y in range(2010,2024):
 for g in ['hitting','pitching']:
  splits=load(y,g);seen=set()
  for a in splits:
   id=a['player']['id'];assert id not in seen,(y,g,id);seen.add(id);s=a['stat'];r='H' if g=='hitting' else ('SP' if n(s,'gamesStarted')>=5 else 'RP');ex=n(s,'atBats') if r=='H' else ip(s)
   names.setdefault(norm(a['player']['fullName']),set()).add(id);ids[id]=a['player']['fullName']
   # Occasional hitters pitch; retain greater normalized exposure for primary-role rows.
   if (y,id) in rows and rows[(y,id)]['ex']/(150 if rows[(y,id)]['role']=='H' else 30)>ex/(150 if r=='H' else 30):continue
   rows[(y,id)]={'id':id,'year':y,'role':r,'stat':s,'ex':ex,'age':n(s,'age'),'position':a.get('position',{}).get('abbreviation','P')}
den={}
for family in ['H','P']:
 v=[vec(a['stat'],a['role']) for a in rows.values() if a['year']<=2012 and (a['role']=='H')==(family=='H') and a['ex']>=(150 if family=='H' else 30)]
 den[family]=np.maximum(1,np.std(v,axis=0))
for a in rows.values():
 factor=1 # Actual production; 2020 never inflated into an invented full season.
 a['score']=float(sum(vec(a['stat'],a['role'])*factor/den['H' if a['role']=='H' else 'P']))
# Fixed historical replacement references, never chosen from held-out results.
rep={}
for family,depth in [('H',156),('P',108)]:
 values=[]
 for y in range(2010,2013):
  v=sorted([a['score'] for a in rows.values() if a['year']==y and (a['role']=='H')==(family=='H') and a['ex']>=(150 if family=='H' else 30)],reverse=True)
  values.extend(v[depth:depth+24])
 rep[family]=float(np.median(values))
for a in rows.values():a['surplus']=a['score']-rep['H' if a['role']=='H' else 'P']
q=[a['score'] for a in rows.values() if a['year']<=2012 and a['ex']>=(400 if a['role']=='H' else 50) and a['score']>0]
thresholds=np.quantile(q,[.30,.60,.85,.98]).tolist()
aliases={'williammyers':'wilmyers','nicholascastellanos':'nickcastellanos','garybrown':'garybrown','josefernandez':'josefernandez','aaronsanchez':'aaronsanchez','albertsalmora':'albertalmoraj r'.replace(' ','')}
identity_extra=json.load(open(RAW/'identity-overrides.json')) if (RAW/'identity-overrides.json').exists() else {}
cohort=[];unresolved=[]
for y in [2012,2013,2017,2018]:
 for p in json.load(open(RAW/f'rankings-{y}.json')):
  key=norm(p['name']); candidates=names.get(aliases.get(key,key),set());id=identity_extra.get(key)
  if id is None and len(candidates)==1:id=next(iter(candidates))
  if id is None:unresolved.append(p);continue
  a=p|{'mlbamId':id,'pitcher':int('HP' in p['position']),'identity_source':'exact season-name or explicit verified override'}
  # Five calendar seasons; zero-production years retained, no career-complete claim.
  future=[rows.get((yr,id),{'surplus':0,'score':0,'ex':0,'role':'SP' if a['pitcher'] else 'H'}) for yr in range(y,y+5)]
  peak=float(np.mean(sorted([x['score'] for x in future],reverse=True)[:2]));regular=sum(x['ex']>=(250 if x['role']=='H' else 40) for x in future)>=2
  label=0 if not regular else 1+sum(peak>=t for t in thresholds[1:])
  prior=[x for (yr,pid),x in rows.items() if pid==id and yr<y];a.update(label=int(label),peak_two_year=peak,age_at_evaluation=(prior[-1]['age']+y-prior[-1]['year']) if prior else None,outcome_years=list(range(y,y+5)))
  cohort.append(a)
(OUT/'identity-unresolved.json').write_text(json.dumps(unresolved,indent=2));(OUT/'cohort.json').write_text(json.dumps(cohort,indent=2))
assert [(p['year'],p['name']) for p in unresolved]==[(2012,'Brody Colvin')], unresolved
# Unresolved identity excluded rather than fabricating a zero outcome.
# First appearance only for development; heldout people disjoint from training.
train=[];seen=set()
for p in sorted(cohort,key=lambda a:(a['year'],a['rank'])):
 if p['year'] in [2012,2013] and p['mlbamId'] not in seen:train.append(p);seen.add(p['mlbamId'])
test=[p for p in cohort if p['year']==2018 and p['mlbamId'] not in seen]
lookup={(p['year'],p['mlbamId']):p['rank'] for p in cohort}
def features(p,trajectory=False):
 x=[math.log(p['rank']),p['pitcher']]
 if trajectory:
  previous=lookup.get((p['year']-1,p['mlbamId']));x += [int(previous is not None),(previous-p['rank'])/100 if previous else 0]
 return x
X=np.array([features(p) for p in train]);y=np.array([p['label'] for p in train]);T=np.array([features(p) for p in test]);truth=np.array([p['label'] for p in test])
model=LogisticRegression(C=.3,max_iter=2000).fit(X,y);pred=model.predict_proba(T)
assert list(model.classes_)==[0,1,2,3,4],model.classes_
baseline=(np.bincount(y,minlength=5)+1)/(len(y)+5);basepred=np.tile(baseline,(len(test),1))
u2=[]
for p in test:
 rank=p['rank'];reach=.22+.58*math.exp(-(rank-1)/160);elite=.015+.20*math.exp(-(rank-1)/35);star=.07+.25*math.exp(-(rank-1)/100);u2.append([1-reach,reach*(1-elite-star-.25),reach*.25,reach*star,reach*elite])
def metrics(pr):return {'log_loss':float(log_loss(truth,pr,labels=range(5))),'multiclass_brier':float(np.mean(np.sum((pr-np.eye(5)[truth])**2,axis=1))),'superstar_brier':float(np.mean((pr[:,4]-(truth==4))**2))}
# Bootstrapped training uncertainty; do not report narrow Wald errors for rare outcomes.
rng=np.random.default_rng(710);boots=[]
grid=[{'rank':r,'pitcher':pitch} for pitch in [0,1] for r in [5,25,50,90]];G=np.array([features(p) for p in grid])
for _ in range(200):
 idx=rng.integers(0,len(y),len(y))
 if len(set(y[idx]))<5:continue
 boots.append(LogisticRegression(C=.3,max_iter=2000).fit(X[idx],y[idx]).predict_proba(G))
arr=np.array(boots)
probabilities=[p|{'probabilities':model.predict_proba(G)[i].tolist(),'bootstrap_90_interval':[np.quantile(arr[:,i,:],.05,axis=0).tolist(),np.quantile(arr[:,i,:],.95,axis=0).tolist()]} for i,p in enumerate(grid)]
# Age/role/workload evolution fitted before holdout; absent next-year production explicitly zero.
def mlb_features(a):return [a['score'],a['ex']/(500 if a['role']=='H' else 150),a['age']-28,max(0,a['age']-30),int(a['role']=='SP'),int(a['role']=='RP')]
pairs=[]
for (yr,id),a in rows.items():
 if a['ex']<(150 if a['role']=='H' else 30) or yr>=2023:continue
 b=rows.get((yr+1,id));pairs.append((yr,a,b['score'] if b else 0))
fit=[x for x in pairs if x[0]<=2016];hold=[x for x in pairs if 2018<=x[0]<=2022 and x[0] not in [2019,2020]]
reg=Ridge(alpha=10).fit([mlb_features(a) for _,a,_ in fit],[v for _,_,v in fit]);diagnostics={}
for role in ['H','SP','RP']:
 subset=[x for x in hold if x[1]['role']==role];actual=np.array([v for _,_,v in subset]);pr=reg.predict([mlb_features(a) for _,a,_ in subset]);naive=np.array([a['score'] for _,a,_ in subset]);diagnostics[role]={'n':len(subset),'ridge_mae':float(np.mean(abs(pr-actual))),'carry_forward_mae':float(np.mean(abs(naive-actual))),'bias':float(np.mean(pr-actual)),'heldout_residual_10_90':[float(x) for x in np.quantile(actual-pr,[.1,.9])],'next_year_absent_rate':float(np.mean([rows.get((yr+1,a['id'])) is None for yr,a,_ in subset]))}
anchors={r:np.quantile([a['surplus'] for a in rows.values() if a['year']<=2012 and a['role']==r and a['ex']>=(400 if r=='H' else 100 if r=='SP' else 40)],[.3,.6,.85,.98]).tolist() for r in ['H','SP','RP']}
result={'status':'FIRST REDUCED-CATEGORY HISTORICAL VALIDATION; NOT PRODUCTION READY','coverage':{'season_years':[2010,2023],'player_seasons':len(rows),'ranking_rows':len(cohort),'train_unique':len(train),'test_unique_unseen':len(test),'training_labels_observed_by':'2017-12-31','heldout_evaluation':'2018 preseason','heldout_outcomes':'2018–2022','train_counts':np.bincount(y,minlength=5).tolist(),'test_counts':np.bincount(truth,minlength=5).tolist()},'thresholds':thresholds,'replacement':rep,'category_dispersion':{k:v.tolist() for k,v in den.items()},'prospect_validation':{'rank_role_logistic':metrics(pred),'training_frequency_baseline':metrics(basepred),'U2_rank_prior':metrics(np.array(u2))},'probability_grid':probabilities,'bootstrap_successful_fits':len(boots),'mlb_validation':diagnostics,'historical_surplus_anchors':anchors,'historical_intrinsic_anchors':{r:np.quantile([a['score'] for a in rows.values() if a['year']<=2012 and a['role']==r and a['ex']>=(400 if r=='H' else 100 if r=='SP' else 40)],[.3,.6,.85,.98]).tolist() for r in ['H','SP','RP']},'mlb_coefficients':reg.coef_.tolist(),'prospect_coefficients':model.coef_.tolist(),'predictions':[p|{'predicted':pr.tolist()} for p,pr in zip(test,pred)],'trajectory_status':'Matched 2013/2012 training versus 2018/2017 test experiment in diagnostics.json','missing_features':['dated historical FV/tools/levels','minor-league performance','injury diagnoses at evaluation','QA3 game-level events','historical Fantrax positional eligibility','weekly team category distributions']}
(OUT/'validation.json').write_text(json.dumps(result,indent=2));print(json.dumps({k:result[k] for k in ['coverage','prospect_validation','mlb_validation','historical_intrinsic_anchors','historical_surplus_anchors']},indent=2))
