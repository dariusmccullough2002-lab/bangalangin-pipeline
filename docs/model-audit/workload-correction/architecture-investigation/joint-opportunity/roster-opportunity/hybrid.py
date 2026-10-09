"""Minimal first-year opportunity adapter; no production or later-year mutation."""
from engine import *
from mean_select import role_group
class HybridForecastEngine:
 def __init__(self,folder=HERE):
  self.folder=Path(folder);self.selection=read(self.folder/'Hybrid_Selection_Freeze.json')['role_choices'];self.count_models={f:joblib.load(self.folder/f'current-{f}.joblib') for f in ['P','H']};self.strong_models={f:joblib.load(HERE.parent/'first-year-repair'/f'current-{f}.joblib') for f in ['P','H']};self.strong_selection=read(HERE.parent/'first-year-repair'/'Selection_Freeze.json')['selected'];self.history_models={}
 def predict(self,zs,evidence=(),asof='2026-10-09',incumbent_components=None):
  out=[]
  for z in zs:
   fam='H' if z['role']=='H' else 'P';asof_year=z['year'];c=copy.deepcopy(incumbent_components[(z['id'],z['year'],z['role'])]) if incumbent_components is not None else incumbent(asof_year,fam,[z])[0];g=role_group(z);method='incumbent' if z['role']=='RP' else self.selection[fam][g]
   if asof_year==2026:count_model=self.count_models[fam];strong_model=self.strong_models[fam]
   else:
    if (asof_year,fam) not in self.history_models:self.history_models[asof_year,fam]=(joblib.load(self.folder/f'test-{fam}-{asof_year}.joblib'),joblib.load(HERE.parent/'first-year-repair'/f'test-{fam}-{asof_year}.joblib'))
    count_model,strong_model=self.history_models[asof_year,fam]
   strong=prior.opportunity(strong_model,[z],[c],self.strong_selection[fam])[0] if z['role']!='RP' else c
   if method=='strong_prior':q=strong
   elif method=='incumbent':q=c
   elif method in {'hybrid_half','hybrid_quarter'}:
    counts=predict_layer(count_model,[z],[c],'tree')[0];key='PA' if fam=='H' else 'IP';weight=.5 if method=='hybrid_half' else .25;q=reconcile_components(c,(1-weight)*strong[key]+weight*counts[key],754 if fam=='H' else 251,fam,'hybrid_half',counts.get('GS',0),counts.get('RA',0),g)
   elif method in {'incumbent_strong_half','incumbent_strong_quarter'}:
    key='PA' if fam=='H' else 'IP';weight=.5 if method=='incumbent_strong_half' else .25;q=reconcile_components(c,weight*strong[key]+(1-weight)*c[key],754 if fam=='H' else 251,fam,method,c.get('GS',0),c.get('RA',0),g)
   else:q=predict_layer(count_model,[z],[c],method)[0]
   if fam=='H' and method=='incumbent':q=reconcile_components(q,q['PA'],754,'H',method,group=g)
   d=decomposition(z);q['hybrid_method']=method;q['role_evidence_group']=g;q.setdefault('opportunity_layer',{}).update({'demonstrated_healthy_opportunity':d['healthy_opportunity'],'observed_latest_opportunity':d['latest_opportunity'],'work_per_appearance':d['depth'],'injury_evidence':'missing','roster_depth_evidence':'missing','opportunity_is_unconditional':True,'no_additional_absence_or_age_discount':True})
   if any(e.get('mlbam_id')==z['id'] for e in evidence):q=apply_evidence(q,z,evidence,asof)
   out.append(q)
  return out
