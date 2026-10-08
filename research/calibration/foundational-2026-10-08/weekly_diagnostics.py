"""Fixed prior-season roster contexts; no optimizer and no actual Fantrax team replay."""
import json,gzip,datetime
from pathlib import Path
import numpy as np
from historical_features import seasons
from category_engine import points,combine,pitching
P=Path(__file__).resolve().parent;O=P/'results';d=json.load(gzip.open(P/'raw/game-inputs.json.gz','rt'));annual=seasons();rng=np.random.default_rng(3505)
roles={str(y):{str(id):a['role'] for (yr,id),a in annual.items() if yr==y} for y in [2017,2023]}
allout=[];rosters=[]
for year in [2018,2024]:
 previous=year-1;pos=d['positions'][str(previous)];H=[a for (y,id),a in annual.items() if y==previous and a['role']=='H' and a['ex']>=250];SP=[a for (y,id),a in annual.items() if y==previous and a['role']=='SP' and a['ex']>=80];RP=[a for (y,id),a in annual.items() if y==previous and a['role']=='RP' and a['ex']>=30]
 H=sorted(H,key=lambda a:a['score'],reverse=True)[:180];SP=sorted(SP,key=lambda a:a['score'],reverse=True)[:90];RP=sorted(RP,key=lambda a:a['score'],reverse=True)[:90]
 def eligible(a,slot):
  p=pos.get(str(a['id']),{});valid={k for k,v in p.items() if v>=20 and k!='1'}
  if not valid and p:valid={max(p,key=p.get)}-{'1'}
  return bool(valid.intersection(slot))
 slots=[('C',{'2'}),('1B',{'3'}),('2B',{'4'}),('3B',{'5'}),('SS',{'6'}),('CI',{'3','5'}),('MI',{'4','6'})]+[('OF',{'7','8','9'})]*5
 def hitter_roster():
  ids=[];assigned=[]
  for label,allowed in slots:
   pool=[a for a in H if a['id'] not in ids and eligible(a,allowed)];assert pool,label;a=pool[int(rng.integers(len(pool)))];ids.append(a['id']);assigned.append([label,a['id']])
  a=[a for a in H if a['id'] not in ids];id=a[int(rng.integers(len(a)))]['id'];return ids+[id],assigned+[['UT',id]]
 contexts=[]
 for i in range(40):
  ids,assign=hitter_roster();sp=rng.choice([a['id'] for a in SP],6,replace=False).tolist();rp=rng.choice([a['id'] for a in RP],3,replace=False).tolist();contexts.append({'H':ids,'SP':sp,'RP':rp,'assign':assign})
 rosters.append({'year':year,'selection':'Random fixed rosters from qualified prior-year pools, seed3505. No current-year selection or week-by-week optimization. 13H +9P=22 active. All H positions satisfy prior20-game or most-played fallback. Generic P slots.','contexts':contexts})
 wks=sorted(w for w in d['weekly'] if w.startswith(str(year)) and f'{year}-04-01'<=w<=f'{year}-09-22' and 'P' in d['weekly'][w] and 'H' in d['weekly'][w]);assert len(wks)>=24
 candidates=[a for (y,id),a in annual.items() if y==year and a['ex']>=(250 if a['role']=='H' else 80 if a['role']=='SP' else 30)]
 # No injury/workload extrapolation: realized missing weekly appearances explicitly zero.
 for candidate in candidates:
  id=candidate['id'];role=candidate['role'];family='H' if role=='H' else 'P';marg=[];replaced=[];eligible_before=[];eligible_after=[];shares=[]
  for c in contexts:
   baseids=c['H'][:-1] if family=='H' else (c['SP'][:-1]+c['RP'] if role=='SP' else c['SP']+c['RP'][:-1]);replacement=c['H'][-1] if family=='H' else (c['SP'][-1] if role=='SP' else c['RP'][-1]);opp=contexts[(contexts.index(c)+17)%len(contexts)];oppids=opp['H'] if family=='H' else opp['SP']+opp['RP']
   if id in baseids or id==replacement or id in oppids:continue
   for wk in wks:
    z=d['weekly'][wk][family];base=combine(*[z.get(str(j),{}) for j in baseids]);other=combine(*[z.get(str(j),{}) for j in oppids]);full=combine(base,z.get(str(id),{}));rep=combine(base,z.get(str(replacement),{}));marg.append(points(full,other,family)-points(base,other,family));replaced.append(points(full,other,family)-points(rep,other,family))
    if family=='P':eligible_before.append(base.get('outs',0)>=105);eligible_after.append(full.get('outs',0)>=105)
  a=np.array(marg);r=np.array(replaced);allout.append({'year':year,'mlbamId':id,'name':candidate['name'],'role':role,'Phase1_intrinsic_score':candidate['score'],'weekly_marginal_points_per_category':a.mean(axis=0).tolist(),'weekly_marginal_total':float(a.sum(axis=1).mean()),'weekly_replacement_delta_per_category':r.mean(axis=0).tolist(),'weekly_replacement_delta_total':float(r.sum(axis=1).mean()),'marginal_context_10_90':np.quantile(a.sum(axis=1),[.1,.9]).tolist(),'eligible_without_candidate':float(np.mean(eligible_before)) if eligible_before else None,'eligible_with_candidate':float(np.mean(eligible_after)) if eligible_after else None,'weeks':len(wks),'context_week_comparisons':len(a)})
 summaries=[]
 for role in ['H','SP','RP']:
  z=[a for a in allout if a['year']==year and a['role']==role];summaries.append({'year':year,'role':role,'n':len(z),'median_marginal_week_points':float(np.median([a['weekly_marginal_total'] for a in z])),'median_replacement_delta':float(np.median([a['weekly_replacement_delta_total'] for a in z])),'marginal_10_90':np.quantile([a['weekly_marginal_total'] for a in z],[.1,.9]).tolist()})
 (O/f'weekly-role-summary-{year}.json').write_text(json.dumps(summaries,indent=2));print(summaries,flush=True)
(O/'weekly-category-diagnostics.json').write_text(json.dumps(allout,indent=2));(O/'fixed-roster-contexts.json').write_text(json.dumps(rosters,indent=2))
