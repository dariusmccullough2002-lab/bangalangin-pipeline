"""Three predeclared engineering iterations, development-only selection."""
from engine import *
from collections import defaultdict

def summarize(rows,methods):
 out={}
 for group in sorted({g for a in rows for g in a['groups']}):
  xs=[a for a in rows if group in a['groups']];out[group]={method:metric([(a[method],a['actual']) for a in xs]) for method in methods}
 return out

def run():
 result={};selection={};allcases={};man=[]
 protocolhash=hashlib.sha256((HERE/'PROTOCOL.md').read_bytes()).hexdigest()
 for fam in ['P','H']:
  variants=P_VARIANTS if fam=='P' else VARIANTS
  rows=[];methods=['incumbent',*variants]
  for year in [2016,2017,2018,2021,2022]:
   xs=[z for rr in (['SP'] if fam=='P' else ['H']) for z in records[rr] if z['year']==year and z['id']%5==4 and z['positive_anchor']]
   model=fit(year,fam);checkpoint(model,HERE/f'dev-{fam}-{year}.joblib',compress=3);man.append(model['manifest']);inc=incumbent(year,fam,xs);pred={name:opportunity(model,xs,inc,name) for name in variants};key='IP' if fam=='P' else 'PA'
   for i,z in enumerate(xs):
    group=cohort(z);groups=['all',group,f'anchor_{year}']
    if fam=='H' and z['x'][0]>=400:groups.append('all_everyday')
    a={'mlbam_id':z['id'],'anchor':year,'groups':groups,'actual':(target(z) or {}).get('stat',{}).get(key,0),'incumbent':inc[i][key]}
    for name in variants:a[name]=pred[name][i][key]
    rows.append(a)
   print('Development fit',fam,year,len(xs),flush=True)
  score=summarize(rows,methods);critical='stable_rotation' if fam=='P' else 'all_everyday';elig={}
  for name in methods:
   elig[name]=score['all'][name]['MAE']<=score['all']['incumbent']['MAE']*1.03 and score[critical][name]['MAE']<=score[critical]['incumbent']['MAE']*1.05
  groups=[g for g in (['stable_rotation','young_entry','interrupted'] if fam=='P' else ['all_everyday','durable','interrupted','young_entry']) if g in score and score[g]['incumbent']['n']>=15]
  obj={name:(score['all'][name]['MAE']+.15*abs(score['all'][name]['bias'])+np.mean([score[g][name]['MAE']+.15*abs(score[g][name]['bias']) for g in groups]))/(150 if fam=='P' else 600) for name in methods}
  selected=min([a for a in methods if elig[a]],key=lambda name:obj[name]);selection[fam]=selected;result[fam]={'scores':score,'objective':obj,'eligible':elig,'objective_groups':groups,'selected':selected};allcases[fam]=rows
  print('Selection',fam,selected,'objectives',obj,'eligible',elig,flush=True)
 put('Development_Results.json',result);put('Development_Cases.json.gz',allcases)
 freeze={'selected':selection,'protocol_sha256':protocolhash,'source_sha256':hashlib.sha256((HERE/'engine.py').read_bytes()).hexdigest(),'manifests':man,'heldout_test_scored':False,'selection_scope':'Only ID4 development; no ID0 new predictions or scores read during selection.'}
 put('Selection_Freeze.json',freeze)
 print('FROZEN',selection,flush=True)
if __name__=='__main__':run()
