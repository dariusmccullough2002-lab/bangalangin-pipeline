"""Correct missing-target bookkeeping from saved predictions, with no repeated fit."""
from joint_model import *
cases=read(OUT/'Joint_Cases.json.gz');extra=read(OUT/'Joint_Additional_Cases.json.gz');prior={(z['mlbam_id'],z['anchor'],z['role']):z for z in read(PARENT/'Quality_Aware_Cases.json.gz')}
for z in cases:z['actual_absent']=not prior[z['mlbam_id'],z['anchor'],z['role']]['actual']
for z in extra:z['actual_absent']=not lookup.get((z['mlbam_id'],z['anchor']+1,'P'))
d=read(OUT/'Joint_Validation.json');methods=['baseline','selected','role_aware','linear_SP',*VARIANTS,'joint_selected'];d['expanded']=scores(cases,methods);chosen=d['selected'];by={(z['mlbam_id'],z['anchor']):z for z in cases};frozen=[]
for z in read(PARENT.parent/'Historical_Cases.json'):
 q=copy.deepcopy(by[z['mlbam_id'],z['anchor']]);q['baseline']=z['baseline']
 for vv in [*VARIANTS,'joint_selected']:q[vv]=category_stats(z['baseline'],q['components'][chosen if vv=='joint_selected' else vv])
 for vv in ['selected','role_aware','linear_SP']:
  ratio=q[vv]['IP']/z['baseline']['IP'];q[vv]={k:v*ratio for k,v in z['baseline'].items()}
 frozen.append(q)
d['frozen94']=scores(frozen,methods);d['additional']=scores(extra,['baseline',*VARIANTS,'joint_selected']);d['scoring_bookkeeping']='Absent target flag kept separately from appended zero appearance counts; all missing-next-season IP/K/QA3 targets remain scored as zero.';save('Joint_Validation.json',d);save('Joint_Cases.json.gz',cases);save('Joint_Additional_Cases.json.gz',extra)
assert abs(d['expanded']['all']['metrics']['IP']['baseline']['MAE']-29.422136250879802)<1e-10
for g in ['all','SP','RP','first_MLB_season','second_MLB_season']:print(g,{k:round(v['MAE'],3) for k,v in d['expanded'][g]['metrics']['IP'].items()})
