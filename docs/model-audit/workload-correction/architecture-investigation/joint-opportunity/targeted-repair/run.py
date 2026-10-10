"""Frozen development selection, untouched2025->2026 evaluation, league replay."""
from engine import *
import joblib,unicodedata
METHODS=['direct_mean','capacity_mean','mean_half'];PROBS=['global_logistic','supported_cohort_logistic']

def model_for(year,fam):
 p=HERE/f'model-{fam}-{year}.joblib'
 if p.exists():
  m=joblib.load(p)
  if fam=='H' and 'legacy_count_mean' not in m:
   cp=HERE.parent/'roster-opportunity'/('current-H.joblib' if year==2026 else f'dev-H-{year}.joblib' if year in [2016,2017,2018,2021,2022] else f'test-H-{year}.joblib');cm=joblib.load(HERE/'benchmark-count-H-2025.joblib') if year==2025 else joblib.load(cp);m['legacy_count_mean']=cm['tree'];legacy.prior.checkpoint(m,p)
  return m
 m=fit_model(year,fam)
 if fam=='H':
  cp=HERE.parent/'roster-opportunity'/('current-H.joblib' if year==2026 else f'dev-H-{year}.joblib' if year in [2016,2017,2018,2021,2022] else f'test-H-{year}.joblib');cm=joblib.load(HERE/'benchmark-count-H-2025.joblib') if year==2025 else joblib.load(cp);m['legacy_count_mean']=cm['tree']
 legacy.prior.checkpoint(m,p);print('FIT',fam,year,m['manifest'],flush=True);return m

def value(c,fam):return c['PA' if fam=='H' else 'IP']
def score(rows,methods):
 return {g:{m:metric([(a[m],a['actual']) for a in rows if g in a['groups']]) for m in methods} for g in sorted({g for a in rows for g in a['groups']})}

def develop():
 result={};selection={}
 for fam in ['H','P']:
  oldrows=read(HERE.parent/'roster-opportunity'/f'Development_{fam}_Cases.json.gz');oldidx={(a['id'],a['anchor']):a for a in oldrows};out=[]
  for year in [2016,2017,2018,2021,2022]:
   roles=['H'] if fam=='H' else ['SP','RP'];zs=[z for rr in roles for z in records[rr] if z['year']==year and z['id']%5==4 and z['positive_anchor']];model=model_for(year,fam);methods0=METHODS+(['active_mean','active_capacity_mean','active_mean_half','preserved_count_mean','count_mean_75','count_mean_half'] if fam=='H' else []);preds={method+'__'+prob:predict_model(model,zs,method,prob) for method in methods0 for prob in PROBS}
   for i,z in enumerate(zs):
    olda=oldidx.get((z['id'],year));actual=(target(z) or {}).get('stat',{}).get('PA' if fam=='H' else 'IP',0);groups=['all',z['role'],cohort_key(z)]+z.get('groups',[]);q={'mlbam_id':z['id'],'anchor':year,'role':z['role'],'groups':list(dict.fromkeys(groups)),'actual':actual}
    if olda:
     q['frozen_incumbent']=olda['incumbent'];q['frozen_count_mean']=olda['tree'];q['groups']=list(dict.fromkeys(q['groups']+olda['groups']))
    else:
     q['frozen_incumbent']=legacy.incumbent(year,fam,[z])[0]['IP'];q['frozen_count_mean']=q['frozen_incumbent']
    for name,ps in preds.items():q[name]=value(ps[i],fam)
    out.append(q)
   print('DEV',fam,year,len(zs),flush=True)
  methods=list(preds)+['frozen_incumbent','frozen_count_mean'];s=score(out,methods);protected=['stable_rotation','young_entry','interrupted'] if fam=='P' else ['everyday','durable','young_entry','interrupted'];protected=[g for g in protected if g in s and s[g]['frozen_incumbent']['n']>=15];comps=['frozen_incumbent','frozen_count_mean'];eligible={};obj={};violation={}
  for name in preds:
   guards=['all']+protected;limits={g:min(s[g][m]['MAE'] for m in comps)*1.05 for g in guards};viol=[max(0,s[g][name]['MAE']/limits[g]-1) for g in guards];eligible[name]=not any(viol);violation[name]=sum(viol);obj[name]=s['all'][name]['RMSE']+.1*abs(s['all'][name]['bias'])+.25*np.mean([s[g][name]['RMSE'] for g in protected])
  choices=[m for m in preds if eligible[m]];sel=min(choices,key=obj.get) if choices else min(preds,key=lambda n:(violation[n],obj[n]));selection[fam]=sel;result[fam]={'metrics':s,'protected':protected,'eligible':eligible,'objective':obj,'violation':violation,'selected':sel,'research_only_if_no_guard_pass':not bool(choices)};put(f'Development_{fam}_Cases.json.gz',out);print('SELECT',fam,sel,eligible,flush=True)
 put('Selection_Freeze.json',{'selection':selection,'development':result,'protocol_sha256':hashlib.sha256((HERE/'Protocol_Freeze.json').read_bytes()).hexdigest(),'implementation_sha256':hashlib.sha256((HERE/'engine.py').read_bytes()).hexdigest(),'reserved_outcomes_used_for_selection':False,'median_comparators_not_blended':True});return selection

def evaluate(selection):
 evalrows=[];casefiles={}
 for fam in ['H','P']:
  oldcases=read(HERE.parent/'roster-opportunity'/f'Integrated_{fam}_Cases.json.gz');oldidx={(a['mlbam_id'],a['anchor'],a['role']):a for a in oldcases};casefiles[fam]=oldcases
  for year in sorted({a['anchor'] for a in oldcases}):
   roles=['H'] if fam=='H' else ['SP','RP'];zs=[z for rr in roles for z in records[rr] if z['year']==year and (z['id'],year,z['role']) in oldidx];model=model_for(year,fam);method,prob=selection[fam].split('__');ps=predict_model(model,zs,method,prob)
   for z,c in zip(zs,ps):
    a=oldidx[z['id'],year,z['role']];key='PA' if fam=='H' else 'IP';q={'mlbam_id':z['id'],'name':a['name'],'anchor':year,'target_season':year+1,'role':z['role'],'groups':a['groups'],'evaluation':'exposed retrospective','actual':a['actual'].get(key,0),'production':a['baseline'].get(key,0),'frozen_hybrid':a['hybrid'].get(key,0),'strong_prior':a['strong_prior'].get(key,0),'repair':value(c,fam),'participation':1-c['probabilities']['absent'],'actual_active':int(a['actual'].get(key,0)>0),'conditional_active':c['opportunity_layer']['conditional_active_workload'],'component':c,'before_component':a['hybrid_components']};evalrows.append(q)
   print('RETROSPECTIVE',fam,year,len(zs),flush=True)
  # New chronological target: no fantasy survivor selection, ID0 never trained.
  zs=[]
  for (ident,stream),hs in hist.items():
   if stream!=fam:continue
   anchor=lookup.get((ident,2025,fam))
   if not anchor or ident%5 not in read(HERE/'Protocol_Freeze.json')['new_reserved_ID_mod5'] or ident in read(HERE/'Protocol_Freeze.json')['reserved_excluded_known_diagnostic_ids']:continue
   rr='H' if fam=='H' else v.observed_role((counts(ident,2025) or {}),anchor['role']);z=historical_z(ident,2025,rr)
   if z['x'] is not None:zs.append(z)
  model=model_for(2025,fam);method,prob=selection[fam].split('__');ps=predict_model(model,zs,method,prob);prior_sel=read(HERE.parent/'first-year-repair/Selection_Freeze.json')['selected'][fam];strongmodel=joblib.load(HERE.parent/'first-year-repair'/f'current-{fam}.joblib')
  # Current prior artifact trained only target<=2025, but model-asof2026 vs2025
  # priors differ: compare preserved2025 baseline incumbent freshly fit asof2025.
  incmodel=legacy.predict_hitter if fam=='H' else legacy.predict_augmented
  if fam=='H':from hitter_model import fit_hitter;im=fit_hitter(2025)
  else:from principal_followup import augment,fit_pitch;im=augment(fit_pitch(2025))
  legacy.prior.checkpoint(im,HERE/f'benchmark-incumbent-{fam}-2025.joblib');inc=incmodel(im,zs);strong=legacy.prior.opportunity(strongmodel,zs,inc,prior_sel)
  for z,c,ic,sc in zip(zs,ps,inc,strong):
   actual=observation(z,2026)['exposure'];key='PA' if fam=='H' else 'IP';b=historical_baseline(z);groups=['all',z['role'],cohort_key(z)];evalrows.append({'mlbam_id':z['id'],'name':lookup[z['id'],2025,fam]['name'],'anchor':2025,'target_season':2026,'role':z['role'],'groups':groups,'evaluation':'new_reserved2025_waveC','actual':actual,'production':(b or {}).get(key,0),'frozen_hybrid':value(ic,fam),'strong_prior':value(sc,fam),'repair':value(c,fam),'participation':1-c['probabilities']['absent'],'actual_active':int(actual>0),'conditional_active':c['opportunity_layer']['conditional_active_workload'],'component':c,'before_component':ic,'benchmark_note':'frozen hybrid family2025 replay from asof2025 incumbent and preserved pre2026 prior; H count branch independently refit asof2025 below'})
  print('RESERVED',fam,len(zs),flush=True)
 # Repair frozen hybrid comparator correctly using actual2025 count fit, never2026 outcome.
 for fam in ['H','P']:
  xs=[a for a in evalrows if a['evaluation']=='new_reserved2025_waveC' and (a['role']=='H')==(fam=='H')];zs=[historical_z(a['mlbam_id'],2025,a['role']) for a in xs];incs=[a['before_component'] for a in xs]
  if fam=='H':
   cm=legacy.fit_layer(2025,'H');legacy.prior.checkpoint(cm,HERE/'benchmark-count-H-2025.joblib');counts0=legacy.predict_layer(cm,zs,incs,'tree')
   for a,c in zip(xs,counts0):a['frozen_hybrid']=.5*a['strong_prior']+.5*c['PA']
  else:
   for a in xs:a['frozen_hybrid']=a['before_component']['IP'] if a['role']=='RP' else .75*a['before_component']['IP']+.25*a['strong_prior']
 put('Chronological_Cases.json.gz',evalrows);csvout('Chronological_Cases.csv',[{k:v for k,v in a.items() if k not in {'component','before_component','groups'}}|{'groups':'|'.join(a['groups'])} for a in evalrows]);summ=[]
 for cohort in ['exposed retrospective','new_reserved2025_waveC']:
  xs=[a for a in evalrows if a['evaluation']==cohort and a['target_season']!=2020]
  for g in sorted({g for a in xs for g in a['groups']}):
   gg=[a for a in xs if g in a['groups']]
   for fam in ['H','P']:
    ys=[a for a in gg if (a['role']=='H')==(fam=='H')]
    if not ys:continue
    row={'evaluation':cohort,'family':fam,'group':g,'n':len(ys),'predicted_participation':float(np.mean([a['participation'] for a in ys])),'observed_participation':float(np.mean([a['actual_active'] for a in ys])),'Brier':float(np.mean([(a['participation']-a['actual_active'])**2 for a in ys]))}
    active=[a for a in ys if a['actual_active']];row['conditional_active_bias']=float(np.mean([a['conditional_active']-a['actual'] for a in active])) if active else None
    for name in ['production','frozen_hybrid','strong_prior','repair']:
     for k,v0 in metric([(a[name],a['actual']) for a in ys]).items():row[name+'_'+k]=v0
    summ.append(row)
 csvout('Chronological_Validation.csv',summ)
 # Fixed earlier gates, populated exactly from original subsets; no relaxation.
 gates=[]
 limits=read(HERE.parent/'roster-opportunity/Hybrid_Release_Gates.json')['gates']
 def add(name,xs,limit,key='repair'):
  val=metric([(a[key],a['actual']) for a in xs])['MAE'];gates.append({'gate':name,'n':len(xs),'value':val,'limit':limit,'pass':val is not None and val<=limit})
 exposed=[a for a in evalrows if a['evaluation']=='exposed retrospective'];original=read(HERE.parent.parent.parent/'Historical_Cases.json') if False else read(HERE.parent.parent.parent/'Historical_Cases.json')
 origkeys={(a['mlbam_id'],a['anchor']) for a in original};orig=[a for a in exposed if a['role']!='H' and (a['mlbam_id'],a['anchor']) in origkeys];expanded_keys={(a['mlbam_id'],a['anchor'],a['role']) for a in read(HERE.parent/'first-year-repair/P_Cases.json.gz')[:1084]};expanded=[a for a in exposed if (a['mlbam_id'],a['anchor'],a['role']) in expanded_keys];standardH=[a for a in exposed if a['role']=='H' and a['target_season']!=2020]
 for name,xs in [('original94',orig),('originalSP',[a for a in orig if a['role']=='SP']),('expandedP',expanded),('H_standard',standardH),('additional_expandedSP',[a for a in expanded if a['role']=='SP']),('additional_youngSP',[a for a in expanded if 'young_SP' in a['groups'] and a['role']=='SP']),('additional_stableSP_vs_strong',[a for a in expanded if 'stable_rotation' in a['groups']]),('additional_durableH_vs_strong',[a for a in standardH if 'durable_four_years' in a['groups']])]:
  lim=next(a['limit'] for a in limits if a['gate']==name);add(name,xs,lim)
 # Exact RBI projection scales frozen independent production rates by workload.
 high=[a for a in exposed if 'high_RBI_comparable62' in a['groups'] and a['target_season']!=2020];bias=[]
 for a in high:
  oldcase=next(b for b in casefiles['H'] if (b['mlbam_id'],b['anchor'])==(a['mlbam_id'],a['anchor']));b=oldcase['baseline'];bias.append(b['RBI']*a['repair']/b['PA']-oldcase['actual'].get('RBI',0))
 val=float(np.mean(bias));gates.append({'gate':'comparable_high_RBI_bias','n':len(high),'value':val,'limit':3,'pass':abs(val)<=3})
 gates.extend([{'gate':'new_reserved_not_used_for_tuning','pass':True},{'gate':'complete_dated_historical_roster_injury_coverage','pass':False,'reason':'current verified roster scenario executed; no historical roster backfill or fabricated medical labels'},{'gate':'same_date_independent_population','pass':False,'reason':'unchanged external benchmark coverage gap'}]);put('Release_Gates.json',{'gates':gates,'all_gates_pass':all(g['pass'] for g in gates),'deploy_authorized':False});return evalrows

if __name__=='__main__':
 sel=develop() if not (HERE/'Selection_Freeze.json').exists() else read(HERE/'Selection_Freeze.json')['selection'];evaluate(sel)
