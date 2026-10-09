from neighbors import *
# Mean-workload selection uses squared-error scoring. Conditional median experts
# remain comparators. Roles derive from current demonstrated use, not tenure.
def role_group(z):
 d=decomposition(z)
 if z['role']=='SP':return 'demonstrated_rotation' if d['latest_opportunity']>=24 and z['x'][17]>=.8 else 'interrupted_rotation' if cohort(z)=='interrupted' else 'other_rotation'
 return 'interrupted_everyday' if cohort(z)=='interrupted' and d['healthy_opportunity']>=120 else 'demonstrated_everyday' if d['latest_opportunity']>=120 else 'other_hitter'
def run():
 specs=['strong_prior','neighbors_50','neighbors_150','neighbors_quarter','neighbors_half'];freeze={};casesout={}
 for fam in ['P','H']:
  rows=read(HERE/f'Development_{fam}_Cases.json.gz');by={(a['id'],a['anchor']):a for a in rows};strong=read(HERE.parent/'first-year-repair'/'Development_Cases.json.gz')[fam];idx={(a['mlbam_id'],a['anchor']):a for a in strong};oldsel=read(HERE.parent/'first-year-repair'/'Selection_Freeze.json')['selected'][fam]
  for year in [2016,2017,2018,2021,2022]:
   zs=[z for z in records['SP' if fam=='P' else 'H'] if z['year']==year and (z['id'],year) in by];mod=joblib.load(HERE/f'neighbor-dev-{fam}-{year}.joblib');p50=npred(mod,zs,50);p150=npred(mod,zs,150)
   for i,z in enumerate(zs):
    a=by[z['id'],year];a['role_group']=role_group(z);a['strong_prior']=idx[z['id'],year][oldsel] if oldsel!='incumbent' else a['incumbent'];a['neighbors_50']=p50[i];a['neighbors_150']=p150[i];a['neighbors_quarter']=.75*a['strong_prior']+.25*p50[i];a['neighbors_half']=.5*(a['strong_prior']+p50[i])
  choices={}
  for group in sorted({a['role_group'] for a in rows}):
   xs=[a for a in rows if a['role_group']==group];s={m:metric([(a[m],a['actual']) for a in xs]) for m in specs};eligible=[m for m in specs if s[m]['MAE']<=s['strong_prior']['MAE']*1.05];choice=min(eligible,key=lambda m:s[m]['RMSE']+.1*abs(s[m]['bias'])) if len(xs)>=30 else 'strong_prior';choices[group]={'selected':choice,'n':len(xs),'metrics':s}
  freeze[fam]=choices;casesout[fam]=rows;print('MEAN SELECT',fam,{g:x['selected'] for g,x in choices.items()},flush=True)
 saveout('Mean_Selection_Freeze.json',{'role_choices':freeze,'source_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'test_used_for_selection':False,'proper_mean_score':'RMSE + 0.1 absolute bias, MAE regression capped5%, groups>=30'})
 # Historical and current outputs reuse models without refitting or test selection.
 results={};flat=[]
 for fam in ['P','H']:
  rows=read(HERE/f'Neighbor_{fam}_Cases.json.gz');zidx={(z['id'],z['year']):z for z in records['SP' if fam=='P' else 'H']}
  for a in rows:
   z=zidx[a['mlbam_id'],a['anchor']];g=role_group(z);a['role_group']=g;a['mean_selected']=a[freeze[fam][g]['selected']];a['groups']+=['role_'+g];flat.append({k:v for k,v in a.items() if k!='groups'})
  results[fam]=summaries(rows,['baseline','incumbent','strong_prior','mean_selected']);saveout(f'Mean_{fam}_Cases.json.gz',rows)
 saveout('Mean_Validation.json',results);csvout('Mean_Chronological_Comparisons.csv',flat)
 current=read(HERE/'Final_Current.json.gz');league={a['id']:a for a in read(OUT/'Past_Only_League_Impact.json.gz')}
 for a in current:
  rr=a['role'];fam='H' if rr=='H' else 'P'
  if rr=='RP':a['mean_selected']=a['strong_prior'];a['mean_method']='preserved_RP';continue
  p=old.players[a['id']];rows=v.seasons(p,rr);z={'id':a['mlbam_id'],'year':2026,'role':rr,'history_override':rows,'x':base['features'](rows,rr,2026,a['mlbam_id']),'bounded_x':base['features'](rows,rr,2026,a['mlbam_id'],True)};g=role_group(z);method=freeze[fam][g]['selected'];a['role_group']=g;a['mean_method']=method;a['mean_selected']=a[method]
 csvout('Mean_Current_Comparisons.csv',current);saveout('Mean_Current.json.gz',current);print('MEAN COMPLETE',flush=True)
if __name__=='__main__':run()
