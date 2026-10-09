"""Read-only shared helpers for the existing audit; no collection or prior fit loops."""
import sys,json,gzip,functools,copy,math
from pathlib import Path
import numpy as np
from sklearn.ensemble import HistGradientBoostingClassifier,HistGradientBoostingRegressor
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import Ridge,LogisticRegression
OUT=Path(__file__).resolve().parent;PARENT=OUT.parent
main=PARENT/'quality_aware.py';e={'__file__':str(main),'__name__':'joint_helpers'}
exec(compile(main.read_text().split('cases=[];manifest=[]')[0],str(main),'exec'),e)
base=e['env'];records=e['records'];lookup=e['lookup'];appear=base['appear'];index=e['index'];first=e['first'];settings=e['settings'];hist=base['hist'];r=base['r'];v=base['v'];m=base['m'];old=base['old'];catalog=base['catalog'];games=r.G
def save(name,value):
 s=json.dumps(value,allow_nan=False,default=lambda x:x.item() if isinstance(x,np.generic) else x)
 if name.endswith('.gz'):(OUT/name).write_bytes(gzip.compress(s.encode(),mtime=0))
 else:(OUT/name).write_text(s)
def read(p):return json.loads(gzip.decompress(p.read_bytes()) if p.suffix=='.gz' else p.read_text())
def metric(pairs):
 a=np.array([x-y for x,y in pairs]);return {'n':len(a),'MAE':float(np.mean(abs(a))),'bias':float(np.mean(a)),'RMSE':float(np.sqrt(np.mean(a*a)))} if len(a) else {'n':0,'MAE':None,'bias':None,'RMSE':None}
def target(z,h=1):return lookup.get((z['id'],z['year']+h,'H' if z['role']=='H' else 'P'))
def counts(ident,year):
 a=appear.get((ident,year));b=games['annual_QA3'].get(str(year),{}).get(str(ident))
 if a is None:return None
 gp=a.get('GP',0);gs=a.get('GS',0)
 return {'GP':gp,'GS':gs,'RA':max(0,gp-gs),'QA3':b.get('QA3') if b else None,'exact_QA3_available':bool(b)}
def capacity(ident,year):
 rows=hist.get((ident,'P'),[]);vals=[]
 for a in rows:
  if a['year']>year:continue
  mi=base['minor'].get((ident,a['year']))
  if base['complete'].get(a['year'],set())!=set(range(11,17)):mi=None
  vals.append(a['stat'].get('IP',0)+(mi or 0))
 return max(vals,default=0)
@functools.lru_cache(None)
def _x(ident,year,rr,calendar):
 rows=hist[ident,'H' if rr=='H' else 'P'];z={'id':ident,'year':year,'role':rr,'x':base['features'](rows,rr,year,ident),'bounded_x':base['features'](rows,rr,year,ident,True)}
 return feature(z,calendar,rows)
def feature(z,calendar=False,rows=None):
 ident,year,rr=z['id'],z['year'],z['role'];rows=rows if rows is not None else z.get('history_override',hist.get((ident,'H' if rr=='H' else 'P'),[]))
 f=np.array(z['bounded_x'],copy=True)
 if calendar:
  by={a['year']:a for a in rows if a['year']<=year};work=[]
  for y in range(year,year-4,-1):
   a=by.get(y);work.append(r.exposure(a['stat'],rr)*(162/60 if y==2020 else 1) if a else 0)
  pos=[a for a in work if a>0];f[:4]=work;f[4]=np.mean(work);f[5]=np.mean(pos) if pos else 0;f[6]=max(pos,default=0);f[7]=min(pos,default=0);f[8]=np.std(work);f[12]=work[0]-work[1];f[28]=f[13]*work[0]/100
  if year==2020:f[15:17]*=162/60
 # Capacity stays raw demonstrated physical work, never synthetic annualized talent.
 f[19:26]=z['x'][19:26]
 if rr=='H':rates=[0.]*7;shares=[0.,0.];cap=0
 else:
  forecast=base['forecast'](rows,rr,year,ident,strict=True);rate=forecast[0] if forecast else old.prior[rr];rates=[rate.get(k,0) for k in ['K','ER','BB','H','QA3','SV','HLD']];shares=[e['minor_share'](ident,first.get(ident)),e['minor_share'](ident,year)];cap=max([a['stat'].get('IP',0)+(base['minor'].get((ident,a['year']),0) if base['complete'].get(a['year'],set())==set(range(11,17)) else 0) for a in rows if a['year']<=year],default=0)
 return np.r_[f,shares,rates,cap,60/162 if year==2020 else 1,int(year-3<=2020<=year),60/162 if first.get(ident)==2020 else 1,int(rr=='SP')]
def xrow(z,h=1,calendar=False):
 f=feature(z,calendar) if 'history_override' in z else _x(z['id'],z['year'],z['role'],calendar)
 return np.r_[f,float(h),f[13]+h]
def training(asof,horizons=(1,),development=False,calendar=False,family='P'):
 roles=['H'] if family=='H' else ['SP','RP'];out=[]
 for rr in roles:
  for z in records[rr]:
   if z['id']%5==0:continue
   for h in horizons:
    ty=z['year']+h
    if ty>min(asof,2025) or (not calendar and (z['year']==2020 or ty==2020)):continue
    t=target(z,h);actual=t['stat'] if t else {};factor=162/60 if calendar and ty==2020 else 1
    weight=60/162 if calendar and ty==2020 else 1
    if family=='H':
     raw=actual.get('PA',0);value=raw*factor;state=0 if not raw else 2 if value>=400 else 1;info=None
    else:
     raw=actual.get('IP',0);info=counts(z['id'],ty)
     if raw and info is None:continue
     state=0 if not raw else 2 if info['GP'] and info['GS']/info['GP']>=.5 else 1;value=raw*factor
    out.append({'z':z,'h':h,'year':ty,'value':value,'raw_value':raw,'weight':weight,'state':state,'info':info,'factor':factor,'actual':actual,'calibration':z['id']%5==4})
 return out
def calibrated_prob(model,X):
 p=model['classifier'].predict_proba(X);full=np.zeros((len(X),3))
 for j,c in enumerate(model['classifier'].classes_):full[:,int(c)]=p[:,j]
 cal=model.get('calibrator')
 if cal is None:return full
 cp=cal.predict_proba(np.log(np.clip(full,1e-6,1)));out=np.zeros_like(full)
 for j,c in enumerate(cal.classes_):out[:,int(c)]=cp[:,j]
 return out
def classifier_fit(rows,X):
 core=np.array([not z['calibration'] for z in rows]);lab=np.array([z['state'] for z in rows]);weights=np.array([z['weight'] for z in rows]);clf=HistGradientBoostingClassifier(**settings).fit(X[core],lab[core],sample_weight=weights[core]);cal=None;calrows=~core
 if calrows.sum()>=100 and len(set(lab[calrows]))==3 and min(np.bincount(lab[calrows],minlength=3))>=10:
  p=clf.predict_proba(X[calrows]);full=np.zeros((len(p),3))
  for j,c in enumerate(clf.classes_):full[:,int(c)]=p[:,j]
  cal=LogisticRegression(C=1,max_iter=500,random_state=2309).fit(np.log(np.clip(full,1e-6,1)),lab[calrows],sample_weight=weights[calrows])
 return clf,cal
def regfit(X,y,weights,linear=False):
 if not len(y):return None
 if linear:
  a=make_pipeline(StandardScaler(),Ridge(alpha=100));a.fit(X,y,ridge__sample_weight=weights);return a
 return HistGradientBoostingRegressor(loss='squared_error',**settings).fit(X,y,sample_weight=weights)
def prediction(reg,X,low=0,high=np.inf):return np.clip(reg.predict(X),low,high) if reg else np.zeros(len(X))
def historical_baseline(z,h=1):
 f=base['forecast'](hist[z['id'],'H' if z['role']=='H' else 'P'],z['role'],z['year'],z['id'],strict=True)
 if f is None:return None
 if h==1:return base['project'](f,z['role'],z['x'][13],z['year'],True)
 # Extend the existing as-of cohort calculation to direct horizons; no final-source curve.
 rr=z['role'];age=round(z['x'][13]);year=z['year'];rates,work=f;pool=[]
 for a in old.AN:
  if a['role']!=rr or a['id']%5==0 or a['year']+h>year or a['year']==2020 or a['year']+h==2020:continue
  ag=r.age_at(a['id'],a['year']);ex=r.exposure(a['stat'],rr)
  if ag is None or abs(ag-age)>4 or ex<(250 if rr=='H' else 80 if rr=='SP' else 30):continue
  b=lookup.get((a['id'],a['year']+h,'H' if rr=='H' else 'P'));pool.append((a['stat'],b['stat'] if b else {}))
 if not pool:return None
 total=sum(r.exposure(a,rr) for a,b in pool);after=sum(r.exposure(b,rr) for a,b in pool);ratio=after/total if total else 0;support=len(pool)/(len(pool)+40);result={}
 for k,val in rates.items():
  before=sum(a.get(k,0) for a,b in pool)/total if total else 0;future=sum(b.get(k,0) for a,b in pool)/after if after else 0;aging=1 if k in ['PA','IP','AB'] else max(0,1+support*((future/before if before else 1)-1));result[k]=val*work*ratio*aging
 if rr=='H':return v.reconcile(result)
 for k in ['SV','HLD']:result[k]=min(result.get(k,0),rates.get(k,0)*work*ratio)
 result['QA3']=min(result.get('QA3',0),result.get('IP',0)/5);return result
