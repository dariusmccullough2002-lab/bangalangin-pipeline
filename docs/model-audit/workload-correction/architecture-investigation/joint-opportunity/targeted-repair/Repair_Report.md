# Targeted workload repair — executable research candidate
Built from engine checkpoint `c4d87203ea1cbf14b23a6b6c05cbe56292961740`; diagnostic checkpoint preserved. No production edits or deployment. **Numerical promotion is blocked: not all protected gates pass.** This is an implemented repair with disclosed validation losses, not an accepted replacement.
## Changes

- `engine.observation`: explicit positive/verified-zero/missing/unverified/not-yet-MLB status, completeness, statistical window, source and acquisition date. Missing exposure/GP/GS remains null, and predictive unknown exposure becomes NaN plus an observation-status indicator. Verified zeros remain0. No observation status asserts medical absence. Full official2026 regular-season census verification matches **all1900 original exposures**;449 zero records are confirmed, and none become positive. Thus the data-semantics defect was real but the suspected2026 exposure errors were not confirmed. Historical acquisition timestamps remain unknown when the preserved source lacks them; no dates were fabricated.
- `evidence_features`, `fz`: rebuild calendar means, count changes, durability, role shares and capacity from status-aware observations. Historical GP availability is current-catalog selected, so GP-derived columns and coverage masks are excluded from hitter statistical inputs. The capacity baseline retains GP as explicit demonstrated usage; it is not a clinical health certificate. Ratio candidates can still be sensitive to nonrandom historical capacity support; this remains a limitation, not proof that coverage bias is eliminated in every capacity-normalized estimator.
- `fit_model`: independent squared-error conditional mean fits; no absolute-error median participates in a selected forecast. Rotation GS/RA means are compared with demonstrated-capacity-normalized response fits. P selected mean_half averages two conditional means, then applies future-state probabilities once. H selected active_capacity_mean forecasts an active conditional mean through demonstrated capacity; weighted normalized loss corresponds to final workload squared error. Unknown capacity falls back to the direct active-mean fit, rather than zero workload. No player-specific floors or named-player selection criteria exist.
- `probabilities`: raw classifier followed by global or cohort calibration, selected on chronological development. Cohorts are established, interrupted, young and unstable; a separate calibrator requires100 completed observations and10 examples per outcome class. Otherwise use global calibration. Current injury diagnoses are never inferred from absent records.
- `allocate_verified`: execution on verified40-man organization membership with explicit2027 continuity assumption. Thirty teams' completed2026 PA, GS and IP rates provide2027 budget scenarios. Allocate compatible unconditional expected units, preserve unmodeled/reserve residual, never scale up players or multiply participation again.1309 players are allocated; other591 have no confirmed membership allocation. This is a membership/budget constraint, **not** a complete independently verified2027 depth chart. Current roster facts are not backfilled into historical evaluation.
- `apply_verified_availability`: keep dated medical facts separate. Facts with no quantified future timetable do not add a penalty. Berríos' reported recovery interval yields an explicitly assumed calendar-based capacity envelope using the official2027 Toronto schedule; it is a scenario, not a verified return date. It clips conditional counts before the final probability mixture, never adds a generic second absence multiplier. All facts/assumptions are saved separately in Availability_Evidence.json and component metadata.
- Independent production-rate scaling, QA3 game-rule yields, bounded SV/HLD and eight-year framework retained. All1900 year2–8 statistical paths are copied exactly in Research_Eight_Year_Overlay.json.gz. Prospect and Trade Analyzer code unchanged. Seven numerical/missing-data and release-blocking contract tests pass. Model artifacts are readable and all frozen prior input/code/model hashes are unchanged.
## Failed candidates were preserved and corrected

Iteration1 role-conditioned H mixture failed durable development guards. Iteration2 added an active conditional mean, passed development guards, but lost some aggregate evaluation accuracy. A full-health40-man allocator falsely assumed simultaneous activity; its failed outputs remain in allocation-iteration1, while the final allocator constrains expected workloads instead. Iteration3 compared preserved expected-mean count candidates without a median. Iteration4 removed nonrandom GP-coverage predictors; development selected capacity means. Every source, selection and prior evaluation remains preserved. Final candidate selection uses ID4 historical development only; named players' current outputs do not select parameters.

Evaluation disclosure: waveA2025->2026 ID0 was scored and exposed, waveB IDs1,2 subsequently scored and exposed, and final waveC IDs3,4 was reserved before final scoring. Each excludes the12 previously disclosed diagnostic players. These are chronological outcome reservations, not player-disjoint lifetime cohorts: historical records for waveB/C players can enter training, but **no2026 outcomes enter any fit or calibrator**. Earlier waves remain reported as exposed evaluations, not relabeled independent final holdouts. Final results have not been used for further parameter tuning. Legacy ID0 gates are already-exposed retrospective evidence.2025 annual facts are acquired retrospectively from a complete source but contain no2026 feature information.
## Final validation
|Population|n|Frozen hybrid MAE|Repair MAE|Frozen RMSE|Repair RMSE|Repair bias|
|---|---:|---:|---:|---:|---:|---:|
|exposed retrospective H|1215|111.8089|120.8566|155.0584|164.0487|29.1359|
|exposed retrospective P|2194|19.7173|19.8902|32.3025|32.6689|-1.8607|
|new_reserved2025_waveC H|272|109.6415|114.8092|150.9799|154.9899|15.0116|
|new_reserved2025_waveC P|323|24.5491|24.6513|34.5026|34.5741|0.6703|

The final candidate does not improve every aggregate benchmark. The successful frozen hybrid remains the benchmark and is not numerically replaced in production. No holdout was retuned to force a pass.
|Protected gate|n|Value|Limit|Pass|
|---|---:|---:|---:|---|
|original94|94|23.419553508486544|23.9972|True|
|originalSP|27|37.24672468500396|36.8801|False|
|expandedP|1084|25.882358574064117|26.4204|True|
|H_standard|1215|120.8565698306207|119.0835|False|
|additional_expandedSP|288|45.856203298223605|47.376|True|
|additional_youngSP|111|41.80647852775302|43.4103|True|
|additional_stableSP_vs_strong|87|49.845010783634386|51.3123|True|
|additional_durableH_vs_strong|24|84.3153626459817|89.1316|True|
|comparable_high_RBI_bias|62|4.868631052819174|3|False|
|new_reserved_not_used_for_tuning||||True|
|complete_dated_historical_roster_injury_coverage||||False|
|same_date_independent_population||||False|
|additional_P_expanded_anchor_2016_stability|121|||True|
|additional_P_expanded_anchor_2017_stability|123|||True|
|additional_P_expanded_anchor_2018_stability|144|||True|
|additional_P_expanded_anchor_2021_stability|192|||True|
|additional_P_expanded_anchor_2022_stability|176|||True|
|additional_P_expanded_anchor_2023_stability|163|||True|
|additional_P_expanded_anchor_2024_stability|165|||True|
|additional_H_standard_anchor_2014_stability|133|||True|
|additional_H_standard_anchor_2015_stability|136|||True|
|additional_H_standard_anchor_2016_stability|135|||True|
|additional_H_standard_anchor_2017_stability|129|||True|
|additional_H_standard_anchor_2018_stability|127|||True|
|additional_H_standard_anchor_2020_stability|108|||True|
|additional_H_standard_anchor_2021_stability|111|||False|
|additional_H_standard_anchor_2022_stability|107|||False|
|additional_H_standard_anchor_2023_stability|116|||True|
|additional_H_standard_anchor_2024_stability|113|||True|

Rotation and durable-cohort repair is measurable: expandedP MAE25.88236 vs prior hybrid25.98282; youngSP41.80648 vs41.97050; stableSP49.84501 vs50.69777; durableH84.31536 vs94.09040. Nevertheless originalSP, overallH and RBI-bias gates remain failed, along with inherited historical roster/injury and matched external coverage requirements. Therefore release remains blocked. Remaining engineering must address aggregate H conditional-retention bias using development data and a genuinely new evaluation target, rather than consume the now-exposed2026 reservations. External forecasts were not used as predictions or training targets.
## Complete replay and diagnostic players
All1900 decomposition sums reproduce their final workload to floating precision. League_1900_All_Statistics.csv contains all categories; League_1900_Before_After.csv supplies conditional opportunity, participation, roster, medical and final transformation contributions. Observation_Verification_1900.csv is the source census comparison; Verification_Sensitivity.csv measures missing-source behavior without inventing zeros. Team_Allocation_Ledger.csv records every executed team constraint and reserve.
|Player|Frozen hybrid|Repair|Change|Participation|Roster delta|Medical delta|
|---|---:|---:|---:|---:|---:|---:|
|Matt Olson|646.95165|632.00764|-14.94401|0.99218|0.00000|0.00000|
|Jose Ramirez|558.23327|494.33727|-63.89600|0.97882|-72.53717|0.00000|
|Juan Soto|597.98367|595.13829|-2.84538|0.98254|0.00000|0.00000|
|Aaron Judge|353.59922|364.71536|11.11614|0.80550|-33.98419|0.00000|
|Gavin Lux|75.23174|146.42813|71.19639|0.44229|0.00000|0.00000|
|Anthony Santander|56.62320|125.81952|69.19632|0.31638|0.00000|0.00000|
|Paul Skenes|127.92158|138.21802|10.29644|0.95016|0.00000|0.00000|
|Zack Wheeler|116.27490|121.05560|4.78069|0.98614|0.00000|0.00000|
|Jacob Misiorowski|127.87629|108.93531|-18.94098|0.97921|-9.02124|0.00000|
|Nolan McLean|119.31271|120.03872|0.72600|0.98330|0.00000|0.00000|
|Jose Berrios|58.72189|57.02998|-1.69191|0.72331|0.00000|-1.34242|
|Ryan Pepiot|34.10098|38.52201|4.42104|0.64958|0.00000|0.00000|
Judge's forecast moves353.59922->364.71536. The253PA median branch is gone, but active-season retention, participation and team opportunity still reduce workload. Verified66GP/285PA2026 evidence is retained; the objective is not to guarantee a healthy full season.

Skenes' conditional SP starts move from the audited23.7 to25.69840; final IP moves127.92158->138.21802. This is a development-selected response repair, not a32-start floor.

## Reproduction and safeguards
```bash
PYTHONDONTWRITEBYTECODE=1 OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 "$CODEX_PRIMARY_RUNTIME_PYTHON" pipeline/docs/model-audit/workload-correction/architecture-investigation/joint-opportunity/targeted-repair/collect_verified.py
PYTHONDONTWRITEBYTECODE=1 OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 "$CODEX_PRIMARY_RUNTIME_PYTHON" pipeline/docs/model-audit/workload-correction/architecture-investigation/joint-opportunity/targeted-repair/run.py recovered/model recovered/beta-unpacked.json
PYTHONDONTWRITEBYTECODE=1 OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 "$CODEX_PRIMARY_RUNTIME_PYTHON" pipeline/docs/model-audit/workload-correction/architecture-investigation/joint-opportunity/targeted-repair/current.py recovered/model recovered/beta-unpacked.json
"$CODEX_PRIMARY_RUNTIME_PYTHON" pipeline/docs/model-audit/workload-correction/architecture-investigation/joint-opportunity/targeted-repair/finalize.py
```
Cached raw verification files carry URL, retrieval time, HTTP date and SHA256. Reproduction uses frozen cached responses; refreshing creates a new forecasting vintage and requires another provenance freeze. Callable adapter: TargetedOpportunityEngine(research_only=True). Default construction blocks numerical promotion whenever gates or explicit deployment authorization are missing. Doctor-window conversion is an explicit scenario; no full clinical model, guaranteed future roster, or validated incremental roster accuracy is claimed.
