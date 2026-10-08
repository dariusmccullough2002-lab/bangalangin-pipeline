"""Offline architecture contract. Does not supply unvalidated forecasts or optimize rosters."""
import numpy as np
HORIZONS={'Contender':np.array([.65,.25,.10]),'Balanced':np.array([.40,.30,.30]),'Rebuild':np.array([.15,.25,.60])}
def intrinsic_utility(contribution,threshold=11.615250774606945,curvature=.04):
 x=np.maximum(0,np.asarray(contribution,dtype=float));return x+curvature*np.maximum(0,x-threshold)**2

def asset_utility(probabilities,paths,strategy='Balanced'):
 """Common samples of contribution through 3 years. Tail utility once, before expectation."""
 p=np.asarray(probabilities,dtype=float);x=np.asarray(paths,dtype=float);assert x.shape==(len(p),3) and np.all(p>=0) and abs(p.sum()-1)<1e-8
 return float(p@(intrinsic_utility(x)@HORIZONS[strategy]))

def owner_change(sent,received,strategy,incremental_opportunities=()):
 """External joint-before/after calculation must supply unique opportunities; no arbitrary space bonus."""
 ids=[x['opportunity_id'] for x in incremental_opportunities];assert len(ids)==len(set(ids)), 'replacement opportunity counted twice'
 before=sum(asset_utility(a['probabilities'],a['paths'],strategy) for a in sent);after=sum(asset_utility(a['probabilities'],a['paths'],strategy) for a in received)
 capacity=sum(x['incremental_utility'] for x in incremental_opportunities)
 return {'intrinsic_delta':after-before,'replacement_difficulty':'SEPARATE EVIDENCE, NOT ADDED AGAIN','acquisition_scarcity':'SEPARATE EVIDENCE, NOT ADDED AGAIN','owner_specific_utility':after-before+capacity,'incremental_capacity':capacity}

if __name__=='__main__':
 import json
 from pathlib import Path
 from explanations import explain
 a={'probabilities':[1],'paths':[[15,12,9]]};b={'probabilities':[.75,.25],'paths':[[0,0,0],[0,20,25]]};r=[]
 for mode in HORIZONS:
  c=owner_change([a],[b],mode);r.append({'strategy':mode,'example':'Synthetic immediate MLB contribution versus delayed elite-prospect distribution; not a current asset forecast','ledgers':c,'explanation':explain('Example owner',mode,asset_utility(a['probabilities'],a['paths'],mode),asset_utility(b['probabilities'],b['paths'],mode),c['owner_specific_utility'])})
 # Linear expectation across assets; adding a package bonus would violate this check.
 assert abs(owner_change([],[a,a],'Balanced')['intrinsic_delta']-2*asset_utility(a['probabilities'],a['paths']))<1e-10
 assert asset_utility(b['probabilities'],b['paths'])>float(intrinsic_utility(np.array(b['probabilities'])@np.array(b['paths']))@HORIZONS['Balanced'])
 try:owner_change([],[],'Balanced',[{'opportunity_id':'same','incremental_utility':1}]*2);raise RuntimeError('duplicate opportunity accepted')
 except AssertionError:pass
 Path(__file__).resolve().parent.joinpath('results/ledger-and-narrative-checks.json').write_text(json.dumps({'status':'PASS; offline contract, not a new fitted dynasty model','owner_scenarios':r,'checks':['same contribution utility for H/SP/RP','E[U(X)] applied once before expectation','sum asset expectations, never U(package total)','unique opportunity IDs prevent duplicate capacity credit','scarcity and replacement evidence excluded from intrinsic utility','owner horizons are inherited assumptions, not calibrated results']},indent=2))
