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

## Combined MLB / raw MiLB comparison

The default lab view now includes a unified prospect search and MLB reference chart. It uses the existing V1 four-component model, without refitting or promoting a new formula. X is the negative of centered Chase/Whiff model terms; Y is the sum of centered Hard-Hit/Barrel terms. Full-precision MLB logit equals baseline + Y − X, so its zero-logit reference is a diagonal meridian. Crosshairs at zero mark development-mean contributions. Conditional coefficient signs are not causal skill effects; Chase is slightly positive and Hard-Hit slightly negative conditional on the other correlated inputs.

There are at most 25 MLB records plus one blue diamond for a selected adequately sampled prospect. MLB landmark labels include the season; an earlier qualified season is used explicitly when no qualified current-year record exists. MLB outcome colors use observed same-season results. Prospect diamonds have no endpoint label, translated probability, score or above/below-line verdict. Their raw four-component measurements are mapped to a visual coordinate only. This does not fulfill a MiLB-to-MLB translation validation.

Prospect search spans the 178-player board audit, with dated season/level selection for the 46 hitters having qualifying panel records. Missing or undersampled records suppress the diamond. The panel shows sampling denominators and counts nearby MLB development records as a sparse-region check; this is not a full four-dimensional support certification or translated uncertainty estimate. Neighbors from both MLB outcome groups are raw metric similarities, never career comps.

### Raw frontier position and investigation list

The selected prospect now shows signed perpendicular distance from the exact four-component reference, computed as (baseline + Y − X) / sqrt(2). Units are fitted-coordinate geometry, not MLB-equivalent performance or a prospect-success probability. Very small distances are labeled near the line to avoid rounding a boundary case into an apparent meaningful gap. Largest positive and negative centered contributions show the fitted arithmetic, including counterintuitive conditional signs; they are not causal explanations or official scouting grades.

A filtered investigation list orders adequately sampled records by raw distance, with season/level, component rates, sample size and dated ownership. Clicking a row selects that exact record. It remains separate from source-of-truth rankings. Unknown/undersampled prospects remain searchable without a plotted point. Historical minor-league development paths and age-matched future-outcome comps remain explicitly pending.

### Additional paired model audit

`python scripts/audit-power-reference.py` fits the Barrel-only comparator with C selected using the original chronological validation design and compares fixed predictions to V1 on the same reused 409 test seasons / 231 players. A paired player-cluster percentile bootstrap (1,000 resamples) gives four-component minus Barrel AUC difference +.00072, interval −.01661 to +.01972. Brier difference is −.00177, interval −.01148 to +.00791. Both span zero. This does not establish clear superiority over Barrel alone or justify promotion. Training/refit uncertainty is omitted; these are descriptive intervals on an already-inspected test, not independent confirmation. No displayed model coefficients change.
