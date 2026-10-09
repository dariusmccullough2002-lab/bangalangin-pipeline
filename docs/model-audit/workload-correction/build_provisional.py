"""Prepare exact candidate catalog, with one reviewed evidence record; no production writes."""
import sys,json,copy,hashlib,gzip,base64,re
from pathlib import Path
sys.dont_write_bytecode=True
ROOT,CAT,HTML=map(lambda x:Path(x).resolve(),sys.argv[1:4]);OUT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/'trade-preview-v23c-evidence-guard'))
import model_asset_fit as m
from evidence_gate import guarded_forecast
v,r,old=m.v,m.r,m.old
manifest=json.loads((OUT/'Provisional_Workload_Manifest.json').read_text());baseline=json.loads(CAT.read_text());candidate=copy.deepcopy(baseline);original=v.recent_forecast;changed=[]
if '--disabled' in sys.argv:
 # Restore the exact frozen header-release HTML, not a regenerated approximation.
 (OUT/'Rollback_Preview.html').write_bytes(HTML.read_bytes())
 (OUT/'Provisional_Rollback_Check.json').write_text(json.dumps({'disabled_gate':True,'asset_count':len(baseline['assets']),'catalog_equal_to_frozen_baseline':True,'exact_original_HTML_sha256':hashlib.sha256(HTML.read_bytes()).hexdigest(),'rollback_HTML_sha256':hashlib.sha256((OUT/'Rollback_Preview.html').read_bytes()).hexdigest()},indent=2))
 print('PASS: exact original HTML restored with disabled policy');sys.exit(0)
def gate(p,role,scenario='base'):return guarded_forecast(original,manifest,p,role,scenario,enabled=manifest.get('enabled_for_candidate',False),context=(v,r,old))
v.recent_forecast=gate
try:
 for a in candidate['assets']:
  if a['id'] not in {e['fantrax_id'] for e in manifest['records']}:continue
  p=old.players[a['id']];ps,audit=m.paths(p);assert audit['projection_audit']['talent_rates']==next(x for x in baseline['assets'] if x['id']==a['id'])['audit']['projection_audit']['talent_rates']
  a['audit']=audit;fit={mode:m.competitive(ps,mode) for mode in r.MODES};neutral=fit['neutral'];a['values']={mode:copy.deepcopy(neutral) for mode in r.MODES};a['competitive_values']=fit;a['annual_expected_utility']=[sum(prob*path[t] for prob,path in ps) for t in range(8)]
  a['competitive_range']={s:{mode:m.competitive(m.paths(p,s)[0],mode)['display'] for mode in r.MODES} for s in ['low','high']};a['range']={s:{mode:a['competitive_range'][s]['neutral'] for mode in r.MODES} for s in ['low','high']}
  a['valuation_quantities']={'intrinsic_dynasty':neutral['display'],'transferable_fundamental':neutral['display'],'market_acquisition':None,'competitive_fit':{mode:z['display'] for mode,z in fit.items()}}
  # Recompute existing finite-state uncertainty; never retain stale pre-correction quantiles.
  atoms=sorted((m.competitive([(1,path)],'neutral')['display'],prob,path) for prob,path in ps)
  quantiles={}
  for q in [.1,.5,.9]:
   cumulative=0
   for value,prob,path in atoms:
    cumulative+=prob
    if cumulative>=q:quantiles[str(q)]=value;break
  a['distribution_summary']['neutral_outcome_quantiles']=quantiles
  threshold=a['distribution_summary']['elite_utility_threshold'];a['distribution_summary']['first_year_zero_contribution_probability']=sum(prob for prob,path in ps if path[0]<=0);a['distribution_summary']['first_year_above_elite_utility_probability']=sum(prob for prob,path in ps if path[0]>threshold)
  a['qualityWarnings'].append('PROVISIONAL BETA: verified same-season MLB + affiliated MiLB workload; MLB-only talent rates unchanged. Predictive superiority is unestablished.')
  changed.append(a['id'])
finally:v.recent_forecast=original
# Recompute saved scenarios only when a changed asset participates. Trade identities preserved.
by={a['id']:a for a in candidate['assets']};trades_changed=[]
for ix,t in enumerate(candidate['trades']):
 if not any(i in changed for ids in t['identities'] for i in ids):continue
 neutral=[sum(by[i]['values']['neutral']['display'] for i in ids) for ids in t['identities']];t['neutral_transfer_packages']=neutral
 for mode in r.MODES:
  packages=[sum(by[i]['competitive_values'][mode]['display'] for i in ids) for ids in t['identities']];bounds=[(sum(by[i]['competitive_range']['low'][mode] for i in ids),sum(by[i]['competitive_range']['high'][mode] for i in ids)) for ids in t['identities']]
  t['modes'][mode].update(package_values=packages,net_first_owner=packages[1]-packages[0],assumption_range=[bounds[1][0]-bounds[0][1],bounds[1][1]-bounds[0][0]],neutral_transfer_change=neutral[1]-neutral[0])
 trades_changed.append(ix)
assert len(candidate['assets'])==2546
for b,a in zip(baseline['assets'],candidate['assets']):
 assert b['id']==a['id']
 if a['id'] not in changed:assert b==a
 else:
  for key in ['owner','ownerAsOf','playerIdentity','career_profile','position','market']:assert b.get(key)==a.get(key)
assert candidate['teams']==baseline['teams']
# Disable gate restores exact output tuple, including original audit object, for every player.
for p in old.players.values():
 rr=v.role(p)
 if rr not in ['SP','RP']:continue
 f=original(p,rr);g=guarded_forecast(original,manifest,p,rr,enabled=False,context=(v,r,old));assert f==g
# Negative evidence checks.
p=old.players[changed[0]];rr=v.role(p)
for case in ['duplicate','wrong_MLB','no_later_confirmation','incomplete_coverage']:
 bad=copy.deepcopy(manifest);q=copy.deepcopy(p)
 if case=='duplicate':bad['records'][0]['components']*=2
 elif case=='wrong_MLB':bad['records'][0]['MLB_outs']+=1
 elif case=='no_later_confirmation':bad['records'][0]['season']=2026
 else:bad['records'][0]['complete_level_queries']=bad['records'][0]['complete_level_queries'][:-1]
 try:guarded_forecast(original,bad,q,rr,enabled=True,context=(v,r,old));raise AssertionError(case+' accepted')
 except ValueError:pass
(OUT/'Provisional_Catalog.json.gz').write_bytes(gzip.compress(json.dumps(candidate,separators=(',',':')).encode(),mtime=0))
s=HTML.read_text();packed=base64.b64encode(gzip.compress(json.dumps(candidate,separators=(',',':')).encode(),mtime=0)).decode();s,n=re.subn(r"const packed='[^']+'",lambda _:"const packed='"+packed+"'",s,count=1);assert n==1
s=s.replace('Forecast and market-pricing limits are documented below.','Selected verified promotion-season workloads are provisional. Forecast and market-pricing limits are documented below.',1)
(OUT/'provisional-preview.html').write_text(s)
report={'status':'READY FOR REVIEW ONLY; NOT DEPLOYED','changed_asset_ids':changed,'unchanged_asset_count':2546-len(changed),'saved_trade_scenarios_recomputed':trades_changed,'identities_ownership_teams_picks_unchanged':True,'MLB_talent_rates_identical':True,'disabled_gate_exact_parity':True,'invalid_evidence_rejected':True,'baseline_catalog_sha256':hashlib.sha256(CAT.read_bytes()).hexdigest(),'rollback':'Disable the offline evidence gate and rebuild from the frozen catalog; original production deployment remains available.'}
(OUT/'Provisional_Regression.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
