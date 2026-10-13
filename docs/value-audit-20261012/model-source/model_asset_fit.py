"""Separate transferable contribution value, competitive fit and market evidence."""
from pathlib import Path
import sys,json,copy,csv,functools,math
import numpy as np
sys.dont_write_bytecode=True
P=Path(__file__).resolve().parent;ROOT=P.parent;sys.path.insert(0,str(ROOT/'trade-preview-v23'));import model_v23 as v
r=v.r;old=v.old
# V2.3C: explicit compact-input recovery. Original B module/file is untouched.
_RECOVERY=json.loads((P/'Recovery_Appearances.json').read_text())
_APPEAR={(a['mlbamId'],a['year']):{'GP':a['GP'],'GS':a['GS']} for a in _RECOVERY['rows']}
v.appearance_history=lambda:_APPEAR
# Retain archived prospect evidence by stable identity independently of eligibility.
PRIOR_REGISTRY=json.loads((P/'Prospect_Prior_Registry.json').read_text())['players']

CONFIG=json.loads((P/'Selection.json').read_text()) if (P/'Selection.json').exists() else {}
FG=json.loads((P/'FG_Preseason_Facts.json').read_text());NAMES={}
for p in old.players.values():NAMES.setdefault(old.normalized_name(p['name']),[]).append(p)
MATCHED={};UNMATCHED=[]
for z in FG:
 candidates=NAMES.get(old.normalized_name(z['name']),[])
 # No guessed aliases or generic name joins; verified crosswalk ID required.
 if len(candidates)==1 and candidates[0].get('mlbamId') and candidates[0].get('team')==z['team']:
  MATCHED[candidates[0]['id']]=z|{'fantraxId':candidates[0]['id'],'mlbamId':candidates[0]['mlbamId'],'identity':'Unique normalized name + organization, existing verified MLBAM/Fantrax link'}
 else:UNMATCHED.append(z|{'reason':'No unique existing identity plus organization match'})
DD={}
for scope,file in [('overall','Dynasty_Dugout_Overall.tsv'),('prospects','Dynasty_Dugout_Prospects.tsv')]:
 for z in csv.DictReader((ROOT/'trade-preview-v22/benchmark_sources'/file).open(),delimiter='\t'):
  i=z['Player ID'].strip('*');DD.setdefault(i,{})[scope]={'rank':int(z['Ranking']),'tier':z['Tier'],'received':'2026-10-08','publication_date':'not independently established','scope':scope+' top500','source':'Dynasty Dugout user-supplied snapshot'}
# Bolte's organizational rank is deliberately not converted into a global rank.
BOLTE={'source':'FanGraphs','date':'2026-04-10','scope':'Athletics Top36','organization_rank':10,'FV':'40+','age_at_source':22.7,'level_at_source':'AAA','ETA_field':2027,'url':'https://blogs.fangraphs.com/athletics-top-36-prospects/','numerical_prior':'Unavailable: outside validated global top100 rank domain; no invented rank or FV-to-fantasy conversion'}
@functools.lru_cache(None)
def ceiling():return max(r.utility(max(0,r.surplus(a['stat'],'H'))) for a in old.AN if a['role']=='H' and a['year']<=2025)
def market(p):
 evidence=[]
 if p['id'] in MATCHED:evidence.append(MATCHED[p['id']]|{'scope':'Global preseason top110 with >=50 FV','usage':'rank prior only if independent of observed MLB season; FV diagnostic, not point bonus'})
 if p['name']=='Henry Bolte':evidence.append(BOLTE)
 if p.get('prospect',{}).get('grades'):evidence.append(p['prospect']['grades']|{'usage':'Dated diagnostic; no new numerical premium'})
 for z in DD.get(p['id'],{}).values():evidence.append(z|{'usage':'Market-attention/consensus diagnostic, not transaction price'})
 return {'estimated_market_value':None,'liquidity_multiplier':None,'evidence':evidence,'status':'Not estimable from available completed transaction prices. Rankings/grades indicate standing, not a calibrated acquisition-cost premium.','no_double_count':'No market number added to contribution or fit; no source rankings converted to bonuses.'}
def restored_prior(p):
 src=MATCHED.get(p['id'])
 if not src or src['rank']>100 or v.role(p)!='H' or p.get('prospect'):return None,None
 hist=v.seasons(p,'H')
 if any(z['year']<2026 and z['role']=='H' and z['stat'].get('PA',0)>0 for z in hist):return None,{'source':src,'status':'Retained as scouting evidence only: publication may include MLB evidence already in forecast; independence not established'}
 q=copy.deepcopy(p);q['age']=src['age'];q['prospect']={'rank':src['rank'],'eta':'2027','provider':'FanGraphs preseason2026','sourceDate':src['date']};paths,audit=r.prospect_paths(q)
 return paths,{'source':src,'status':'Preseason prior precedes first observed MLB season; next forecast-year path alignment remains provisional','prior_audit':audit,'standalone_prior_neutral':r.evaluate_paths(paths,'neutral')['display']}
def match_mean(atoms,target,max_utility):
 capacity=sum(prob for prob,path in atoms if path>0)*max_utility
 if capacity+1e-9<target:return None
 lo,hi=0.,1.
 while sum(prob*min(max_utility,x*hi) for prob,x in atoms)<target and hi<1e9:hi*=2
 for _ in range(60):
  mid=(lo+hi)/2
  if sum(prob*min(max_utility,x*mid) for prob,x in atoms)<target:lo=mid
  else:hi=mid
 return [min(max_utility,x*(lo+hi)/2) for prob,x in atoms]
def paths(p,scenario='base'):
 retained=None
 if not p.get('prospect') and p['id'] in PRIOR_REGISTRY:
  retained=PRIOR_REGISTRY[p['id']]
  p=copy.deepcopy(p);p['prospect']=copy.deepcopy(retained['prospect'])
 result,audit=_paths_with_evidence(p,scenario)
 if p['id'] in PRIOR_REGISTRY:
  audit=copy.deepcopy(audit);audit['identity_prior_registry']={'stable_id':p['id'],'status':'Archived prospect evidence retained independently of current eligibility metadata','metadata_restored_this_call':bool(retained),'source':PRIOR_REGISTRY[p['id']]['source']}
 if retained:
  audit['identity_retained_prior']={'source':retained['source'],'policy':'Archived dated prior retained by stable Fantrax identity when presentation/eligibility metadata disappears; no added premium, no new mean adjustment','registry_key':p['id']}
 return result,audit

def _paths_with_evidence(p,scenario='base'):
 baseline,audit=v.player_paths(p,scenario);prior,info=restored_prior(p)
 if info:audit=copy.deepcopy(audit);audit['restored_scouting_prior']=info
 if not prior:return baseline,audit
 selected=CONFIG.get('distribution_selection','MLB_only');accepted=selected!='MLB_only' and CONFIG['distribution_scores']['final'][selected]['CRPS']<CONFIG['distribution_scores']['final']['MLB_only']['CRPS'] and CONFIG['distribution_scores']['final'][selected]['Brier_elite']<=CONFIG['distribution_scores']['final']['MLB_only']['Brier_elite']
 e=sum(z['stat'].get('PA',0) for z in v.seasons(p,'H') if z['role']=='H');k=float(selected) if selected!='MLB_only' else 600.;w=e/(e+k);audit['restored_scouting_prior'].update(MLB_evidence_weight=w,prior_weight=1-w,prior_strength_PA=k,policy='Mean-preserving uncertainty only; debut mean phase-in disabled after worse cached low-PA forecast error',mean_prior_weight=0.,mean_MLB_weight=1.,debut_mean_adjustment_enabled=False,accepted_distribution=accepted,market_value=None)
 if not accepted:
  audit['restored_scouting_prior']['status']+='; forecast blend not adopted after inadequate distribution validation'
  return baseline,audit
 mixed=[(prob*w,list(path)) for prob,path in baseline]+[(prob*(1-w),list(path)) for prob,path in prior]
 for t in range(8):
  mlb_mean=sum(prob*path[t] for prob,path in baseline);prior_mean=sum(prob*path[t] for prob,path in prior)
  # Fixed existing 100-PA rate pseudocount defines a continuous debut phase-in.
  # Chronological tests do not show meaningful point-accuracy gains; below250PA provisional.
  target=mlb_mean;adjusted=match_mean([(prob,path[t]) for prob,path in mixed],target,ceiling())
  if adjusted is None:
   audit['restored_scouting_prior']['status']+='; physically bounded mean match infeasible: baseline retained'
   return baseline,audit
  for (_,path),x in zip(mixed,adjusted):path[t]=x
 audit['kind']='hybrid';audit['MLB_reliability']=w;audit['distribution_space']='Expected fantasy contribution utility; coherent nonnegative latent surplus states, not fabricated player category observations';audit['utility_once']='Frozen state utility is represented once; no additive upside, recovery, scouting or market bonus';return mixed,audit
def competitive(ps,mode):
 # Smooth time preference over the same frozen contribution paths. No price haircut.
 discount={'neutral':.88,'balanced':.88,'contender':.75,'rebuild':.94}[mode]
 w=np.array([discount**t for t in range(8)]);w*=sum(old.weights('neutral'))/sum(w)
 vals=np.asarray([path for prob,path in ps])@w;pr=np.asarray([prob for prob,path in ps]);mean=float(pr@vals);sd=float(np.sqrt(pr@((vals-mean)**2)))
 return {'display':r.DISPLAY*mean,'underlying':mean,'expected_before_risk_preference':mean,'outcome_dispersion':sd,'risk_preference_deduction':0.,'annual_time_discount':discount,'meaning':'Competitive production fit, not transferable asset price; uncertainty shown separately'}

def build():
 D=copy.deepcopy(json.loads((ROOT/'trade-preview-v23/model/v23_results.json').read_text()));evidence={};baseline={a['id']:copy.deepcopy(a) for a in D['assets']};changed=[]
 for ix,a in enumerate(D['assets']):
  if ix%250==0:print('Catalog',ix,flush=True)
  if a['audit']['kind']=='pick':
   slots=[a['audit']['overall']] if a['audit']['overall'] else [(a['audit']['round']-1)*12+x for x in range(1,13)];ps=[]
   for slot in slots:
    pp,unused=v.base.pick_slot(a['audit']['year'],slot);ps.extend((prob/len(slots),path) for prob,path in pp)
   a['competitive_values']={mode:competitive(ps,mode) for mode in r.MODES};a['competitive_range']={}
   for scenario in ['low','high']:
    samples=[v.base.pick_slot(a['audit']['year'],slot,scenario,policy='consensus' if scenario=='low' else 'best_available',spread=12 if scenario=='low' else 4)[0] for slot in slots]
    a['competitive_range'][scenario]={mode:(min if scenario=='low' else max)(competitive(pp,mode)['display'] for pp in samples) for mode in r.MODES}
   neutral=copy.deepcopy(a['values']['neutral']);a['values']={mode:copy.deepcopy(neutral) for mode in r.MODES};a['range']={scenario:{mode:a['range'][scenario]['neutral'] for mode in r.MODES} for scenario in ['low','high']};a['market']={'estimated_market_value':None,'evidence':[],'status':'No calibrated transaction price. Future slot/class uncertainty retained.'};continue
  p=old.players[a['id']];ps,audit=paths(p);a['audit']=audit;fit={mode:competitive(ps,mode) for mode in r.MODES};neutral=fit['neutral'];a['values']={mode:copy.deepcopy(neutral) for mode in r.MODES};a['competitive_values']=fit;a['annual_expected_utility']=[sum(prob*path[t] for prob,path in ps) for t in range(8)]
  if audit['kind']=='unmodeled':a['values']={mode:{'display':None,'underlying':None} for mode in r.MODES};a['competitive_values']=copy.deepcopy(a['values'])
  a['competitive_range']={s:{mode:(competitive(paths(p,s)[0],mode)['display'] if audit['kind']!='unmodeled' else None) for mode in r.MODES} for s in ['low','high']};a['range']={s:{mode:a['competitive_range'][s]['neutral'] for mode in r.MODES} for s in ['low','high']};a['market']=market(p)
  a['qualityWarnings']=[x for x in a.get('qualityWarnings',[]) if 'not retained resale value' not in x];a['qualityWarnings'].append('Neutral transferable fundamental value stays strategy-invariant. Competitive fit is a separate timing/risk score; neither quantity estimates a realized resale price.');a['valuation_quantities']={'intrinsic_dynasty':neutral['display'],'transferable_fundamental':neutral['display'],'market_acquisition':None,'competitive_fit':{mode:x['display'] for mode,x in fit.items()}}
  if audit.get('restored_scouting_prior'):
   a['qualityWarnings'].append('Debut mean adjustment disabled: low-PA forecast error worsened. Dated prior shapes uncertainty only. The inherited zero-MLB routing boundary can cause a promotion valuation jump; early-debut value is provisional.')
  if audit.get('restored_scouting_prior'):changed.append({'name':a['name'],'id':a['id'],'previous_neutral':baseline[a['id']]['values']['neutral']['display'],'new_neutral':neutral['display'],'prior':audit['restored_scouting_prior']})
 by={a['id']:a for a in D['assets']}
 for t in D['trades']:
  neutral=[sum(by[i]['values']['neutral']['display'] for i in ids) for ids in t['identities']];t['neutral_transfer_packages']=neutral;t['market_price_assessment']='Unavailable; no market premium inferred'
  for mode in r.MODES:
   packages=[sum(by[i]['competitive_values'][mode]['display'] for i in ids) for ids in t['identities']];bounds=[(sum(by[i]['competitive_range']['low'][mode] for i in ids),sum(by[i]['competitive_range']['high'][mode] for i in ids)) for ids in t['identities']];t['modes'][mode].update(package_values=packages,net_first_owner=packages[1]-packages[0],assumption_range=[bounds[1][0]-bounds[0][1],bounds[1][1]-bounds[0][0]],meaning='Competitive fit, not transfer price',neutral_transfer_change=neutral[1]-neutral[0])
 D.update(version='V2.3C identity-prior guard candidate',valuation_architecture='Neutral transfer fundamentals, separate competitive-fit utility, unpriced market evidence. No summed total or arbitrary retention floor.',warnings=D['warnings']+['Competitive fit does not replace neutral trade-asset value; market transaction prices remain unestimated'])
 (P/'model').mkdir(exist_ok=True);(P/'model/results.json').write_text(json.dumps(D,indent=2));(P/'Restored_Priors.json').write_text(json.dumps({'matched':MATCHED,'unmatched':UNMATCHED,'restored':changed},indent=2));print('Saved',len(D['assets']),'assets;',len(changed),'restored prior cases')
if __name__=='__main__':build()
