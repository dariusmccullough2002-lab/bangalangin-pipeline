"""Read recovered production model without rebuilding or modifying it."""
import sys,json,hashlib
from pathlib import Path
root=Path(sys.argv[1]).resolve();sys.path.insert(0,str(root/'trade-preview-v23c-evidence-guard'))
import model_asset_fit as m
out=Path(__file__).parent/'inputs/model-evidence.json'
names=['Kyle Bradish','Jose Soriano','Colt Keith','Tarik Skubal','Paul Skenes','Eury Perez','Spencer Strider','Shane McClanahan','Mason Montgomery','Emmanuel Clase','Josh Hader','Michael King','Reid Detmers','Fernando Tatis Jr.']
result={'display_multiplier':m.r.DISPLAY,'reference_workload':m.r.REFERENCE,'replacement_floor':m.r.floor,'category_references':m.old.refs,'category_dispersion':{k:v.tolist() for k,v in m.old.dens.items()},'players':{},'source_hashes':{}}
for p in m.old.players.values():
 if p['name'] not in names:continue
 ps,audit=m.paths(p);rr=m.v.role(p);forecast=m.v.recent_forecast(p,rr)
 if not forecast or audit['kind']!='MLB':continue
 rates,work,fa=forecast;age=round(float(p.get('age') or 26));import numpy as np
 q=int(np.searchsorted(m.v.base.CUTS[rr],m.r.surplus({k:v*work for k,v in rates.items()},rr)/work*m.r.REFERENCE[rr]));curve=m.v.curve(rr,age,q)
 annual=[]
 for t,s in enumerate(audit['annual_projection']):
  vector=m.old.vector(s,rr,m.old.refs)/m.old.dens['H' if rr=='H' else 'P'];gross=sum(vector);replacement=m.r.floor[rr]*m.r.exposure(s,rr)/m.r.REFERENCE[rr];expected=sum(prob*path[t] for prob,path in ps)
  annual.append({'year':2027+t,'workload':m.r.exposure(s,rr),'cohort_workload_multiplier':curve['path'][t]['workload'],'cohort_rate_multipliers':curve['path'][t]['rates'],'projection':s,'signed_category_contributions':vector.tolist(),'gross_category_score':gross,'replacement_deduction':replacement,'central_surplus':gross-replacement,'central_utility':m.r.utility(gross-replacement),'state_expected_utility':expected,'discount':.88**t,'discounted_display_contribution':expected*.88**t*m.r.DISPLAY})
 sensitivity=[]
 for label,capacity in [('recent_baseline',work),('latest_observed',m.r.exposure(max(m.v.seasons(p,rr),key=lambda z:z['year'])['stat'],rr)),('healthy_observed',fa.get('healthy_observed_workload',work)),('historical_role_reference',m.r.REFERENCE[rr])]:
  ratio=capacity/work;variants=[]
  for probability,statpath in zip([.25,.5,.25],audit['outcome_state_projections']):
   vals=[m.r.utility(m.r.surplus({k:v*ratio for k,v in s.items()},rr)) for s in statpath];variants.append((probability,vals))
  sensitivity.append({'label':label,'initial_workload':capacity,'value':m.competitive(variants,'neutral')['display'],'usage':'Diagnostic counterfactual, not validated forecasting correction'})
 hist=m.v.seasons(p,rr)
 result['players'][p['id']]={'name':p['name'],'mlbamId':p.get('mlbamId'),'role':rr,'position':p.get('position'),'history':hist,'forecast_audit':fa,'base_workload':work,'talent_rates':rates,'age':age,'cohort':{k:v for k,v in curve.items() if k!='path'},'annual':annual,'value':m.competitive(ps,'neutral')['display'],'paths':ps,'workload_sensitivity':sensitivity,'risk_deduction':0,'additional_injury_penalty':0,'role_retention_penalty':0,'verified_appearances':{str(z['year']): (p.get('pit',{}) if z['year']==2026 else m.v.appearance_history().get((z['id'],z['year']),{})) for z in hist}}
for folder in ['trade-preview-v22/model','trade-preview-v23','trade-preview-v23c-evidence-guard']:
 for f in (root/folder).glob('*.py'):result['source_hashes'][str(f.relative_to(root))]=hashlib.sha256(f.read_bytes()).hexdigest()
out.write_text(json.dumps(result,indent=2));print('Exported exact model evidence',len(result['players']))
