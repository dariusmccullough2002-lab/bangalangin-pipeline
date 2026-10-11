# One frozen starter state-severity correction

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
