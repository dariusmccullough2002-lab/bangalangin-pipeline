"""Offline replacement-access diagnostic. No website writes, trade fitting or deploy operations."""
import json,math,statistics,sys,copy,random,itertools,hashlib,re
from pathlib import Path
from functools import lru_cache
ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/'inputs'))
import u2_prototype as u
# Normalize missing grade containers in memory only; missing grades remain unknown.
for player_id,p in list(u.P.items()):
 if p.get('prospect') and p['prospect'].get('grades') is None:
  q=copy.deepcopy(p);q['prospect']['grades']={};u.P[player_id]=q
COHORT=json.load(open(ROOT/'inputs/free-prospect-cohort.json'))
COVERAGE=json.load(open(ROOT/'inputs/scouting-coverage-audit.json'))
STATUSES=json.load(open(ROOT/'inputs/roster-statuses.json'))
PREVIOUS=json.load(open(ROOT/'inputs/u2_results.json'))
# Cache numerical evidence only; no coefficient or probability changes.
score0=u.score
@lru_cache(None)
def scorecache(id,multi=True):return score0(u.P[id],multi)
u.score=lambda p,multi=True:scorecache(p['id'],multi)
RESTRICTED={c['id'] for c in u.cases()[0]['a']+u.cases()[0]['b']}

@lru_cache(None)
def gross_player(id,mode):return gross(u.P[id],mode)
def gross(p,mode,tail_scale=1,scouting=True):
 r=u.role(p)
 if not (p.get('prospect') and u.volume(p)<(250 if r=='H' else 100)):return u.player_value(p,mode,'B')
 prob=u.probabilities(p,tail=tail_scale,scouting=scouting);eta=int((re.search(r'20\d\d',str(p['prospect'].get('eta') or '2030')) or re.search(r'20\d\d','2030')).group());age=float(p.get('age') or 26);w=u.weights(mode)
 values=[]
 for t in range(len(w)):
  ramp=max(0,min(1,(2027+t-eta+1)/2));aging=math.exp(-.04*max(0,age+t-29))
  values.append(sum(q*u.utility(s*aging,1.35) for q,s in zip(prob,[0]+u.ANCHOR[r]))*ramp)
 return sum(v*wt for v,wt in zip(values,w))

def pick_value(p,mode,slot=None,shift=0,width=12):
 assert p['round'] in range(1,6),'R6–20 never have trade value'
 indices=list(range(max(0,slot-1-width),min(len(u.DRAFT),slot+width))) if slot else list(range((p['round']-1)*12,p['round']*12))
 return statistics.mean(gross(u.draft_proxy(u.DRAFT[max(0,min(i+shift,len(u.DRAFT)-1))],p['year']),mode) for i in indices)

def asset_value(p,mode,slot=None,shift=0,width=12):
 return pick_value(p,mode,slot,shift,width) if p.get('kind')=='pick' else gross_player(p['id'],mode)

# Empirical available identities; forecast distributions borrowed from matched owned scouting peers.
def fv(p):
 v=(p.get('prospect',{}).get('grades') or {}).get('fv')
 try:return float(str(v).replace('+',''))+(2.5 if '+' in str(v) else 0)
 except:return None

def donor_set(c):
 role='SP' if c['position']=='SP' else 'H'
 peers=[p for p in u.P.values() if p.get('prospect') and u.role(p)==role and fv(p)==c['fv'] and p['id'] not in RESTRICTED and abs(p['age']-c['age'])<=3 and abs(int((re.search(r'20\d\d',str(p['prospect'].get('eta') or '2030')) or re.search(r'20\d\d','2030')).group())-c['eta'])<=2]
 if len(peers)<4:peers=[p for p in u.P.values() if p.get('prospect') and u.role(p)==role and fv(p)==c['fv'] and p['id'] not in RESTRICTED]
 assert len(peers)>=4
 assert all((p['prospect'].get('grades') or {}).get('source')=='FanGraphs' for p in peers)
 return peers

def donor_proxy(c,p):
 z=copy.deepcopy(u.P[c['fantraxId']]);z['prospect']={'rank':p['prospect']['rank'],'eta':str(c['eta'])};return z

def cohort_distribution():
 out=[]
 for c in COHORT:
  peers=donor_set(c);proxies=[donor_proxy(c,p) for p in peers]
  values={m:{'p25':u.quant([gross(p,m) for p in proxies],.25),'median':u.quant([gross(p,m) for p in proxies],.5),'mean':statistics.mean(gross(p,m) for p in proxies),'p75':u.quant([gross(p,m) for p in proxies],.75)} for m in u.MODES}
  out.append(c|{'peer_ids':[p['id'] for p in peers],'peer_count':len(peers),'values':values,'elite_probability_mean':statistics.mean(u.probabilities(p)[4] for p in proxies),'probabilities_mean':[statistics.mean(u.probabilities(p)[i] for p in proxies) for i in range(5)]})
 return out
COHORT_VALUES=cohort_distribution()

# Full measured qualified MLB FA set. Zero-data prospects remain unknown, not zero-valued substitutes.
def fa_distribution():
 return [{'id':p['id'],'name':p['name'],'age':p['age'],'position':p['position'],'role':u.role(p),'owner':p['owner'],'values':{m:gross_player(p['id'],m) for m in u.MODES},'evidence':'Single-season MLB extrapolation; not measured career outcome probability'} for p in u.FA]
MLB_FA=fa_distribution()

def smooth(delta,free=2,lam=3,tau=2):
 f=lambda x:lam*tau*math.log1p(math.exp(x/tau))
 return f(delta-free)-f(-free)

def comparison(a,b,variant='corrected',free=(2,2),lam=3,shift=0,tail=1,width=12,scouting=True,late_quality=1,future_quality=1):
 out={}
 for m in u.MODES:
  if variant=='frozen':
   v=[sum(u.asset_value(p,m,'B') for p in s) for s in [a,b]]
  else:
   v=[]
   for s in [a,b]:
    v.append(sum(gross(p,m,tail,scouting) if p.get('kind')!='pick' and (tail!=1 or not scouting) else asset_value(p,m,(56 if p['id']==a[2]['id'] else 58 if p['id']==a[3]['id'] else None) if variant=='corrected' and len(a)==5 else None,shift,width)*(late_quality if p.get('kind')=='pick' and p['round']==5 else future_quality if p.get('kind')=='pick' and p['year']>2027 else 1) for p in s))
  burden=lambda s:sum(1 if p.get('kind')!='pick' else .88**(p['year']-2026) for p in s)
  delta=burden(b)-burden(a)
  costs=[smooth(delta,free[0],lam),smooth(-delta,free[1],lam)]
  out[m]={'surrendered':v,'received':[v[1],v[0]],'capacity_adjustment':[-x for x in costs],'net':[v[1]-v[0]-costs[0],v[0]-v[1]-costs[1]]}
 return out

# Scalar recreation can substitute production, but cannot certify an equivalent superstar distribution.
def diagnostics(candidates,mode,strict_position=False,tail_match=False,alpha=.8,stat='median',availability=1):
 out=[]
 for targetid in ['06f1c','05mx9','06ps2']:
  p=u.P[targetid];v=gross_player(targetid,mode);e=u.probabilities(p)[4];r=u.role(p)
  options=[]
  for x in candidates:
   if (x['position']=='SP')!=(r=='SP'):continue
   if strict_position and x['position']!=p['position']:continue
   amount=x['values'][mode][stat]
   if amount<alpha*v or (tail_match and x['elite_probability_mean']<alpha*e):continue
   options.append((amount,x))
  # Under incomplete coverage this is observed-candidate count, not a league-wide scarcity certificate.
  out.append({'id':targetid,'name':p['name'],'intrinsic':v,'elite_probability':e,'coverage_target':alpha,'observed_comparables':len(options),'comparable_ids':[x['fantraxId'] for _,x in options],'access_probability_scenario':1-(1-availability)**len(options),'best_alternative_value':max([x for x,_ in options],default=None)})
 return out

def roster_audit():
 out=[]
 for t in STATUSES['teams']:
  current=[p for p in u.P.values() if p['owner']==t['name']];old={p['fantraxId']:p for p in t['players']};ir=[p for p in current if old.get(p['id'],{}).get('status')=='INJURED_RESERVE'];unknown=[p for p in current if p['id'] not in old]
  out.append({'team':t['name'],'owned':len(current),'known_ir':len(ir),'non_ir_conservative':len(current)-len(ir),'current_total_openings_conservative':max(0,63-len(current)+len(ir)),'unknown_status_ids':[p['id'] for p in unknown],'status_as_of':'2026-10-06','ownership_as_of':'2026-10-07','2027_fypd_rights':sum(p['owner']==t['name'] and p['year']==2027 for p in u.PICK.values()),'interpretation':'Current snapshot; not post-FYPD openings. No assumed expansion; unknown statuses treated as non-IR.'})
 return out

# Mechanism diagnostic: finite capacity, 11 competing owners, weighted selection without replacement.
# Competition policies are explicit scenarios, not inferred historical behavior.
def draft_access_sim(mode='rebuild',capacity=1,competition_capacity=8,focal_slot=8,preclaims=0,policy='balanced',focal_policy='need-directed',targeted_competitors=0,seed=710,iterations=600):
 sources=[]
 for x in COHORT_VALUES:sources.append({'id':x['fantraxId'],'name':x['name'],'role':'SP' if x['position']=='SP' else 'H','value':x['values'][mode]['median'],'tail':x['elite_probability_mean'],'is_prospect':True})
 for x in MLB_FA:
  if x['values'][mode]>0:sources.append({'id':x['id'],'name':x['name'],'role':x['role'],'value':x['values'][mode],'tail':None,'is_prospect':False})
 sources=[x for x in sources if x['value']>0]
 rng=random.Random(seed);last_round=5;chosen_counts={x['fantraxId']:0 for x in COHORT_VALUES};amounts=[];selects=[];pitch_comparable=0;tail_comparable=0;target=gross_player('06f1c',mode)
 for run in range(iterations):
  pool=sources.copy();caps=[competition_capacity]*12;caps[focal_slot-1]=capacity;focal=[]
  def choose():
   # Broad policies reveal crowding, not market asks. Avoid exact-rank omniscient drafting.
   w=[max(.1,x['value'])**1.4*(3 if policy=='prospect-focused' and x['is_prospect'] else 3 if policy=='MLB-focused' and not x['is_prospect'] else 15 if policy=='pitcher-focused' and x['role']=='SP' else 1) for x in pool]
   return rng.choices(range(len(pool)),weights=w,k=1)[0]
  for _ in range(min(preclaims,len(pool))):pool.pop(choose())
  for round in range(6,21):
   for owner in range(12):
    if not pool or caps[owner]<=0:continue
    qualifying=[i for i,x in enumerate(pool) if x['role']=='SP' and x['value']>=.8*target and x['tail'] is not None and x['tail']>=.8*u.probabilities(u.P['06f1c'])[4]]
    need_choice=(owner==focal_slot-1 and focal_policy=='need-directed' and not any(x['role']=='SP' for x in focal)) or (owner!=focal_slot-1 and owner<targeted_competitors and round==6)
    selection=max(qualifying,key=lambda i:pool[i]['value']) if need_choice and qualifying else choose()
    x=pool.pop(selection);caps[owner]-=1;last_round=max(last_round,round)
    if owner==focal_slot-1:focal.append(x)
  for x in focal:
   if x['id'] in chosen_counts:chosen_counts[x['id']]+=1
  amounts.append(sum(x['value'] for x in focal));selects.append(len(focal));pitch_comparable+=any(x['role']=='SP' and x['value']>=.8*target for x in focal)
  tail_comparable+=any(x['role']=='SP' and x['value']>=.8*target and x['tail'] is not None and x['tail']>=.8*u.probabilities(u.P['06f1c'])[4] for x in focal)
 return {'focal_post_fypd_capacity':capacity,'competitor_capacity_each':competition_capacity,'focal_draft_slot':focal_slot,'preclaims':preclaims,'policy':policy,'focal_policy':focal_policy,'targeted_competitors':targeted_competitors,'iterations':iterations,'last_round_selected':last_round,'mean_harvest':statistics.mean(amounts),'p10_harvest':u.quant(amounts,.1),'p90_harvest':u.quant(amounts,.9),'mean_selections':statistics.mean(selects),'prob_obtaining_mean_value_pitcher_comparable_to_wenninger':pitch_comparable/iterations,'prob_obtaining_tail_screened_prospect_comparable_to_wenninger':tail_comparable/iterations,'prospect_acquisition_rates':{id:n/iterations for id,n in chosen_counts.items()},'scope':'Conditional on these current available identities surviving until the draft; 7 screened prospects + positive-model MLB FAs only; scalar pitcher comparability is not tail equivalence.'}

# Regeneration is evaluated jointly: one free agent cannot replace multiple lost assets.
# Loss-specific scenario upper bound only, not an additive scarcity premium or final trade verdict.
def rebuild_package(lost_ids,mode,capacity=1,q=.5,stat='median',alpha=.8,strict=False):
 targets=[u.P[id] for id in lost_ids];candidates=COHORT_VALUES
 options={p['id']:[c for c in candidates if ((c['position']=='SP')==(u.role(p)=='SP')) and (not strict or c['position']==p['position']) and c['values'][mode][stat]>=alpha*gross_player(p['id'],mode) and c['elite_probability_mean']>=alpha*u.probabilities(p)[4]] for p in targets}
 choices=[None]+[c['fantraxId'] for c in candidates];best=0;bestmap={}
 for selected in itertools.combinations([c['fantraxId'] for c in candidates],min(capacity,len(candidates))):
  for target_subset in itertools.combinations(targets,min(len(targets),len(selected))):
   for perm in itertools.permutations(selected,min(len(targets),len(selected))):
    n=0;mapping={}
    for p,cid in zip(target_subset,perm):
     c=next(c for c in candidates if c['fantraxId']==cid)
     if c in options[p['id']]:n+=min(gross_player(p['id'],mode),c['values'][mode][stat])*q;mapping[p['id']]=cid
    if n>best:best=n;bestmap=mapping
 return {'lost_ids':lost_ids,'joint_recreation_bound':best,'chosen_ids':bestmap,'capacity':capacity,'per_candidate_access_assumption':q,'original_intrinsic':sum(gross_player(p['id'],mode) for p in targets),'not_recreated':max(0,sum(gross_player(p['id'],mode) for p in targets)-best),'caution':'Partial mean-value/tail-screened recovery bound; not literal recreation of unique assets, paid pick rights or acquisition price; access q assumed.'}

def main():
 proposal=u.cases()[0];a,b=proposal['a'],proposal['b'];frozen=comparison(a,b,'frozen');gross_unknown=comparison(a,b,'gross');corrected=comparison(a,b)
 # Exact additive attribution: old prospect floor and old pick exclusivity assumption, then slot information.
 decomposition={}
 for m in u.MODES:
  v=frozen[m];old_prosp=[u.asset_value(p,m,'B') for p in [a[0],a[1],b[0]]];new_prosp=[gross_player(p['id'],m) for p in [a[0],a[1],b[0]]]
  oldpick=sum(u.asset_value(p,m,'B') for p in a[2:]);newpick=sum(asset_value(p,m) for p in a[2:]);slotpick=sum(asset_value(p,m,56 if i==0 else 58 if i==1 else None) for i,p in enumerate(a[2:]));diff_prosp=sum(new_prosp[:2])-new_prosp[2]-sum(old_prosp[:2])+old_prosp[2]
  decomposition[m]={'Sandlot_frozen_net':v['net'][1],'intrinsic_received_minus_given':v['received'][1]-v['surrendered'][1],'old_smooth_capacity_cost':-v['capacity_adjustment'][1],'remove_hypothetical_prospect_floor_effect':diff_prosp,'remove_assumed_postR5_FYPD_exclusivity_floor_effect':newpick-oldpick,'exact_56_58_slot_effect':slotpick-newpick,'corrected_net_same_capacity':corrected[m]['net'][1]}
  assert abs(v['net'][1]+diff_prosp+newpick-oldpick+slotpick-newpick-corrected[m]['net'][1])<1e-8
 assetrows=[]
 for i,p in enumerate(a+b):
  assetrows.append({'id':p['id'],'name':p['name'],'slot':56 if i==2 else 58 if i==3 else None,'values':{m:{'frozen_U2':u.asset_value(p,m,'B'),'gross_unknown_slot':asset_value(p,m),'corrected_intrinsic':asset_value(p,m,56 if i==2 else 58 if i==3 else None)} for m in u.MODES},'elite_probability':u.probabilities(p)[4] if p.get('prospect') else None})
 scenarios={}
 for label,opts in [('Same capacity, slot-conditioned choice window',{}),('No capacity costs',{'lam':0}),('Conservative current openings Shea5 Sandlot1',{'free':(5,1)}),('No post-FYPD capacity either owner',{'free':(0,0)}),('Three post-FYPD openings both owners',{'free':(3,3)}),('Capacity lambda1',{'lam':1}),('Capacity lambda6',{'lam':6}),('Capacity lambda12',{'lam':12}),('Draft pool selected10 positions stronger',{'shift':-10}),('Draft pool selected10 positions weaker',{'shift':10}),('Narrow choice window6',{'width':6}),('Broad choice window24',{'width':24}),('Deterministic class rank equals slot: diagnostic only',{'width':0}),('Late FYPD outcomes half as valuable',{'late_quality':.5}),('Late FYPD outcomes1.5x',{'late_quality':1.5}),('Late FYPD outcomes2x',{'late_quality':2}),('No capacity cost plus late FYPD2x',{'late_quality':2,'lam':0}),('Future class -20%',{'future_quality':.8}),('Future class +20%',{'future_quality':1.2}),('Remove unvalidated scouting residual',{'scouting':False}),('Superstar tail half',{'tail':.5}),('Superstar tail 1.5x',{'tail':1.5})]:scenarios[label]=comparison(a,b,**opts)
 ladder={m:{label:diagnostics(COHORT_VALUES,m,**opts) for label,opts in [('Functional mean >=80%',{}),('Functional mean and superstar probability >=80%',{'tail_match':True}),('Same position, mean and tail >=80%',{'tail_match':True,'strict_position':True}),('P25 peers, mean and tail',{'tail_match':True,'stat':'p25'}),('P75 peers, mean and tail',{'tail_match':True,'stat':'p75'}),('60% recreation threshold',{'tail_match':True,'alpha':.6}),('95% recreation threshold',{'tail_match':True,'alpha':.95})]} for m in u.MODES}
 sims={}
 for cap in [0,1,3,6]:
  for comp in [5,8,12,15]:sims[f'capacity{cap}_competition{comp}']=draft_access_sim(capacity=cap,competition_capacity=comp)
 for label,opts in [('One earlier owner targets comparable pitchers',{'targeted_competitors':1}),('Two earlier owners target comparable pitchers',{'targeted_competitors':2}),('Four earlier owners target comparable pitchers',{'targeted_competitors':4}),('MLB-focused',{'policy':'MLB-focused'}),('Pitcher-focused',{'policy':'pitcher-focused'}),('Focal not need-directed',{'focal_policy':'portfolio'}),('Prospect-focused',{'policy':'prospect-focused'}),('12 early claims',{'preclaims':12}),('36 early claims',{'preclaims':36}),('Early owner slot2',{'focal_slot':2}),('Late owner slot12',{'focal_slot':12})]:sims[label]=draft_access_sim(**opts)
 regeneration={m:[rebuild_package(ids,m,capacity=cap,q=q,strict=strict) for ids in [['05mx9','06f1c'],['06ps2']] for cap in [0,1,2] for q in [.25,.5,.75] for strict in [False,True]] for m in u.MODES}
 stress=[]
 for c in u.cases()[1:4]:
  # Picks here unknown slots; no trade-specific tuning.
  stress.append({'id':c['id'],'teams':c['teams'],'sends':[[p['name'] for p in c[k]] for k in ['a','b']],'frozen':comparison(c['a'],c['b'],'frozen'),'gross':comparison(c['a'],c['b'],'gross'),'label':'NOW stress only; no THEN or REALIZED inference'})
 baseline_intrinsic=[gross_player(id,'rebuild') for id in ['05mx9','06f1c','06ps2']]
 no_access=diagnostics([],'rebuild',tail_match=True)
 pick_round6_rejected=False
 try:pick_value({'round':6,'year':2027},'rebuild')
 except AssertionError:pick_round6_rejected=True
 invariants={'round6_cannot_receive_trade_value':pick_round6_rejected,'zero_access_changes_diagnostic_only':all(x['observed_comparables']==0 for x in no_access) and baseline_intrinsic==[gross_player(id,'rebuild') for id in ['05mx9','06f1c','06ps2']],'frozen_U2_reproduced':all(abs(frozen[m]['net'][1]-PREVIOUS['cases'][0]['comparisons'][m]['B']['net'][1])<1e-8 for m in u.MODES),'no_nontradable_round_in_assets':all(p['round']<=5 for p in u.PICK.values()),'cohort_ids_are_unique':len({c['fantraxId'] for c in COHORT})==len(COHORT),'cohort_free_by_export_id':all(u.P[c['fantraxId']]['owner']=='Free agent' for c in COHORT),'cohort_excludes_FYPD_restricted':all(c['name'] not in {d['name'] for d in u.DRAFT} for c in COHORT),'capacity_zero_yields_zero_harvest':all(x['mean_harvest']==0 for x in sims.values() if x['focal_post_fypd_capacity']==0),'draft_turns_never_exceed_20':all(x['last_round_selected']<=20 for x in sims.values()),'same_FA_not_reused_in_package':all(len(set(x['chosen_ids'].values()))==len(x['chosen_ids']) for arr in regeneration.values() for x in arr)}
 assert all(invariants.values())
 owned_ladder={}
 for mode in u.MODES:
  rows=[]
  for target in [u.P['06f1c'],u.P['05mx9'],u.P['06ps2']]:
   peers=[p for p in u.P.values() if p.get('prospect') and p['owner']!='Free agent' and p['id']!=target['id'] and u.role(p)==u.role(target) and gross_player(p['id'],mode)>=.8*gross_player(target['id'],mode) and u.probabilities(p)[4]>=.8*u.probabilities(target)[4]]
   rows.append({'target_id':target['id'],'owned_compatible_prospect_count':len(peers),'owners':sorted({p['owner'] for p in peers}),'peer_ids':[p['id'] for p in peers],'market_asking_price':None})
  owned_ladder[mode]=rows
 lottery={}
 for side in [a,b]:
  ep=[]
  for i,p in enumerate(side):
   if p.get('kind')=='pick':
    slot=56 if p['id']==a[2]['id'] else 58 if p['id']==a[3]['id'] else None
    indices=list(range(max(0,slot-13),min(len(u.DRAFT),slot+12))) if slot else list(range((p['round']-1)*12,p['round']*12))
    ep.append(statistics.mean(u.probabilities(u.draft_proxy(u.DRAFT[j],p['year']))[4] for j in indices))
   else:ep.append(u.probabilities(p)[4])
  lottery['package' if side is a else 'Josuar']={'asset_superstar_probabilities':ep,'prob_at_least_one_if_independent':1-math.prod(1-x for x in ep),'expected_number_of_superstars':sum(ep),'label':'U2 outcome hypotheses, not fitted frequencies; different arrival times and roster requirements; no trade-price implication'}
 output={'status':'OFFLINE DIAGNOSTIC; NOT A DEPLOYABLE FORMULA OR FAIRNESS MODEL','as_of':'2026-10-07','rules':{'formal_rounds':20,'tradable_rounds':[1,2,3,4,5],'FA_access_rounds':list(range(6,21)),'observed_early_stopping_rounds':'10–17, capacity behavior reported by user; not a formal limit'},'owned_reacquisition_ladder':owned_ladder,'superstar_lottery':lottery,'assets':assetrows,'frozen':frozen,'gross_unknown_slots':gross_unknown,'corrected_same_capacity':corrected,'decomposition':decomposition,'sensitivities':scenarios,'FA_cohort':COHORT_VALUES,'MLB_FA':MLB_FA,'rosters':roster_audit(),'replacement_ladder':ladder,'draft_access_scenarios':sims,'joint_regeneration':regeneration,'stress_tests':stress,'invariants':invariants}
 (ROOT/'results.json').write_text(json.dumps(output,indent=2));print(json.dumps({'decomposition':decomposition,'cohort':[(c['name'],c['peer_count'],c['values']['rebuild'],c['elite_probability_mean']) for c in COHORT_VALUES],'ladder':ladder['rebuild'],'invariants':invariants},indent=2))
if __name__=='__main__':main()
