"""Fixed diagnostic removal of two verified MiLB starting-share features only."""
import joint_model as j
from joint_model import *
original_xrow=j.xrow
def without_minor(z,h=1,calendar=False):
 x=original_xrow(z,h,calendar).copy();x[29:31]=0;return x
j.xrow=without_minor
cases=read(OUT/'Joint_Cases.json.gz');by={(z['mlbam_id'],z['anchor'],z['role']):z for z in cases};result=[];manifest=[]
for year in [2018,2021,2024]:
 model=j.fit_pitch(year);manifest.append(model['manifest']);joblib.dump(model,OUT/f'minor-ablation-{year}.joblib',compress=3);xs=[z for rr in ['SP','RP'] for z in records[rr] if z['year']==year and (z['id'],year,z['role']) in by];pred=j.predict_pitch(model,xs,variant='joint_linear_depth')
 for z,p in zip(xs,pred):
  q=copy.deepcopy(by[z['id'],year,z['role']]);q['without_MiLB_role']=category_stats(q['baseline'],p);q['without_MiLB_role_components']=p;result.append(q)
 print('MiLB role ablation completed',year,flush=True)
save('Minor_Role_Ablation.json',{'scores':scores(result,['baseline','joint_selected','without_MiLB_role']),'manifests':manifest,'removed_feature_indices':[29,30],'scope':'Fixed exploratory three-anchor diagnostic; physical capacity and all MLB/talent features unchanged. Not used for test-label model selection.'});save('Minor_Role_Ablation_Cases.json.gz',result)
