"""General role/appearance/depth model; future states are labels, never inputs."""
from shared import *
import joblib
VARIANTS=['joint_raw','joint_calibrated','joint_linear_depth','joint_calendar']
def fit_pitch(asof,horizons=(1,),development=False,calendar=False):
 rows=training(asof,horizons,development,calendar,'P');X=np.stack([xrow(z['z'],z['h'],calendar) for z in rows]);clf,cal=classifier_fit(rows,X)
 use=np.array([not z['calibration'] or not development for z in rows]);weights=np.array([z['weight'] for z in rows]);labels=np.array([z['state'] for z in rows]);countregs={};depth={};linear={};qa={};caps={}
 for state in [1,2]:
  mask=use&(labels==state)
  for key in ['GS','RA']:
   vals=np.array([(z['info'][key]*z['factor'] if z['info'] else 0) for z in rows]);countregs[state,key]=regfit(X[mask],vals[mask],weights[mask]);caps[key]=max(caps.get(key,0),float(np.quantile(vals[mask],.995)))
 for kind in ['SP','RP']:
  mask=np.array([bool(z['info'] and z['info']['GP']>0 and ((z['info']['GS']==z['info']['GP'] and z['info']['GS']>=3) if kind=='SP' else z['info']['GS']==0)) for z in rows])&use
  vals=np.array([z['raw_value']/z['info']['GP'] if z['info'] and z['info']['GP'] else 0 for z in rows]);w=np.array([min(30,z['info']['GP']) if z['info'] else 0 for z in rows])*weights
  depth[kind]=regfit(X[mask],vals[mask],w[mask]);linear[kind]=regfit(X[mask],vals[mask],w[mask],True);caps[kind+'_depth']=float(np.quantile(vals[mask],.995));caps[kind+'_n']=int(mask.sum())
  qmask=mask&np.array([bool(z['info'] and z['info']['exact_QA3_available']) for z in rows]);q=np.array([z['info']['QA3']/z['info']['GP'] if z['info'] and z['info']['QA3'] is not None and z['info']['GP'] else 0 for z in rows]);qa[kind]=regfit(X[qmask],q[qmask],w[qmask]);caps[kind+'_QA3_n']=int(qmask.sum())
 model={'classifier':clf,'calibrator':cal,'counts':countregs,'depth':depth,'linear':linear,'qa':qa,'caps':caps,'calendar':calendar,'asof':asof,'horizons':list(horizons),'manifest':{'asof':asof,'latest_target':max(z['year'] for z in rows),'horizon_support':{str(h):sum(z['h']==h for z in rows) for h in horizons},'classifier_ID_mods':[1,2,3],'calibration_ID_mods':[4],'regressor_ID_mods':[1,2,3] if development else [1,2,3,4],'training_rows':len(rows),'calendar_target_weights':'actual2020 confidence60/162' if calendar else '2020 anchor/target excluded','pure_role_support':caps}}
 return model
def predict_pitch(model,zs,h=1,variant='joint_calibrated'):
 X=np.stack([xrow(z,h,model['calendar']) for z in zs]);prob=calibrated_prob(model,X)
 if variant=='joint_raw':prob=calibrated_prob(model|{'calibrator':None},X)
 regs=model['linear'] if variant=='joint_linear_depth' else model['depth'];caps=model['caps'];sd=prediction(regs['SP'],X,0,caps['SP_depth']);rd=prediction(regs['RP'],X,0,caps['RP_depth']);sq=prediction(model['qa']['SP'],X,0,1);rq=prediction(model['qa']['RP'],X,0,1);sq=np.minimum(sq,sd/5);rq=np.minimum(rq,rd/5)
 means={'IP':np.zeros(len(zs)),'GS':np.zeros(len(zs)),'RA':np.zeros(len(zs)),'QA3':np.zeros(len(zs))}
 conditional={}
 for state in [1,2]:
  gs=prediction(model['counts'][state,'GS'],X,0,caps['GS']);ra=prediction(model['counts'][state,'RA'],X,0,caps['RA']);bad=(gs<ra) if state==2 else (gs>ra);avg=(gs+ra)/2;gs=np.where(bad,avg,gs);ra=np.where(bad,avg,ra)
  ip=gs*sd+ra*rd;q=gs*sq+ra*rq;conditional[state]={'GS':gs,'RA':ra,'IP':ip,'QA3':q}
  for k in means:means[k]+=prob[:,state]*conditional[state][k]
 means['QA3']=np.minimum(means['QA3'],means['IP']/5)
 return [{**{k:float(v[i]) for k,v in means.items()},'probabilities':{'absent':float(prob[i,0]),'RP':float(prob[i,1]),'SP':float(prob[i,2])},'IP_per_start':float(sd[i]),'IP_per_relief':float(rd[i]),'QA3_per_start':float(sq[i]),'QA3_per_relief':float(rq[i]),'conditional':{str(l):{k:float(v[i]) for k,v in d.items()} for l,d in conditional.items()},'capacity_feature':float(X[i,38]),'horizon':h} for i in range(len(zs))]
def category_stats(baseline,pred):
 f=pred['IP']/baseline['IP'] if baseline.get('IP') else 0;out={k:v*f for k,v in baseline.items()};out['IP']=pred['IP'];out['QA3']=pred['QA3']
 for k in ['SV','HLD']:out[k]=baseline.get(k,0)*min(1,f)
 return out
def scores(cases,methods):
 out={}
 for group in sorted({g for z in cases for g in z['groups']}):
  xs=[z for z in cases if group in z['groups']];out[group]={'n':len(xs),'metrics':{}}
  for k in ['IP','K','QA3','ER','BB','H','SV','HLD','GS','RA']:
   out[group]['metrics'][k]={}
   for method in methods:
    valid=[z for z in xs if method in z and k in z[method] and (k in z['actual'] or z.get('actual_absent',not z['actual']))]
    if valid:out[group]['metrics'][k][method]=metric([(z[method][k],z['actual'].get(k,0)) for z in valid])
 return out
def extra_groups(z):
 f=z['x'];g=[]
 if f[0]==0:g.append('returning_after_missed_season')
 if f[13]<=26 and f[0]<100 and f[20]>0:g.append('young_promotion_capacity')
 if f[13]<=26 and z['role']=='SP':g.append('young_SP')
 if f[13]>26 and z['role']=='SP':g.append('established_SP')
 if f[26]:g.append('observed_role_transition')
 return g
def run_one_year():
 prior=read(PARENT/'Quality_Aware_Cases.json.gz');linear_cases=read(PARENT/'Conditional_SP_Cases.json.gz');by={(z['mlbam_id'],z['anchor'],z['role']):z for z in prior};line={(z['mlbam_id'],z['anchor'],z['role']):z for z in linear_cases};dev={v:[] for v in VARIANTS};man=[]
 for year in [2016,2017,2018,2021,2022]:
  xs=[z for rr in ['SP','RP'] for z in records[rr] if z['year']==year and z['id']%5==4 and z['positive_anchor']]
  models={False:fit_pitch(year,development=True),True:fit_pitch(year,development=True,calendar=True)}
  for variant in VARIANTS:
   model=models[variant=='joint_calendar'];pred=predict_pitch(model,xs,variant=variant)
   for z,p in zip(xs,pred):
    b=historical_baseline(z);actual=(target(z) or {}).get('stat',{});st=category_stats(b,p);dev[variant].append({'role':z['role'],'prediction':st,'actual':actual})
  print('Joint development completed',year,flush=True)
 development={vv:{rr:{k:metric([(z['prediction'][k],z['actual'].get(k,0)) for z in dev[vv] if z['role']==rr]) for k in ['IP','K','QA3']} for rr in ['SP','RP']} for vv in VARIANTS}
 objective={vv:sum((development[vv][rr]['IP']['MAE']+.25*abs(development[vv][rr]['IP']['bias']))/(150 if rr=='SP' else 50)+.2*development[vv][rr]['K']['MAE']/(150 if rr=='SP' else 50)+.2*development[vv][rr]['QA3']['MAE']/(15 if rr=='SP' else 1) for rr in ['SP','RP']) for vv in VARIANTS};chosen=min(VARIANTS,key=lambda x:objective[x]);save('Development_Selection.json',{'scores':development,'objective':objective,'selected':chosen,'selection':'Development only; no incumbent dominance inferred'});print('Selected joint development',chosen,objective,flush=True)
 cases=[];extra=[]
 for year in [2014,2015,2016,2017,2018,2020,2021,2022,2023,2024]:
  models={False:fit_pitch(year),True:fit_pitch(year,calendar=True)}
  for cal,model in models.items():man.append(model['manifest']);joblib.dump(model,OUT/f'pitch-model-{year}-{int(cal)}.joblib',compress=3)
  xs=[z for rr in ['SP','RP'] for z in records[rr] if z['year']==year and z['id']%5==0 and (z['positive_anchor'] or z['x'][0]==0)]
  predictions={vv:predict_pitch(models[vv=='joint_calendar'],xs,variant=vv) for vv in VARIANTS}
  for i,z in enumerate(xs):
   key=z['id'],year,z['role'];q=copy.deepcopy(by[key]) if key in by else {'mlbam_id':z['id'],'name':z['name'],'anchor':year,'role':z['role'],'groups':z['groups'],'actual':(target(z) or {}).get('stat',{}),'baseline':historical_baseline(z)}
   if q['baseline'] is None:continue
   q['actual_absent']=not q['actual'];q['groups']=list(dict.fromkeys(q['groups']+extra_groups(z)));info=counts(z['id'],year+1);q['actual']=q['actual']|({'GS':info['GS'],'RA':info['RA']} if info else {'GS':0,'RA':0} if not q['actual'] else {})
   if key in line:q['linear_SP']=line[key]['linear_SP']
   q['components']={vv:predictions[vv][i] for vv in VARIANTS}
   for vv in VARIANTS:q[vv]=category_stats(q['baseline'],predictions[vv][i])|{'GS':predictions[vv][i]['GS'],'RA':predictions[vv][i]['RA']}
   q['joint_selected']=q[chosen]
   if key in by:cases.append(q)
   else:extra.append(q)
  print('Joint test completed',year,len(cases),len(extra),flush=True)
 assert len(cases)==1084 and {(z['mlbam_id'],z['anchor'],z['role']) for z in cases}==set(by)
 original=read(PARENT.parent/'Historical_Cases.json');idx={(z['mlbam_id'],z['anchor']):z for z in cases};frozen=[]
 for z in original:
  q=copy.deepcopy(idx[z['mlbam_id'],z['anchor']]);q['baseline']=z['baseline']
  for vv in [*VARIANTS,'joint_selected']:q[vv]=category_stats(z['baseline'],q['components'][chosen if vv=='joint_selected' else vv])
  for vv in ['selected','role_aware','linear_SP']:
   ratio=q[vv]['IP']/z['baseline']['IP'];q[vv]={k:v*ratio for k,v in z['baseline'].items()}
  frozen.append(q)
 methods=['baseline','selected','role_aware','linear_SP',*VARIANTS,'joint_selected'];result={'selected':chosen,'expanded':scores(cases,methods),'frozen94':scores(frozen,methods),'additional':scores(extra,['baseline',*VARIANTS,'joint_selected']),'manifests':man,'cases':1084,'additional_cases':len(extra),'scope':'Exploratory exposed historical labels. Calendar target2020 confidence weighted, role labels never input.'}
 save('Joint_Validation.json',result);save('Joint_Cases.json.gz',cases);save('Joint_Additional_Cases.json.gz',extra)
 for g in ['all','SP','RP','first_MLB_season','second_MLB_season']:print(g,{k:round(v['MAE'],3) for k,v in result['expanded'][g]['metrics']['IP'].items()},flush=True)
if __name__=='__main__':run_one_year()
