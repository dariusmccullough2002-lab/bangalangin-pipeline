from pathlib import Path
import hashlib,json,gzip,joblib,gc
HERE=Path(__file__).resolve().parent
results=[]
for p in sorted(HERE.rglob('*.joblib')):
 assert p.stat().st_size>0
 model=joblib.load(p);manifest=model.get('manifest',{}) if isinstance(model,dict) else {};assert not manifest or manifest.get('target_end',manifest.get('max_target',manifest.get('latest_target',0)))<=manifest.get('asof',model.get('asof',9999))
 results.append({'path':str(p.relative_to(HERE)),'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'readable':True,'manifest':manifest});del model;gc.collect()
(HERE/'Fitted_Artifact_Verification.json').write_text(json.dumps({'models':results,'count':len(results),'all_readable':True}))
# Exact QA3 contract; copied definition from preserved league implementation,
# never a substitution of conventional QS (six innings/three earned runs).
def qa3(outs,er):return outs>=15 and er<=2 or outs>=18 and er<=3
fixtures=[(15,2,True),(15,3,False),(18,3,True),(14,0,False),(21,4,False)]
assert all(qa3(o,e)==expected for o,e,expected in fixtures)
coverage=json.loads(gzip.decompress(Path('recovered/model/trade-preview-v22/model/inputs/game-inputs.json.gz').read_bytes()))['coverage']
assert sum(a['additional_QA3'] for a in coverage)>0 and sum(a['QA3_nonstarters'] for a in coverage)>0
(HERE/'QA3_Verification.json').write_text(json.dumps({'definition':'5+ IP and <=2 ER OR6+ IP and <=3 ER; starter status not required','fixtures':fixtures,'preserved_cache_years':len(coverage),'additional_over_conventional_QS':sum(a['additional_QA3'] for a in coverage),'nonstarter_qualifying_appearances':sum(a['QA3_nonstarters'] for a in coverage),'forecast_inputs':'preserved exact QA3 annual/game aggregates; rate/appearance mixture retained'}))
print('Verified',len(results),'fitted artifacts and QA3 contract')
