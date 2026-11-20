# Power Translation Lab: Phase 2 exploratory audit

November 20, 2026. No model is promoted. Main rankings, grades, profiles, trade values, Decision Lab and recommendations are unchanged.

## Readability

The MLB scatterplot shows at most 25 deterministic representative seasons, covering both endpoint outcomes and the four impact/risk regions when available. The active selection is retained. Full-sample tables, searches, quadrant statistics, model estimates and nearest neighbors do not use this visual subsample. This is a reading aid, not a representative estimate of prevalence.

Impact/risk reference lines use fixed development means: risk z = 0 and Hard-Hit = its 2015–2023 qualified development mean. The separate Chase/Whiff view uses illustrative 35% / 30% cuts. Neither is a validated success boundary. The conditional V1 fitted boundary is hidden by default and available only in impact/risk mode, under the existing four-dimensional support guard. No diagonal boundary is forced onto the data.

## Study design

`python scripts/research-power-phase2.py` reproduces 900 comparisons: 15 candidate specifications × 12 endpoints × 5 sample guards. Endpoints are all nine combinations of ISO .180/.200/.220 and wOBA .320/.330/.340, plus xSLG .420/.450/.480. Samples are 150, 200, 300, 400 PA and qualified proxy (502, 186 in 2020).

Models include Hard-Hit, Barrel, Chase+Whiff, Hard-Hit+Barrel, four components, pairwise interactions, quadratic terms, additive splines, shallow tree, random forest, and regularized gradient boosting. The discipline extension adds Zone Swing, Zone Miss, Swing, K and BB. Same-season ISO/wOBA baselines overlap the endpoint and are diagnostic ceilings, not promotion candidates. xSLG is an outcome proxy.

Specifications are fixed, not selected using test outcomes. Training uses seasons through 2023; reused temporal tests use 2024–2026. Unlike V1, these sensitivity candidates fix logistic C=1 rather than selecting C on the earlier validation period. Rolling origins cover 2020–2026. Because Phase 1 already inspected these years, this is exploratory evidence, not independent confirmation. Nine related thresholds and repeated player-seasons are not independent replications.

Reported metrics include AUC, Brier, log loss, precision, recall, false-positive and false-negative rates, top-decile lift and probability-bucket calibration. Region tables retain sample sizes, Wilson intervals, medians and ISO outcome percentiles. Wilson intervals are descriptive, not player-cluster-adjusted inference. Strong causal conclusions or universal danger cutoffs are unwarranted.

## Findings

At the qualified ISO .200 / wOBA .330 endpoint (409 test seasons): Barrel AUC .91296, Hard-Hit+Barrel .91295, four components .91403. Nonlinear models did not improve this primary comparison. Brier improves from .13461 for Barrel to .13096 for four components. The extended discipline specification reaches .92294 AUC and .11652 Brier, but needs independent confirmation, stability evaluation and feature ablation before any promotion.

Four components improve over Barrel by approximately −.0024 to +.0528 AUC across the 60 endpoint/sample combinations. This variation argues against assuming one formula is uniformly better. Four-component rolling AUC is .845 in 2020, .896 in 2021, .879 in 2022, .875 in 2023, .933 in 2024, .926 in 2025 and .884 in 2026. Barrel outperforms the four-component model in 2026. Extreme profiles remain sparse: the reused qualified test has only three seasons at Chase ≥38 and Whiff ≥33, spread across separate Barrel bands. No universal no-survival threshold is established.

Separate next-year tests use predictors at t and target outcomes at t+1. Training target years end in 2023; tests are targets in 2024–2026. The 382 retained pairs require qualified input seasons and 200+ PA the following year. Four-component AUC is .819 versus .823 for prior ISO+wOBA; the discipline extension reaches .831 versus .830 for prior ISO+wOBA+K+BB. These small differences do not establish improvement. Attrition is censored and introduces selection bias. A separate two-consecutive-success outcome is exported, likewise conditional on retained playing time.

## Minor-league progress

`python scripts/build-power-minor.py` downloads official Savant regular-season aggregates for 2024–2026 separately in AAA and FSL A. A companion zones 11–14 export reconstructs Chase as outside-zone swings / outside-zone pitches. Whiff is whiffs / swings. Hard-Hit and Barrel/BBE come directly from their named aggregate fields. Unknown locations are excluded from the Chase denominator. Each source URL, retrieval date and SHA-256 is recorded. Initial incorrect detail exports returned exhibition games; those exports were rejected and are not part of the panel.

The panel contains 58 records for November-board hitters. Fifty-two records for 46 unique hitters pass the exploratory guard: 100+ source PA, 100+ swings, 100+ outside-zone pitches, all four observed components, and 50+ tracked BBE. Tracked BBE is recovered from barrels_total / Barrel/BBE fraction when positive; zero-barrel samples without a verified denominator remain below the guard. No values are inferred from prose. Fantasy ownership remains the dated October 6 snapshot and may be stale.

Minor charts show raw Chase and Hard-Hit with same-year, same-level all-source peer medians; point area represents Barrel. All four components appear in the player panel and table. At most 25 minor records are drawn at once. No age is inferred for historical seasons from current board age. No MLB probability, translated score, prospect grade, future-outcome classification or survival boundary is produced. Same-level medians are not park or competition adjustments. Tracking coverage outside AAA/FSL is not assumed.

## Remaining work and promotion

HR and OPS endpoints are absent from the frozen 19-column MLB source; wRC+ remains unavailable. EV90, max EV, Pull-Air and raw launch-angle panels are not available in this source. Three-way interaction promotion and a separately tuned GAM remain deferred. MiLB development-to-MLB outcomes, age/level/park adjustments and maturation paths are not validated. A new prospect model requires a frozen historical MiLB cohort, later opportunities/outcomes with censoring, chronological validation and a meaningful baseline comparison.

Promotion requires baseline improvement or demonstrated prospect-specific value; endpoint and time stability; calibration; adequate extreme samples; understandable baseball logic; sample sensitivity robustness; and clear explanation. The present evidence supports continued experimental use only.

All detailed CSVs and JSON are linked on the live experimental page. Source snapshots remain fixed; neither study is an automatic refresh feed.
