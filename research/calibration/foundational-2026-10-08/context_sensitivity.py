"""Gate decomposition for selected players, reusing saved fixed contexts."""
import json,gzip
from pathlib import Path
import numpy as np
from category_engine import combine,points
P=Path(__file__).resolve().parent;O=P/'results';d=json.load(gzip.open(P/'raw/game-inputs.json.gz','rt'));contexts=json.load(open(O/'fixed-roster-contexts.json'))[1]['contexts'];allrows=json.load(open(O/'weekly-category-diagnostics.json'));names=['Aaron Judge','Juan Soto','Josh Naylor','Brandon Nimmo','Tarik Skubal','Zack Wheeler','Kevin Gausman','Carlos Rodón','Emmanuel Clase','Josh Hader']
wks=sorted(w for w in d['weekly'] if w.startswith('2024') and '2024-04-01'<=w<='2024-09-22' and 'P' in d['weekly'][w]);out=[]
for a in allrows:
 if a['year']!=2024 or a['name'] not in names:continue
 id=a['mlbamId'];role=a['role'];family='H' if role=='H' else 'P';normal=[];nogate=[];conditional=[];repl=[];conditional_repl=[]
 for i,c in enumerate(contexts):
  baseids=c['H'][:-1] if family=='H' else (c['SP'][:-1]+c['RP'] if role=='SP' else c['SP']+c['RP'][:-1]);replacement=c['H'][-1] if family=='H' else (c['SP'][-1] if role=='SP' else c['RP'][-1]);opp=contexts[(i+17)%len(contexts)];oppids=opp['H'] if family=='H' else opp['SP']+opp['RP']
  if id in baseids or id==replacement or id in oppids:continue
  for wk in wks:
   z=d['weekly'][wk][family];base=combine(*[z.get(str(j),{}) for j in baseids]);other=combine(*[z.get(str(j),{}) for j in oppids]);full=combine(base,z.get(str(id),{}));rep=combine(base,z.get(str(replacement),{}));n=points(full,other,family)-points(base,other,family);r=points(full,other,family)-points(rep,other,family);normal.append(n);repl.append(r)
   # days=0 disables eligibility for diagnostic decomposition only, never production category scoring.
   ng=points(full,other,family,days=0)-points(base,other,family,days=0);nogate.append(ng)
   if family=='H' or (base.get('outs',0)>=105 and other.get('outs',0)>=105):conditional.append(n);conditional_repl.append(r)
 out.append({'name':a['name'],'mlbamId':id,'role':role,'all_context_marginal':np.mean(normal,axis=0).tolist(),'all_context_replacement_delta':float(np.mean(np.sum(repl,axis=1))),'eligibility_gate_disabled_marginal':np.mean(nogate,axis=0).tolist(),'eligibility_effect_total':float(np.mean(np.sum(np.array(normal)-np.array(nogate),axis=1))),'both_background_and_opponent_eligible_n':len(conditional),'conditional_marginal':np.mean(conditional,axis=0).tolist() if conditional else None,'conditional_replacement_delta':float(np.mean(np.sum(conditional_repl,axis=1))) if conditional else None,'conditional_warning':'Conditioning on observed qualifying backgrounds is a diagnostic selection, not a forecast or estimate of actual Fantrax owner utility.'})
(O/'eligibility-context-sensitivity.json').write_text(json.dumps(out,indent=2));print(json.dumps(out,indent=2))
