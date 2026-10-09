# V2.3C path uncertainty, opportunity and RBI continuation

## Recommendation

Keep numerical changes offline. Continue from parent `5652f392830713d5567af4bdb8aa492320406ab6` on `review/capacity-opportunity-attrition-20261009`; the remote branch had no subsequent commits. All additions live under `joint-opportunity/path-rbi`. No production, Beta, header/UI, ownership, picks, rankings or prior research artifact is modified.

This continuation implements an exact role/availability path evaluator and a bounded alternative; tests general conditional-start and reliever-QA3 alternatives; completes an annual-data league-wide RBI audit; and saves all-asset projection/value/rank sensitivities. The path architecture is useful for further research. None of the complete numerical combinations clears release gates.

## Preserved comparisons

The previous joint opportunity, appearance/depth, MiLB capacity, past-only and calendar models are reused. Original historical IDs and predictions remain unchanged. The affiliated debut ledger is not recollected: all266 owned MLB-pitching assets retain verified coverage, with11 unresolved identities and86 no-recorded-MLB-debut states still explicit. No names enter fitting.

The baseline and previous direct-linear-SP and joint candidates remain separate. The inherited baseline/category normalizers and rate-aging curves retain their historical provenance; this continuation does not certify them as wholly past-only talent models. Existing retrospective outcomes have been inspected, so no independent prospective confirmation is claimed.

## Implemented eight-year role/availability paths

The new state process has three states: absent/RP/SP for pitchers and absent/part-time/regular for hitters. Year-specific marginal probabilities and conditional opportunity forecasts come from saved models. A historical family/age transition estimator uses completed seasons through each forecast anchor, excludes holdout/development identities from association fitting, and includes post-debut absence/return transitions. Iterative proportional fitting joins adjacent-year marginals while retaining historical transition association. Every associated transition table preserves both marginals, allowing continued roles, transitions, absence and return.

An association-versus-independence development comparison uses ID-remainder4 outcomes and stationary proxy marginals. This is a limited development criterion, not player-specific joint calibration. Both families select association. The retrospective confirmation diagnostic uses saved player marginals at horizons2–6, rather than the proxy marginals.

| Adjacent-season joint log loss (lower is better) | pairs | Independence | Association |
|---|---:|---:|---:|
| Hitters |594|1.6544|1.4138|
| Pitchers |980|1.4616|1.2467|

Association improves both2019 and2021 test anchors. These are repeated player/anchor/horizon observations, not594 or980 independent careers. Chronology and transition matrices are saved. Longer trajectories and years7/8 are not validated by these pairs.

The evaluator computes exact first and second moments of discounted contribution over all paths by dynamic programming; no Monte Carlo sampling is needed. For12 diagnostic players, all6,561 eight-year role histories are enumerated and their probabilities sum to one. Enumeration independently reproduces the dynamic-programming neutral mean. Existing three contribution-amplitude branch probabilities and prospect branches remain; those amplitudes are not newly calibrated conditional talent distributions.

Production is realized within each role/workload state before replacement surplus and nonlinear utility are calculated. Participation is applied once. The previous cohort workload attrition is not multiplied again. Neutral and timing-specific competitive fit remain separate from unestimated acquisition prices. No RP market penalty or player bonus is added. The separate role-floor sensitivity changes the replacement reference with future pitching role; current-player per-IP talent rates remain frozen, so role-specific talent validation is incomplete.

### What path propagation actually changes

The existing competitive evaluator is a discounted sum of annual utility with zero risk deduction. Holding annual marginal emissions constant, correlation changes dispersion but cannot change the expected discounted value. Nonlinear utility applied before averaging can change expected value; no risk haircut is imposed.

| Player | Production neutral | Prior joint mean | Path neutral, same role floor | Independent dispersion | Correlated dispersion |
|---|---:|---:|---:|---:|---:|
| Judge |71.40|43.39|44.44|24.50|42.85|
| Ramírez |42.27|33.19|33.19|11.26|18.27|
| Olson |32.88|38.07|38.07|9.18|13.17|
| Misiorowski |93.41|102.41|102.86|28.27|36.13|
| Skenes |94.91|79.27|79.35|20.57|29.06|
| Wheeler |53.01|62.62|62.62|14.22|21.52|
| McLean |42.90|42.98|42.98|12.51|17.77|
| Cade Smith |39.23|39.08|39.08|11.11|13.80|

Dispersion is modeled standard deviation in the existing display scale, not a calibrated confidence interval or market-price range. Most large prior value shifts survive path propagation. They mainly reflect changed workload/aging forecasts and horizon assumptions, rather than the act of collapsing a mean alone. Judge's first-year model has16.58% absence probability and43.57% regular probability, conditional active483.05PA and expected402.96PA; his frozen2026 snapshot has285PA. This is observed low exposure, not a new injury diagnosis. Ramírez/Freeman's exact probabilities and annual workload/rate effects are in the diagnostic atoms. Full talent accuracy is outside this workload experiment.

### Physical-support failure and bounded follow-up

Mean-preserving hitter state rescaling plus inherited low/base/high workload amplitudes can produce implausible emissions: the initial diagnostic maximum exceeded900PA. Those outputs remain saved as a failed unbounded experiment.

The bounded follow-up uses completed nonholdout historical maximum support:754PA for hitters,114IP for principal relievers and251IP for starters. Hitter part-time base support stops at400PA, with regular base support400–754PA. It matches the saved mean where feasible and records infeasibility; inherited workload amplitudes are capped within role support. Pitcher components retain distinct conditional starts/relief opportunity, with bounded IP and QA3≤IP/5. These empirical caps are a fixed research assumption, not claimed immutable physical laws.

All136,800 bounded emissions pass workload/count checks. Across current asset/horizon rows,186 hitter means cannot be matched exactly; the maximum base-mean workload difference across H/P is0.9708. Inherited amplitudes are clipped1,596 times. Thus this candidate corrects physical support but changes the inherited uncertainty distribution; it is not a harmless UI or distribution-only fix. The bounded value tables expose that effect.

| Distribution scoring | cases | Deterministic saved mean CRPS | Role-mixture CRPS | Bounded-mixture CRPS |
|---|---:|---:|---:|---:|
| Pitchers |1084|26.0508|21.2606|21.2608|
| Extended hitters |1215|116.0835|88.5420|88.5524|

CRPS rewards informative distributions, so the deterministic score equals MAE. These improvements do not certify intervals. The discrete mixtures still omit within-role continuous workload variation and joint talent/availability dependence. One-year realized-utility MAE barely changes: pitchers0.905456→0.905814 and hitters1.236066→1.236373. Better workload distribution scoring has not demonstrated better dynasty contribution point estimates.

## Further general opportunity calibration

A fixed standardized ridge(alpha100) models conditional future-SP starts from age, observed current/prior GS, GP, tenure and verified workload capacity/MiLB usage. Completed-target fitting excludes test identities. A177-case development conditional-GS comparison favors the direct model: MAE7.50 versus7.74 for a fixed blend. The development blend uses latest GS; the test blend uses the incumbent conditional-GS forecast, so the blend is explicitly exploratory, not an identically tuned selected variant.

| IP MAE | Frozen baseline | Previous linear SP | Past-only joint | New direct GS | Fixed GS blend |
|---|---:|---:|---:|---:|---:|
| Expanded1084 |29.42|25.92|26.05|25.87|25.90|
| Expanded current SP288 |51.75|46.38|46.54|46.00|46.05|
| Original94 |24.97|23.77|23.00|24.07|23.48|
| Original current SP27 |39.10|37.55|35.88|40.27|37.90|
| Young SP111 |44.88|42.33|41.91|42.57|42.05|

The direct model improves several expanded-season results but worsens original starters, young starters, and first-season QA3. It is rejected for release. It does not alter absence/role probabilities, which retain the previous calibration limitations. Current direct-GS diagnostic innings: Skenes143.49, Misiorowski140.46, McLean136.24, Wheeler133.00. These are not targets or accepted projections.

A fixed pooled principal-RP QA3/GS alternative learns exact QA3 counts plus a pure-relief offset from past-only cases. Expanded RP QA3 MAE worsens0.5782→0.6019, versus0.4869 baseline. It is rejected. Original starter QA3 improves slightly but does not offset the RP failure. The definition remains5+IP with≤2ER OR6+IP with≤3ER. No QS substitution or fabricated game labels occurs. SV/HLD do not grow from added workload; cause-specific leverage/role-specific rates remain unfinished.

All chronology, season/cohort MAE, RMSE, biases and per-case forecasts are saved. New candidate current values alter year1 only; years2–8 retain the prior joint forecasts. They are explicitly first-year opportunity sensitivities inside an eight-year evaluator, not validated horizon-wide GS models.

## League-wide RBI audit and Soto reconstruction

Official Baseball Savant's Soto table reports109RBI in2024,105 in2025 and68 in482PA in2026.2025 had120 runs, not120RBI. These totals match this frozen Soto snapshot; no player record is replaced. Source URLs and dated independent projection evidence are saved in `Independent_RBI_Evidence.json`.

Soto's recent-year weights are2023=.1,2024=.2,2025=.3,2026=.4. They yield620.7 weighted PA and91.4 weighted RBI, or0.147253RBI/PA. Production uses a100-PA prior at0.115351RBI/PA, reducing the rate to0.142827. The retained first-year rate-aging factor is0.963757, yielding0.137650. Multiplying by640.1657 projected PA reproduces88.1189 RBI exactly.

His starting workload is628.734PA; the production first-year workload multiplier increases that to640.166 rather than reducing it. The forecast is nonetheless lower than his healthy715PA season. At640.166PA, the raw recent rate gives94.266RBI; the100-PA regression reduces that to91.433 and rate aging reduces it to88.119. Both lower playing time versus a healthy season and rate shrinkage/aging contribute. No120-RBI target is justified by these inputs.

The independent dated ZiPS3YR2027 reference has666PA/100RBI, about96.12RBI at640.17PA. It is an April21 reference, not a fresh October forecast or a model target. This difference is diagnostic only.

The systematic audit covers841 supported current hitters and all1215 ordinary-season historical cases, preserving682 original cases. It compares past-only league priors and fixed pseudocounts0/25/100/300.455 development cases favor0, both with and without frozen rate aging. Unaged and aging-preserved experiments are separately retained. Selection uses baseline workload on development and fixed incumbent workload on historical test; this design difference limits transfer of the chosen strength.

| RBI test | cases | Baseline MAE / bias | Joint workload, old rates | Zero-prior, frozen aging |
|---|---:|---:|---:|---:|
| All ordinary-season |1215|20.466 /+4.428|15.349 /−0.263|15.295 /−0.506|
| Original |682|19.886 /+1.191|17.418 /−0.646|17.417 /−0.804|
| Forecast-date high RBI |62|20.697 /−9.923|20.824 /+0.368|21.074 /+3.298|
|600PA anchor hitters |132|20.866 /−9.872|19.905 /−0.325|19.942 /+0.440|

High-RBI is defined before the target season: anchor≥500PA and≥90RBI. The baseline underforecasting in that cohort is substantial, but the joint workload model already removes most signed bias. Lower rate regression provides only0.054 fewer aggregate RBI MAE, increases RMSE, and worsens high-RBI and everyday-hitter gates. There is no support for a league-wide RBI uplift or a Soto override.

At production PA, the aging-preserved zero-prior sensitivity yields Soto90.85RBI, Alonso91.91, Olson79.96, and Pasquantino78.62; exact outputs are saved. Soto falls to85.48 with the prior joint602.31PA workload. This illustrates why raising RBI/PA alone does not cure an opportunity reduction. Current matrices preserve frozen rate aging across horizons; RBI is bounded below by HR and above by4PA where a sensitivity otherwise violates count support. Coherent and unaged sensitivities remain separate.

Lineup spot, projected team offense, runners-on-base opportunities and expected teammate performance are not explicitly present in the cached annual-rate estimator. Historical effects enter implicitly through player RBI rates; no new context was fabricated. A complete context-aware RBI forecast therefore remains unfinished. The available evidence supports retaining incumbent rates pending a better chronologically validated context model, rather than forcing a rate increase.

## Full-league impacts and reproducibility

Three independent output families each cover all2546 assets, with1900 supported MLB assets and646 frozen/unsupported entries. Prospect/pick/two-way/identity boundaries stay unchanged. `Path_League_Impact*` separates mean collapse, independence, correlation, future-role replacement and an unaged RBI sensitivity. `Candidate_League_Impact*` isolates frozen-aging RBI and direct/blended GS/RP-QA3 first-year sensitivities; `Candidate_Annual_Production.csv` supplies year/category output. `Bounded_Path_League*` and `Bounded_Annual_Production.csv` expose physically bounded states. All existing competitive modes and neutral ranks are reported. No acquisition-price estimate is created.

For example, physically bounded neutral values remain Judge43.31, Ramírez33.14, Olson37.38, Misiorowski102.70, Skenes79.16, Wheeler62.56, McLean42.75 and Cade Smith39.10. The frozen-aging RBI path sensitivity gives Olson38.82 and Soto86.65. These are diagnostic value changes, not ranking recommendations. The high Misiorowski value survives because long-horizon workload and inherited contribution/talent assumptions remain; path correlation alone cannot remove it under this evaluator.

Run scripts with `recovered/model recovered/beta-unpacked.json` as the two positional arguments. The earlier verified recovery package and source caches remain required. New research code imports shared read-only helpers, not completed collection loops. `current-GS.joblib` preserves the new current conditional-GS fit. Saved case outputs avoid rerunning fits. Recovery ZIP pieces, byte/hash manifest, source scripts and restore instructions accompany this checkpoint.

## Failed gates and next work

* Candidate-specific original-SP, young-SP and RP-QA3 regressions prevent adoption of new GS/QA3 alternatives.
* Retain incumbent RBI rates: zero-prior gains are too small and high-producer/everyday/RMSE checks worsen. Context inputs and larger dated cohorts are still needed.
* Path probability accounting, exact valuation moments and physical-support checks pass; joint multi-year interval calibration, within-role workload uncertainty, talent/role dependence, mixture overlap and two-way validation remain open.
* Longitudinal association has retrospective support at adjacent horizons2–6; years7/8 and longer-path dispersion remain unsupported by chronological outcome tests.
* Hitter prior-IL/durability failures and current opportunity reductions are not fixed by propagating uncertainty. Preserve the prior limitations and exact diagnostics.
* Universal MiLB capacity remains preserved, but11 identities and historical foreign/independent capacity coverage are still incomplete. No recollection or fabricated zero records.
* Future2027 outcomes remain the prospective gate; freeze any verified final2026 update before examining them. No numerical deployment is authorized or performed.
