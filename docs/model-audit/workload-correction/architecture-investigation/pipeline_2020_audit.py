"""Source-level pandemic ledger and role-cap sensitivity; no data normalization writes."""
import sys,json,hashlib,ast
from pathlib import Path
import numpy as np
ROOT=Path(sys.argv[1]).resolve();OUT=Path(__file__).resolve().parent
sys.dont_write_bytecode=True;sys.path.insert(0,str(ROOT/'trade-preview-v23c-evidence-guard'))
import model_asset_fit as m
v,r,old=m.v,m.r,m.old
entries=[
 ('trade-preview-v22/model/prototype.py','collect_cached_seasons','Actual MLB counts and exact game-level QA3; retain actual2020 exposure.','Source truth, not a schedule-adjusted capacity estimate.','active source'),
 ('trade-preview-v22/model/prototype.py','QUAL','Early2010–2012 priors, reference scale, category denominators and replacement floors.','No2020 inclusion.','active frozen calibration'),
 ('trade-preview-v22/model/career_forecast.py','estimate','Career talent weights and effective exposure use actual2020 PA/IP; calendar and healthy workload annualize162/60.','Talent uses actual opportunity denominators. Blanket diagnostic workload annualization does not distinguish individual availability.','diagnostic only for current default'),
 ('trade-preview-v22/model/career_forecast.py','cap','98th-percentile role cap annualizes2020; other seasons raw.','Role caps feed current default. Historical frozen caps include future seasons; past-only testing uses as-of caps.','active cap'),
 ('trade-preview-v23/model_v23.py','recent_forecast','Current recent/healthy workloads use2023–2026 only; role prior<=2012. Historical translated windows can include raw2020.','Current source has no direct2020 input; historical workload windows require schedule treatment.','active default'),
 ('trade-preview-v22/model/model_v22.py','annual','Derived aging exposure and counts all scale162/60 for2020.','Scales once; no rewrite of actual source. Rate ratio preserved within a season, but normalized season gets full exposure weight in pooled rates.','active derived helper'),
 ('trade-preview-v22/model/model_v22.py','cohorts','Anchors2011–2017 with previous seasons; targets through2025 across8 horizons.','Anchors/quality bins have no2020. First-year targets2012–2018 have no2020; later horizons can include normalized2020.','active cohort membership'),
 ('trade-preview-v23/model_v23.py','curve','Separate hitter/pitcher future indexes; calls base.annual once on each target.','No second medical multiplier. Cohort workload ratio includes nonparticipation, aging and role/availability changes without individual durability conditioning.','active workload/rate aging'),
 ('trade-preview-v23/model_v23.py','mlb_role_paths','Starting workload times direct horizon-specific curve; mean-one uncertainty states.','First-year factor is horizon1, not a compounded8-year factor. Later paths may inherit2020-normalized cohort outcomes.','active final projections'),
 ('trade-preview-v23/model_v23.py','mlb_paths','Two-way overlap uses projected starts and162-game denominator.','2020 not directly used for current overlap; separate streams retained.','active two-way'),
 ('trade-preview-v22/model/revised.py','aging','Observed consecutive-season rate/workload pairs use raw2019->2020 and2020->2021.','Not sufficient schedule handling, but this legacy MLB aging forecast is superseded by V2.3; do not patch it as though it controls current default.','legacy diagnostic'),
 ('trade-preview-v22/model/revised.py','career','Empirical prospect career/arrival contribution paths contain actual2020 fantasy production.','These are realized contribution paths, not physical-capacity measurements. Changing their targets would be a separate prospect-distribution experiment, not this workload correction.','active prospect evidence'),
 ('trade-preview-v23c-evidence-guard/model_asset_fit.py','paths','Identity-prior registry restores archived prospect evidence; additional mixture can preserve MLB mean.','Registry/ranks are not COVID workload normalization or additional medical penalties. Keep prior atoms unchanged.','active identity guard'),
 ('trade-preview-v22/model/model_v2.py','annual','Same2020-derived annualization in preserved previous model.','Superseded current MLB path; do not rewrite historic checkpoints.','archived/diagnostic'),
 ('trade-preview-v22/model/model_v21.py','annual','Same2020-derived annualization in preserved previous model.','Superseded current MLB path; preserve original validation comparisons.','archived/diagnostic'),
 ]
ledger=[]
for path,unit,treatment,assessment,status in entries:
 file=ROOT/path;s=file.read_text();tree=ast.parse(s);line=next((n.lineno for n in ast.walk(tree) if isinstance(n,(ast.FunctionDef,ast.ClassDef)) and n.name==unit),None)
 if line is None:line=next((i for i,t in enumerate(s.splitlines(),1) if unit in t),None)
 ledger.append({'file':path,'unit':unit,'line':line,'source_sha256':hashlib.sha256(file.read_bytes()).hexdigest(),'treatment':treatment,'assessment':assessment,'status':status})
caps={}
for rr in ['H','SP','RP']:
 vals=[z for z in old.AN if z['role']==rr and r.exposure(z['stat'],rr)>0]
 caps[rr]={method:float(np.quantile([r.exposure(z['stat'],rr)*(162/60 if z['year']==2020 and method=='annualized' else 1) for z in vals if method!='omit2020' or z['year']!=2020],.98)) for method in ['raw','annualized','omit2020']}
assert all(abs(caps[rr]['annualized']-v.cf.cap(rr))<1e-8 for rr in caps)
(OUT/'Pipeline_2020_Audit.json').write_text(json.dumps({'ledger':ledger,'role_cap_sensitivities':caps,'actual2020_records':{rr:sum(z['year']==2020 and z['role']==rr for z in old.AN) for rr in ['H','SP','RP']},'policy':'Preserve actual2020 counts. Normalize derived workload features/appropriate training targets only, with separate provenance and historical tests. No global rewrite.','current_first_year_aging_targets':'2012–2018: no2020. Current recent window2023–2026: no2020.','QA3':'Actual exact game events retained:5IP<=2ER OR6IP<=3ER. No conventionalQS substitution.'},indent=2));print('Pipeline2020 audit',caps,flush=True)
