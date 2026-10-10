# Full-role versus expected-season workload: bounded research test

**The separation improves interpretation, but neither expected-season candidate beats the preserved strong benchmark overall. No candidate is selected or approved for numerical release. Production and dynasty calculations are unchanged.**

Continues research checkpoint `7b8ab45fdd4809881245543398672215f237f300`. Definitions and candidates were committed before candidate scoring (`31bc3af` local protocol commit). All scored 2026 waves are exposed; no genuinely untouched sample was established in the preserved data. Results below are exploratory chronological replays, not fresh holdout results. No parameters were changed after examining candidate errors. Output adapter defects were corrected without changing the scored workload estimators.

## What is, and is not, a full-role estimate

True full availability means eligibility on every scheduled season date, with the specified role retained throughout. Annual PA/IP/GP/GS cannot certify that condition. No preserved complete daily injury/active-roster history establishes it. Therefore the transparent full-role scheduling estimate is a **hypothetical role scenario**, and the historically fitted alternative is explicitly a **high-usage role-retention proxy**, not a medically verified full-availability forecast. The proxy is never trained on all partly active seasons and then relabeled healthy. Its eligible seasons meet the frozen count and role conditions; those conditions still cannot prove clinical health.

Role slots are 155 GP everyday, 115 GP platoon, 80 GP bench, 32 GS starter, 65 relief appearances, or 12 GS + 30 relief appearances swingman. These describe role scheduling while available, including ordinary rest/rotation spacing; they are not playing-time floors. Latest positive verified usage determines the scenario from forecast-date evidence only. Hitter PA/GP identifies everyday (>=3.8), platoon (>=2.8), or bench; missing GP is unknown, with a clearly flagged PA-only everyday proxy at >=400 PA. Pitcher start share >=.8 is starter, <=.1 reliever, otherwise swingman. A verified-zero latest season can inform expected risk while a prior positive role supplies the hypothetical retained-role scenario.

Fitted proxy eligibility: same forecast/observed annual role, GP>=145 everyday / >=100 platoon / >=70 bench; >=30 starts for starters; >=60 relief appearances for relievers; >=40 total appearances for swingmen. Pandemic 2020 targets are excluded. Missing GP cannot qualify. At least60 core training rows per role are required; otherwise the transparent scenario is used. Bench and swingman fits lack sufficient support even at the final vintage. Hitter GP coverage is current-catalog selected and is not a random historical census; proxy results must not be generalized to all players. No full-season MLB arrival scenario is substituted for a prospect forecast. All646 unsupported/prospect/two-way paths remain unchanged, with a separate fallback inventory.

## Exact calculation and risk accounting

For role scenario appearances A and frozen as-of appearance depth d, C = A*d (pitchers: C = GS*d_SP + RA*d_RP). Full-role counts use the role template or a squared-error count fit restricted to eligible proxy outcomes. Depth uses existing status-aware 3:2:1 usage smoothing; no talent engine is refit. Counting-stat rates are copied from production; QA3 yields are restored from the completed prior replay that implements the league rule (>=5 IP and <=2 ER, OR >=6 IP and <=3 ER).

The mutually exclusive joint outcomes s are absent, retained/high-usage, retained/reduced-usage, changed role, and unknown role. For each nonzero state the fitted squared-error ratio r_s estimates E(actual workload / scenario C | state, forecast inputs). Count-normalized fitting weights are proportional to C^2; all blended/displayed statistical targets are means. W = C * sum_{s!=absent} p_s*r_s. Participation q = 1-p_absent; conditional-active workload W/q is a derived display, not another model discount. The absence term is exactly -p_absent*C; each other term is p_s*C*(r_s-1). Their sum plus C reproduces W to numerical precision. Changed roles may exceed the specified role scenario; only absolute PA/IP bounds apply.

This is a joint-outcome model, not independently identified medical and demotion hazards. A reduced same-role season can reflect injury, time in the minors, roster competition, or other causes; the annual data cannot assign causation. **The retained/reduced contribution must not be called an injury adjustment.** Unknown outcomes remain separate, not silently assigned to an injured or bench state. Historical missed time in predictor features does not by itself prove a double multiplier: absence and active-shortened outcomes are disjoint targets here.

The current counting-stat adapter uses scenario q once and normalizes the preserved rate-role composition within active outcomes. Hitter active opportunity is represented without a400-PA conditional floor. Pitcher count feasibility (36 GS,85 appearances) is attributed separately before roster allocation. This adapter is a sensitivity, not evidence that its reductions improve accuracy. The independent role composition remains inherited; no new destination-specific role-transition superiority is claimed.

For team channel b, scale = min(1, verified team budget_b / sum expected demand_b). Apply it to compatible unconditional expected quantities only, never sum all hypothetical healthy capacities. Current40-man membership continuing into2027 is an assumption. Historical current rosters are not backfilled. Dated medical facts without a quantified forecast-year return window have zero numeric adjustment. The retained Berrios calendar-window envelope clips conditional starts; it is a timetable assumption, not an independent second medical probability. Independence from interruption risk is not clinically validated. With/without-allocator and medical-envelope columns are supplied; neither mechanism is accepted just because it lowers team totals.

## Historical results

4004 eligible player-season forecasts, including1562 observed zero-workload outcomes. Legacy matched populations plus the last2026 wave are replayed; earlier scored waves remain preserved context, not a fresh selection set. Core IDs mod5 1/2/3 fit models, ID4 calibrates probabilities, and target years never exceed min(forecast anchor,2025). The2026 target is never used in fitting. Cases cover annual incumbents; pre-MLB arrival forecasts are outside this count-validation population.

|Family|Model|n|MAE|RMSE|Bias|
|---|---|---|---|---|---|
|H|production|1487|160.67|186.91|44.25|
|H|frozen_hybrid|1487|111.41|154.32|0.31|
|H|strong_prior|1487|110.97|158.76|-7.14|
|H|repair|1487|119.75|162.43|26.55|
|H|expected_structural|1487|115.77|158.68|-2.15|
|H|expected_fitted|1487|115.79|158.80|-2.26|
|P|production|2517|28.98|38.66|8.88|
|P|frozen_hybrid|2517|20.34|32.59|-1.70|
|P|strong_prior|2517|20.35|32.99|-1.43|
|P|repair|2517|20.50|32.92|-1.54|
|P|expected_structural|2517|20.86|33.41|-0.43|
|P|expected_fitted|2517|20.88|33.40|-0.40|

The candidates reduce prior-repair bias, but lose MAE and RMSE to the frozen hybrid. Paired player-cluster intervals in Paired_Comparisons.csv describe exposed evidence only. Neither a selected name receiving more workload nor agreement with production constitutes historical accuracy.

|Conditional proxy population|Model|n|MAE|RMSE|Bias|
|---|---|---|---|---|---|
|H|full_structural|196|39.13|51.33|-12.60|
|H|full_fitted|196|40.57|52.10|-6.50|
|P|full_structural|285|8.04|11.13|0.40|
|P|full_fitted|285|8.70|12.01|1.58|

The fitted proxy does not improve conditional errors over the transparent scenario overall. This is selection-conditioned usage evaluation, not validation among medically verified fully available players. In total481 outcomes meet the proxy; sparse role cells, unknown hitter GP, and survivor-selected GP coverage limit conclusions.

|Family|Cohort|n|Predicted participation|Observed|Brier|Prior Brier|Active workload bias|
|---|---|---|---|---|---|---|---|
|H|aging33plus|286|0.43|0.41|0.14|0.14|-13.04|
|H|all|1487|0.72|0.71|0.11|0.11|-2.69|
|H|established|1050|0.69|0.67|0.11|0.11|-4.34|
|H|interrupted|222|0.66|0.64|0.15|0.15|-18.68|
|H|uncertain_role|823|0.58|0.56|0.16|0.15|-5.20|
|H|young|318|0.90|0.90|0.08|0.08|-9.33|
|P|aging33plus|437|0.33|0.35|0.09|0.09|1.67|
|P|all|2517|0.52|0.55|0.14|0.14|1.30|
|P|established|1838|0.47|0.50|0.12|0.12|0.77|
|P|interrupted|167|0.58|0.59|0.16|0.16|3.03|
|P|uncertain_role|1362|0.31|0.34|0.15|0.15|1.23|
|P|young|538|0.71|0.75|0.17|0.18|3.06|

Role-retention Brier scores and five-state calibration bins are saved separately. Unknown future roles are excluded from known-role calibration but remain in unconditional workload validation. Workload deciles are formed from forecast-date workloads, not outcomes. All protected cohorts, per-anchor paired stability rules, and the original high-RBI bias gate retain their thresholds.

|Candidate|Failed gate|Value|Existing limit|
|---|---|---|---|
|expected_structural|original94|24.65|24.00|
|expected_structural|originalSP|38.74|36.88|
|expected_structural|expandedP|26.66|26.42|
|expected_structural|additional_expandedSP|48.28|47.38|
|expected_structural|additional_youngSP|44.55|43.41|
|expected_structural|additional_stableSP_vs_strong|52.13|51.31|
|expected_structural|additional_durableH_vs_strong|140.87|89.13|
|expected_structural|additional_P_expanded_anchor_2017_stability|32.41|unknown|
|expected_fitted|original94|24.82|24.00|
|expected_fitted|originalSP|38.97|36.88|
|expected_fitted|expandedP|26.69|26.42|
|expected_fitted|additional_expandedSP|48.33|47.38|
|expected_fitted|additional_youngSP|44.69|43.41|
|expected_fitted|additional_stableSP_vs_strong|52.06|51.31|
|expected_fitted|additional_durableH_vs_strong|139.41|89.13|
|both|untouched_evaluation_sample|unknown|unknown|
|both|verified_historical_daily_availability_and_role|unknown|unknown|
|both|historical_allocator_accuracy_identifiable|unknown|unknown|

A missing untouched holdout, historical daily health/role coverage, and historical allocator accuracy evidence also block release. No gate is relaxed or redefined to rescue a candidate. Preserved_Release_Gates.json retains the previous complete gate record.

## Current population attribution

|Group|n|full_role_PA_IP|absence_adjustment|retained_reduced_adjustment|changed_role_adjustment|high_usage_adjustment|unknown_role_adjustment|count_feasibility_adjustment|team_allocation_adjustment|medical_envelope_adjustment|final_expected|
|---|---|---|---|---|---|---|---|---|---|---|---|
|H|841|404.54|-98.55|-49.10|-24.08|1.46|-16.05|0.00|-0.72|0.00|217.50|
|SP|273|151.99|-33.63|-24.28|-16.31|0.25|0.00|-0.00|-1.13|0.00|76.89|
|RP|786|78.52|-38.61|-15.94|-2.53|-0.59|0.00|-0.02|-0.08|0.00|20.75|

These are arithmetic contributions in a declared order, not causal injury effects. The league CSV also supplies raw expected workload, production, frozen hybrid, previous repair, and exact reconciliation residuals. Roster and medical scenarios are not included in the historical accuracy estimates because adequate dated historical evidence is absent.

## Diagnostic illustrations (not tuning targets)

|Player|Full-role proxy/scenario|Conditional active|Participation|Raw expected|Allocator|Final sensitivity|Previous repair|
|---|---|---|---|---|---|---|---|
|Matt Olson|687.58|626.29|0.99|621.95|0.00|621.95|632.01|
|Jose Ramirez|659.62|526.10|0.95|499.71|0.00|499.71|494.34|
|Juan Soto|689.93|570.24|0.98|561.42|0.00|561.42|595.14|
|Aaron Judge|676.24|471.06|0.90|425.91|-12.46|413.46|364.72|
|Gavin Lux|444.99|235.01|0.40|93.62|0.00|93.62|146.43|
|Anthony Santander|649.23|451.89|0.26|119.32|0.00|119.32|125.82|
|Paul Skenes|182.60|139.09|0.96|133.75|0.00|133.75|138.22|
|Zack Wheeler|188.32|151.41|0.97|146.54|0.00|146.54|121.06|
|Jacob Misiorowski|174.33|144.63|0.97|140.25|-15.69|124.56|108.94|
|Nolan McLean|184.93|146.29|0.98|143.15|0.00|143.15|120.04|
|Jose Berrios|183.10|58.73|0.70|40.91|0.00|40.91|57.03|
|Ryan Pepiot|165.44|59.14|0.51|30.43|0.00|30.43|38.52|

**Paul Skenes:** full-role 182.60 -> conditional active 139.09 -> raw unconditional 133.75 -> count adapter 0.00 -> roster 0.00 -> medical 0.00 -> final sensitivity 133.75. Latest verified usage is 174.33 PA/IP, 32.00 GP, 32.00 GS. The healthy-role scenario is hypothetical and is not the realistic expected-season forecast.

**Aaron Judge:** full-role 676.24 -> conditional active 471.06 -> raw unconditional 425.91 -> count adapter 0.00 -> roster -12.46 -> medical 0.00 -> final sensitivity 413.46. Latest verified usage is 285.00 PA/IP, 66.00 GP, unknown GS. The healthy-role scenario is hypothetical and is not the realistic expected-season forecast.

Skenes retaining a full rotation scenario does not establish that all future active seasons have32 starts. The old25.7 conditional count and the new lower active expectation are forecasts across active shortened/changed-role seasons, not estimates of healthy full-role capacity. Judge is still classified as an everyday role scenario despite the verified shortened latest season; his expected forecast remains lower because the interruption/state model forecasts a mixture of outcomes. No player-specific floor or forced upward forecast appears in the implementation. The generic candidates fail protected gates; these named outputs cannot justify acceptance.

## What earned a place, what failed, what remains unresolved

- **Earned as research/reporting structure:** separate role scenario and unconditional expectation, preserved observation status, explicit joint-risk attribution, exactly one absence mixture, and transparent role fallbacks. They expose why an active expectation can be much lower than full-role capacity. This does not establish numerical superiority.
- **Failed as replacement estimates:** both new expected candidates lose overall MAE/RMSE against the strong benchmark and fail protected gates. Fitted full-role proxies add fitting complexity without improving overall proxy errors. Retain the benchmark; do not promote either candidate.
- **Not validated:** team-budget allocation, medical-window independence, daily role retention, true full-health scenarios, and realistic arrival probability for unsupported prospects. The team allocator changes current outputs but has no matched historical accuracy test. A fresh future vintage or genuinely untouched outcome sample is needed before selecting further numerical repairs.
- **Confirmed output defects corrected:** a naive scale-only count adapter exceeded36 starts (maximum43.4237), and the pre-roster template omitted completed QA3 yields. Fixed bounds and restored frozen QA3 yields are separate from opportunity-model tuning; their contributions remain auditable.

No new talent model, prospect translations, eight-year paths, dynasty value, replacement accessibility or Trade Analyzer logic is changed.

## Reproduction and executable references

Restore the three preserved checkpoint archives (first-year-repair/restore_checkpoint.py, roster-opportunity/restore_checkpoint.py, targeted-repair/restore.py), then run:

```bash
PYTHONDONTWRITEBYTECODE=1 OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 "$CODEX_PRIMARY_RUNTIME_PYTHON" docs/model-audit/workload-correction/architecture-investigation/joint-opportunity/full-workload-scenario/run.py /absolute/recovered/model /absolute/recovered/beta-unpacked.json
PYTHONDONTWRITEBYTECODE=1 OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 "$CODEX_PRIMARY_RUNTIME_PYTHON" docs/model-audit/workload-correction/architecture-investigation/joint-opportunity/full-workload-scenario/test_contracts.py /absolute/recovered/model /absolute/recovered/beta-unpacked.json
"$CODEX_PRIMARY_RUNTIME_PYTHON" docs/model-audit/workload-correction/architecture-investigation/joint-opportunity/full-workload-scenario/summarize.py
```

|Source|Function|Line|
|---|---|---|
|full-workload-scenario/run.py|forecast_role|55|
|full-workload-scenario/run.py|target_label|71|
|full-workload-scenario/run.py|inputs|82|
|full-workload-scenario/run.py|depths|86|
|full-workload-scenario/run.py|fit|113|
|full-workload-scenario/run.py|predict|155|
|full-workload-scenario/run.py|component_for|266|
|full-workload-scenario/run.py|current|295|
|targeted-repair/engine.py|observation|28|
|targeted-repair/engine.py|evidence_features|47|
|targeted-repair/engine.py|fz|85|
|targeted-repair/engine.py|fit_model|93|
|targeted-repair/engine.py|predict_model|132|
|targeted-repair/engine.py|allocate_verified|160|
|targeted-repair/engine.py|apply_verified_availability|193|

The CSVs, compressed player components, fitted joblib artifacts, protocol, manifests, calibration bins and gate outputs constitute the reproducible checkpoint.
