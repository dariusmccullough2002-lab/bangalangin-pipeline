"""Fixed chronology correction: past-only ability priors and stream-correct debut flag."""
import joint_model as j, principal_followup as pmod, hitter_model as hm
from principal_followup import *
original_xrow=j.xrow
@functools.lru_cache(None)
def prior_at(rr,year):
 xs=[a for a in old.AN if a['role']==rr and a['id']%5!=0 and a['year']<=min(year,2025) and a['year']!=2020];total=sum(r.exposure(a['stat'],rr) for a in xs)
 return {k:sum(a['stat'].get(k,0) for a in xs)/total if total else 0 for k in old.fields[rr]}
def past_xrow(z,h=1,calendar=False):
 x=original_xrow(z,h,calendar).copy();ident,year,rr=z['id'],z['year'],z['role'];rows=z.get('history_override',hist.get((ident,'H' if rr=='H' else 'P'),[]))
 if rr=='H':
  firstH=min([a['year'] for a in rows if a['year']<=year and a['stat'].get('PA',0)>0],default=None);x[41]=60/162 if firstH==2020 else 1
 else:
  past=[a for a in rows if year-3<=a['year']<=year and a['role']==rr and a['stat'].get('IP',0)>0];prior=prior_at(rr,year);mass=sum({year-3:.1,year-2:.2,year-1:.3,year:.4}[a['year']] for a in past)
  if mass:
   weighted=[(a['stat'],{year-3:.1,year-2:.2,year-1:.3,year:.4}[a['year']]/mass) for a in past];ex=sum(a['IP']*w for a,w in weighted);rates={k:(sum(a.get(k,0)*w for a,w in weighted)+30*prior.get(k,0))/(ex+30) for k in prior}
  else:rates=prior
  x[31:38]=[rates.get(k,0) for k in ['K','ER','BB','H','QA3','SV','HLD']]
 return x
j.xrow=pmod.xrow=hm.xrow=past_xrow

def run():
 cases=read(OUT/'Principal_Cases.json.gz');extras=read(OUT/'Principal_Additional_Cases.json.gz');by={(z['mlbam_id'],z['anchor'],z['role']):z for z in cases+extras};manifest=[]
 for year in sorted({z['anchor'] for z in cases+extras}):
  model=pmod.augment(j.fit_pitch(year));joblib.dump(model,OUT/f'past-pitch-{year}.joblib',compress=3);manifest.append(model['manifest']);xs=[z for rr in ['SP','RP'] for z in records[rr] if z['year']==year and (z['id'],year,rr) in by];ps=pmod.predict_augmented(model,xs)
  for z,p in zip(xs,ps):
   q=by[z['id'],year,z['role']];q['past_only']=category_stats(q['baseline'],p)|{'GS':p['GS'],'RA':p['RA']};q['components']['past_only']=p
  print('Past-only pitching completed',year,flush=True)
 original=read(PARENT.parent/'Historical_Cases.json');idx={(z['mlbam_id'],z['anchor']):z for z in cases};frozen=[]
 for z in original:
  q=copy.deepcopy(idx[z['mlbam_id'],z['anchor']]);q['baseline']=z['baseline'];q['past_only']=category_stats(z['baseline'],q['components']['past_only']);q['principal_QA3']=category_stats(z['baseline'],q['components']['principal_QA3']);frozen.append(q)
 save('Past_Only_Pitch_Validation.json',{'expanded':scores(cases,['baseline','linear_SP','principal_QA3','past_only']),'frozen94':scores(frozen,['baseline','principal_QA3','past_only']),'additional':scores(extras,['baseline','principal_QA3','past_only']),'manifests':manifest,'scope':'Past-only ability prior excludes holdout IDs and post-anchor seasons. Frozen baseline and comparison category-rate normalization retained for comparability; not newly fitted past-only category/valuation baseline. Fixed correction, not test-selected.'});save('Past_Only_Pitch_Cases.json.gz',cases);save('Past_Only_Pitch_Additional.json.gz',extras)
 hc=read(OUT/'Hitter_Cases.json.gz');he=read(OUT/'Hitter_Additional_Cases.json.gz');byH={(z['mlbam_id'],z['anchor']):z for z in hc+he};manH=[]
 for year in sorted({z['anchor'] for z in hc+he}):
  model=hm.fit_hitter(year);joblib.dump(model,OUT/f'past-hitter-{year}.joblib',compress=3);manH.append(model['manifest']);xs=[z for z in records['H'] if z['year']==year and (z['id'],year) in byH];ps=hm.predict_hitter(model,xs)
  for z,p in zip(xs,ps):q=byH[z['id'],year];q['past_only']=hm.statscale(q['baseline'],p);q['components']['past_only']=p
  print('Stream-correct hitter completed',year,flush=True)
 standard=[z for z in he if z['anchor']+1!=2020];save('Past_Only_Hitter_Validation.json',{'preserved':hm.scores(hc,['baseline','selected','hitter_selected','past_only']),'combined_standard':hm.scores(hc+standard,['baseline','selected','hitter_selected','past_only']),'additional':hm.scores(he,['baseline','hitter_selected','past_only']),'manifest':manH,'scope':'H debut-season calendar flag now uses observed H stream rather than pitching debut mapping; no future first-pitching year leaks into H features.'});save('Past_Only_Hitter_Cases.json.gz',hc);save('Past_Only_Hitter_Additional.json.gz',he)
 if '--current' in sys.argv:
  for horizons,tag in [((1,),'one'),(tuple(range(1,9)),'eight')]:
   pm=pmod.augment(j.fit_pitch(2026,horizons));hh=hm.fit_hitter(2026,horizons);joblib.dump(pm,OUT/f'past-current-pitch-{tag}.joblib',compress=3);joblib.dump(hh,OUT/f'past-current-hitter-{tag}.joblib',compress=3)
  print('Past-only current models saved',flush=True)
if __name__=='__main__':run()
