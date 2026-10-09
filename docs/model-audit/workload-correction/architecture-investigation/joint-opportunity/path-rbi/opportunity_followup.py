"""Fixed general conditional GS and pooled principal-RP exact-QA3 candidates."""
import sys
from pathlib import Path
HERE=Path(__file__).resolve().parent;sys.path.insert(0,str(HERE.parent))
import past_only_followup
from shared import *
from continuation import put,writecsv,pcases,pextra
from principal_followup import predict_augmented
import joblib

def fx(z):
 ident,y=z['id'],z['year'];age=z['x'][13];cap=capacity(ident,y);now=counts(ident,y) or {};prev=counts(ident,y-1) or {};f=z['x']
 gs=float(f[16]);gp=float(f[15]);cap=max(cap,float(f[21]),float(f[25]));return np.array([gs,prev.get('GS',0),age,f[14],cap,gp,f[0],e['minor_share'](ident,y),gs*min(f[14],5)])
def fit(y,development=False):
 xs=training(y);keep=[z for z in xs if z['state']==2 and (not development or not z['calibration'])];X=np.stack([fx(z['z']) for z in keep]);Y=np.array([z['info']['GS'] for z in keep]);reg=make_pipeline(StandardScaler(),Ridge(alpha=100));reg.fit(X,Y)
 relief=[z for z in xs if z['state']==1 and z['info'] and z['info']['exact_QA3_available'] and (not development or not z['calibration'])];gp=sum(z['info']['RA'] for z in relief);gs=sum(z['info']['GS'] for z in relief);q=sum(z['info']['QA3'] for z in relief);pure=[z for z in relief if z['info']['GS']==0];offset=sum(z['info']['QA3'] for z in pure)/max(1,sum(z['info']['RA'] for z in pure));qgs=max(0,min(1,(q-offset*gp)/max(1,gs)))
 return reg,qgs,offset,{'asof':y,'latest_target':max(a['year'] for a in keep),'GS_rows':len(keep),'RP_rows':len(relief),'RP_QA3_per_GS':qgs,'RP_pure_relief_QA3_rate':offset,'regressor_ID_mods':[1,2,3] if development else [1,2,3,4]}
def adjust(c,gs,qgs,rpq,blend=False,qonly=False):
 c=copy.deepcopy(c);p=c['probabilities'];a=c['conditional']['2'];oldgs=a['GS'];newgs=oldgs if qonly else (.5*oldgs+.5*gs if blend else gs);oldq=a['QA3'];qper=max(0,(oldq-a['RA']*rpq)/oldgs) if oldgs else 0;a['GS']=newgs;a['IP']=newgs*a['IP_per_start']+a['RA']*a['IP_per_relief'];a['QA3']=min(a['IP']/5,newgs*min(qper,a['IP_per_start']/5)+a['RA']*rpq)
 if qonly:
  a=c['conditional']['1'];a['QA3']=min(a['IP']/5,a['GS']*min(qgs,a['IP_per_start']/5)+a['RA']*min(rpq,a['IP_per_relief']/5))
 c['IP']=sum(p['RP' if s=='1' else 'SP']*a['IP'] for s,a in c['conditional'].items());c['QA3']=sum(p['RP' if s=='1' else 'SP']*a['QA3'] for s,a in c['conditional'].items());c['GS']=sum(p['RP' if s=='1' else 'SP']*a['GS'] for s,a in c['conditional'].items());return c

def score(zs):
 out={}
 for g in sorted({g for z in zs for g in z['groups']}):
  xs=[z for z in zs if g in z['groups']];out[g]={k:{s:metric([(z[s].get(k,0),z['actual'].get(k,0)) for z in xs if s in z]) for s in ['baseline','linear_SP','past_only','linear_GS','blend_GS','pooled_RP_QA3']} for k in ['IP','K','QA3','ER','BB','H']}
 return out

def run():
 dev={s:[] for s in ['linear_GS','blend_GS']};man=[]
 for year in [2016,2017,2018,2021,2022]:
  reg,qgs,rpq,mn=fit(year,True);man.append(mn)
  # New development selection judges conditional GS directly: no inherited group4 fitted conditional forecasts.
  xs=[z for z in training(year+1) if z['z']['year']==year and z['h']==1 and z['state']==2 and z['calibration']]
  if not xs:continue
  preds=np.clip(reg.predict(np.stack([fx(z['z']) for z in xs])),0,36)
  for z,p in zip(xs,preds):
   prev=(counts(z['z']['id'],year) or {}).get('GS',0);dev['linear_GS'].append((p,z['info']['GS']));dev['blend_GS'].append((.5*prev+.5*p,z['info']['GS']))
 ds={s:metric(a) for s,a in dev.items()};chosen=min(ds,key=lambda s:ds[s]['MAE']+.25*abs(ds[s]['bias']))
 out=copy.deepcopy(pcases);extras=copy.deepcopy(pextra);bys={(z['mlbam_id'],z['anchor'],z['role']):z for z in out+extras}
 for year in sorted({z['anchor'] for z in out+extras}):
  reg,qgs,rpq,mn=fit(year);man.append(mn);xs=[z for rr in ['SP','RP'] for z in records[rr] if z['year']==year and (z['id'],year,rr) in bys];gs=np.clip(reg.predict(np.stack([fx(z) for z in xs])),0,36)
  for z,g in zip(xs,gs):
   q=bys[z['id'],year,z['role']];c=q['components']['past_only']
   for name,bl,qo in [('linear_GS',False,False),('blend_GS',True,False),('pooled_RP_QA3',False,True)]:
    pred=adjust(c,float(g),qgs,rpq,bl,qo);ratio=pred['IP']/q['baseline']['IP'] if q['baseline']['IP'] else 0;q[name]={k:v*ratio for k,v in q['baseline'].items()};q[name]['IP']=pred['IP'];q[name]['QA3']=pred['QA3']
    for k in ['SV','HLD']:q[name][k]=q['baseline'].get(k,0)*min(1,ratio)
    q['components'][name]=pred
  print('Opportunity scored',year,flush=True)
 frozen=[];idx={(z['mlbam_id'],z['anchor']):z for z in out}
 for z in read(PARENT.parent/'Historical_Cases.json'):
  q=copy.deepcopy(idx[z['mlbam_id'],z['anchor']]);q['baseline']=z['baseline']
  for name in ['linear_SP','past_only','linear_GS','blend_GS','pooled_RP_QA3']:
   if name=='linear_SP':ratio=idx[z['mlbam_id'],z['anchor']][name]['IP']/q['baseline']['IP'];qa=q[name]['QA3']
   else:ratio=q['components'][name]['IP']/q['baseline']['IP'];qa=q['components'][name]['QA3']
   q[name]={k:v*ratio for k,v in q['baseline'].items()};q[name]['QA3']=qa
  frozen.append(q)
 put('Opportunity_Validation.json',{'development_conditional_GS':ds,'selected':chosen,'development_selection_scope':'Conditional GS criterion; blend selector uses latest observed GS rather than incumbent conditional model to avoid reusing fitted group4 targets. Test blend mixes fitted incumbent with new directGS and therefore not an identically tuned development variant; both remain exploratory.','expanded':score(out),'frozen94':score(frozen),'additional':score(extras),'manifests':man});put('Opportunity_Cases.json.gz',out);put('Opportunity_Additional.json.gz',extras)
 # Current general diagnostic and league first-year component changes.
 reg,qgs,rpq,mn=fit(2026);current=[]
 for z in read(OUT/'Past_Only_League_Impact.json.gz'):
  if z.get('role') not in ['SP','RP'] or z['status']!='supported_MLB':continue
  ident=z['mlbam_id'];p=old.players[z['id']];rows=v.seasons(p,z['role']);f=base['features'](rows,z['role'],2026,ident);zz={'id':ident,'year':2026,'role':z['role'],'x':f};g=float(np.clip(reg.predict(fx(zz)[None])[0],0,36));c=z['variants']['joint_principal']['components'][0];q={'id':z['id'],'name':z['name'],'role':z['role'],'baseline_IP':z['baseline_annual'][0]['IP'],'incumbent_IP':c['IP'],'incumbent_QA3':c['QA3'],'incumbent_conditional_GS':c['conditional']['2']['GS']}
  for name,bl,qo in [('linear_GS',False,False),('blend_GS',True,False),('pooled_RP_QA3',False,True)]:
   cc=adjust(c,g,qgs,rpq,bl,qo);q[name+'_IP']=cc['IP'];q[name+'_QA3']=cc['QA3'];q[name+'_conditional_GS']=cc['conditional']['2']['GS']
  current.append(q)
 writecsv('Opportunity_Current.csv',current);put('Opportunity_Current_Manifest.json',mn);joblib.dump(reg,HERE/'current-GS.joblib',compress=3);print('Completed opportunity',ds,flush=True)
if __name__=='__main__':run()
