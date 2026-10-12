"""Bounded actual-model evidence correction. Never writes production publication files."""
import sys,json,gzip,copy,math,csv,hashlib,base64,re
from pathlib import Path
import numpy as np
D=Path(__file__).resolve().parent; ROOT=D.parents[1]
MODEL=Path(sys.argv[1]).resolve(); RESEARCH=Path(sys.argv[2]).resolve()
sys.path.insert(0,str(MODEL/'trade-preview-v23c-evidence-guard'));import model_asset_fit as m
r=m.r
read=lambda p:json.loads(gzip.decompress(p.read_bytes()) if p.suffix=='.gz' else p.read_text())
def write(name,x):(D/name).write_text(json.dumps(x,indent=2,allow_nan=False)+'\n')
def csvwrite(name,x):
 with (D/name).open('w',newline='') as f:
  w=csv.DictWriter(f,list(dict.fromkeys(k for z in x for k in z)));w.writeheader();w.writerows(x)
AP={(z['mlbamId'],z['year']):z for z in read(MODEL/'trade-preview-v23c-evidence-guard/Recovery_Appearances.json')['rows']}
AN={(z['id'],z['year']):z for z in m.old.AN if z['role']!='H'}
# Fixed completed calibration years. Identity holdout excluded from event priors.
cal=[z for z in m.old.AN if z['role']!='H' and z['year']<=2012 and z['id']%5!=0 and AP.get((z['id'],z['year']),{}).get('GS')==0 and AP[(z['id'],z['year'])]['GP']>0]
games=sum(AP[z['id'],z['year']]['GP'] for z in cal)
PRIORS={k:sum(z['stat'].get(k,0) for z in cal)/games for k in ['SV','HLD']}
assert games>0 and sum(PRIORS.values())<=1

def opportunities(rows,ip,k):
 """rows are (verified decimal-IP stat, GP, recency weight); no start mixtures."""
 den=sum(gp*w for s,gp,w in rows);ips=sum(s['IP']*w for s,gp,w in rows)
 if den<=0:return None
 # Existing relief depth pseudocount: ten appearances at one inning each.
 depth=max(.25,min(3,(ips+10)/(den+10)));n=ip/depth
 rates={event:(sum(s.get(event,0)*w for s,gp,w in rows)+k*PRIORS[event])/(den+k) for event in ['SV','HLD']}
 assert sum(rates.values())<=1+1e-10
 return {'SV':n*rates['SV'],'HLD':n*rates['HLD'],'expected_appearances':n,'depth':depth,'evidence_appearances_weighted':den,'probabilities':rates}

def evidence(ident,year):
 rows=[]
 for lag,w in [(0,3),(1,2),(2,1)]:
  key=(ident,year-lag);z=AN.get(key);a=AP.get(key)
  if not z or not a or a['GP']<=0 or a['GS']!=0:continue
  s=z['stat']
  if not all(event in s for event in ['SV','HLD']) or s['SV']+s['HLD']>a['GP']:continue
  rows.append((s,a['GP'],w))
 return rows
cases=[]
for z in read(RESEARCH/'Debut_Chronological_Cases.json.gz'):
 if z['role']!='RP' or AP.get((z['mlbam_id'],z['anchor']),{}).get('GS')!=0:continue
 rows=evidence(z['mlbam_id'],z['anchor'])
 if not rows:continue
 row={'id':z['mlbam_id'],'name':z['name'],'anchor':z['anchor'],'stage':'development' if z['anchor']<=2018 else 'later','actual':z['actual'],'baseline':z['baseline']}
 for k in [5,10,20,40]:
  ev=opportunities(rows,z['baseline']['IP'],k);s=copy.deepcopy(z['baseline']);s.update({a:ev[a] for a in ['SV','HLD']});row[str(k)]=s
  assert all(s[a]==z['baseline'][a] for a in s if a not in ['SV','HLD'])
 cases.append(row)
def summary(rows):
 out={}
 for method in ['baseline','5','10','20','40']:
  out[method]={'n':len(rows)}
  for field in ['SV','HLD','SVH7','utility']:
   def value(s):return 3*s.get('SV',0)+2*s.get('HLD',0) if field=='SVH7' else r.utility(r.surplus(s,'RP')) if field=='utility' else s.get(field,0)
   errors=[value(z[method])-value(z['actual']) for z in rows]
   out[method][field]={'MAE':float(np.mean(np.abs(errors))),'bias':float(np.mean(errors))}
 return out
metrics={stage:summary([z for z in cases if z['stage']==stage]) for stage in ['development','later']}
chosen=min(['5','10','20','40'],key=lambda k:(metrics['development'][k]['SVH7']['MAE'],metrics['development'][k]['utility']['MAE']))
gate=all(metrics['later'][chosen][f]['MAE']<=metrics['later']['baseline'][f]['MAE'] for f in ['SVH7','utility'])
write('Reliever_Validation.json',{'priors':PRIORS,'selected_pseudocount':int(chosen),'metrics':metrics,'release_gate_pass':gate,'scope':'Previously inspected chronological identity-holdout cases; no new independent holdout'})
csvwrite('Reliever_Chronological_Comparisons.csv',[{'id':z['id'],'name':z['name'],'anchor':z['anchor'],'stage':z['stage'],**{method+'_'+field:z[method].get(field,0) for method in ['actual','baseline',chosen] for field in ['IP','SV','HLD']}} for z in cases])
# Replay exact current production catalog, with a reversible forecast overlay.
cat=json.loads(gzip.decompress(base64.b64decode(re.search("const packed='([^']+)'",(ROOT/'trade-analyzer-beta/index.html').read_text())[1])))
original=m.v.recent_forecast;current=[];unavailable=[];candidate=copy.deepcopy(cat);byid={a['id']:a for a in candidate['assets']}
for a in cat['assets']:
 if a['audit'].get('kind')!='MLB' or a['audit'].get('role')!='RP':continue
 p=m.old.players[a['id']];ident=p.get('mlbamId');hist=m.v.seasons(p,'RP');rows=[]
 for lag,w in [(0,3),(1,2),(2,1)]:
  z=next((z for z in hist if z['year']==2026-lag and z['role']=='RP' and z['stat'].get('IP',0)>0),None)
  if not z:continue
  ap=p.get('pit',{}) if lag==0 else AP.get((ident,2026-lag),{})
  if not ap or ap.get('GP',0)<=0 or ap.get('GS')!=0:continue
  s=z['stat'];gp=ap['GP']
  if not all(k in s for k in ['SV','HLD']) or s['SV']+s['HLD']>gp:continue
  rows.append((s,gp,w))
 if not rows:unavailable.append({'id':a['id'],'name':a['name'],'reason':'No matched pure-relief appearance evidence'});continue
 paths,audit=m.paths(p);baseline=m.competitive(paths,'neutral')['display'];assert abs(baseline-a['values']['neutral']['display'])<1e-8
 rate,work,fa=original(p,'RP');ev=opportunities(rows,work,int(chosen))
 # Keep the original aging cohort and states fixed. Changing leverage must not
 # silently change quality-quartile routing and therefore all other forecasts.
 au=copy.deepcopy(audit);ps=[]
 for (prob,path),states in zip(paths,audit['outcome_state_projections']):
  changed=[]
  for t,st in enumerate(states):
   st=st.copy()
   for event in ['SV','HLD']:
    if t==0 and rate[event]>0:st[event]*=(ev[event]/work)/rate[event]
    elif t==0:assert ev[event]==0, 'Unsupported zero-event future trajectory'
   changed.append(r.utility(r.surplus(st,'RP')))
  ps.append((prob,changed))
 s=copy.deepcopy(audit['projection']);b=audit['projection']
 for event in ['SV','HLD']:s[event]*=(ev[event]/work)/rate[event] if rate[event]>0 else 1
 assert all(s[k]==b[k] for k in b if k not in ['SV','HLD'])
 # This is an actual-model catalog candidate, preserving every future reward.
 assert all(newpath[1:]==oldpath[1:] for (pr,newpath),(oldpr,oldpath) in zip(ps,paths))
 asset=byid[a['id']];asset['audit'].update(copy.deepcopy(audit));asset['audit']['outcome_state_projections']=copy.deepcopy(audit['outcome_state_projections']);asset['audit']['annual_projection']=copy.deepcopy(audit['annual_projection']);asset['audit']['projection']=copy.deepcopy(s);asset['audit']['annual_projection'][0]=copy.deepcopy(s)
 for states in asset['audit']['outcome_state_projections']:
  for event in ['SV','HLD']:states[0][event]*=(ev[event]/work)/rate[event] if rate[event]>0 else 1
 assert all(abs(sum(pr*states[0][key] for (pr,path),states in zip(ps,asset['audit']['outcome_state_projections']))-s[key])<1e-8 for key in s)
 asset['audit']['relief_opportunity_repair']={'scope':'First forecast year only; future assignment model unchanged','pseudocount':int(chosen),'evidence':ev,'aging_cohort_frozen':True}
 asset['annual_expected_utility'][0]=sum(pr*path[0] for pr,path in ps)
 assert asset['annual_expected_utility'][1:]==a['annual_expected_utility'][1:]
 fit={mode:m.competitive(ps,mode) for mode in r.MODES}
 asset['values']={mode:copy.deepcopy(fit['neutral']) for mode in r.MODES};asset['competitive_values']=fit
 asset['valuation_quantities'].update(intrinsic_dynasty=fit['neutral']['display'],transferable_fundamental=fit['neutral']['display'],competitive_fit={mode:v['display'] for mode,v in fit.items()})
 for scenario,factor in [('low',.85),('high',1.15)]:
  original_paths,unused=m.paths(p,scenario);changed=copy.deepcopy(original_paths)
  for j,(pr,path) in enumerate(changed):
   st=asset['audit']['outcome_state_projections'][j][0];st={k:v*factor for k,v in st.items()};path[0]=r.utility(r.surplus(st,'RP'))
  asset['competitive_range'][scenario]={mode:m.competitive(changed,mode)['display'] for mode in r.MODES}
  asset['range'][scenario]={mode:asset['competitive_range'][scenario]['neutral'] for mode in r.MODES}
 asset['qualityWarnings'].append('Saves and holds use separate shrunk appearance probabilities in forecast year one; innings and years2-8 are unchanged. Future bullpen assignment remains uncertain.')
 value=m.competitive(ps,'neutral')['display'];current.append({'id':a['id'],'name':a['name'],'production':baseline,'candidate':value,'delta':value-baseline,'IP':b['IP'],'production_SV':b['SV'],'candidate_SV':s['SV'],'production_HLD':b['HLD'],'candidate_HLD':s['HLD'],'release_gate_pass':gate,'scope':'first-year opportunity correction; years2-8 unchanged'})
csvwrite('Reliever_Current_Comparison.csv',current);write('Reliever_Unsupported.json',unavailable)
# Recalculate cached trade packages against the same corrected asset identities.
for trade in candidate['trades']:
 neutral=[sum(byid[i]['values']['neutral']['display'] for i in ids) for ids in trade['identities']];trade['neutral_transfer_packages']=neutral
 for mode in r.MODES:
  packages=[sum(byid[i]['competitive_values'][mode]['display'] for i in ids) for ids in trade['identities']];bounds=[(sum(byid[i]['competitive_range']['low'][mode] for i in ids),sum(byid[i]['competitive_range']['high'][mode] for i in ids)) for ids in trade['identities']]
  trade['modes'][mode].update(package_values=packages,net_first_owner=packages[1]-packages[0],assumption_range=[bounds[1][0]-bounds[0][1],bounds[1][1]-bounds[0][0]],neutral_transfer_change=neutral[1]-neutral[0])
candidate['version']='V2.3D first-year relief opportunity correction candidate'
(D/'Candidate_Catalog.json.gz').write_bytes(gzip.compress(json.dumps(candidate,separators=(',',':')).encode(),mtime=0))
packed=base64.b64encode(gzip.compress(json.dumps(candidate,separators=(',',':')).encode(),mtime=0)).decode()
html=(ROOT/'trade-analyzer-beta/index.html').read_text();html=re.sub("const packed='[^']+'",lambda z:"const packed='"+packed+"'",html,count=1)
(D/'Actual_Model_Candidate.html').write_text(html)

# Use complete preserved scrutiny rather than the misleading broad >=250PA summary.
scr=read(MODEL/'trade-preview-v23b-stabilized/Debut_Scrutiny.json')
pitch=read(RESEARCH/'Debut_Chronological_Validation.json')
write('Existing_Candidate_Decisions.json',{'prospect':{'decision':scr['decision'],'later_sub250':scr['summary']['later']['0–250'],'limitations':scr['limitations']},'pitcher':{'first_MLB_season':pitch['scores']['first_MLB_season'],'young':pitch['scores']['young'],'decision':'Neither direct professional-IP substitution nor bounded opportunity version passes historical workload gate'}})
write('Verification.json',{'protocol_sha256':hashlib.sha256((D/'Protocol.json').read_bytes()).hexdigest(),'production_html_sha256':hashlib.sha256((ROOT/'trade-analyzer-beta/index.html').read_bytes()).hexdigest(),'reliever_current_exact_replays':len(current),'current_nonleverage_counts_unchanged':True,'production_written':False,'release_gate_pass':gate,'scope':'first-year opportunity correction; years2-8 unchanged'})
print(json.dumps({'chosen':chosen,'release_gate':gate,'metrics':metrics,'current_players':len(current),'largest_changes':sorted(current,key=lambda z:-abs(z['delta']))[:6]},indent=2))
