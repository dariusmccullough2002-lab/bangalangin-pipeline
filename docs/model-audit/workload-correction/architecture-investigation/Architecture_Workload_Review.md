# V2.3C capacity, opportunity and attrition investigation — October 9, 2026

## Recommendation

Continue with a general expected-MLB-workload architecture conditioned on capacity, role, MLB-only ability and demonstrated durability. This investigation produced substantially stronger alternatives than replacing MLB workload with combined innings. The best pitching direction improves both preserved aggregate benchmarks, and the hitter model improves durable and ordinary cohorts. **Do not release numerical changes yet.** Conditional starting-pitcher workload, several QA3 subgroups, pandemic transitions, uncertainty and longer horizons remain insufficiently calibrated. Production numbers, the deployed header and V2.3B rollback are unchanged.

This is a continuation of cc80da73 on `review/debut-workload-role-20261009`, itself continuing the October 9 projection audit. Previous collected innings, historical cases, failed-candidate scores and all research are retained. New experiments live on `review/capacity-opportunity-attrition-20261009`; no application or production valuation file is changed.

## Completed evidence and remaining coverage

The existing universal ledger covers 1,287 pitching or secondary pitching-history assets, not just the three named diagnostics. It retains debut-year MLB innings, verified affiliated MiLB innings, combined workload and provenance separately. There are 1,190 verified affiliated debut-year queries: 959 have positive MiLB innings and 231 have no affiliated record in successfully queried sources. There are 958 combined-workload corrections with MLB evidence, 86 assets without a recorded MLB pitching debut, and 11 unresolved identities (all free agents). All 266 owned MLB-pitching assets have verified coverage. Minor-league-only prospects retain their evidence automatically; no fabricated zero replaces missing evidence.

Those are ledger counts, not a claim that 1,287 pitchers receive higher projections. Secondary eligibility/history and two-way streams are audited separately. Other professional leagues, independent assignments and some older career covariates remain incomplete. Affiliated innings provide verified capacity evidence, not guaranteed total career coverage or a medical health assessment. Existing individual-source crosschecks for Misiorowski, McLean and Smith agree with the deduplicated league data; completed collection was reused rather than repeated.

## Exact workload mechanism

The default estimator uses positive matching-role MLB seasons from 2023–2026, weights 0.1/0.2/0.3/0.4 renormalized to available observations, blends 70% recent workload and 30% median of the highest two workloads, then shrinks toward an early-population role prior. It applies an age/quality-conditioned cohort workload factor afterward. There is no additional explicit injury penalty in this path, and the first-year multiplier is not an eight-year factor accidentally applied to 2027.

Matt Olson's trace is exact:

| Stage | PA |
|---|---:|
| Weighted recent workload | 705.4000 |
| Healthy observed workload | 722.0000 |
| 70/30 blend | 710.3800 |
| Population prior shrinkage | −28.7686 |
| Forecast starting workload | 681.6114 |
| First-year cohort multiplier | 0.8810715172 |
| Cohort reduction | −81.0630 |
| Final frozen 2027 projection | 600.5484 |

The cap does not bind. His first-year cohort contains 113 anchors from 76 players, with total anchor workload 62,453.5 and next-year workload 55,026, including three zero-next-workload anchors. The 81.1 PA disappear in that single cohort ratio. The systemic concern is two population-level regressions insufficiently conditioned on demonstrated durability, rather than a proven duplicate medical penalty. The same architecture can conflate abbreviated MLB opportunity with workload capacity for promoted pitchers.

Misiorowski's 134.8133 starting IP receive factor 0.95736379, ending at 129.0654. McLean's 130.5333 receive 0.92027377, ending at 120.1264. Smith's 71.3858 receive 0.85487643, ending at 61.0260. These exact traces are in `Exact_Workload_Traces.json`.

## Alternative architecture and safeguards

The first fixed experiments compare ridge regression, direct mean-workload boosting, participation probability × conditional workload, a no-capacity ablation and bounded 2020 workload features. They learn expected MLB workload once rather than attaching the original cohort attrition multiplier again. Historical features include calendar seasons with zero opportunity, capacity history, debut timing, role usage, age and durable workload runs. MiLB performance never becomes MLB talent.

Follow-up exploratory models explicitly forecast absent/RP/SP assignment and conditional workload. The strongest adds existing regressed MLB-only K/ER/BB/H/QA3/SV/HLD evidence as role/opportunity predictors. Those talent estimates themselves remain unchanged. No names, manual increases or individual eligibility gates are used.

Training targets must be completed by each forecast date. Held-out ID%5=0 identities never enter fitting; development selection uses ID%5=4, with initial training on groups 1–3, and final fitting on groups 1–4. Hyperparameters were fixed before initial scoring. Role/quality follow-ups are clearly marked exploratory after failure inspection; previously exposed historical labels are not a pristine prospective test. Full protocols and date manifests are preserved.

All current sensitivities change first-year workload only. Years 2–8, prospect mixture atoms and weights remain frozen. MLB production categories scale with workload using unchanged rate and rate-aging inputs. QA3 remains **at least 5 IP with no more than 2 ER, OR at least 6 IP with no more than 3 ER**. Increased capacity creates no saves/holds: those totals are capped at baseline and reduced proportionally when expected innings fall. This consistency guard is not a replacement for closer/setup opportunity modeling. Two-way stream evidence is evaluated, while combined two-way valuation is retained pending overlap validation.

## Historical results

Errors below are mean absolute errors; lower is better. The expanded evaluation preserves the exact 1,084 pitcher cases (411 players). The expanded hitter evaluation has 682 cases (208 players).

| Evaluation | Frozen baseline | Primary workload model | Role + MLB-ability direction |
|---|---:|---:|---:|
| Pitcher IP, expanded 1,084 | 29.42 | 27.03 | **26.23** |
| Pitcher K, expanded | 28.06 | 26.03 | **25.33** |
| Pitcher QA3, expanded | 1.92 | 1.82 | **1.78** |
| SP IP, expanded 288 | 51.75 | 48.78 | **47.35** |
| RP IP, expanded 796 | 21.34 | 19.16 | **18.58** |
| Pitcher IP, preserved 94 | 24.97 | 25.96 | **23.77** |
| Pitcher K, preserved 94 | 23.29 | — | **22.55** |
| Pitcher QA3, preserved 94 | 1.67 | — | **1.65** |
| Hitter PA, 682 | 155.62 | **129.81** | not changed |
| Durable hitter PA, 18 cases / 10 players | 150.30 | **97.26** | not changed |
| Ordinary regular PA, 255 | 156.11 | **138.22** | not changed |
| Repeated observed shortfall PA, 391 | 153.84 | **119.75** | not changed |
| Age 33+ hitter PA, 106 | 151.21 | **110.84** | not changed |

Hitter overall signed bias improves from +13.25 to −10.79 PA; durable bias from −97.09 to −23.31. Repeated observed shortfall is a workload proxy, not an injury diagnosis. An additional verified prior MLB injured-list subset has only 45 hitter, five starter and one reliever cases: hitter PA MAE improves 162.63→157.90 and SP IP 35.58→29.22, but the single RP worsens. It cannot certify clinical or league-wide injury safety.

Player-cluster bootstrap 95% intervals for MAE change: all hitters −32.29 to −19.34 PA; durable hitters −71.01 to −32.94 PA; all quality-aware pitchers −4.24 to −2.19 IP; SP −7.71 to −1.13 IP. These preserve repeated seasons per player, but are exploratory and not multiplicity-adjusted prospective confirmation.

Important weaknesses remain. In the 94-case set RP K error slightly worsens 18.60→18.76 and RP QA3 0.70→0.77; first-season QA3 1.46→1.49 and swingman QA3 3.21→3.24 also worsen. Actual next-season starters in the expanded set barely improve (51.07→50.79 IP), and the corresponding 22 older cases worsen 32.81→35.53. Much of the aggregate gain comes from forecasting nonparticipation more accurately: 303 absent-next-season cases improve 28.89→19.49 IP. That is useful but does not demonstrate improved conditional forecasts for established young starters.

The clean MiLB ablation retains debut MLB evidence and removes only MiLB capacity. Starter aggregate IP error is 49.24 with capacity versus 49.04 without; first-season SP improves 43.21→41.69 with capacity, but second-season SP remains worse than baseline. Verified historical capacity is correct data regardless of whether its present integration improves every metric. Earlier direct substitution failed because professional capacity was translated too directly into future MLB opportunity. Simple attenuation retained that mismatch and lacked explicit participation, role and durable opportunity conditioning.

The older 94 baseline is preserved literally, including its inherited full-source preprocessing. The expanded benchmark uses past-only preprocessing. Do not mistake them for byte-identical baseline construction. All alternative IP/K/ER/BB/H/QA3 errors and biases are saved in the validation JSON files.

## Comprehensive 2020 findings

`Pipeline_2020_Audit.json` maps 15 pipeline components, with source locations/hashes and active versus diagnostic/legacy status.

* Current 2027 recent workload uses 2023–2026. The role prior uses 2010–2012. The first-year aging anchors are 2011–2017 with outcomes 2012–2018. Thus 2020 does not explain Olson's 2027 reduction.
* Current cohort annualization scales 2020 counting workloads once by 162/60 where it appears at later horizons. Career-rate exposure remains actual MLB evidence, appropriately avoiding fabricated talent sample size.
* Role caps annualize 2020. H raw/normalized caps are 681.88/682, SP 219/219.67, RP 75.67/76.67; Olson's cap is nonbinding.
* Historical recent-workload estimators can consume raw 2020 totals, even when aging diagnostics have annualization. Legacy aging paths also contain raw shortened totals; they do not drive current MLB first-year projections.
* Experimental training on raw 2020 targets worsens hitter MAE to 137.45 versus 131.22 for the comparable exclusion-based hurdle model. Historical schedule-aware target/feature treatment improves it to 129.92, but pitching improvements are mixed. Do not normalize actual MLB talent evidence or all realized fantasy production globally.
* Prospect empirical career outcomes contain actual 2020 production. Rewriting those distributions is a separate unvalidated intervention; those paths remain untouched.

Additional chronological tests were scored without selecting models on their results:

| Forecast cohort | Baseline raw | Bounded baseline | Primary | Schedule-aware |
|---|---:|---:|---:|---:|
| 2020→2021 H PA, 86 | 168.21 | 162.36 | 183.05 | **152.02** |
| 2020→2021 SP IP, 38 | 58.10 | 52.25 | **51.13** | 51.13 |
| 2020→2021 RP IP, 108 | 20.79 | 20.23 | **19.85** | 19.85 |
| 2015 cold-start H PA, 108 | 148.44 | same | **127.33** | 127.33 |
| 2015 cold-start SP IP, 36 | **63.97** | same | 65.99 | 65.99 |
| 2015 cold-start RP IP, 86 | 21.04 | same | **17.33** | 17.33 |

The primary hitter candidate catastrophically underprojects 2021 after raw shortened-season features (bias −124.59 PA). The schedule-aware version reduces that to −16.40. This is a genuine historical release gate: a default model must recognize schedule exposure consistently, not just in an aging plot. Pitcher 2021 signed biases remain −29.49 SP / −10.94 RP despite improved absolute error; normalization is not sufficient alone.

## Current diagnostics — experimental, not deployed

These are the strongest architectural direction: primary hurdle hitter + role/MLB-ability pitcher. They are comparisons, not individualized endorsements.

| Player | Baseline PA/IP | Candidate PA/IP | Baseline K / HR | Candidate K / HR | Baseline QA3 | Candidate QA3 | Neutral baseline → candidate |
|---|---:|---:|---:|---:|---:|---:|---:|
| Matt Olson | 600.55 PA | 628.66 PA | 26.55 HR | 27.79 HR | — | — | 32.88→33.38 |
| Jacob Misiorowski | 129.07 IP | **104.62 IP** | 166.21 K | 134.73 K | 16.01 | 12.98 | 93.41→89.23 |
| Nolan McLean | 120.13 IP | **116.99 IP** | 124.69 K | 121.43 K | 15.06 | 14.67 | 42.90→42.63 |
| Cade Smith | 61.03 IP | 63.68 IP | 76.83 K | 80.17 K | 0.0294 | 0.0307 | 39.23→39.48 |

Olson's contender fit changes to 39.34, balanced/neutral 33.38 and rebuild 30.72; the full table contains baseline and candidate fit for every strategy. His adjustment is learned, not a manual 700-PA target. Smith retains 15.81 saves / 9.17 holds: more innings do not manufacture closing opportunities. His role forecast still needs separate leverage validation.

Misiorowski and McLean have high predicted starter probabilities (~0.944 and ~0.951), yet the conditional workload model produces conservative means. Wheeler and Skenes similarly receive large reductions. These counterintuitive examples expose the next failure mechanism: a model can predict role/absence better but still regress conditional MLB workload too strongly. Verified debut MiLB capacity is included; it does not automatically increase their final forecasts. No hidden selection of the most favorable candidate is used. The five initial candidate alternatives and two role-aware follow-ups retain their own current outputs.

`Strongest_Direction_Material_Impact.csv` covers every material change (10 PA, 1 IP or 1 neutral point), with player, public fantasy organization, age, role, verified debut workloads, categories, neutral value and four strategy fit scores. `Opportunity_Current_Impact.json.gz` provides all five initial alternatives for every modeled asset, with baseline categories/value/fit; separate role/quality files contain follow-ups. Island is displayed publicly while internal ownership identity stays untouched. No acquisition-market price, scouting bonus or replacement-scarcity premium is introduced.

## Integrity and unfinished release gates

All 2,546 assets are accounted for: 1,900 evaluated current assets and 646 unchanged assets. The catalog SHA256 remains `aadad4dc7763510da7eba928aae5018af1bc48cfacd8b5f510ca5f5cd0995235`; baseline neutral-value reproduction error is zero. Identities, ownership, picks, saved calculations, future years, prospect paths, MLB-only rates and exact QA3 are preserved. Assertions check hitter component coherence, proportional pitcher counts, no leverage creation, fitted-target dates and exact historical case identities. No production or UI regression build is needed because this commit modifies only research documents/data/scripts.

Remaining limitations: small durable and injury subsets; older MLB covariate censoring (historical stream starts in 2010 while current careers can be longer); missing non-affiliated professional evidence; incomplete role/QA3 opportunities; unresolved first-MLB-activity boundary; uncalibrated acquisition prices; first-year-only sensitivities and unrecalibrated forecast distributions. The current saved player/ownership data are not guaranteed live Fantrax information.

## Specific next experiments

1. Calibrate **conditional SP workload** among verified established/promotion cohorts, using capacity as a bounded prior rather than a direct replacement, with explicit MLB opportunity and participation kept separate. Compare shrinkage strength and calibration bins for high recent workloads; do not select a rule by Misiorowski's result.
2. Fit next-season starts, relief appearances and expected innings per start jointly, then calculate QA3 from the league's exact thresholds. This addresses role assignment/depth and the residual subgroup QA3 failures without changing MLB talent rates.
3. Make schedule exposure an explicit common feature with a missing/uncertain availability state. Validate the special 2020→2021 transition before allowing a generic fitter to process shortened seasons. Keep actual outcomes and talent samples untouched.
4. Extend pre-2010 historical covariates from the existing career source, verify as-of provenance, and rerun affected veteran/cold-start subsets only. Do not recollect already verified debut innings.
5. Reserve a subsequent untouched chronological cohort for confirmation; calibrate uncertainty and years 2–8 before claiming dynasty improvement. Complete two-way workload overlap checks and leverage opportunity modeling separately.

This is a defensible improvement in general forecasting architecture with measurable historical progress. It is not yet a release-approved valuation engine.
