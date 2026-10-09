from mean_select import *
METHODS=['strong_prior','incumbent','tree','ridge_1000','hybrid_half']
def run():
 choices={};development={}
 for fam in ['P','H']:
  rows=read(HERE/f'Development_{fam}_Cases.json.gz');by={(a['id'],a['anchor']):a for a in rows};strong=read(HERE.parent/'first-year-repair'/'Development_Cases.json.gz')[fam];idx={(a['mlbam_id'],a['anchor']):a for a in strong};sel=read(HERE.parent/'first-year-repair'/'Selection_Freeze.json')['selected'][fam]
  for z in records['SP' if fam=='P' else 'H']:
   if (z['id'],z['year']) not in by:continue
   a=by[z['id'],z['year']];a['role_group']=role_group(z);a['strong_prior']=idx[z['id'],z['year']][sel] if sel!='incumbent' else a['incumbent'];a['hybrid_half']=.5*(a['strong_prior']+a['tree'])
  choices[fam]={};development[fam]={}
  for g in sorted({a['role_group'] for a in rows}):
   xs=[a for a in rows if a['role_group']==g];s={m:metric([(a[m],a['actual']) for a in xs]) for m in METHODS};eligible=[m for m in METHODS if s[m]['MAE']<=s['strong_prior']['MAE']*1.05];chosen=min(eligible,key=lambda m:s[m]['RMSE']+.1*abs(s[m]['bias'])) if len(xs)>=30 else 'strong_prior';choices[fam][g]=chosen;development[fam][g]={'n':len(xs),'scores':s,'selected':chosen,'eligible':eligible}
 print('HYBRID CHOICES',choices,flush=True);saveout('Hybrid_Selection_Freeze.json',{'role_choices':choices,'development':development,'source_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'heldout_used_for_selection':False,'proper_mean_score':'RMSE +0.1absbias; MAE<=strong prior105%; group n>=30','scope':'Four previously exposed retrospective iterations; new hybrid selection only uses preserved ID4 development outcomes'})
 results={};flat=[]
 for fam in ['P','H']:
  rows=read(HERE/f'Neighbor_{fam}_Cases.json.gz');idx={(z['id'],z['year']):z for z in records['SP' if fam=='P' else 'H']}
  for a in rows:
   z=idx[a['mlbam_id'],a['anchor']];g=role_group(z);a['role_group']=g;a['groups']+=['role_'+g];a['hybrid_half']=.5*(a['strong_prior']+a['tree']);a['hybrid']=a[choices[fam][g]];flat.append({k:v for k,v in a.items() if k!='groups'})
  results[fam]=summaries(rows,['baseline','incumbent','strong_prior','hybrid']);saveout(f'Hybrid_{fam}_Cases.json.gz',rows)
 saveout('Hybrid_Validation.json',results);csvout('Hybrid_Chronological_Comparisons.csv',flat)
if __name__=='__main__':run()
