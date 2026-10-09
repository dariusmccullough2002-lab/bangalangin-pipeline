from run_helpers import *

def nf(z):
 d=decomposition(z);f=past.past_xrow(z,1,z['role']=='H')
 if z['role']=='H':return np.array([z['x'][13]/8,d['healthy_opportunity']/45,d['latest_opportunity']/60,d['depth'],z['x'][11]/3])
 return np.array([z['x'][13]/8,d['healthy_opportunity']/9,d['latest_opportunity']/12,d['depth']/2,f[32]*3,f[31]/max(.15,f[33])/3,z['x'][17]*2])
def nfit(year,fam):
 rows=[a for a in training(year,calendar=fam=='H',family=fam) if not a['calibration'] and (fam=='H' or a['z']['role']=='SP') and a['z']['positive_anchor']]
 X=np.stack([nf(a['z']) for a in rows]);Y=np.array([a['value']/decomposition(a['z'])['depth'] if fam=='H' else (a['info'] or {}).get('GS',0) for a in rows]);return {'X':X,'Y':Y,'manifest':{'asof':year,'max_target':max(a['year'] for a in rows),'mods':[1,2,3],'n':len(rows),'family':fam}}
def npred(model,zs,k):
 out=[]
 for z in zs:
  dist=np.sum((model['X']-nf(z))**2,axis=1);idx=np.argsort(dist)[:k];w=1/(.5+dist[idx]);n=np.average(model['Y'][idx],weights=w);d=decomposition(z);out.append(float(n*d['depth']))
 return out

def run():
 selection={};dev={};models={};spec=['neighbors_50','neighbors_150','neighbors_quarter','neighbors_half'];P=HERE.parent/'first-year-repair'
 for fam in ['P','H']:
  cases=read(HERE/f'Development_{fam}_Cases.json.gz');by={(a['id'],a['anchor']):a for a in cases};strong=read(P/'Development_Cases.json.gz')[fam];strongidx={(a['mlbam_id'],a['anchor']):a for a in strong};strongsel=read(P/'Selection_Freeze.json')['selected'][fam]
  for year in [2016,2017,2018,2021,2022]:
   zs=[z for z in records['SP' if fam=='P' else 'H'] if (z['id'],z['year']) in by and z['year']==year];mod=nfit(year,fam);checkpoint(mod,HERE/f'neighbor-dev-{fam}-{year}.joblib');p50=npred(mod,zs,50);p150=npred(mod,zs,150)
   for i,z in enumerate(zs):
    a=by[z['id'],year];a['strong_prior']=strongidx[z['id'],year][strongsel] if strongsel!='incumbent' else a['incumbent'];a['neighbors_50']=p50[i];a['neighbors_150']=p150[i];a['neighbors_quarter']=.75*a['strong_prior']+.25*p50[i];a['neighbors_half']=.5*(a['strong_prior']+p50[i])
  methods=['strong_prior']+spec;score=summaries(cases,methods);g='stable_rotation' if fam=='P' else 'everyday';eligible={s:score['all'][s]['MAE']<=score['all']['strong_prior']['MAE']*1.03 and score[g][s]['MAE']<=score[g]['strong_prior']['MAE']*1.05 for s in methods};obj={s:score['all'][s]['MAE']+.15*abs(score['all'][s]['bias'])+score[g][s]['MAE'] for s in methods};selection[fam]=min([s for s in methods if eligible[s]],key=obj.get);dev[fam]={'scores':score,'eligible':eligible,'objectives':obj,'selected':selection[fam]};print('NEIGHBOR DEV',fam,selection[fam],obj,flush=True)
 saveout('Neighbor_Selection_Freeze.json',{'selected':selection,'development':dev,'ID0_used_for_selection':False,'source_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest()})
 result={};allrows=[]
 for fam in ['P','H']:
  rows=read(HERE/f'Test_{fam}_Cases.json.gz');by={(a['mlbam_id'],a['anchor']):a for a in rows};strong=read(P/f'{fam}_Cases.json.gz');idx={(a['mlbam_id'],a['anchor']):a for a in strong};key='PA' if fam=='H' else 'IP'
  for year in sorted({a['anchor'] for a in rows}):
   zs=[z for z in records['SP' if fam=='P' else 'H'] if z['year']==year and (z['id'],year) in by];mod=nfit(year,fam);checkpoint(mod,HERE/f'neighbor-test-{fam}-{year}.joblib');p50=npred(mod,zs,50);p150=npred(mod,zs,150)
   for i,z in enumerate(zs):
    a=by[z['id'],year];a['strong_prior']=idx[z['id'],year]['revised'][key];a['neighbors_50']=p50[i];a['neighbors_150']=p150[i];a['neighbors_quarter']=.75*a['strong_prior']+.25*p50[i];a['neighbors_half']=.5*(a['strong_prior']+p50[i]);a['neighbor_selected']=a[selection[fam]]
  result[fam]=summaries(rows,['baseline','incumbent','selected','strong_prior']+spec+['neighbor_selected']);saveout(f'Neighbor_{fam}_Cases.json.gz',rows);allrows.extend([{k:v for k,v in a.items() if k!='groups'} for a in rows]);mod=nfit(2026,fam);checkpoint(mod,HERE/f'neighbor-current-{fam}.joblib')
 saveout('Neighbor_Validation.json',result);csvout('Final_Chronological_Comparisons.csv',allrows)
 # Current named and complete population comparisons, without arbitrary floors.
 league=read(OUT/'Past_Only_League_Impact.json.gz');priorcurrent={a['id']:a for a in read(P/'Current_League.json.gz')};current=[]
 for a in league:
  if a['status']!='supported_MLB':continue
  rr=a['role'];p=old.players[a['id']];rows=v.seasons(p,rr);z={'id':a['mlbam_id'],'year':2026,'role':rr,'history_override':rows,'x':base['features'](rows,rr,2026,a['mlbam_id']),'bounded_x':base['features'](rows,rr,2026,a['mlbam_id'],True)};fam='H' if rr=='H' else 'P';key='PA' if fam=='H' else 'IP';b=a['baseline_annual'][0];q=priorcurrent[a['id']];strong=q['revised'][key];d=decomposition(z)
  mod=joblib.load(HERE/f'neighbor-current-{fam}.joblib');n50=npred(mod,[z],50)[0] if rr!='RP' else strong;n150=npred(mod,[z],150)[0] if rr!='RP' else strong;pred={'strong_prior':strong,'neighbors_50':n50,'neighbors_150':n150,'neighbors_quarter':.75*strong+.25*n50,'neighbors_half':.5*(strong+n50)};val=pred[selection[fam]] if rr!='RP' else strong
  current.append({'id':a['id'],'mlbam_id':z['id'],'name':a['name'],'role':rr,'chosen':selection[fam] if rr!='RP' else 'preserved_RP','baseline':b[key],**pred,'final_workload':val,'healthy_role_appearances':d['healthy_opportunity'],'work_per_appearance':d['depth'],'evidence_state':'usage inferred; complete roster depth and medical timetable missing'})
 csvout('Final_Current_Comparisons.csv',current);saveout('Final_Current.json.gz',current);print('NEIGHBOR COMPLETE',selection,flush=True)
if __name__=='__main__':run()
