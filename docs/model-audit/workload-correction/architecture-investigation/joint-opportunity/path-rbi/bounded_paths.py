"""Bound role-conditioned workload and inherited amplitudes; retain unbounded experiment."""
import sys
from pathlib import Path
HERE=Path(__file__).resolve().parent;sys.path.insert(0,str(HERE.parent))
from continuation import *

def caps_at(y):
 return {role:max(z['stat'].get('PA' if role=='H' else 'IP',0) for z in old.AN if z['role']==role and z['id']%5 not in [0,4] and z['year']<=min(y,2025)) for role in ['H','RP','SP']}

def bounded_work(c,role,cap):
 p,raw,conds,_=conditional_states(c,role)
 if role!='H':return p,np.minimum(raw,[0,cap['RP'],cap['SP']]),conds
 # Match saved hurdle mean only inside role-support bounds. Infeasibility is explicit.
 lo=np.array([0,0,400.]);hi=np.array([0,400.,cap['H']]);target=c['PA'];raw=np.array([0,c['conditional_part_PA'],c['conditional_regular_PA']]);goal=min(p@hi,max(p@lo,target));left,right=0.,10.
 for _ in range(70):
  mid=(left+right)/2;work=np.clip(raw*mid,lo,hi)
  if p@work<goal:left=mid
  else:right=mid
 return p,np.clip(raw*((left+right)/2),lo,hi),[{}, {}, {}]

def run():
 bounds=caps_at(2026);prior={z['id']:z for z in read(HERE/'Path_League_Impact.json.gz')};out=[];annual=[];gates={'caps_completed_through':2025,'caps_from_nonholdout_core':bounds,'emissions':0,'hitter_mean_infeasible_rows':0,'max_base_mean_workload_difference':0.,'inherited_amplitude_clipped':0};checks=[]
 for z in league:
  row={'id':z['id'],'name':z['name'],'role':z['role'],'status':z['status'],'baseline':z['baseline_values'],'prior_mean':z['variants']['joint_principal']['values']}
  if z['status']!='supported_MLB':row['values']=z['baseline_values'];out.append(row);continue
  role=z['role'];key='PA' if role=='H' else 'IP';ps,_=m.paths(old.players[z['id']]);ma=v.mlb_role_paths(old.players[z['id']],role)[1];bp=np.array([a[0] for a in ps[:3]]);new=z['variants']['joint_principal'];P=[];E=[];statsout=[]
  for t in range(8):
   c=new['components'][t];p,work,conds=bounded_work(c,role,bounds);P.append(p);diff=float(p@work-c[key]);gates['max_base_mean_workload_difference']=max(gates['max_base_mean_workload_difference'],abs(diff));gates['hitter_mean_infeasible_rows']+=int(role=='H' and abs(diff)>1e-6);per=[];bs=[]
   for j in range(3):
    factor=ma['outcome_state_projections'][j][t][key]/ma['annual_projection'][t][key] if ma['annual_projection'][t][key] else 0;u=[]
    for s in range(3):
     future=role if role=='H' or s==0 else 'RP' if s==1 else 'SP';cap=0 if s==0 else 400 if role=='H' and s==1 else bounds[future];w=min(cap,work[s]*factor);gates['inherited_amplitude_clipped']+=int(w+1e-8<work[s]*factor)
     st={k:(v*w/new['annual'][t][key] if new['annual'][t][key] else 0) for k,v in new['annual'][t].items()}
     if role=='H':st=v.reconcile(st);st['RBI']=min(4*st['PA'],max(st['HR'],st['RBI']));assert st['HR']<=st['H']<=st['AB']<=st['PA']+1e-7
     else:st['QA3']=min(w/5,conds[s].get('QA3',0)*w/work[s] if work[s] else 0)
     assert st[key]<=cap+1e-7 and st[key]>=0;u.append(r.utility(r.surplus(st,future)));gates['emissions']+=1
     if j==1:bs.append(st)
    per.append(u)
   E.append(per);mean={k:float(sum(p[s]*bs[s].get(k,0) for s in range(3))) for k in new['annual'][t]};annual.append({'id':z['id'],'name':z['name'],'role':role,'horizon':t+1,'target_mean_workload':c[key],'bounded_base_mean_difference':diff,**mean});statsout.append(mean)
  P=np.array(P);E=np.array(E);K=[np.array(k) for k in prior[z['id']]['transition_kernels']];values={};sd={}
  for mode in r.MODES:
   d={'neutral':.88,'balanced':.88,'contender':.75,'rebuild':.94}[mode];w=np.array([d**t for t in range(8)]);w*=sum(old.weights('neutral'))/sum(w);mu=second=0
   for j in range(3):a,b=moments(P,K,E[:,j,:],w);mu+=bp[j]*a;second+=bp[j]*b
   for pr,path in ps[3:]:v0=float(np.array(path)@w);mu+=pr*v0;second+=pr*v0*v0
   values[mode]=r.DISPLAY*mu;sd[mode]=r.DISPLAY*math.sqrt(max(0,second-mu*mu))
  row.update(values=values,dispersion=sd,annual=statsout);out.append(row)
 # Historical bounded mixture scoring, keeping the empirical bound chronological.
 for fam,xs in [('H',hcases+[z for z in hextra if z['anchor']+1!=2020]),('P',pcases)]:
  for z in xs:
   role=z['role'];key='PA' if role=='H' else 'IP';c=z['components']['past_only'];p,w,_=bounded_work(c,role,caps_at(z['anchor']));actual=z['actual'].get(key,0)
   crps=float(p@abs(w-actual)-.5*np.sum(p[:,None]*p[None,:]*abs(w[:,None]-w[None,:])));checks.append({'family':fam,'mlbam_id':z['mlbam_id'],'anchor':z['anchor'],'role':role,'groups':z['groups'],'CRPS':crps,'mean_error':float(p@w-actual),'mean_shift':float(p@w-c[key])})
 sc={}
 for fam in ['H','P']:
  ys=[z for z in checks if z['family']==fam];sc[fam]={g:{'n':len(xs:= [z for z in ys if g in z['groups']]),'CRPS':float(np.mean([z['CRPS'] for z in xs])),'workload_MAE':float(np.mean([abs(z['mean_error']) for z in xs])),'workload_bias':float(np.mean([z['mean_error'] for z in xs])),'infeasible_mean_rows':sum(abs(z['mean_shift'])>1e-6 for z in xs)} for g in sorted({g for z in ys for g in z['groups']})}
 for name in ['baseline','prior_mean','values']:
  for rank,z in enumerate(sorted([a for a in out if a[name].get('neutral') is not None],key=lambda a:-a[name]['neutral']),1):z.setdefault('ranks',{})[name]=rank
 flat=[]
 for z in out:
  q={k:z[k] for k in ['id','name','role','status']}
  for name in ['baseline','prior_mean','values']:
   for mode,val in z[name].items():q[name+'_'+mode]=val
  for mode,val in z.get('dispersion',{}).items():q['sd_'+mode]=val
  for name,val in z.get('ranks',{}).items():q[name+'_rank']=val
  flat.append(q)
 put('Bounded_Path_League.json.gz',out);writecsv('Bounded_Path_League.csv',flat);writecsv('Bounded_Annual_Production.csv',annual);put('Bounded_Path_Integrity.json',gates);put('Bounded_Distribution_Validation.json',sc);put('Bounded_Distribution_Cases.json.gz',checks);print('Bounded gates',gates,flush=True)
if __name__=='__main__':run()
