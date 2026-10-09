"""Chronological hitter extension with shared schedule features; preserve old results."""
from shared import *
import joblib
H_VARIANTS=['calendar_hurdle','calendar_mix_tree','calendar_mix_linear']
def fit_hitter(asof,horizons=(1,),development=False):
 rows=training(asof,horizons,development,True,'H');X=np.stack([xrow(z['z'],z['h'],True) for z in rows]);clf,cal=classifier_fit(rows,X);use=np.array([not z['calibration'] or not development for z in rows]);y=np.array([z['value'] for z in rows]);w=np.array([z['weight'] for z in rows]);lab=np.array([z['state'] for z in rows]);regs={}
 for state in [1,2]:
  mask=use&(lab==state);regs[state]=regfit(X[mask],y[mask],w[mask])
 mask=use&(lab==2);linear=regfit(X[mask],y[mask],w[mask],True);mask=use&(lab>0);hurdle=regfit(X[mask],y[mask],w[mask]);cap=float(np.quantile(y[use&(y>0)],.995))
 return {'classifier':clf,'calibrator':cal,'regs':regs,'linear':linear,'hurdle':hurdle,'cap':cap,'asof':asof,'horizons':list(horizons),'calendar':True,'manifest':{'asof':asof,'latest_target':max(z['year'] for z in rows),'horizon_support':{str(h):sum(z['h']==h for z in rows) for h in horizons},'classifier_ID_mods':[1,2,3],'calibration_ID_mods':[4],'regressor_ID_mods':[1,2,3] if development else [1,2,3,4],'training_rows':len(rows),'target2020_confidence_weight':60/162}}
def predict_hitter(model,zs,h=1,variant='calendar_hurdle'):
 X=np.stack([xrow(z,h,True) for z in zs]);p=calibrated_prob(model,X);regular=prediction(model['linear'] if variant=='calendar_mix_linear' else model['regs'][2],X,400,model['cap']);part=prediction(model['regs'][1],X,0,400);cond=prediction(model['hurdle'],X,0,model['cap']);pa=(1-p[:,0])*cond if variant=='calendar_hurdle' else p[:,1]*part+p[:,2]*regular
 return [{'PA':float(pa[i]),'probabilities':{'absent':float(p[i,0]),'part_time':float(p[i,1]),'regular':float(p[i,2])},'conditional_PA':float(cond[i]),'conditional_regular_PA':float(regular[i]),'conditional_part_PA':float(part[i]),'horizon':h} for i in range(len(zs))]
def statscale(b,p):return v.reconcile({k:value*p['PA']/b['PA'] for k,value in b.items()})
def groups(z):
 f=z['x'];g=[]
 if f[0]==0:g.append('returning_after_missed_season')
 if f[13]<=26 and f[14]<=2:g.append('young_first_full_opportunity')
 if 100<=f[0]<400:g.append('part_time_opportunity_candidate')
 return g
def scores(cases,methods):
 out={}
 for g in sorted({g for z in cases for g in z['groups']}):
  xs=[z for z in cases if g in z['groups']];out[g]={'n':len(xs),'players':len({z['mlbam_id'] for z in xs}),'metrics':{}}
  for k in ['PA','AB','H','HR','TB','R','RBI','BB','SB']:
   out[g]['metrics'][k]={}
   for method in methods:
    valid=[z for z in xs if method in z]
    if valid:out[g]['metrics'][k][method]=metric([(z[method].get(k,0),z['actual'].get(k,0)) for z in valid])
 return out
def run():
 existing=[z for z in read(PARENT/'Opportunity_Test_Cases.json.gz') if z['role']=='H'];by={(z['mlbam_id'],z['anchor']):z for z in existing};extraold={(z['mlbam_id'],z['anchor']):z for z in read(PARENT/'Additional_Anchor_Cases.json.gz') if z['role']=='H'};dev={vv:[] for vv in H_VARIANTS};manifest=[]
 for year in [2016,2017,2018,2021,2022]:
  model=fit_hitter(year,development=True);xs=[z for z in records['H'] if z['year']==year and z['id']%5==4 and z['positive_anchor']]
  for vv in H_VARIANTS:
   pred=predict_hitter(model,xs,variant=vv)
   for z,p in zip(xs,pred):dev[vv].append((statscale(historical_baseline(z),p),(target(z) or {}).get('stat',{})))
  print('Hitter development completed',year,flush=True)
 d={vv:{k:metric([(a.get(k,0),b.get(k,0)) for a,b in dev[vv]]) for k in ['PA','HR']} for vv in H_VARIANTS};objective={vv:(d[vv]['PA']['MAE']+.25*abs(d[vv]['PA']['bias']))/600+.2*d[vv]['HR']['MAE']/40 for vv in H_VARIANTS};chosen=min(H_VARIANTS,key=lambda vv:objective[vv]);save('Hitter_Development.json',{'selected':chosen,'scores':d,'objective':objective});print('Selected hitter development',chosen,objective,flush=True)
 cases=[];extras=[];prior_method=read(PARENT/'Opportunity_Validation.json')['selected_by_development']['H']
 for year in [2014,2015,2016,2017,2018,2019,2020,2021,2022,2023,2024]:
  model=fit_hitter(year);manifest.append(model['manifest']);joblib.dump(model,OUT/f'hitter-model-{year}.joblib',compress=3);xs=[z for z in records['H'] if z['year']==year and z['id']%5==0 and (z['positive_anchor'] or z['x'][0]==0)];preds={vv:predict_hitter(model,xs,variant=vv) for vv in H_VARIANTS}
  needs=[z for z in xs if (z['id'],year) not in by and (z['id'],year) not in extraold]
  incumbent={}
  if needs:
   originalmodel=base['fit'](base['training']('H',year),prior_method);ps=base['predict'](originalmodel,needs,prior_method,base['cap_at']('H',year))[0];incumbent={z['id']:float(a) for z,a in zip(needs,ps)}
  for i,z in enumerate(xs):
   key=z['id'],year;b=historical_baseline(z)
   if b is None:continue
   q=copy.deepcopy(by[key]) if key in by else {'mlbam_id':z['id'],'name':z['name'],'anchor':year,'role':'H','groups':z['groups'],'baseline':b,'actual':(target(z) or {}).get('stat',{})}
   q['groups']=list(dict.fromkeys(q['groups']+groups(z)));q['components']={vv:preds[vv][i] for vv in H_VARIANTS}
   if key not in by:
    pa=extraold[key]['primary'] if key in extraold else incumbent[z['id']];q['selected']=statscale(q['baseline'],{'PA':pa})
   for vv in H_VARIANTS:q[vv]=statscale(q['baseline'],preds[vv][i])
   q['hitter_selected']=q[chosen]
   if year+1==2020:q['groups'].append('unexpected_shortened_target_2020')
   if key in by:cases.append(q)
   else:extras.append(q)
  print('Hitter test completed',year,len(cases),len(extras),flush=True)
 assert len(cases)==682 and {(z['mlbam_id'],z['anchor']) for z in cases}==set(by)
 methods=['baseline','selected',*H_VARIANTS,'hitter_selected'];standard=[z for z in extras if z['anchor']+1!=2020];result={'selected':chosen,'preserved':scores(cases,methods),'additional_standard':scores(standard,methods),'additional_all_with_shock':scores(extras,methods),'combined_standard':scores(cases+standard,methods),'manifest':manifest,'scope':'Additional chronological scoring; previous labels and preprocessing already exposed, not pristine confirmation. Shock2020 scored separately.'}
 # Independently documented prior IL placements are historical diagnostic labels only.
 il=read(PARENT/'Verified_Availability_Checks.json')['sources'];ilby={z['mlbam_id']:z for z in il};subset=[]
 for z in cases+standard:
  placements=ilby.get(z['mlbam_id'],{}).get('placements',[])
  if any(f"{z['anchor']-2}-01-01"<=t['date']<=f"{z['anchor']}-12-31" for t in placements):subset.append(z)
 result['documented_prior_IL']=scores(subset,methods);save('Hitter_Validation.json',result);save('Hitter_Cases.json.gz',cases);save('Hitter_Additional_Cases.json.gz',extras)
 for group in ['all','durable_four_years','aging_33plus']:print(group,{k:round(a['MAE'],2) for k,a in result['combined_standard'][group]['metrics']['PA'].items()},flush=True)
if __name__=='__main__':run()
