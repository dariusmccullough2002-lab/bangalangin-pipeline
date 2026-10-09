"""Additive path-valued uncertainty and bounded RBI/opportunity diagnostics."""
import sys
from pathlib import Path
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent))
from shared import *
import csv,itertools,collections
from sklearn.linear_model import Ridge
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

def put(name,d):
 data=json.dumps(d,allow_nan=False,default=lambda a:a.item() if isinstance(a,np.generic) else a).encode()
 (HERE/name).write_bytes(gzip.compress(data,mtime=0) if name.endswith('.gz') else data)
def writecsv(name,rows):
 cols=list(dict.fromkeys(k for a in rows for k in a));f=(HERE/name).open('w',newline='');w=csv.DictWriter(f,cols);w.writeheader();w.writerows(rows);f.close()

league=read(OUT/'Past_Only_League_Impact.json.gz')
hcases=read(OUT/'Past_Only_Hitter_Cases.json.gz');hextra=read(OUT/'Past_Only_Hitter_Additional.json.gz')
pcases=read(OUT/'Past_Only_Pitch_Cases.json.gz');pextra=read(OUT/'Past_Only_Pitch_Additional.json.gz')

def state(ident,y,fam):
 a=lookup.get((ident,y,fam));s=a['stat'] if a else {}
 if fam=='H':return 0 if s.get('PA',0)<=0 else 2 if s['PA']*(162/60 if y==2020 else 1)>=400 else 1
 c=counts(ident,y)
 return 0 if s.get('IP',0)<=0 else 2 if c and c['GP'] and c['GS']/c['GP']>=.5 else 1
@functools.lru_cache(None)
def transition(fam,asof,ab):
 C=np.ones((3,3));n=0;latest=0
 for (ident,stream),rows in hist.items():
  if stream!=fam or ident%5 in [0,4]:continue
  firsty=min(a['year'] for a in rows)
  lasty=max(a['year'] for a in rows)
  # Ending past observed history is genuine recorded MLB absence, not a missing 2026 target.
  for year in range(max(2011,firsty),min(asof,2025)):
   age=r.age_at(ident,year)
   if age is None or r.agebin(age)!=ab or year in [2019,2020]:continue
   C[state(ident,year,fam),state(ident,year+1,fam)]+=1;n+=1;latest=max(latest,year+1)
 # Smooth empty age groups towards independence; every cell remains positive.
 T=C/C.sum(axis=1,keepdims=True)
 return T,{'family':fam,'asof':asof,'agebin':ab,'pairs':n,'latest_target':latest,'fit_ID_mods':[1,2,3],'matrix':T.tolist()}

def transport(a,b,T):
 a=np.asarray(a,float);b=np.asarray(b,float);Q=np.maximum(1e-300,a[:,None]*T)
 for i in range(500):
  Q*=np.divide(a,Q.sum(axis=1),out=np.zeros(3),where=Q.sum(axis=1)>0)[:,None]
  Q*=np.divide(b,Q.sum(axis=0),out=np.zeros(3),where=Q.sum(axis=0)>0)[None,:]
  if max(np.max(abs(Q.sum(axis=1)-a)),np.max(abs(Q.sum(axis=0)-b)))<1e-11:break
 assert np.max(abs(Q.sum(axis=1)-a))<1e-8 and np.max(abs(Q.sum(axis=0)-b))<1e-8
 return Q

def marg(c,rr):return np.array([c['probabilities'][s] for s in (['absent','part_time','regular'] if rr=='H' else ['absent','RP','SP'])])

def score_pairs(xs):return {'n':len(xs),'mean_logloss':float(np.mean([-math.log(max(x,1e-12)) for x in xs])) if xs else None}
def path_validation():
 hs=read(OUT/'Past_Only_Horizon_Cases.json.gz');d={};out={};manifest=[]
 for fam in ['H','P']:
  scores={k:[] for k in ['independent','associated']};groups={}
  by=collections.defaultdict(dict)
  for z in hs:
   if ('H' if z['role']=='H' else 'P')==fam:by[z['mlbam_id'],z['anchor'],z['role']][z['horizon']]=z
  for (ident,anchor,rr),years in by.items():
   for h,z in years.items():
    if h+1 not in years:continue
    q=years[h+1];a=marg(z['components'],rr);b=marg(q['components'],rr);age=r.age_at(ident,anchor+h)
    T,man=transition(fam,anchor,r.agebin(age));Q=transport(a,b,T)
    s=state(ident,anchor+h,fam);t=state(ident,anchor+h+1,fam)
    for k,val in [('independent',a[s]*b[t]),('associated',Q[s,t])]:scores[k].append(val);groups.setdefault(str(anchor),{kk:[] for kk in scores})[k].append(val)
    manifest.append(man)
  out[fam]={'test':{k:score_pairs(a) for k,a in scores.items()},'by_anchor':{y:{k:score_pairs(a) for k,a in ss.items()} for y,ss in groups.items()}}
 # Development pair association selection uses observed current/next state joint frequencies,
 # fixed transition estimator; target years completed by forecast anchor+2.
 for fam in ['H','P']:
  ds={k:[] for k in ['independent','associated']}
  for (ident,stream),rows in hist.items():
   if stream!=fam or ident%5!=4:continue
   for anchor in [2016,2017,2018,2021,2022]:
    if anchor<min(z['year'] for z in rows):continue
    age=r.age_at(ident,anchor)
    if age is None:continue
    T,_=transition(fam,anchor,r.agebin(age));s=state(ident,anchor+1,fam);t=state(ident,anchor+2,fam)
    freq=T.sum(axis=0)/3;Q=transport(freq,freq,T)
    ds['independent'].append(freq[s]*freq[t]);ds['associated'].append(Q[s,t])
  sc={k:score_pairs(a) for k,a in ds.items()};chosen=min(sc,key=lambda k:sc[k]['mean_logloss']);d[fam]={'selected':chosen,'scores':sc,'scope':'Transition association development uses pooled stationary proxy marginals, not fitted player marginals. Fixed estimator evaluation; not player-specific joint calibration.'}
 put('Path_Validation.json',{'development':d,'chronological_test':out,'manifests':list({json.dumps(z,sort_keys=True):z for z in manifest}.values()),'scope':'Retrospective pair likelihood on saved horizons2–6; no horizon7/8 confirmation. Association fitted from past-only core identities. Development proxy design is limited.'})
 return d

@functools.lru_cache(None)
def leagueprior(y):
 xs=[z for z in old.AN if z['role']=='H' and z['year']<=min(y,2025) and z['id']%5 not in [0,4] and z['year']!=2020]
 return sum(z['stat'].get('RBI',0) for z in xs)/sum(z['stat']['PA'] for z in xs)
def rate(ident,y,strength,rows=None):
 rows=hist.get((ident,'H'),[]) if rows is None else rows
 xs=[a for a in rows if y-3<=a['year']<=y and a['stat'].get('PA',0)>0];weights=[(a['year']-(y-4))/10 for a in xs];mass=sum(weights)
 if not mass:return leagueprior(y),{}
 pa=sum(a['stat']['PA']*w/mass for a,w in zip(xs,weights));rbi=sum(a['stat'].get('RBI',0)*w/mass for a,w in zip(xs,weights));prior=leagueprior(y);value=(rbi+strength*prior)/(pa+strength)
 return value,{'season_weights':{str(a['year']):w/mass for a,w in zip(xs,weights)},'weighted_PA':pa,'weighted_RBI':rbi,'raw_RBI_PA':rbi/pa,'league_prior':prior,'pseudocount_PA':strength,'prior_fraction':strength/(pa+strength)}
def rbi_groups(ident,y):
 a=lookup.get((ident,y,'H'),{}).get('stat',{});g=['all',f'anchor_{y}'];age=r.age_at(ident,y)
 if a.get('PA',0)>=500 and a.get('RBI',0)>=90:g+=['high_RBI_anchor']
 if age and age>=33:g+=['aging33plus']
 if a.get('PA',0)>=600:g+=['everyday600']
 return g

def rbi_audit():
 dev={str(s):[] for s in [0,25,100,300]};devrows=[]
 for z in records['H']:
  if z['id']%5!=4 or z['year'] not in [2016,2017,2018,2021,2022] or not z['positive_anchor']:continue
  y=z['year'];t=(target(z) or {}).get('stat',{});b=historical_baseline(z)
  if b is None:continue
  for s in [0,25,100,300]:
   rr,_=rate(z['id'],y,s);dev[str(s)].append((rr*b['PA'],t.get('RBI',0)))
 score={k:metric(a) for k,a in dev.items()};chosen=int(min(score,key=lambda k:score[k]['MAE']+.25*abs(score[k]['bias'])))
 out=[]
 for z in hcases+[a for a in hextra if a['anchor']+1!=2020]:
  ident,y=z['mlbam_id'],z['anchor'];pa=z['past_only']['PA'];actual=z['actual'];q={'mlbam_id':ident,'name':z['name'],'anchor':y,'groups':rbi_groups(ident,y),'actual':actual.get('RBI',0),'actual_PA':actual.get('PA',0),'baseline':z['baseline'].get('RBI',0),'incumbent':z['past_only'].get('RBI',0),'PA':pa,'preserved':z in hcases}
  for s in [0,25,100,300]:
   rr,_=rate(ident,y,s);q[f'strength{s}']=rr*pa;q[f'rate_diagnostic{s}']=rr*actual.get('PA',0)
  q['selected']=q[f'strength{chosen}'];out.append(q)
 sc={}
 for g in sorted({g for z in out for g in z['groups']}|{'preserved682'}):
  xs=[z for z in out if z['preserved']] if g=='preserved682' else [z for z in out if g in z['groups']]
  sc[g]={k:metric([(z[k],z['actual']) for z in xs]) for k in ['baseline','incumbent','selected',*[f'strength{s}' for s in [0,25,100,300]],*[f'rate_diagnostic{s}' for s in [0,25,100,300]]]}
 put('RBI_Validation.json',{'selected_pseudocount':chosen,'development':score,'scores':sc,'scope':'Selected strength on forecast-date group4 baseline workload development. Test uses fixed past-only workload. Conditional actual-PA diagnostics are not deployable forecasts. New priors past-only; existing talent aging not applied to these direct one-year rates. Context not in cached annual features.'});put('RBI_Cases.json.gz',out)
 current=[]
 for z in league:
  if z.get('role')!='H' or z['status']!='supported_MLB':continue
  p=old.players[z['id']];rows=v.seasons(p,'H');ident=z['mlbam_id'];rr,a=rate(ident,2026,chosen,rows);au=v.mlb_role_paths(p,'H')[1]['projection_audit'];b=z['baseline_annual'][0];histrows=[{'year':x['year'],'PA':x['stat'].get('PA'),'RBI':x['stat'].get('RBI'),'HR':x['stat'].get('HR')} for x in rows]
  current.append({'id':z['id'],'mlbam_id':ident,'name':z['name'],'baseline_PA':b['PA'],'baseline_RBI':b['RBI'],'baseline_rate':b['RBI']/b['PA'],'new_rate':rr,'RBI_rate_only':rr*b['PA'],'joint_PA':z['variants']['joint_principal']['annual'][0]['PA'],'RBI_joint_workload':rr*z['variants']['joint_principal']['annual'][0]['PA'],'rate_evidence':a,'production_talent_rate':au['talent_rates']['RBI'],'production_workload':au['projected_workload'],'production_recent_workload':au['recent_workload'],'history':histrows,'production_year1_rate_aging':b['RBI']/b['PA']/au['talent_rates']['RBI']})
 put('RBI_Current_Audit.json.gz',current)
 return chosen,{z['id']:z for z in current}

# Exact discounted path moments: retain probability of every Markov history without sampling.
def moments(p,trans,emissions,w):
 mass=p[0].copy();M=mass*emissions[0]*w[0];S=mass*(emissions[0]*w[0])**2
 for t in range(1,8):
  mass=mass@trans[t-1];priorM=M@trans[t-1];priorS=S@trans[t-1];reward=emissions[t]*w[t]
  M=priorM+mass*reward;S=priorS+2*reward*priorM+mass*reward**2
 return float(M.sum()),float(S.sum())

def conditional_states(c,rr):
 p=marg(c,rr)
 if rr=='H':
  raw=np.array([0,c['conditional_part_PA'],c['conditional_regular_PA']]);scale=c['PA']/(p@raw) if p@raw else 0;work=raw*scale
  return p,work,[{}, {}, {}],scale
 return p,np.array([0,c['conditional']['1']['IP'],c['conditional']['2']['IP']]),[{},c['conditional']['1'],c['conditional']['2']],1

def full_league(dev,rbi):
 assets={z['id']:z for z in catalog['assets']};result=[];flat=[];diagnostics=[];checks={'max_workload_mean_difference':0.,'max_probability_error':0.,'emission_checks':0,'enumeration_checks':0};transmanifest=[]
 for ix,z in enumerate(league):
  row={'id':z['id'],'name':z['name'],'role':z['role'],'status':z['status'],'baseline':z['baseline_values'],'prior_mean_values':z['variants']['joint_principal']['values'],'variants':{}}
  if z['status']!='supported_MLB':
   for name in ['paths_independent','paths_correlated','paths_RBI']:row['variants'][name]={'values':z['baseline_values']}
   result.append(row);continue
  rr=z['role'];fam='H' if rr=='H' else 'P';pplayer=old.players[z['id']];paths,_=m.paths(pplayer);ma=v.mlb_role_paths(pplayer,rr)[1];branchprob=np.array([a[0] for a in paths[:3]]);states=ma['outcome_state_projections'];means=ma['annual_projection'];new=z['variants']['joint_principal'];probs=[];state_stats=[];emission_base=[];emission_role=[];emission_rbi=[];annual_expect=[];scaleH=[]
  for t in range(8):
   c=new['components'][t];p,work,conds,hs=conditional_states(c,rr);scaleH.append(hs);probs.append(p);key='PA' if rr=='H' else 'IP';assert abs(p@work-c[key])<1e-6
   checks['max_workload_mean_difference']=max(checks['max_workload_mean_difference'],abs(p@work-c[key]));stats=[];utilities=[];roleutilities=[];rbiutilities=[];expect={}
   for j in range(3):
    factor=states[j][t][key]/means[t][key] if means[t][key] else 0;us=[];urs=[];ubs=[];ss=[]
    for s in range(3):
     st={k:(val*work[s]/new['annual'][t][key]*factor if new['annual'][t][key] else 0) for k,val in new['annual'][t].items()}
     if rr=='H':st=v.reconcile(st);assert st['HR']<=st['H']<=st['AB']<=st['PA']+1e-7 and st['H']+3*st['HR']<=st['TB']+1e-7
     else:
      st['QA3']=conds[s].get('QA3',0)*factor;assert st['QA3']<=st['IP']/5+1e-7
     checks['emission_checks']+=1;ss.append(st);us.append(r.utility(r.surplus(st,rr)))
     # Role-specific replacement is separated from fixed-role Jensen effect. Frozen per-IP rates retained.
     future_rr=rr if rr=='H' or s==0 else 'RP' if s==1 else 'SP';urs.append(r.utility(r.surplus(st,future_rr)))
     rb=dict(st)
     if rr=='H':
      ratio=rbi[z['id']]['new_rate']/z['baseline_annual'][0]['RBI']*z['baseline_annual'][0]['PA'] if z['baseline_annual'][0]['RBI'] else 1;rb['RBI']*=ratio
     ubs.append(r.utility(r.surplus(rb,future_rr)))
    stats.append(ss);utilities.append(us);roleutilities.append(urs);rbiutilities.append(ubs)
   state_stats.append(stats);emission_base.append(utilities);emission_role.append(roleutilities);emission_rbi.append(rbiutilities)
   annual_expect.append({k:float(sum(p[s]*stats[1][s].get(k,0) for s in range(3))) for k in new['annual'][t]})
  probs=np.array(probs);emission_base=np.array(emission_base);emission_role=np.array(emission_role);emission_rbi=np.array(emission_rbi);trans=[];Qs=[];ind=[]
  for t in range(7):
   age=z['age']+t+1;T,man=transition(fam,2026,r.agebin(age));Q=transport(probs[t],probs[t+1],T);K=np.divide(Q,probs[t][:,None],out=np.tile(probs[t+1],(3,1)),where=probs[t][:,None]>0);trans.append(K);Qs.append(Q);ind.append(np.tile(probs[t+1],(3,1)));transmanifest.append(man)
  specs={'paths_independent':(ind,emission_base),'paths_correlated':(trans if dev[fam]['selected']=='associated' else ind,emission_base),'paths_role_floor':(trans,emission_role),'paths_RBI':(trans,emission_rbi)}
  for name,(K,E) in specs.items():
   fits={};disp={};inddisp={}
   for mode in r.MODES:
    discount={'neutral':.88,'balanced':.88,'contender':.75,'rebuild':.94}[mode];w=np.array([discount**t for t in range(8)]);w*=sum(old.weights('neutral'))/sum(w);mu=second=0
    for j in range(3):
     a,b=moments(probs,K,E[:,j,:],w);mu+=branchprob[j]*a;second+=branchprob[j]*b
    for pr,path in paths[3:]:value=float(np.array(path)@w);mu+=pr*value;second+=pr*value**2
    fits[mode]=r.DISPLAY*mu;disp[mode]=r.DISPLAY*math.sqrt(max(0,second-mu*mu))
   row['variants'][name]={'values':fits,'dispersion':disp}
  row['annual_expected_base_state']=annual_expect;row['probabilities']=probs.tolist();row['transition_kernels']=[a.tolist() for a in trans];row['hitter_conditional_mean_scale']=scaleH
  result.append(row)
  if z['name'] in ['Juan Soto','Aaron Judge','Jose Ramirez','José Ramírez','Matt Olson','Freddie Freeman','Jacob Misiorowski','Paul Skenes','Zack Wheeler','Nolan McLean','Cade Smith','Pete Alonso','Vinnie Pasquantino']:
   # Full exact enumeration independently checks DP across all 6,561 role paths.
   atoms=[];w=np.array([.88**t for t in range(8)]);w*=sum(old.weights('neutral'))/sum(w)
   for seq in itertools.product(range(3),repeat=8):
    pr=probs[0,seq[0]]
    for t in range(1,8):pr*=trans[t-1][seq[t-1],seq[t]]
    util=[[float(emission_base[t,j,seq[t]]) for t in range(8)] for j in range(3)];atoms.append({'probability':float(pr),'states':seq,'talent_utility_paths':util})
   assert abs(sum(a['probability'] for a in atoms)-1)<1e-8
   exact=sum(a['probability']*sum(branchprob[j]*float(np.array(a['talent_utility_paths'][j])@w) for j in range(3)) for a in atoms)+sum(pr*float(np.array(path)@w) for pr,path in paths[3:])
   # Mean independent of association under additive annual utility.
   assert abs(exact*r.DISPLAY-row['variants']['paths_independent']['values']['neutral'])<1e-6;checks['enumeration_checks']+=1
   diagnostics.append({'id':z['id'],'name':z['name'],'role':rr,'annual_stats_by_talent_and_role':state_stats,'baseline_annual':z['baseline_annual'],'mean_annual':new['annual'],'probabilities':probs.tolist(),'kernels':[a.tolist() for a in trans],'values':row,'atoms':atoms})
  if ix%250==0:print('Path league',ix,flush=True)
 # Rank all variants against preserved catalog inclusive picks/prospects.
 for name in ['baseline','prior_mean','paths_independent','paths_correlated','paths_role_floor','paths_RBI']:
  key=lambda z:z['baseline'] if name=='baseline' else z['prior_mean_values'] if name=='prior_mean' else z['variants'].get(name,{'values':z['baseline']})['values']
  for rank,z in enumerate(sorted([a for a in result if key(a).get('neutral') is not None],key=lambda a:-key(a)['neutral']),1):z.setdefault('ranks',{})[name]=rank
 for z in result:
  q={k:z[k] for k in ['id','name','role','status']}
  for mode in r.MODES:q['baseline_'+mode]=z['baseline'][mode];q['prior_mean_'+mode]=z['prior_mean_values'][mode]
  for name,va in z['variants'].items():
   for mode in r.MODES:q[name+'_'+mode]=va['values'][mode];q[name+'_delta_'+mode]=va['values'][mode]-z['baseline'][mode] if va['values'][mode] is not None and z['baseline'][mode] is not None else None;q[name+'_sd_'+mode]=va.get('dispersion',{}).get(mode)
  for k,vv in z.get('ranks',{}).items():q[k+'_rank']=vv
  flat.append(q)
 put('Path_League_Impact.json.gz',result);writecsv('Path_League_Impact.csv',flat);put('Diagnostic_Path_Atoms.json.gz',diagnostics);put('Path_Integrity.json',checks);put('Transition_Manifests.json',list({json.dumps(z,sort_keys=True):z for z in transmanifest}.values()))
 return result,checks

if __name__=='__main__':
 dev=path_validation();print('Transition validation saved',flush=True)
 strength,rb=rbi_audit();print('RBI selected',strength,flush=True)
 results,checks=full_league(dev,rb);print('Completed paths',checks,flush=True)
