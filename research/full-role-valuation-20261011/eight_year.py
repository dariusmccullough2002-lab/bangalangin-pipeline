"""Reproducible current-catalog eight-year sensitivities; never writes publication files."""
import json,gzip,csv,base64,re,sys,copy,math,hashlib,subprocess
from pathlib import Path
from collections import Counter
import numpy as np
D=Path(__file__).resolve().parent;ROOT=D.parents[1];MODEL=Path(sys.argv[1]).resolve()
sys.path.insert(0,str(MODEL/'trade-preview-v23c-evidence-guard'));import model_asset_fit as m
r=m.r
def read(p):return json.loads(gzip.decompress(p.read_bytes()) if p.suffix=='.gz' else p.read_text())
def write(n,a):
 b=json.dumps(a,indent=2,allow_nan=False).encode();(D/n).write_bytes(gzip.compress(b,mtime=0) if n.endswith('.gz') else b)
def csvwrite(n,rows):
 with (D/n).open('w',newline='') as f:
  w=csv.DictWriter(f,list(dict.fromkeys(k for a in rows for k in a)));w.writeheader();w.writerows(rows)
catalog=json.loads(gzip.decompress(base64.b64decode(re.search("const packed='([^']+)'",(ROOT/'trade-analyzer-beta/index.html').read_text())[1])))
full={a['id']:a for a in read(D/'Current_Lines.json.gz')};details=[];rows=[];replay_errors=[];caps=0;checks=Counter()
for a in catalog['assets']:
 base=a['values']['neutral']['display'];row={'id':a['id'],'name':a['name'],'role':a['audit'].get('role'),'kind':a['audit']['kind'],'production':base,'year1_only':base,'full_role_anchored':base,'status':'unchanged unsupported','cohort':full.get(a['id'],{}).get('cohort','unchanged')}
 rows.append(row)
 f=full.get(a['id'])
 if not f or a['audit']['kind']!='MLB' or any(f['lines']['full_role'].get(k) is None for k in m.old.fields[a['audit']['role']]):continue
 p=m.old.players.get(a['id'])
 if p is None:row['status']='missing original player';continue
 ps,e=m.paths(p);rr=e['role'];mean=e['annual_projection'];states=e['outcome_state_projections'];b=mean[0];anchor=f['lines']['full_role'];key='PA' if rr=='H' else 'IP'
 replay=m.competitive(ps,'neutral')['display'];delta=abs(replay-base)
 if delta>1e-8 or any(abs(b.get(k,0)-a['audit']['projection'].get(k,0))>1e-8 for k in set(b)|set(a['audit']['projection'])):
  row['status']='baseline replay mismatch';replay_errors.append({'name':a['name'],'delta':delta});continue
 checks['exact_baseline_replays']+=1
 factors=[s[0][key]/b[key] for s in states]
 assert len(ps)==len(states)==3 and abs(sum(pr for pr,path in ps)-1)<1e-10
 for state,factor in zip(states,factors):
  for k,val in b.items():assert abs(state[0][k]-val*factor)<1e-8
 # Maintain the same mean-one production uncertainty and evaluate utility once.
 def stat(s,factor):
  z={k:float(v*factor) for k,v in s.items()}
  if rr=='H':z=m.v.reconcile(z)
  else:z['QA3']=min(z['QA3'],z['IP']/5)
  return z
 first=copy.deepcopy(ps)
 for j,(pr,path) in enumerate(first):path[0]=r.utility(r.surplus(stat(anchor,factors[j]),rr))
 assert all(pr==op and path[1:]==oldpath[1:] for (pr,path),(op,oldpath) in zip(first,ps))
 checks['future_rewards_frozen_year1_only']+=1;row['status']='year1 supported';row['year1_only']=m.competitive(first,'neutral')['display']
 row['production_year1_expected_utility']=sum(pr*path[0] for pr,path in ps);row['conditional_year1_expected_utility']=sum(pr*path[0] for pr,path in first)
 supported=all(b.get(k,0)>0 or (anchor.get(k,0)==0 and all(s.get(k,0)==0 for s in mean)) for k in m.old.fields[rr])
 case={'id':a['id'],'name':a['name'],'role':rr,'probabilities':[pr for pr,path in ps],'uncertainty_factors':factors,'production_mean_lines':mean,'production_utility_paths':ps,'year1_only_utility_paths':first,'extended_supported':supported}
 if supported:
  means=[]
  for s in mean:
   z={k:anchor[k]*s.get(k,0)/b[k] if b.get(k,0)>0 else 0. for k in m.old.fields[rr]}
   cap=754 if rr=='H' else 251
   if z[key]>cap:
    fac=cap/z[key];z={k:v*fac for k,v in z.items()};caps+=1
   if rr!='H':z['QA3']=min(z['QA3'],z['IP']/5)
   if rr=='H':z=m.v.reconcile(z)
   means.append(z)
  extended=[(pr,[r.utility(r.surplus(stat(s,factors[j]),rr)) for s in means]) for j,(pr,path) in enumerate(ps)]
  assert [pr for pr,path in extended]==[pr for pr,path in ps]
  row['full_role_anchored']=m.competitive(extended,'neutral')['display'];row['status']='both sensitivities supported';checks['extended_supported']+=1
  case.update(full_role_anchored_mean_lines=means,full_role_anchored_utility_paths=extended)
 else:row['extended_reason']='Zero baseline event lacks a supported relative future trajectory; original extended route retained'
 for mode in ['contender','balanced','rebuild']:
  row['production_fit_'+mode]=m.competitive(ps,mode)['display'];row['year1_only_fit_'+mode]=m.competitive(first,mode)['display'];row['full_role_anchored_fit_'+mode]=m.competitive(extended if supported else ps,mode)['display']
 details.append(case)
for method in ['production','year1_only','full_role_anchored']:
 for rank,a in enumerate(sorted([a for a in rows if a[method] is not None],key=lambda a:(-a[method],a['id'])),1):a[method+'_rank']=rank
for a in rows:
 if a['production'] is None:continue
 for method in ['year1_only','full_role_anchored']:
  a[method+'_delta']=a[method]-a['production'];a[method+'_pct']=100*a[method+'_delta']/a['production'] if a['production'] else None;a[method+'_rank_gain']=a['production_rank']-a[method+'_rank']
csvwrite('Eight_Year_Comparison.csv',rows);write('Eight_Year_Paths.json.gz',details)
names={'Aaron Judge','Matt Olson','Shea Langeliers','Gavin Lux','Paul Skenes','Zack Wheeler','Raisel Iglesias','Matt Brash'}
csvwrite('Eight_Year_Examples.csv',[a for a in rows if a['name'] in names]);csvwrite('Eight_Year_Largest_Changes.csv',sorted([a for a in rows if a.get('full_role_anchored_delta') is not None],key=lambda a:-abs(a['full_role_anchored_delta']))[:50])
summary=[]
for group in ['all_supported','everyday','platoon','bench','catcher','starter','reliever']:
 xs=[a for a in rows if a['status']=='both sensitivities supported' and (group=='all_supported' or a['cohort']==group)]
 for method in ['year1_only','full_role_anchored']:
  ds=[a[method+'_delta'] for a in xs];pct=[a[method+'_pct'] for a in xs if a[method+'_pct'] is not None]
  summary.append({'group':group,'method':method,'n':len(xs),'mean_delta':float(np.mean(ds)) if ds else None,'median_delta':float(np.median(ds)) if ds else None,'median_pct':float(np.median(pct)) if pct else None,'increased':sum(d>1e-8 for d in ds),'decreased':sum(d< -1e-8 for d in ds)})
csvwrite('Eight_Year_Role_Summary.csv',summary)
byname={a['name']:a for a in rows};trades=[]
for left,right in [('Aaron Judge','Zack Wheeler'),('Matt Olson','Raisel Iglesias'),('Shea Langeliers','Matt Brash'),('Gavin Lux','Paul Skenes')]:
 for method in ['production','year1_only','full_role_anchored']:trades.append({'side_A_sends':left,'side_B_sends':right,'method':method,'A_sends':byname[left][method],'B_sends':byname[right][method],'A_receives_minus_sends':byname[right][method]-byname[left][method]})
csvwrite('Eight_Year_Package_Examples.csv',trades)
assert not replay_errors
changes=subprocess.check_output(['git','diff','--name-only','ce326ae24cd0e6d016b1ff0fefb23ffd54903ba9','--',':(exclude)research/full-role-valuation-20261011'],cwd=ROOT,text=True).splitlines();assert not changes
write('Eight_Year_Verification.json',{'pre_score_protocol_local_commit':'6491193','checks':dict(checks),'mean_path_cap_events':caps,'catalog_assets':len(rows),'statuses':dict(Counter(a['status'] for a in rows)),'baseline_replay_errors':replay_errors,'publication_files_changed':changes,'independent_historical_eight_year_accuracy':'not evaluated; inherited current path assumptions only','source_hashes':{str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in [D/'Eight_Year_Protocol.json',ROOT/'trade-analyzer-beta/index.html',D/'Current_Lines.json.gz',MODEL/'trade-preview-v23c-evidence-guard/model_asset_fit.py']},'production_adoption':False})
print(json.dumps(read(D/'Eight_Year_Verification.json')))
