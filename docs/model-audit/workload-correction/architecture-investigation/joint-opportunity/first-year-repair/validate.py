"""One retrospective check after development freeze. Never selects variants."""
from engine import *
from collections import defaultdict

def cluster_interval(xs,key,comp='past_only',seed=2309):
 by=defaultdict(list)
 for z in xs:by[z['mlbam_id']].append(abs(z['revised'].get(key,0)-z['actual'].get(key,0))-abs(z[comp].get(key,0)-z['actual'].get(key,0)))
 if not by:return None
 arrays=list(by.values());rng=np.random.default_rng(seed);sizes=np.array([len(a) for a in arrays]);sums=np.array([sum(a) for a in arrays]);idx=rng.integers(0,len(arrays),(1500,len(arrays)));samples=sums[idx].sum(axis=1)/sizes[idx].sum(axis=1)
 return {'players':len(arrays),'mean_MAE_change':sum(sums)/sum(sizes),'cluster95':np.quantile(samples,[.025,.975]).tolist(),'resamples':1500}

def score(xs,fam):
 key='PA' if fam=='H' else 'IP';out={}
 for group in sorted({g for z in xs for g in z['groups']}):
  rows=[z for z in xs if group in z['groups']];methods=['baseline','linear_SP','selected','past_only','revised'];out[group]={'n':len(rows),'players':len({z['mlbam_id'] for z in rows}),'metrics':{}}
  for k in (['PA','AB','H','HR','TB','R','RBI','BB','SB'] if fam=='H' else ['IP','K','QA3','ER','BB','H','SV','HLD']):
   out[group]['metrics'][k]={a:metric([(z[a].get(k,0),z['actual'].get(k,0)) for z in rows if a in z]) for a in methods if any(a in z for z in rows)}
  out[group]['paired_vs_joint']=cluster_interval(rows,key)
 return out

def run():
 freeze=read(HERE/'Selection_Freeze.json');assert not freeze['heldout_test_scored'];selected=freeze['selected'];man=[];checks=0;allcases={}
 for fam in ['P','H']:
  keep=read(OUT/('Past_Only_Pitch_Cases.json.gz' if fam=='P' else 'Past_Only_Hitter_Cases.json.gz'));extra=read(OUT/('Past_Only_Pitch_Additional.json.gz' if fam=='P' else 'Past_Only_Hitter_Additional.json.gz'))
  cases=copy.deepcopy(keep+extra);bys={(a['mlbam_id'],a['anchor'],a['role']):a for a in cases}
  for year in sorted({a['anchor'] for a in cases}):
   model=joblib.load(HERE/f'test-{fam}-{year}.joblib') if (HERE/f'test-{fam}-{year}.joblib').exists() and (HERE/f'test-{fam}-{year}.joblib').stat().st_size>0 else fit(year,fam);checkpoint(model,HERE/f'test-{fam}-{year}.joblib',compress=3);man.append(model['manifest']);xs=[z for rr in (['SP','RP'] if fam=='P' else ['H']) for z in records[rr] if z['year']==year and (z['id'],year,z['role']) in bys]
   inc=[bys[z['id'],year,z['role']]['components']['past_only'] for z in xs];new=inc if selected[fam]=='incumbent' else opportunity(model,xs,inc,selected[fam])
   for z,c in zip(xs,new):
    a=bys[z['id'],year,z['role']];a['revised_components']=c;a['revised']=stats(a['baseline'],c,z['role'],z);a['groups']=list(dict.fromkeys(a['groups']+[cohort(z)]))
    if fam=='H':
     if z['x'][0]>=400:a['groups'].append('all_everyday')
     if z['x'][0]>=600:a['groups'].append('high_PA')
     current=lookup.get((z['id'],year,'H'),{}).get('stat',{})
     if current.get('RBI',0)>=90:a['groups'].append('high_RBI')
    if fam=='P' and z['role']=='RP':
     # Retained RP expert is checked for expected/IP/QA3 consistency, not re-fitted.
     assert a['revised']['QA3']<=a['revised']['IP']/5+1e-7
    else:assert_coherent(c,a['revised'],z['role'],model['cap']);checks+=1
   print('Test scored',fam,year,len(xs),flush=True)
  put(f'{fam}_Cases.json.gz',cases);n=len(keep);allcases[fam]=(cases[:n],cases[n:])
 p,pe=allcases['P'];h,he=allcases['H'];original=read(PARENT.parent/'Historical_Cases.json');idx={(z['mlbam_id'],z['anchor']):z for z in p};frozen=[]
 for z in original:
  q=copy.deepcopy(idx[z['mlbam_id'],z['anchor']]);q['baseline']=z['baseline'];q['groups']=z['subgroups']+['all','original94'];q['actual']=z['actual']
  for method in ['linear_SP','past_only','revised']:
   c=q['revised_components'] if method=='revised' else q['components']['past_only'] if method=='past_only' else {'IP':q['linear_SP']['IP'],'QA3':q['linear_SP']['QA3'],'GS':0,'RA':0}
   q[method]=stats(q['baseline'],c,q['role'],mixture_leverage=method=='revised')
  frozen.append(q)
 put('Original94_Cases.json.gz',frozen)
 hs=h+[z for z in he if z['anchor']+1!=2020];res={'pitch_expanded':score(p,'P'),'pitch_additional':score(pe,'P'),'original94':score(frozen,'P'),'hitter_preserved':score(h,'H'),'hitter_combined_standard':score(hs,'H'),'hitter_shock2020':score([z for z in he if z['anchor']+1==2020],'H'),'manifests':man,'physical_checks':checks,'selection_unchanged':selected,'scope':'Previously exposed retrospective safety benchmark; selected exactly once using ID4 development before these scores. Category-rate/aging normalizers preserved for fair workload comparison, not newly certified past-only talent.'}
 put('Validation.json',res)
 limits=[('expanded_P','pitch_expanded','all','IP',26.4204),('expanded_SP','pitch_expanded','SP','IP',47.376),('young_SP','pitch_expanded','young_SP','IP',43.4103),('original94','original94','all','IP',23.9972),('original_SP','original94','SP','IP',36.8801),('H_combined','hitter_combined_standard','all','PA',119.0835),('H_preserved','hitter_preserved','all','PA',133.81)]
 gates=[]
 for label,pool,g,k,limit in limits:
  measured=res[pool][g]['metrics'][k]['revised']['MAE'];gates.append({'gate':label,'value':measured,'maximum':limit,'pass':measured<=limit})
 for label,pool,g,k,tol in [('established_SP_bias','pitch_expanded','established_SP','IP',3),('everyday_H_MAE','hitter_combined_standard','all_everyday','PA',5),('high_RBI_MAE','hitter_combined_standard','high_RBI','RBI',1)]:
  s=res[pool][g]['metrics'][k];before=abs(s['past_only']['bias']) if 'bias' in label else min(s[a]['MAE'] for a in ['selected','past_only'] if a in s);after=abs(s['revised']['bias']) if 'bias' in label else s['revised']['MAE'];gates.append({'gate':label,'value':after,'maximum':before+tol,'pass':after<=before+tol})
 s=res['hitter_combined_standard']['high_RBI']['metrics']['RBI']['revised'];gates.append({'gate':'high_RBI_signed_bias','value':abs(s['bias']),'maximum':3,'pass':abs(s['bias'])<=3})
 for pool in ['pitch_expanded','hitter_combined_standard']:
  key='IP' if pool=='pitch_expanded' else 'PA'
  for g,s in res[pool].items():
   if not g.startswith('anchor_') or s['n']<30:continue
   a=s['metrics'][key];diff=s['paired_vs_joint'];critical=a['revised']['MAE']>a['past_only']['MAE']*1.1 and diff['cluster95'][0]>0
   gates.append({'gate':pool+'_'+g+'_stability','value':a['revised']['MAE'],'joint':a['past_only']['MAE'],'cluster95':diff['cluster95'],'pass':not critical})
 for pool,fam,groups in [('pitch_expanded','P',['stable_rotation','interrupted']),('hitter_combined_standard','H',['durable_four_years','interrupted'])]:
  key='IP' if fam=='P' else 'PA'
  for g in groups:
   s=res[pool].get(g)
   if not s:continue
   a=s['metrics'][key];diff=s['paired_vs_joint'];critical=a['revised']['MAE']>a['past_only']['MAE']*1.1 and diff['cluster95'][0]>0
   gates.append({'gate':pool+'_'+g+'_cohort','n':s['n'],'value':a['revised']['MAE'],'joint':a['past_only']['MAE'],'cluster95':diff['cluster95'],'pass':not critical})
 gates.append({'gate':'expert_chronology_and_mean_stat_coherence','pass':True,'checked':checks})
 put('Release_Gates.json',{'gates':gates,'historical_workload_pass':all(a['pass'] for a in gates),'ready_for_release_review':False,'additional_required':['Independent matched forecast diagnostic and attribution limitations','First-year adapter replay and frozen future-path verification','Resolve any failed critical numerical gates'],'selected':selected,'no_test_reselection':True})
 print('GATES',json.dumps(gates),flush=True)
if __name__=='__main__':run()
