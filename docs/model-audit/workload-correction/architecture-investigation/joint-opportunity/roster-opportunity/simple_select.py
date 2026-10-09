"""Simplified family-level blend. Existing role features handle player roles;
no per-cohort model router. Proper mean scoring and development cohort guards.
"""
from mean_select import *
METHODS=['strong_prior','incumbent','tree','ridge_1000','hybrid_half','hybrid_quarter','incumbent_strong_half','incumbent_strong_quarter']
def run():
 choices={};development={}
 for fam in ['P','H']:
  rows=read(HERE/f'Development_{fam}_Cases.json.gz');by={(a['id'],a['anchor']):a for a in rows};strong=read(HERE.parent/'first-year-repair'/'Development_Cases.json.gz')[fam];idx={(a['mlbam_id'],a['anchor']):a for a in strong};sel=read(HERE.parent/'first-year-repair'/'Selection_Freeze.json')['selected'][fam]
  for a in rows:
   a['strong_prior']=idx[a['id'],a['anchor']][sel] if sel!='incumbent' else a['incumbent'];a['hybrid_half']=.5*(a['strong_prior']+a['tree']);a['hybrid_quarter']=.75*a['strong_prior']+.25*a['tree'];a['incumbent_strong_half']=.5*(a['strong_prior']+a['incumbent']);a['incumbent_strong_quarter']=.25*a['strong_prior']+.75*a['incumbent']
  score=summaries(rows,METHODS);groups=[g for g in (['stable_rotation','young_entry','interrupted'] if fam=='P' else ['everyday','durable','young_entry','interrupted']) if g in score and score[g]['strong_prior']['n']>=15];eligible={m:score['all'][m]['MAE']<=1.05*score['all']['strong_prior']['MAE'] and all(score[g][m]['MAE']<=1.05*score[g]['strong_prior']['MAE'] for g in groups) for m in METHODS};objective={m:score['all'][m]['RMSE']+.1*abs(score['all'][m]['bias'])+.25*np.mean([score[g][m]['RMSE'] for g in groups]) for m in METHODS};selected=min([m for m in METHODS if eligible[m]],key=objective.get);choices[fam]=selected;development[fam]={'scores':score,'eligible':eligible,'objective':objective,'groups':groups,'selected':selected};print('SIMPLE SELECT',fam,selected,objective,eligible,flush=True)
 saveout('Simple_Selection_Freeze.json',{'family_choices':choices,'development':development,'source_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'test_used_for_selection':False,'source_note':'Simplification after disclosed hybrid safety results; same ID4 dev selection, ID0 retrospective already exposed.'})
 # Keep adapter interface stable: every role evidence group uses the same family
 # method; roles remain inspectable features, not a proliferation of routers.
 saveout('Hybrid_Selection_Freeze.json',{'role_choices':{'P':{g:choices['P'] for g in ['demonstrated_rotation','interrupted_rotation','other_rotation']},'H':{g:choices['H'] for g in ['demonstrated_everyday','interrupted_everyday','other_hitter']}},'family_choices':choices,'development':development,'source_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'heldout_used_for_selection':False,'routing':'one frozen method per family; existing RP preserved','previous_experiments_preserved':True})
if __name__=='__main__':run()
