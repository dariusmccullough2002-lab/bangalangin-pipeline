"""Score fixed blend using already saved past-only fits, without retraining."""
from past_only_followup import *
cases=read(OUT/'Past_Only_Pitch_Cases.json.gz');extra=read(OUT/'Past_Only_Pitch_Additional.json.gz');by={(z['mlbam_id'],z['anchor'],z['role']):z for z in cases+extra}
for year in sorted({z['anchor'] for z in cases+extra}):
 model=joblib.load(OUT/f'past-pitch-{year}.joblib');xs=[z for rr in ['SP','RP'] for z in records[rr] if z['year']==year and (z['id'],year,rr) in by];ps=pmod.predict_augmented(model,xs,blend=True)
 for z,p in zip(xs,ps):q=by[z['id'],year,z['role']];q['past_only_blend']=category_stats(q['baseline'],p)|{'GS':p['GS'],'RA':p['RA']};q['components']['past_only_blend']=p
original=read(PARENT.parent/'Historical_Cases.json');idx={(z['mlbam_id'],z['anchor']):z for z in cases};frozen=[]
for z in original:
 q=copy.deepcopy(idx[z['mlbam_id'],z['anchor']]);q['baseline']=z['baseline']
 for method in ['principal_QA3','past_only','past_only_blend']:q[method]=category_stats(z['baseline'],q['components'][method])
 frozen.append(q)
result=read(OUT/'Past_Only_Pitch_Validation.json');result['expanded']=scores(cases,['baseline','linear_SP','principal_QA3','past_only','past_only_blend']);result['frozen94']=scores(frozen,['baseline','principal_QA3','past_only','past_only_blend']);result['additional']=scores(extra,['baseline','principal_QA3','past_only','past_only_blend']);save('Past_Only_Pitch_Validation.json',result);save('Past_Only_Pitch_Cases.json.gz',cases);save('Past_Only_Pitch_Additional.json.gz',extra);print('Saved past-only fixed blend scores',flush=True)
