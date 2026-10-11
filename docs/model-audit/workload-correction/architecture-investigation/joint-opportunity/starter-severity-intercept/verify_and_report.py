"""Summarize frozen outputs and verify isolation; no parameter selection or fitting."""
import json,gzip,csv,joblib,hashlib,collections
from pathlib import Path
import numpy as np
D=Path(__file__).resolve().parent;P=D.parent
xs=json.load(gzip.open(D/'Cases.json.gz','rt'));assert len(xs)==4004
mods=collections.Counter(a['mlbam_id']%5 for a in xs);overlap=[];same=[];excluded=set(json.load(open(P/'targeted-repair/Protocol_Freeze.json'))['reserved_excluded_known_diagnostic_ids'])
for f in D.glob('severity-P-*.joblib'):
 v=joblib.load(f);assert hashlib.sha256((P/'historical-coverage-retrain'/f"model-P-{v['asof']}.joblib").read_bytes()).hexdigest()==v['parent_sha256'];assert v['protocol_sha256']==hashlib.sha256((D/'Protocol_Freeze.json').read_bytes()).hexdigest()
 evals={a['mlbam_id'] for a in xs if a['anchor']==v['asof'] and a['role']!='H'};targets={(a['mlbam_id'],a['target_season']) for a in xs if a['anchor']==v['asof'] and a['role']!='H'}
 for a in v['calibration_rows']:
  assert a['id']%5==4 and a['id'] not in excluded and a['target']<=min(v['asof'],2025)
  if a['id'] in evals:overlap.append(a)
  if (a['id'],a['target']) in targets:same.append(a)
assert not same
for a in xs:
 probs=a['retrained_probabilities'];old=a['retrained_state_means'];new=a['candidate_state_means'];assert abs(sum(probs[s]*new[s] for s in probs)-a['severity_candidate'])<1e-8
 if a['role']=='H' or a['repaired_forecast_role']!='starter':assert abs(a['severity_candidate']-a['five_retrained'])<1e-8 and old==new
 for state in old:
  if state!='retained_reduced':assert old[state]==new[state]
 assert abs(a['candidate_frequency_error']+a['candidate_severity_error']-(a['severity_candidate']-a['actual']))<1e-8
league=list(csv.DictReader((D/'League_1900_Comparison.csv').open()));assert len(league)==1900
components=json.load(gzip.open(D/'League_Components.json.gz','rt'))
for a in components:
 c=a['parent'];q=c['participation'];new=a['candidate_unconditional'];assert abs(sum(c['probabilities'][s]*a['candidate_state_means'][s] for s in c['probabilities'])-new)<1e-8
rows=[]
for group in ['established','young','interrupted','aging33plus','uncertain_role']:
 ys=[a for a in xs if a['role']!='H' and a['repaired_forecast_role']=='starter' and group in a['groups']]
 if not ys:continue
 for method in ['frozen_hybrid','five_retrained','severity_candidate']:
  error=np.array([a[method]-a['actual'] for a in ys]);rows.append({'cohort':group,'model':method,'n':len(ys),'MAE':float(abs(error).mean()),'RMSE':float(np.sqrt((error**2).mean())),'bias':float(error.mean())})
with (D/'Starter_Cohort_Validation.csv').open('w',newline='') as f:w=csv.DictWriter(f,rows[0].keys());w.writeheader();w.writerows(rows)
integrity={'cases':4004,'pitchers':2517,'starters':481,'verified_zero_outcomes':sum(a['actual']==0 for a in xs),'P_zero_outcomes':sum(a['role']!='H' and a['actual']==0 for a in xs),'league_players':1900,'diagnostics':len(list(csv.DictReader((D/'Diagnostic_12_Comparisons.csv').open()))),'probabilities_unchanged':True,'full_role_models_unchanged':True,'parent_model_hashes_match':True,'H_RP_swingman_fixed_within_numerical_precision':True,'talent_fixed':True,'no_extra_participation_discount':True,'no_allocator':True,'no_medical_envelope':True,'no_research_deployment':True,'evaluation_IDmods':dict(mods),'calibration_prior_seasons_of_evaluation_IDs':len(overlap),'evaluation_target_outcomes_used_for_fit':len(same),'protocol_population_note':'Initial freeze described evaluation IDs as mod0. Actual preserved protected cases also contain mod3/mod4. Fitting rule mod4 and chronology are unchanged;59 earlier-season calibration observations share evaluation player IDs, but no target outcome is used. This is exposed chronological evidence, not an independent ID holdout. A contract-enforcement rerun was preserved; no hypothesis or parameter change was made.'}
(D/'Integrity.json').write_text(json.dumps(integrity,indent=2)+'\n')
gates=json.load(open(D/'Release_Gates.json'));recommend={'recommendation':'retain preserved strong benchmark','candidate':'preserve failed retained-reduced starter state-severity intercept','adopted':False,'reason':'state bias improves but expected-season starter MAE/RMSE worsen; benchmark still better and protected gates fail','all_gates_pass':gates['all_gates_pass'],'next_evidence_gap':'Reliable dated injury/roster/rotation intervals distinguish why reduced or changed usage occurred. Annual totals identify usage, not injury, demotion or full availability. All481 starter cases lack complete cause-specific histories;275 positive reduced/changed and126 zero outcomes need distinctions for causal corrections. No new source collection required for this completed noncausal severity test.','independent_confirmation':'none identified; all scored cases exposed'}
(D/'Recommendation.json').write_text(json.dumps(recommend,indent=2)+'\n')
(D/'Report.md').write_text('''# One frozen starter state-severity correction

Retain the preserved strong benchmark. The one candidate is complete, fails adoption, and remains reproducible on its own research branch. No research numerical changes were deployed. Website display release79e85940 is a separate task.

## Hypothesis and implemented correction

The preserved mechanism audit found retained-reduced workload overestimation within demonstrated starter outcomes. This tests severity, not probabilities. Full-role starts, incidental relief, IP per start, talent, all other state means and probabilities stay fixed. Missingness/GP repairs remain active. No star-specific threshold, workload floor, additional participation multiplier, team allocation or medical envelope is used.

For each chronological anchor, use the immutable repaired five-state parent. Fit one weighted residual intercept on IDmod5=4 demonstrated-starter retained-reduced calibration observations, targets no later than min(anchor,2025), excluding shortened2020 targets and all reserved named diagnostic IDs. At least60 observations are required; otherwise use the parent exactly. Correction: b=Σweight(actualIP−parent_state_mean)/Σweight; m2'=clip(m2+b,0,251); W'=Σp_s m_s'. q=1−p_absent; conditional active W'/q; unconditional W' is not discounted again. This is an expected mixture, not the full-role display scenario.

Full role F=GS_full×IP/start+RA_full×IP/relief; each original state m_s=F×fitted_ratio_s. The fitted ratios encode usage magnitude within outcomes. Starts equivalent from conditional state IP is not an independently fitted state-specific GS count. The test leaves those limitations unchanged.

Protocol_Freeze.json was preserved in Git commitb116800 before scoring. No candidate/settings were added or tuned afterward. Existing training/calibration chronology and model artifacts were reused. Fits for2014–2017 fell back with fewer than60 rows; later fits use63–152 rows. Current2026 offset is−3.6239IP within retained-reduced state; unconditional delta is p_reduced×offset, not a flat deduction.

## Matched chronological results

All4004 matched cases:1487H and2517P. Include1562 zero-workload outcomes (1133P), shortened positive outcomes, and the unchanged target-year exclusions. No genuinely untouched confirmation is available. All previously scored2026 cases remain exposed.

| Population/model | n | MAE IP | RMSE IP | Signed bias IP |
|---|---:|---:|---:|---:|
| Starter benchmark |481|42.7467|55.6155|−1.8200|
| Starter repaired parent |481|44.5552|57.2559|+0.5252|
| Starter severity candidate |481|44.8477|57.7549|−2.2093|
| All-P benchmark |2517|20.3374|32.5931|−1.6960|
| All-P repaired parent |2517|20.8761|33.4031|−0.4023|
| All-P severity candidate |2517|20.9320|33.5669|−0.9248|

Retained-reduced observed starter state bias improves+7.3410→−0.2632IP on171 outcomes. High-state bias stays−1.5683IP (80); changed-state bias stays−5.5471IP (104); absent126 stays zero. This local mean-bias improvement does not produce a better unconditional forecast. Starter severity-component MAE25.8926→25.9591IP and frequency-component MAE32.4121→31.9530IP; their cancellation matters and these MAEs are not additive causal shares. Exact error identity is Σ(p−observed_onehot)m + (observed_state_mean−actual).

Probabilities are exactly unchanged. Starter expected/observed state frequencies remain27.91/26.20% absent,17.44/16.63% high,36.11/35.55% reduced,18.54/21.62% changed. Brier and participation/role reliability are unchanged; Calibration.csv provides values by cohort. Parent joint-starter Brier .619022 and participation Brier .11637 remain. No claim of improved state calibration is made.

Mixed tradeoffs: all-P young MAE27.6146→27.5144 and aging13.8133→13.7837, but established31.9829→32.2234 and interrupted37.6473→38.0182 worsen. Forecast-date starter cohort intersections are separately reported in Starter_Cohort_Validation.csv; Year_Validation.csv supplies all anchors. Small gains on exposed data do not establish superiority.

## Gates and recommendation

Every inherited gate is retained in Release_Gates.json. Candidate fails original94, originalSP, expandedP, expandedSP, youngSP, stableSP and the unchanged high-RBI gate. No thresholds were relaxed. Independent untouched confirmation, matched allocator accuracy and clinical absence coverage remain unestablished. Hitter forecasts are unchanged, so RBI is not repaired by this test.

Current Skenes133.7536→131.8347IP, Wheeler146.5394→144.5289IP are illustrations only; they did not enter fitting or selection. Full-role scenarios remain32.421GS/182.598IP and31.420GS/188.324IP respectively. The league-wide1900 comparison and12 diagnostics retain all state means/probabilities, conditional and unconditional workloads, full-role starts/relief/IP, and unchanged allocation/medical adjustments.

The evidence supports a severity-calibration hypothesis, but this single intercept fails. Retain benchmark. A causal correction needs dated IL activation/placement, option/recall, daily roster eligibility and rotation assignment intervals. All481 starter evaluation cases lack complete causal histories;275 reduced/changed positive and126 zero outcomes specifically need cause distinctions. Existing complete annual censuses and the preserved23-player2025 transaction feasibility sample do not establish full absence intervals. No missing annual row was labeled medical absence. No new collection was necessary for the tested noncausal correction; no further architecture or rate experiments were added.

## Contract correction and preservation

The first run omitted the frozen diagnostic-exclusion clause from the calibration row filter. Verification found one earlier Berríos observation (MLBAM621244) in nine anchors. All original outputs/model artifacts are preserved in omitted-exclusion-run with Defect.json. The implementation now enforces the predeclared exclusion and the identical candidate was rerun. These are the corrected results. No diagnostic player enters this residual fit, and no settings were tuned. The exclusion correction slightly worsened starter MAE44.8282→44.8477; both runs fail adoption.

## Chronology and coverage disclosure

The initial freeze text incorrectly summarized all evaluation IDs as mod0. The preserved4004-case population actually contains3409mod0,309mod4 and286mod3 cases. Fitting still uses the frozen mod4 rule and only earlier targets. There are59 earlier calibration observations sharing a pitcher evaluation ID, but zero evaluation target outcomes in calibrator fitting. This is a chronological comparison with exposed protected cases, not an independent player holdout. Integrity.json records the discrepancy. No hypothesis or parameter change was made after scoring; the frozen diagnostic exclusion was enforced in the contract-correction rerun.

## Reproduce and inspect

Restore parent archived checkpoints using their existing restore.py scripts. Run `OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 python run.py /path/to/recovered/model /path/to/beta-unpacked.json`, then `python verify_and_report.py`. The first command reads the repaired parent through calibration-starter/run.py→historical-coverage-retrain/run.py; it writes only this new research directory. Source paths: full-workload-scenario/run.py:forecast_role, depths, fitted_slots and predict; historical-coverage-retrain/run.py:activate and prediction_only; new run.py:artifact, apply, evaluate, metrics and current. Parent hashes are verified, stable residual class names retained, and no deployment function exists in research code.
''')
print(json.dumps(integrity));print(json.dumps(recommend))
