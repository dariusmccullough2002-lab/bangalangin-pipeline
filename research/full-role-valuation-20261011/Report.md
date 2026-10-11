# BangaLangin Pipeline: offline full-role contribution experiment

**Recommendation: retain full-role scenarios as conditional contribution diagnostics. Do not adopt them as expected forecasts or dynasty valuations.** The existing benchmark improves workload accuracy versus the saved production replay, but this is a reexpression of an already preserved method, not a newly validated expected-workload model. Hitter utility accuracy does not improve, and the expected workload reductions can remain severe for individual current players. Production adoption is not authorized and has not occurred.

## Scope and provenance

Production base is `ce326ae24cd0e6d016b1ff0fefb23ffd54903ba9`, which includes `975ab6e`. All switches, AFL links, pitching histories and removal of 2B/3B display columns are preserved. The separate research branch adds files only under this directory. Local pre-score protocol commit: `1984a3c`. Forecast-date full-role components come from checkpoint `5e00a76d83f1d0427add2132ec75beef3da6adf4`, using its parent components only; the failed starter-severity and five-state expected candidates are not adopted.

## Exact production input trace

The live beta reads a packed precomputed V2.3C catalog. Its numeric model is **not** the older root `trade-model.js` helper. The restored engine path is `model_asset_fit.paths` → `model_v23.player_paths/mlb_role_paths` → `revised.surplus` → the original `prototype.utility` → `model_asset_fit.competitive`.

1. **Current role and starting workload:** V2.3 routes pitcher seasons by GS/GP (SP at >=0.5), preserving separate two-way streams. Positive same-role observed seasons in 2023–2026 receive 0.1/0.2/0.3/0.4 recency weights, renormalized over available positive seasons. Recent workload and the median of the two largest observed workloads blend 70/30, then shrink toward the early-history role median with weight `1/(N+3)` and receive the inherited 98th-percentile role cap. Zero/missing current seasons are not treated as diagnosed injury; selection of positive seasons is a limitation.
2. **Rates:** Counts per PA/IP use the same observed seasons and a 100-PA hitter or 30-IP pitcher rate pseudocount. First-year rates also inherit the saved rate-aging factor. This experiment retains the final first-year production line's rates; it does not refit rates or apply age twice.
3. **Workload aging/attrition:** `model_v23.curve` fixes 2011–2017 cohort anchors and quality bins, initially matching age within two years, broadening to four years when unique-player support is below 20. Future exposure totals include players who disappear and role changes. The first-year projection multiplies starting workload by the direct horizon-1 exposure ratio. Later horizons use their own direct ratios, not repeated multiplication of year 1. This factor already contains aging, nonparticipation and role/availability loss in aggregate.
4. **Uncertainty:** Three mean-one production states have probabilities 0.25/0.50/0.25 and factors `1-spread`, 1, `1+spread`, with spread `0.25+0.2*(1-reliability)`. These are contribution uncertainty states, **not** the research five-state participation model. Utility is nonlinear, so expected state utility differs from utility of the displayed mean line.
5. **Prospects/identity evidence:** MLB/prospect hybrids can mix archived prospect paths using MLB reliability. V2.3C can retain dated scouting priors by stable ID and make a mean-preserving distribution adjustment; it adds no scouting/market bonus. These routes remain untouched by this experiment.
6. **Contribution and replacement:** Hitter categories are HR, R, RBI, SB, AVG impact and OPS impact. Pitching categories are negative ER, K, `3*SV+2*HLD`, actual QA3, K/BB impact and WHIP impact. Components divide by the frozen early-history category dispersions. Replacement subtracts `floor(role)*exposure/reference(role)`. Role reference exposures are H=509 PA, SP=171 IP, RP=56.6667 IP. Floors are H=4.614672, SP=-0.348355 and RP=0.113167 category units. The negative SP floor creates a replacement credit with more IP; it is an inherited provisional parameter, not a new pitcher bonus.
7. **Utility and time:** `max(0,surplus)+0.1*max(0,surplus-T)^2/T`, T=7.070951. Neutral time discount is 0.88; contender 0.75, rebuild 0.94, with equalized time-weight mass. V2.3C risk preference deduction is zero. The historical workload and state uncertainty already account for risk; no extra medical/team/participation discount should be layered onto these counts.
8. **Replacement access:** Dated available-player alternatives, legal roster capacity and rounds 6–20 acquisition access remain diagnostics. No new scarcity premium, RP market penalty, role-floor refit or trade-price inference is introduced. Weekly 35-IP eligibility is a team constraint; this annual replay does not simulate lineup eligibility.

The display sidecars do not currently feed valuations. Hitter/RP full-role workloads are GP/RA × observed appearance depth; starters use saved GS/RA × depth. The separate research five-state mean is Σp(state)×F×within-state-ratio, already including absence. Workload conditional on MLB participation divides that mean by participation. Neither research quantity is silently substituted for the production projection here.

## Frozen experiment

**Conditional:** substitute the saved full-role first-year line and compute signed contribution, exposure-matched replacement surplus and utility using the exact frozen engine. No additional workload-aging, participation, medical or team discount is applied. Starter QA3 retains saved per-appearance performance yields and bounds. Relief SV/HLD use historical events per appearance; QA3 uses a separate preserved yield. Current catcher scenarios retain the disclosed demonstrated-GP sensitivity. Unsupported, prospect/hybrid, swingman and two-way asset routes are retained.

**Expected comparison:** `F × (W_benchmark/F)`, with the preserved benchmark's unconditional workload and the existing 754-PA/251-IP bounds. The ratio can exceed one for role expansion; full-role workload is never forced above production. This is algebraically the benchmark workload, not evidence that decomposition improves its forecast. Opportunity events remain separate: the candidate retains the full-role event rate over expected appearances, which is an explicit retained-leverage assumption. Historical saved benchmark SV/HLD/QA3 are supplied separately for comparison.

The primary utility columns are **utility of the statistical line**, comparable across methods. Production's actual probability-weighted first-year utility and eight-year display value appear only as context. This experiment does not substitute a new first-year reward into eight-year dynasty paths or claim a revised market valuation. Current ranks are first-year line-utility ranks within the same complete supported comparison universe.

## Historical workload results

3,382 supported player-anchor cases from 4,121 preserved cases. These are exposed chronological replays; forecast-date predictors and saved models are reused, with no new independent holdout. Training outcomes precede the anchor in the saved component lineage. Historical scenarios never use current sidecars. All paired methods use the same supported rows.

| Forecast-date usage group | N | Production MAE / RMSE | Full-role MAE / RMSE | Benchmark expected MAE / RMSE |
| --- | --- | --- | --- | --- |
| everyday | 472 | 163.79 / 192.90 | 189.49 / 271.40 | 139.10 / 185.16 |
| platoon | 495 | 167.82 / 193.75 | 257.58 / 295.45 | 116.78 / 158.25 |
| bench | 285 | 148.17 / 166.21 | 190.38 / 206.41 | 64.76 / 113.11 |
| starter | 481 | 57.34 / 66.40 | 97.22 / 115.83 | 42.92 / 56.81 |
| reliever | 1649 | 18.76 / 22.21 | 55.23 / 61.44 | 12.03 / 18.90 |

Units are PA for hitters and IP for pitchers. They are not averaged together. Benchmarks meet the frozen workload MAE/RMSE comparison gates, including the 5% role-slice regression limit. Those gates do not establish utility improvement or independent release readiness.

**Historical catcher accuracy is unavailable.** The archive has no dated catcher-versus-DH positional series suitable for this replay. Current catcher eligibility is not used to classify past roles. Consequently usage-only hitter slices may contain catchers; they are not catcher-free cohorts. Current catcher sensitivity is reported separately, and cannot be called historically validated.

### Conditional retained-high-usage proxies

| Group | N | Production MAE | Full-role MAE |
| --- | --- | --- | --- |
| everyday | 119 | 205.60 | 31.88 |
| platoon | 56 | 115.59 | 59.86 |
| bench | 16 | 51.99 | 44.99 |
| starter | 70 | 67.19 | 11.37 |
| reliever | 148 | 27.45 | 7.10 |

These evaluation-only slices select next-year retained-role high usage (145 everyday games, 100 platoon games, 70 bench games, 30 starts or 60 pure-relief appearances). They show that the full-role foundation describes those outcomes better. They do not establish the probability that a player reaches them, medical availability, or unbiased expected-season value.

## Category and utility accuracy

Complete paired category scoring covers 1,718 cases through 2025. 2026 workload is scored separately; matching verified complete category outcomes were not reconstructed from incomplete current exports. Missing opportunity data is not zero.

| Group / statistic | N | Production MAE | Full-role MAE | Expected candidate MAE | Preserved benchmark MAE |
| --- | --- | --- | --- | --- | --- |
| H / HR | 764 | 6.223 | 7.160 | 6.073 | 6.073 |
| H / RBI | 764 | 19.795 | 22.894 | 19.151 | 19.151 |
| H / utility | 764 | 1.801 | 2.032 | 1.823 | 1.823 |
| starter / K | 285 | 44.534 | 63.771 | 43.156 | 43.156 |
| starter / QA3 | 285 | 6.023 | 9.429 | 5.640 | 5.581 |
| starter / utility | 285 | 1.709 | 2.124 | 1.662 | 1.635 |
| reliever / SV | 669 | 3.014 | 3.014 | 2.290 | 2.556 |
| reliever / HLD | 669 | 4.704 | 6.440 | 4.597 | 4.429 |
| reliever / utility | 669 | 0.876 | 1.026 | 0.830 | 0.834 |

The expected version slightly worsens hitter utility MAE versus production despite improving HR/RBI count MAE. Pitcher utility improves versus production in the covered sample, but remains slightly worse than the preserved benchmark overall. Separate leverage opportunity assumptions do not uniformly beat the benchmark (notably holds and starter QA3). This is not sufficient evidence for a new valuation model.

Aggregate ERA=9ΣER/ΣIP, WHIP=(ΣH+ΣBB)/ΣIP, AVG=ΣH/ΣAB, OBP=(ΣH+ΣBB+ΣHBP)/(ΣAB+ΣBB+ΣHBP+ΣSF) and SLG=ΣTB/ΣAB. Aggregate OPS sums aggregate OBP and SLG. `Aggregate_Ratios.csv` supplies these quantities; individual ratios are never averaged. Actual QA3 remains 5+ IP with <=2 ER OR 6+ IP with <=3 ER.

## Current representative examples

| Player / role | Production PA/IP | Full-role PA/IP | Expected benchmark PA/IP | Production surplus | Full-role surplus | Expected surplus |
| --- | --- | --- | --- | --- | --- | --- |
| Matt Olson / everyday | 600.55 | 684.88 | 646.95 | 3.99 | 4.55 | 4.30 |
| Shea Langeliers / catcher | 482.92 | 582.01 | 457.56 | 3.31 | 3.99 | 3.13 |
| Aaron Judge / everyday | 469.41 | 667.91 | 353.60 | 8.80 | 12.53 | 6.63 |
| Gavin Lux / platoon | 458.45 | 445.73 | 75.23 | 0.91 | 0.88 | 0.15 |
| Paul Skenes / starter | 165.32 | 182.60 | 127.92 | 8.22 | 9.05 | 6.34 |
| Zack Wheeler / starter | 142.43 | 188.32 | 116.27 | 7.24 | 9.26 | 5.72 |
| Raisel Iglesias / reliever | 52.20 | 65.22 | 49.43 | 3.32 | 4.80 | 3.64 |
| Matt Brash / reliever | 39.56 | 57.07 | 25.42 | 1.46 | 2.42 | 1.08 |

Surplus units are the frozen signed category scale; these are not 0–100 dynasty prices. Lux’s conditional platoon workload is lower than production. The inherited expected benchmark still falls to 75.23 PA for Lux, 353.60 PA for Judge and 127.92 IP for Skenes: sample-wide accuracy does not settle these current individual cases. Current full-role evidence includes repaired official workload observations while fixed production talent lines preserve older export evidence; that source mismatch is deliberate for attribution, not a complete source refresh.

## Ranking, value-gap and trade implications

| Player | Production first-year utility | Full-role utility | Expected utility | Full-role rank gain |
| --- | --- | --- | --- | --- |
| Matt Olson | 3.99 | 4.55 | 4.30 | -20 |
| Shea Langeliers | 3.31 | 3.99 | 3.13 | -27 |
| Aaron Judge | 8.85 | 12.95 | 6.63 | 1 |
| Gavin Lux | 0.91 | 0.88 | 0.15 | -266 |
| Paul Skenes | 8.23 | 9.11 | 6.34 | -1 |
| Zack Wheeler | 7.24 | 9.33 | 5.72 | 3 |
| Raisel Iglesias | 3.32 | 4.80 | 3.64 | 31 |
| Matt Brash | 1.46 | 2.42 | 1.08 | 32 |

Positive rank gain means moving up. A player can gain absolute surplus while losing relative rank because other players gain more. No website ranking is changed.

In the matched first-year line comparison, Olson exceeds Iglesias by 0.667 utility units in production; the conditional comparison reverses that gap to Iglesias ahead by 0.252. The expected benchmark comparison restores Olson ahead by 0.659. This reversal involves retained save opportunities as well as IP, not a universal hitter/pitcher workload discount. Judge–Wheeler and other gaps are provided in the reproducible tables, without extrapolating them through eight years.

Optional relief deployment, ratio protection, weekly eligibility, free-agent alternatives and legal roster slots can make a reliever's roster-specific marginal value zero or negative. The frozen common contribution scale does not estimate that manager-specific value or league acquisition price. No arbitrary RP penalty or pitcher/hitter equalization is applied. A full-role RP rank increase should not be interpreted as scarce dynasty trade demand.

### Largest absolute conditional utility changes

| Player | Role | Production utility | Full-role utility | Change | Rank gain |
| --- | --- | --- | --- | --- | --- |
| Eiberson Castellano | reliever | 0.36 | 6.53 | 6.17 | 965 |
| Randy Wynne | reliever | 0.21 | 6.22 | 6.01 | 1217 |
| Brandon Woodruff | starter | 3.01 | 7.74 | 4.73 | 119 |
| Logan Henderson | starter | 4.40 | 8.75 | 4.35 | 45 |
| Aaron Judge | everyday | 8.85 | 12.95 | 4.10 | 1 |
| Brandon Walter | starter | 3.27 | 7.13 | 3.86 | 91 |
| Chris Sale | starter | 7.10 | 10.36 | 3.26 | 9 |
| Spencer Schwellenbach | starter | 4.98 | 8.17 | 3.19 | 22 |
| Jacob Misiorowski | starter | 8.09 | 10.98 | 2.89 | 4 |
| Jacob deGrom | starter | 4.69 | 7.57 | 2.88 | 21 |
| Tyler Glasnow | starter | 4.03 | 6.90 | 2.86 | 40 |
| Nate Lavender | reliever | 1.42 | 4.27 | 2.84 | 258 |

Large tiny-sample jumps such as Castellano and Wynne show a key limitation: positive MLB appearance evidence can support a hypothetical workload while the frozen talent estimate remains highly uncertain. These are diagnostic conditional scenarios, not credible expected breakout or trade-value claims. No result-driven support threshold was added after scoring.

## Coverage, limitations and decision

Current supported scenarios: 1,653, with 1,652 complete contribution lines. 893 catalog assets retain their existing routes. Current scenario groups: everyday=176, catcher=131, platoon=265, bench=249, reliever=621, starter=211.

The full-role foundation is useful for inspecting player-specific capacity and conditional category contribution. It does **not** solve high-RBI rate bias, catcher/DH capacity, future bullpen assignments or missing workload evidence. Increasing PA preserves RBI/PA and can amplify its bias. Historical samples are current-catalog selected and repeatedly exposed; cases are correlated across players/years. GP high-usage training proxies are not injury labels. No complete catcher holdout or team-level weekly trade utility exists.

**Decision:** keep production unchanged. Retain the full-role contribution comparison for review. Preserve the benchmark expected-workload reexpression as a baseline, not a newly improved model. The remaining gap is a validated role-transition/availability adjustment with dated catcher capacity and future leverage opportunity support. The archived rejected five-state and severity candidates do not fill that gap, and a new adjustment was not fitted merely to improve selected examples.

## Reproduction and files

Run `python3 research/full-role-valuation-20261011/run.py MODEL_ROOT JOINT_OPPORTUNITY_ROOT`, then `python3 research/full-role-valuation-20261011/report.py` and `python3 research/full-role-valuation-20261011/verify.py`.

MODEL_ROOT is the preserved `BangaLangin_V23C_Verified_Recovery_Package.zip` (Library ID `libfile_2c011e615d8881918652c11b88514df6`), with the preserved V22 model package available (`BangaLangin_Trade_Analyzer_V22.zip`, ID `libfile_b4c78f8efa008191b1bba763036c0004`). The verified V23C recovery package already includes these baseline model paths; the original V22 archive was checked as a recovery reference.

JOINT_OPPORTUNITY_ROOT is restored from Git checkpoint `5e00a76d83f1d0427add2132ec75beef3da6adf4`, path `docs/model-audit/workload-correction/architecture-investigation/joint-opportunity`. Run the preserved restore scripts in targeted-repair, roster-opportunity, full-workload-scenario, historical-coverage-retrain and starter-severity-intercept. Each verifies chunk/archive hashes before restoring. No completed research is refitted. `Reproduction_Manifest.json` records input SHA256 hashes and exact source paths; `Frozen_Category_Parameters.json` records the retained scale.

Deliverables: `Current_Comparison.csv`, `Current_Lines.json.gz`, `Historical_Player_Comparisons.csv`, `Historical_Lines.json.gz`, `Historical_Metrics.csv`, `Aggregate_Ratios.csv`, `Representative_Examples.csv`, `Largest_Changes.csv`, unsupported-case tables, protocol, gates, coverage and verification. Historical `production` is the preserved forecast-date V2.3 chronological baseline, not a claim of contemporaneous live website snapshots. Saved benchmark counts are compared separately wherever the same complete category case exists.
