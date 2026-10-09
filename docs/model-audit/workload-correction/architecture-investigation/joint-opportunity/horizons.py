"""Fixed pooled horizon extrapolation; explicit completed-target and support gates."""
from principal_followup import *
from hitter_model import fit_hitter,predict_hitter,statscale
TAG='past-' if '--past-only' in sys.argv else ''
RESULT='Past_Only_' if TAG else ''
if TAG:import past_only_followup

def run():
 out=[];man=[]
 for year in [2019,2021,2023]:
  pm=joblib.load(OUT/f'{TAG}horizon-pitch-{year}.joblib') if (OUT/f'{TAG}horizon-pitch-{year}.joblib').exists() else augment(fit_pitch(year,horizons=tuple(range(1,9))))
  hm=joblib.load(OUT/f'{TAG}horizon-hitter-{year}.joblib') if (OUT/f'{TAG}horizon-hitter-{year}.joblib').exists() else fit_hitter(year,horizons=tuple(range(1,9)))
  joblib.dump(pm,OUT/f'{TAG}horizon-pitch-{year}.joblib',compress=3);joblib.dump(hm,OUT/f'{TAG}horizon-hitter-{year}.joblib',compress=3);man.append({'pitch':pm['manifest'],'hitter':hm['manifest']})
  for family,model in [('P',pm),('H',hm)]:
   xs=[z for rr in (['H'] if family=='H' else ['SP','RP']) for z in records[rr] if z['year']==year and z['id']%5==0 and z['positive_anchor']]
   for h in range(2,9):
    if year+h>2025 or year+h==2020 or model['manifest']['horizon_support'][str(h)]<100:continue
    pred=predict_hitter(hm,xs,h) if family=='H' else predict_augmented(pm,xs,h,True)
    for z,p in zip(xs,pred):
     b=historical_baseline(z,h)
     if b is None:continue
     if b.get('PA' if family=='H' else 'IP',0)>0:candidate=statscale(b,p) if family=='H' else category_stats(b,p)
     else:
      rates=base['forecast'](hist[z['id'],'H' if family=='H' else 'P'],z['role'],year,z['id'],strict=True)[0];candidate={k:val*p['PA' if family=='H' else 'IP'] for k,val in rates.items()}
      if family=='H':candidate=v.reconcile(candidate)
      else:candidate['QA3']=p['QA3'];candidate['SV']=0;candidate['HLD']=0
     out.append({'mlbam_id':z['id'],'name':z['name'],'anchor':year,'horizon':h,'role':z['role'],'groups':list(dict.fromkeys(z['groups']+[f'horizon_{h}',f'anchor_{year}'])),'baseline':b,'candidate':candidate,'actual':(target(z,h) or {}).get('stat',{}),'components':p})
  print('Chronological horizon completed',year,len(out),flush=True)
 result={'manifests':man,'role_horizon':{},'scope':'Fixed exploratory pooled horizon model; baseline extension is as-of cohort reference, not original saved multi-year benchmark. Current history2013-2025 cannot validate horizons7/8 chronologically. No independent confirmation claimed.'}
 for rr in ['H','SP','RP']:
  for h in range(2,9):
   xs=[z for z in out if z['role']==rr and z['horizon']==h];key='PA' if rr=='H' else 'IP'
   if xs:result['role_horizon'][f'{rr}_{h}']={'n':len(xs),key:{mm:metric([(z[mm][key],z['actual'].get(key,0)) for z in xs]) for mm in ['baseline','candidate']}}
 save(RESULT+'Horizon_Cases.json.gz',out);save(RESULT+'Horizon_Validation.json',result)
 if '--historical-only' in sys.argv:return
 pm=augment(fit_pitch(2026,horizons=tuple(range(1,9))));hm=fit_hitter(2026,horizons=tuple(range(1,9)))
 joblib.dump(pm,OUT/'current-pitch-eight.joblib',compress=3);joblib.dump(hm,OUT/'current-hitter-eight.joblib',compress=3)
 # First-year model remains the development-selected architecture rather than pooled-horizon extrapolation.
 pm1=augment(fit_pitch(2026));hm1=fit_hitter(2026)
 joblib.dump(pm1,OUT/'current-pitch-one.joblib',compress=3);joblib.dump(hm1,OUT/'current-hitter-one.joblib',compress=3)
 save('Current_Model_Manifest.json',{'pitch8':pm['manifest'],'hitter8':hm['manifest'],'pitch1':pm1['manifest'],'hitter1':hm1['manifest'],'training_target_ceiling':2025});print('Current models saved',flush=True)
if __name__=='__main__':run()
