"""Reuse completed appearance fits; amend QA3 context and conditional workload only."""
from joint_model import *
def augment(model,development=False):
 rows=training(model['asof'],model['horizons'],development,model['calendar'],'P');use=np.array([not z['calibration'] or not development for z in rows]);X=np.stack([xrow(z['z'],z['h'],model['calendar']) for z in rows]);labels=np.array([z['state'] for z in rows]);weights=np.array([z['weight'] for z in rows]);qmask=np.array([bool(z['info'] and z['info']['GP']>0 and z['info']['GS']==0 and z['info']['exact_QA3_available']) for z in rows])&use
 # Exact rare relief QA3 observed totals; raw GP retains actual evidence weight.
 count=sum(z['info']['QA3'] for i,z in enumerate(rows) if qmask[i]);gp=sum(z['info']['GP'] for i,z in enumerate(rows) if qmask[i]);rpq=count/gp if gp else 0;startregs={};direct={};support={}
 for state in [1,2]:
  mask=use&(labels==state)&np.array([bool(z['info'] and z['info']['GS']>0 and z['info']['exact_QA3_available']) for z in rows]);ys=np.array([max(0,min(1,(z['info']['QA3']-z['info']['RA']*rpq)/z['info']['GS'])) if z['info'] and z['info']['GS'] and z['info']['QA3'] is not None else 0 for z in rows]);w=np.array([z['info']['GS'] if z['info'] else 0 for z in rows])*weights;startregs[state]=regfit(X[mask],ys[mask],w[mask]);support[state]=int(mask.sum())
  mask=use&(labels==state);values=np.array([z['value'] for z in rows]);direct[state]=regfit(X[mask],values[mask],weights[mask],state==2)
 model=copy.copy(model);model['principal_QA3']={'start':startregs,'relief_probability':rpq,'start_training_rows':support,'pure_relief_appearances':gp,'pure_relief_QA3':count};model['direct_conditional']=direct;return model
def predict_augmented(model,zs,h=1,blend=False):
 parts=predict_pitch(model,zs,h,'joint_linear_depth');X=np.stack([xrow(z,h,model['calendar']) for z in zs]);q=model['principal_QA3'];p=calibrated_prob(model,X);startprob={l:prediction(q['start'][l],X,0,1) for l in [1,2]};direct={l:prediction(model['direct_conditional'][l],X) for l in [1,2]};out=[]
 for i,z in enumerate(parts):
  sd=z['IP_per_start'];rd=z['IP_per_relief'];ip=0;qa=0;conds={}
  for l in [1,2]:
   c=z['conditional'][str(l)];gs,ra=c['GS'],c['RA'];ss,rs=sd,rd
   if blend:
    total=.5*c['IP']+.5*direct[l][i]
    if l==2 and gs>0:ss=float(np.clip((total-ra*rd)/gs,0,model['caps']['SP_depth']))
    elif ra>0:rs=float(np.clip((total-gs*sd)/ra,0,model['caps']['RP_depth']))
   ci=gs*ss+ra*rs;cq=gs*min(startprob[l][i],ss/5)+ra*min(q['relief_probability'],rs/5);ip+=p[i,l]*ci;qa+=p[i,l]*cq;conds[str(l)]={**c,'IP':float(ci),'QA3':float(cq),'IP_per_start':ss,'IP_per_relief':rs}
  out.append({**z,'IP':float(ip),'QA3':float(min(qa,ip/5)),'conditional':conds,'QA3_principal_context':True,'conditional_blend':blend})
 return out
def run():
 cases=read(OUT/'Joint_Cases.json.gz');extras=read(OUT/'Joint_Additional_Cases.json.gz');bys={(z['mlbam_id'],z['anchor'],z['role']):z for z in cases+extras};manifest=[]
 for year in sorted({z['anchor'] for z in cases+extras}):
  model=augment(joblib.load(OUT/f'pitch-model-{year}-0.joblib'));joblib.dump(model,OUT/f'principal-model-{year}.joblib',compress=3);manifest.append({'anchor':year,'QA3_offset':model['principal_QA3']['relief_probability'],'QA3_support':model['principal_QA3']['start_training_rows']});xs=[z for rr in ['SP','RP'] for z in records[rr] if z['year']==year and (z['id'],year,rr) in bys]
  for method,blend in [('principal_QA3',False),('conditional_blend',True)]:
   pred=predict_augmented(model,xs,blend=blend)
   for z,p in zip(xs,pred):
    q=bys[z['id'],year,z['role']];q[method]=category_stats(q['baseline'],p)|{'GS':p['GS'],'RA':p['RA']};q['components'][method]=p
  print('Principal follow-up',year,flush=True)
 original=read(PARENT.parent/'Historical_Cases.json');by={(z['mlbam_id'],z['anchor']):z for z in cases};frozen=[]
 for z in original:
  q=copy.deepcopy(by[z['mlbam_id'],z['anchor']]);q['baseline']=z['baseline']
  for vv in [*VARIANTS,'joint_selected','principal_QA3','conditional_blend']:q[vv]=category_stats(z['baseline'],q['components'][read(OUT/'Joint_Validation.json')['selected'] if vv=='joint_selected' else vv])
  for vv in ['selected','role_aware','linear_SP']:
   f=q[vv]['IP']/z['baseline']['IP'];q[vv]={k:v*f for k,v in z['baseline'].items()}
  frozen.append(q)
 methods=['baseline','selected','role_aware','linear_SP','joint_selected','principal_QA3','conditional_blend'];save('Principal_Validation.json',{'expanded':scores(cases,methods),'frozen94':scores(frozen,methods),'additional':scores(extras,['baseline','joint_selected','principal_QA3','conditional_blend']),'manifest':manifest,'scope':'Fixed exploratory follow-up after initial QA3 failure; blend50/50 not test-selected. QA3 offset is aggregate modeling, not verified component split.'});save('Principal_Cases.json.gz',cases);save('Principal_Additional_Cases.json.gz',extras)
 print(scores(cases,methods)['all']['metrics']['IP'],flush=True);print(scores(cases,methods)['all']['metrics']['QA3'],flush=True)
if __name__=='__main__':run()
