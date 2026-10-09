"""Separate RBI prior shrinkage from inherited rate aging; preserve unaged experiment."""
import sys
from pathlib import Path
HERE=Path(__file__).resolve().parent;sys.path.insert(0,str(HERE.parent))
from continuation import *

def aging(ident,y,b):
 rows=hist[ident,'H'];f=base['forecast'](rows,'H',y,ident,strict=True)
 if not f or not f[0]['RBI'] or not b.get('PA'):return 1.
 return b['RBI']/b['PA']/f[0]['RBI']
def run():
 dev={str(s):[] for s in [0,25,100,300]}
 for z in records['H']:
  if z['id']%5!=4 or z['year'] not in [2016,2017,2018,2021,2022] or not z['positive_anchor']:continue
  b=historical_baseline(z)
  if b is None:continue
  t=(target(z) or {}).get('stat',{});a=aging(z['id'],z['year'],b)
  for s in [0,25,100,300]:rr,_=rate(z['id'],z['year'],s);dev[str(s)].append((rr*a*b['PA'],t.get('RBI',0)))
 ds={k:metric(x) for k,x in dev.items()};selected=int(min(ds,key=lambda k:ds[k]['MAE']+.25*abs(ds[k]['bias'])));cases=[]
 for z in hcases+[x for x in hextra if x['anchor']+1!=2020]:
  ident,y=z['mlbam_id'],z['anchor'];a=aging(ident,y,z['baseline']);q={'mlbam_id':ident,'name':z['name'],'anchor':y,'groups':rbi_groups(ident,y),'preserved':z in hcases,'actual':z['actual'].get('RBI',0),'actual_PA':z['actual'].get('PA',0),'baseline':z['baseline']['RBI'],'incumbent':z['past_only']['RBI'],'aging_factor':a}
  for s in [0,25,100,300]:rr,_=rate(ident,y,s);q['strength'+str(s)]=rr*a*z['past_only']['PA'];q['actualPA'+str(s)]=rr*a*z['actual'].get('PA',0)
  q['selected']=q['strength'+str(selected)];cases.append(q)
 scores={}
 for g in sorted({g for z in cases for g in z['groups']}|{'preserved682'}):
  xs=[z for z in cases if z['preserved']] if g=='preserved682' else [z for z in cases if g in z['groups']]
  scores[g]={k:metric([(z[k],z['actual']) for z in xs]) for k in ['baseline','incumbent','selected',*[f'strength{s}' for s in [0,25,100,300]],*[f'actualPA{s}' for s in [0,25,100,300]]]}
 put('RBI_Aging_Validation.json',{'development':ds,'selected_pseudocount':selected,'scores':scores,'scope':'Frozen baseline per-year RBI rate-aging multiplier retained to isolate past-only prior/pseudocount. Unaged direct-rate experiment preserved separately. All evaluations retrospective.'});put('RBI_Aging_Cases.json.gz',cases)
 current=[]
 for z in read(HERE/'RBI_Current_Audit.json.gz'):
  rr,ev=rate(z['mlbam_id'],2026,selected,v.seasons(old.players[z['id']],'H'));a=z['production_year1_rate_aging'];q={**z,'raw_selected_RBI_rate':rr,'aged_selected_RBI_rate':rr*a,'RBI_rate_only_aged':rr*a*z['baseline_PA'],'RBI_joint_workload_aged':rr*a*z['joint_PA'],'rate_ratio_for_frozen_aging_horizons':rr/z['production_talent_rate'],'selected_pseudocount':selected};current.append(q)
 put('RBI_Aging_Current.json.gz',current);print('Aged selected',selected,ds,flush=True)
if __name__=='__main__':run()
