# Supported-class hitter calibration and starter probability correction

## Recommendation

Retain the preserved strong benchmark. Both frozen candidates are fully implemented and tested, but neither earns adoption. Hitter supported-class calibration improves probability calibration and workload RMSE while worsening workload MAE. Starter-only calibration changes probabilities without fixing conditional severity; its workload gains are negligible/mixed and it fails protected gates. The completed GP repair, original/repaired models and failed experiments are preserved. No additional candidates or parameters were tried after scoring.

The comparison comprises the same 4,004 chronological cases (1,487 H, 2,517 P) and 1,900 current players. Every scored evaluation sample remains exposed. No untouched confirmation sample was identified. These are exploratory results, not independent release evidence. Talent rates, production, years 2–8, prospect translations, dynasty valuation and Trade Analyzer are unchanged; no deployment occurred.

## Starter mechanism: what the code actually fits

Forecast roles use the latest positive verified MLB usage in the previous three seasons: GS/GP ≥ .8 starter, ≤ .1 reliever, otherwise swingman. No future innings threshold defines prediction roles. Annual target GS/GP defines retrospective usage labels only.

The 9,513 preserved P training observations comprise 2,142 demonstrated starters, 6,232 relievers and 1,139 swingmen. The classifier pools P with role indicators, but full-role proxy fits and conditional workload regressions route by forecast-date role. Thus reliever numerical predominance is established; reliever-caused starter compression is not. No severity model is simply averaging all RP and SP workloads together.

Exact implemented opportunity equations:

- As-of starter depth: `(Σ w·IP + 27.5)/(Σ w·GS + 5)`, weights 3/2/1 for the latest three qualifying seasons with GS/GP≥.8; clipped to 2.5–7 IP/start. Relief depth uses pure-relief observations and `(Σ w·IP+10)/(Σ w·GP+10)`, clipped .25–3.
- Fitted scenario: `F = full_GS·starter_depth + full_RA·relief_depth`. Full slots use squared-error regressors on the retained high-usage proxy (starter target GS≥30), with preserved structural fallbacks; GS≤36, RA≤85. This is a high-usage scenario, not medically verified full availability.
- Conditional state workload: `m_s = F·ratio_s(X)`, with a role/state Ridge ratio fit (alpha250, sample weight proportional to F²) when ≥60 core cases, otherwise the preserved empirical ratio fallback. Absolute workloads remain bounded at251IP; absent m=0. State-specific GS counts are not fitted here, so IP/depth is an appearance equivalent, not an independent start-count forecast.
- State probabilities: the preserved classifier predicts mutually exclusive absence, retained high usage, retained reduced usage, changed usage and evidence-residual states. `q=1−p_absent`; `W=Σ p_s·m_s`; `E[IP|MLB participation]=W/q`.

No additional participation, roster or medical discount follows W. Age/workload history enter classifier and conditional regressions as features; there is no extra multiplicative age attrition. Conditional severity is trained within its outcome state, so observed reduced-state missed time is not multiplied by another reduced-time factor. This is not the former median/mean blend.

Across 481 demonstrated-starter evaluation cases, predicted versus observed frequencies are: absence27.91%/26.20%, high retained17.44%/16.63%, reduced retained36.11%/35.55%, changed18.54%/21.62%. Within-state biases are −1.568IP high, +7.341 reduced and −5.547 changed. Frequency-component MAE32.412IP exceeds severity-component MAE25.893, but these cancelling algebraic components are not additive causal error shares.

Established starter reduced-state bias is +14.136IP; young +4.876; interrupted +3.124. Interrupted starter frequencies overpredict absence43.60% versus40.19% and reduced usage36.08% versus28.97%, while underpredicting changed usage13.18% versus19.63%. Aging starters instead underpredict absence47.09% versus54.12%. There is no evidence for a universal upward workload correction or player-specific floor. Preserved_Pitcher_State_Audit.csv contains all cohorts and states.

### Actual features and limitations

The five-state model uses the preserved repaired evidence feature vector and role indicators: workload history, age/tenure, GP/GS and shares, demonstrated depth/capacity, missingness and preserved historical performance-rate features (K/ER/BB/H/QA3/SV/HLD at indices31:38). The direct model uses workload/age/tenure indices0:15, GS/GP-share indices17/18, role indicators and exposure missingness. No velocity, pitch-tracking, team roster, batting-order or dated medical input enters these opportunity estimators. Talent-rate engines elsewhere are not a source of new injury intelligence here.

Annual GP/GS/IP can identify these usage proxies, not the cause of an interrupted season. All481 starter cases lack complete clinical availability/roster-transition labels; 275 positive reduced/changed outcomes and126 zero outcomes specifically lack causal injury/demotion/exit distinctions. The preserved source attempts comprise complete annual censuses and the prior23-player2025 transaction feasibility sample; no complete absence intervals were established. Precise additional evidence would be dated IL placement/activation, option/recall, daily roster eligibility and rotation assignment intervals matched to each anchor/target. Those gaps do not prevent this probability/calibration test, but prevent a causal injury-specific correction. No medical label was fabricated or backfilled from current news.

## Why Wheeler and Skenes disagree across models

These are illustrations, not fitting targets. Their frozen2026 records show Skenes32GS/32GP and174⅓IP; Wheeler28GS/28GP and162IP. Both have observed-positive statuses. Diagnostic_History.csv preserves all four input seasons, cutoffs and source references.

Skenes's five-state full-role fit is32.421GS and182.598IP. It falls to139.095IP conditional on participation, then133.754 unconditional. Only5.341IP of that last step comes from nonparticipation. The larger reduction is the outcome mixture:40.83% high-retained at190.083IP,52.95% reduced-retained at101.174IP,2.38% changed at108.082IP and3.84% absent. Thus the current five-state mechanism is not a healthy32-start estimate silently changed to23.7 starts. It retains32.421 scenario starts, then prices lower-usage outcomes.

Wheeler's corresponding scenario is31.420GS/188.324IP; participation96.78%, active conditional151.408 and unconditional146.539. His direct forecast is71.182IP versus Skenes131.700. The direct model estimates unconditional mean IP directly, with no identifiable internal participation/state decomposition. Exact boosting leaf traces reproduce predictions: common intercept34.423 plus97.277 tree increments for Skenes, versus36.759 for Wheeler. Age appears on52/55 of their100 tree routes; workload and role splits also participate. These path counts are not causal feature importance and do not establish medical absence. Their different feature regions and conditional response fits explain mechanical divergence, not which individual future outcome is correct. Historical starter MAE favors the benchmark over both methods.

Starter calibration leaves every state mean and scenario slot unchanged. It moves Skenes133.754→141.851IP and Wheeler146.539→151.393, but these selected increases do not justify adoption.

## Frozen supported-class corrections

Protocol_Freeze.json was committed before candidate scoring in local commit6dc6b22. Only two tests were authorized and fitted:

1. H: multinomial logistic calibration over the classifier-supported classes0/1/2/3. C=1 and max_iter=1000 remain the inherited settings; inputs are log-clipped raw supported-class probabilities. Numerical clipping prevents log(0); it does not create residual examples or residual probability mass.
2. P: the same calibration fitted only on demonstrated-starter calibration rows, applied only to demonstrated-starter forecasts. Relievers and swingmen are exactly unchanged. This narrowly tests the confirmed calibration-support omission and starter cohort probability errors.

Underlying classifiers, feature matrices, full-role regressors, conditional severity models and talent rates are fixed. Calibration uses IDmod4 only, with targets≤min(anchor,2025), excluding shortened2020 targets and retaining inherited pitcher2020-anchor exclusions. Evaluation IDs/outcomes are not used for fitting. At least100 calibration rows and10 examples in every supported class are required; unsupported observed targets reject calibration rather than inventing support. H calibrators fit at all12 anchors; P fits at11, with2014's60-row sample falling back unchanged.

The stable export has indices0..4. `unknown_role` and `retention_unidentifiable` are names for index4, not separate classes to pool. Index4 gets zero when unsupported. Genuine missing observation statuses and insufficient-role fallbacks remain in the data; zero support is not a claim that future role uncertainty vanishes. Calibrator manifests preserve support, partitions, dates and hashes of immutable parent artifacts.

## Before/after validation

`five_retrained` is the uncalibrated repaired parent; `calibrated_workload` means the relevant family candidate, not a selected combined model. H and P changes are evaluated separately. Units PA for H, IP for P.

| Family/cohort | Model | n | MAE | RMSE | Bias |
|---|---|---|---|---|---|
| H/all | frozen_hybrid | 1487 | 111.412 | 154.320 | +0.309 |
| H/all | five_retrained | 1487 | 112.517 | 154.684 | +5.047 |
| H/all | direct_retrained | 1487 | 113.766 | 154.091 | -0.075 |
| H/all | calibrated_workload | 1487 | 114.604 | 153.697 | +4.947 |
| P/all | frozen_hybrid | 2517 | 20.337 | 32.593 | -1.696 |
| P/all | five_retrained | 2517 | 20.876 | 33.403 | -0.402 |
| P/all | direct_retrained | 2517 | 21.409 | 33.931 | -0.031 |
| P/all | calibrated_workload | 2517 | 20.906 | 33.402 | -0.297 |
| P/demonstrated_starter | frozen_hybrid | 481 | 42.747 | 55.616 | -1.820 |
| P/demonstrated_starter | five_retrained | 481 | 44.555 | 57.256 | +0.525 |
| P/demonstrated_starter | direct_retrained | 481 | 45.761 | 58.325 | +3.416 |
| P/demonstrated_starter | calibrated_workload | 481 | 44.710 | 57.251 | +1.078 |

H joint-state Brier improves .61324→.59366; participation Brier .10769→.10732. Workload MAE worsens2.087PA, although RMSE improves.987PA. Established-hitter MAE130.599→132.803, aging75.216→79.550, interrupted126.465→127.744 and young146.026→146.467 all worsen. Aging bias rises18.496→22.735PA. Better probabilities are not enough.

Starter joint Brier changes only .619022→.618868; participation Brier worsens .11637→.11902. Starter MAE worsens .155IP and RMSE improves .005IP, an immaterial difference on exposed data. Whole-P MAE20.876→20.906. The established P cohort improves31.983→31.713MAE, but interrupted P worsens37.647→38.823. Reliability_Bins.csv preserves fixed ten-bin probability reliability; State_Frequencies.csv preserves expected/observed frequencies and fixed conditional severity; Year_Validation.csv contains all matched years. No bin/sample definitions were optimized after scoring.

Every inherited gate is evaluated separately in Release_Gates_H_calibration_alone.json and Release_Gates_P_starter_calibration_alone.json. H passes the RBI gate and hitter protected numeric limits but fails the unchanged P gates and the overall H MAE criterion. P passes the stable-rotation threshold after calibration, yet fails original94/SP, expandedP/SP, youngSP, RBI (H unchanged) and the2017 expanded-P anchor stability gate. Independent confirmation, allocator accuracy and clinical coverage remain unestablished. No threshold was relaxed.

## RBI: fixed-rate arithmetic versus rate error

The actual research adapter computes `predicted_RBI = baseline_RBI/baseline_PA × expected_PA`, then hitter reconciliation. The preserved baseline rate comes from weighted historical RBI (weights.1/.2/.3/.4 renormalized over observed seasons),100PA regression toward the preserved2010–2012 development prior, and the preexisting as-of aging rate multiplier. There is no dated lineup/team-run context adjustment in this formula. The current calibration test adds none.

With a fixed per-PA rate r and identical rates across workload states, summing state production gives `Σ p_s r m_s = r W`. Partial-season states do not automatically require another rate penalty. Reconciliation changes RBI by numerical roundoff only in these cases; no arithmetic/routing defect was found.

Exact evaluation-only decomposition:

`predicted_RBI − actual_RBI = r(forecast_PA − actual_PA) + (r·actual_PA − actual_RBI)`.

Actual PA is used only after forecasting, never as a prediction input. The second term isolates fixed-rate error at realized exposure.

| population | model | n | total_error | workload_error_contribution | rate_error_at_actual_PA |
|---|---|---|---|---|---|
| all_retrospective_hitters | frozen_hybrid | 1215 | -0.162 | -0.184 | +0.022 |
| all_retrospective_hitters | five_retrained | 1215 | +0.542 | +0.519 | +0.022 |
| all_retrospective_hitters | calibrated_workload | 1215 | +0.475 | +0.452 | +0.022 |
| high_RBI_gate62 | frozen_hybrid | 62 | +3.436 | -0.546 | +3.982 |
| high_RBI_gate62 | five_retrained | 62 | +3.535 | -0.447 | +3.982 |
| high_RBI_gate62 | calibrated_workload | 62 | +0.813 | -3.169 | +3.982 |

The high-RBI group is selected by forecast-date anchor PA≥500 and RBI≥90, not future RBI; source validate_hybrid.py lines21–23 verifies this. It is an outcome-selected prior-season extreme-performance group, so regression to the mean and selection effects limit generalization. The preserved research universe is also not a random census of all hitters. No target-season high-RBI filter was introduced.

The parent +3.535 RBI bias comprises −.447 workload and +3.982 fixed-rate error. Calibration's +.813 total bias passes the±3 gate by making the workload offset −3.169, while rate error stays +3.982. Passing this gate through lower PA does not repair RBI talent. Across all1,215 retrospective hitters the same rate diagnostic bias is only+.022, so the problem is cohort-specific. The benchmark rows above hold the same rate fixed and substitute benchmark workload; they are not a new production RBI export.

A concrete next rate proposal, outside this experiment: reuse preserved RBI aging experiments and freeze one ablation separating the100PA rate prior, historical extreme-season regression and as-of RBI aging multiplier; evaluate both actual-PA diagnostic rate error and unconditional RBI error on the existing forecast-date high-RBI group and all hitters. Historical batting-order/RISP/team-run opportunity would be needed to test team-context explanations. The present evidence supports targeted rate-regression/aging investigation, not blanket rate cuts for shortened seasons. No rate parameters were changed here.

## Code and deliverables

Implemented_Code_Trace.json preserves actual function bodies and file/line references. Principal locations:

- full-workload-scenario/run.py: role_from44, forecast_role55, target_label71, depths86, full-role fit113, ratio regressions139–148, predict155–173; old all-five calibration gate127–128.
- targeted-repair/engine.py: observation28, evidence_features47, forecast cohort71, fz84.
- direct-workload-correction/run.py: features16–20, direct mean fit21–28, clipping29; no participation multiplier.
- first-year-repair/engine.py: stats128–134 and its reconciliation call.
- validate_debut.py: weighted/regressed rate forecast32–62, asof_curve69–88 and project89–95.
- calibration-starter/run.py: supported-class calibration and stable mapping via the inherited predict function; branch guard retains nonstarter P outputs; evaluation proves identical severity and probability-only deltas.

League_1900_Comparison.csv contains separate H-only and P-only candidate columns plus parent forecasts, full-role scenarios, probabilities and explicit non-selection. No combined candidate was scored or selected. Diagnostic_12_Comparisons.csv and Diagnostic_State_Decomposition.csv preserve all illustrations. Direct_Pitcher_Tree_Leaves.csv reproduces the direct pitcher forecasts and exact paths; RBI_Player_Decomposition.csv supplies every diagnostic contribution.

Restore this checkpoint with `python restore.py`, then restore parent checkpoint archives with their existing scripts. Run mechanism_audit.py, run.py, trace_current.py and test_contracts.py with `/path/to/recovered/model /path/to/beta-unpacked.json`; report.py needs no source arguments. Use the preserved numpy/scikit-learn/joblib environment and single-thread BLAS. Parent model artifacts remain immutable. No new sources were collected and no prior checkpoint was discarded. Production and deployment remain unchanged.
