from hybrid import *
from run_helpers import saveout,csvout
from collections import defaultdict

def ci(xs,key):
 by=defaultdict(list)
 for a in xs:by[a['mlbam_id']].append(abs(a['hybrid'].get(key,0)-a['actual'].get(key,0))-abs(a['strong_prior'].get(key,0)-a['actual'].get(key,0)))
 arrays=list(by.values());rng=np.random.default_rng(2718);sizes=np.array([len(x) for x in arrays]);sums=np.array([sum(x) for x in arrays]);idx=rng.integers(0,len(arrays),(1500,len(arrays)));samples=sums[idx].sum(1)/sizes[idx].sum(1)
 return {'players':len(arrays),'delta_MAE':float(sums.sum()/sizes.sum()),'player_cluster95':np.quantile(samples,[.025,.975]).tolist()}
def score(rows,key):
 result={}
 for g in sorted({g for a in rows for g in a['groups']}):
  xs=[a for a in rows if g in a['groups']];result[g]={'n':len(xs),'metrics':{k:{m:metric([(a[m].get(k,0),a['actual'].get(k,0)) for a in xs]) for m in ['baseline','past_only','strong_prior','hybrid']} for k in (['PA','RBI','HR','R','SB'] if key=='PA' else ['IP','K','QA3','SV','HLD'])},'paired':ci(xs,key)}
 return result
adapter=HybridForecastEngine();allcases={};flat=[];checks=0
for fam in ['P','H']:
 cases=read(HERE.parent/'first-year-repair'/f'{fam}_Cases.json.gz');idx={(z['id'],z['year'],z['role']):z for rr in (['H'] if fam=='H' else ['SP','RP']) for z in records[rr]}
 for number,a in enumerate(cases):
  if number%100==0:print('CASE',fam,number,a['anchor'],a['mlbam_id'],flush=True)
  z=idx[a['mlbam_id'],a['anchor'],a['role']];c=adapter.predict([z],asof=str(z['year'])+'-12-31',incumbent_components={(z['id'],z['year'],z['role']):a['components']['past_only']})[0];q=copy.deepcopy(a);q['strong_prior']=a['revised'];q['hybrid']=stats(a['baseline'],c,z['role'],z);q['hybrid_components']=c;q['groups']=list(dict.fromkeys(a['groups']+['role_'+role_group(z)]));key='PA' if fam=='H' else 'IP'
  if fam=='H':
   anchor=lookup.get((z['id'],z['year'],'H'),{}).get('stat',{})
   if anchor.get('PA',0)>=500 and anchor.get('RBI',0)>=90:q['groups'].append('high_RBI_comparable62')
  if z['role']!='RP':assert_coherent(c,q['hybrid'],z['role'],754 if fam=='H' else 251)
  checks+=1;flat.append({'mlbam_id':z['id'],'name':z['name'],'role':z['role'],'anchor':z['year'],'target_year':z['year']+1,'method':c['hybrid_method'],'actual':q['actual'].get(key,0),'baseline':q['baseline'].get(key,0),'past_only':q['past_only'].get(key,0),'strong_prior':q['strong_prior'].get(key,0),'hybrid':q['hybrid'][key]});allcases.setdefault(fam,[]).append(q)
 print('INTEGRATED HISTORY',fam,len(cases),flush=True)
for f,xs in allcases.items():saveout('Integrated_'+f+'_Cases.json.gz',xs)
p=allcases['P'];h=[a for a in allcases['H'] if a['anchor']+1!=2020];orig=read(HERE.parent/'first-year-repair'/'Original94_Cases.json.gz');by={(a['mlbam_id'],a['anchor']):a for a in p};original=[]
for a in orig:
 q=copy.deepcopy(a);b=by[a['mlbam_id'],a['anchor']];q['strong_prior']=a['revised'];q['hybrid']=stats(a['baseline'],b['hybrid_components'],a['role']);q['groups']=a['groups'];original.append(q)
res={'P_expanded':score(p[:1084],'IP'),'P_all':score(p,'IP'),'H_standard':score(h,'PA'),'original94':score(original,'IP'),'checks':checks,'previous_test_exposure':True};saveout('Integrated_Validation.json',res);csvout('Integrated_Chronological_Comparisons.csv',flat)
gates=[]
for name,pool,g,key,limit in [('original94','original94','all','IP',23.9972),('originalSP','original94','SP','IP',36.8801),('expandedP','P_expanded','all','IP',26.4204),('H_standard','H_standard','all','PA',119.0835)]:
 val=res[pool][g]['metrics'][key]['hybrid']['MAE'];gates.append({'gate':name,'value':val,'limit':limit,'pass':val<=limit})
x=res['H_standard'].get('high_RBI_comparable62')
if x:
 val=abs(x['metrics']['RBI']['hybrid']['bias']);gates.append({'gate':'comparable_high_RBI_bias','n':x['n'],'value':val,'limit':3,'pass':val<=3})
gates.extend([{'gate':'same_date_roster_allocated_independent_population','pass':False,'reason':'Only public conditional ZiPS article sample; January external dates differ from own December input cutoff.'},{'gate':'complete_dated_roster_and_injury_coverage','pass':False,'reason':'Dated evidence contract and team budgets implemented; complete historical organization rosters/return timetables unavailable.'},{'gate':'chronology_and_stat_coherence','pass':True,'checks':checks}]);saveout('Hybrid_Release_Gates.json',{'gates':gates,'ready_for_release_review':False,'deploy_authorized':False,'all_gates_pass':all(a['pass'] for a in gates)});print('GATES',gates,flush=True)
