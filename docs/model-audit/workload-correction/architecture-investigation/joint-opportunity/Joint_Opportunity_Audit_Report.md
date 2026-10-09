# BangaLangin V2.3C: recovered joint-opportunity audit

The interrupted research was recovered and continued from `8c7df81d6b3fb45905c826aade9919a73aac7ae2` on `review/capacity-opportunity-attrition-20261009`. The original 1,084 pitching and 682 hitter cases, their exact baseline predictions, source caches, failed experiments, and earlier results are retained. All changes in this checkpoint are additive research files. No production projection, valuation, UI, header or website file is changed.

The new joint approach improves the original starter benchmark, durability diagnostics and the 2020 schedule test. It does **not** dominate the strongest prior experiments across all cohorts/categories. Full dynasty valuation remains an offline sensitivity, with material ranking effects and incomplete uncertainty propagation. **No numerical release is recommended yet.**

## Recovery and reproducibility

The recovered parent preserved 441 prior blobs and added twelve continuation artifacts. Recovery verified 365 of 369 original audit artifacts locally; four files larger than the content-download limit remained intact on GitHub rather than being replaced. Source training/game/model helpers came from the verified recovery package. The catalog SHA256 remains `aadad4dc7763510da7eba928aae5018af1bc48cfacd8b5f510ca5f5cd0995235`. The final tree comparison verifies every parent blob is retained unchanged, including the deployed header correction (`d757773e`) and unrelated website files. Main was `ca15ab54d31e6b8f19c782d1b5185d8aed57bda0` at recovery.

Saved fitted models avoid repeating completed fits. Large model/case/impact artifacts are stored in recoverable pieces listed in `Recovery_Manifest.json`; run `python restore_artifacts.py` after downloading this directory. Pieces have byte counts and SHA256/Git blob checks. Research uses the existing preserved model root and extracted catalog as the two positional arguments; no site build or deployment is needed.

## Model and chronology

Pitching now models absent/RP/SP probabilities, starts and relief appearances conditional on principal role, pure-role IP per appearance, and exact QA3 expectations separately. Verified debut/current MiLB starting shares and raw combined MLB+MiLB workload are evidence features. Physical capacity is not converted into guaranteed MLB opportunity. Expected innings are the probability-weighted sum of starts × starting depth and relief appearances × relief depth. Future role, GP/GS and workload are labels only. Historical age and known forecast horizon are inputs; no names, arbitrary bonuses or player targets enter fitting.

The development-only selector chose joint linear starting depth. A fixed principal-role QA3 amendment addresses the initial model applying pure-starter QA3 rates to sporadic starts/openers in relief-dominant seasons. A fixed 50/50 blend with direct conditional workload was tested separately. These follow-ups were specified after exposed retrospective diagnostics and are exploratory; they were not selected as deployment winners using test labels. Mixed-role innings and QA3 splits are not directly verified: the principal-role QA3 relief offset is an aggregate modeling assumption. Rare relief QA3 is learned, not hardcoded to zero.

A final chronology audit found inherited full-history MLB ability priors in the initial joint features and an H calendar flag sourced from pitching-debut mapping. Both initial results are preserved. The `Past_Only_*` follow-up replaces ability priors with non-holdout records completed by each feature anchor and uses the observed hitter stream for its debut flag. All new workload/role fits exclude MLBAM-ID remainder 0 and targets after the anchor; current multi-horizon training explicitly stops at completed 2025 outcomes rather than treating unavailable 2026 targets as absence. Frozen baseline category priors, rate aging and utility normalizers retain their original provenance for comparison. They are not newly validated chronological talent/category baselines.

Identity remainder 4 supplies development outcomes and past-only calibration. It is longitudinal development, not independent identity confirmation. Historical test identities were never fitted, but their outcomes and earlier preprocessing choices have been examined. Results are retrospective chronological tests; no pristine confirmation claim is made. `PROSPECTIVE_CONFIRMATION.md` specifies the future completed-2027 gate.

## Pitching: preserved benchmarks

| IP MAE cohort | n | Baseline | Prior linear-SP | Past-only joint | Fixed blend |
| --- | --- | --- | --- | --- | --- |
| Expanded all | 1084 | 29.42 | 25.92 | 26.05 | 25.87 |
| Expanded current SP | 288 | 51.75 | 46.38 | 46.54 | 46.12 |
| Expanded current RP | 796 | 21.34 | 18.52 | 18.64 | 18.55 |
| Expanded first MLB | 253 | 24.24 | 21.95 | 21.13 | 21.18 |
| Expanded second MLB | 159 | 26.53 | 24.13 | 24.87 | 24.62 |
| Frozen 94 all | 94 | 24.97 | 23.77 | 23.00 | 23.47 |
| Frozen 94 SP | 27 | 39.10 | 37.55 | 35.88 | 36.99 |
| Frozen 94 RP | 67 | 19.28 | 18.22 | 17.81 | 18.03 |
| Frozen 94 second MLB | 28 | 21.20 | 19.39 | 19.94 | 20.37 |

The original first candidate improved expanded MAE from 29.42 to 27.03 but still regressed starters in the original benchmark. The expanded set is dominated by 796 RP cases versus 288 SP; aggregate improvement can conceal a starter problem. The later direct linear-SP sensitivity reached 25.92 expanded MAE. The new past-only count×depth architecture reaches 26.05 expanded, 23.00 frozen 94 and 35.88 frozen-SP. It improves the frozen starter gate while slightly losing to the prior linear-SP direction across the expanded set (46.54 vs 46.38 SP). Second-season forecasting still favors the prior linear-SP sensitivity in the expanded set (24.13 vs 24.87).

Expanded past-only IP bias is -2.51 and RMSE 36.74, versus baseline bias 1.82 and RMSE 38.80. It beats baseline IP MAE in each of the seven preserved anchor seasons, but not the prior direction in every season. The paired player-cluster bootstrap MAE delta versus prior linear-SP is +0.13, 95% interval [-0.46,+0.73]. This is not evidence of a decisive improvement over that prior direction.

Role transitions explain remaining underprediction. The prior/new forecasts overpredict SP→absent and SP→RP, and underpredict continuing starters and RP→SP. A larger physical-workload total alone does not determine starts. For current Skenes, the past-only model gives 93.8% SP probability but only 23.7 conditional starts, producing 132.86 expected IP despite 187.67 demonstrated raw capacity. For Misiorowski, 97.5% SP probability and 21.2 conditional starts produce 124.50 IP from 174.67 raw capacity. These are general-model outputs, not individual adjustments: conditional start counts remain too regressive for some established/high-opportunity examples. The fixed blend lifts these estimates but weakens the original starter benchmark. A blanket starter uplift would not fix transition/absence bias.

Calibration improved the high-confidence SP bin: initial raw mean 90.85%, observed 85.47% over 117 cases; the final past-only calibrated bin mean 89.42%, observed 90.80% over 87 cases. Final multiclass Brier=.3871 and logloss=.6395. Bin membership changes with the model, so these are calibration diagnostics rather than paired proof. Full bins and transition MAE/bias are in `Diagnostics.json`.

| Expanded category | Baseline MAE | Prior linear-SP MAE | Past-only MAE | Past-only bias |
| --- | --- | --- | --- | --- |
| K | 28.063 | 24.997 | 25.128 | -2.934 |
| QA3 | 1.917 | 1.765 | 1.783 | -0.208 |
| ER | 13.980 | 12.346 | 12.468 | -2.081 |
| BB | 10.852 | 9.531 | 9.500 | -1.222 |
| H | 27.843 | 24.479 | 24.660 | -2.669 |
| SV | 1.966 | 1.704 | 1.719 | 0.035 |
| HLD | 3.251 | 2.910 | 2.906 | -0.664 |

Exact QA3 uses game outs/ER: at least 5 IP with≤2 ER OR at least 6 IP with≤3 ER. It is not quality starts, starts alone, ERA/IP-derived QA3 or rate-scaled synthetic target labels. The principal-role amendment improves frozen-SP QA3 MAE 4.073→3.362 and expanded-SP 5.868→5.113. Expanded RP QA3 remains worse: baseline 0.487, prior 0.485, new 0.578. That category gate fails. Save/hold counts never increase from extra workload. K/ER/BB/H/SV/HLD and hitter talent rates remain frozen per-opportunity rates for this workload audit; role-specific talent and leverage deployment are unfinished.

## Verified MiLB usage and universal capacity

The league/catalog ledger retains 1,287 pitching streams:1,190 verified affiliated-debut queries,959 positive MiLB results,231 no recorded affiliated workload,958 combined-workload corrections,86 no recorded MLB pitching debut and 11 unresolved identities. All 266 owned MLB pitching assets were already covered by verified debut evidence. The correction is universal and evidence-based, with no Misiorowski exception. Verified missing coverage is distinct from observed zero.

| Fixed 2018/2021/2024 ablation | n | With MiLB role MAE | Without MiLB role MAE |
| --- | --- | --- | --- |
| all | 501 | 24.946 | 25.202 |
| SP | 130 | 45.383 | 46.553 |
| RP | 371 | 17.785 | 17.721 |
| first_MLB_season | 120 | 17.973 | 18.039 |
| young_SP | 50 | 44.960 | 45.642 |

Only the two verified MiLB starting-share features were removed; physical capacity, MLB roles and ability features were retained. Aggregate and SP MAE favor MiLB usage; RP does not. Young-SP predictions remain worse than baseline in this diagnostic. This is limited retrospective evidence that minor usage helps opportunity, not proof that every young pitcher should receive more innings. The ablation retains initial frozen-prior feature provenance and is not a new pristine confirmation test.

All 86 no-debut cases have cached affiliated workload;81 are SP,3 RP and 2 H/two-way eligibility. Their predebut capacity is retained separately, without inventing an MLB debut season. The 11 ambiguous provider links remain withheld. Nine have a single age-compatible candidate, Trevor Martin has two, and Yunior Marte has a material age conflict. Snapshot teams, exact cached candidate DOBs, MLB/MiLB years and the unresolved rationale are saved in `Coverage_Followup.json`. Age/team/name resemblance is insufficient to establish a stable provider identity.

The existing GitHub international-professionals research also contained 12 official-source native-league pitching snapshots for 2026. Their innings, appearance counts, sources and correct baseball-decimal conversion are preserved in `Foreign_Workload_Evidence.json`. None has a verified identity match to the current 2,546-asset catalog (six match the broader old crosswalk outside that catalog). They therefore do not alter league projections. Their 2026 records cannot supply older NPB/KBO debut-season workload for Olson/Ohtani or other historical cases. Foreign professional history and college/independent overlap remain incomplete; zero affiliated records is not zero total professional capacity.

## Hitters and schedule normalization

| PA cohort | cases | players | Baseline MAE | Prior candidate MAE | Past-only calendar MAE | New bias |
| --- | --- | --- | --- | --- | --- | --- |
| Preserved all | 682 | 208 | 155.62 | 129.81 | 132.06 | -6.27 |
| Preserved durable 4 years | 18 | 10 | 150.30 | 97.26 | 93.57 | -20.26 |
| Preserved age 33+ | 106 | 52 | 151.21 | 110.84 | 113.99 | -8.24 |
| Extended ordinary-season all | 1215 | 263 | 165.29 | 116.53 | 116.08 | 0.04 |
| Extended durable 4 years | 24 | 12 | 146.19 | 110.41 | 94.97 | -24.82 |
| Extended age 33+ | 255 | 95 | 178.69 | 77.98 | 81.27 | 7.54 |
| Extended returning missed season | 223 | 154 | 200.87 | 31.83 | 37.04 | 1.51 |
| Extended young first full opportunity | 197 | 114 | 166.82 | 153.21 | 154.84 | -17.48 |

The new hitter selector chose calendar hurdle on development data. It improves baseline, durability and aggregate extended bias, but is worse than the prior candidate on the original 682-case aggregate, aging, returning and young first-full-opportunity cohorts. The extension adds 533 ordinary-season cases to make 1,215;117 unexpected 2019→2020 shortened targets are reported separately, never silently pooled to claim ordinary-season gains. Returning after a missed recorded season is not automatically returning from medical IL.

The documented prior-IL diagnostic has 57 cases and 7 players. PA MAE: baseline 160.76, prior 167.67, past-only 168.35. The injury/availability gate fails. The cached nine-player IL sources are not comprehensive enough for an individualized medical forecast. No extra injury multiplier was added.

On the extended ordinary-season set, PA MAE 165.29→116.08 and bias 46.54→0.04; RMSE 190.67→157.21. Category MAE also improves baseline, but not every prior-category score: HR4.650 prior vs 4.653 new, SB2.721 prior vs 2.830 new. Better workload bias does not establish uniformly better fantasy-category forecasting.

Matt Olson's original 681.6 PA starting workload and 0.88107 first-year cohort multiplier yield 600.55 PA. No second injury penalty or multi-year attrition multiplier explains that first-year reduction. That cohort uses 2012–2018 outcomes, so COVID did not cause his specific reduction. The prior workload candidate gives 628.66 PA; the past-only calendar model gives 639.42 PA, conditional active 645.24 PA and absent probability 0.90%. It replaces the old workload attrition with modeled participation and conditional workload; it does not apply another cohort workload penalty. This does not prove every durable hitter is fixed: Freeman and Ramírez remain lower than baseline, and Judge falls 469.41→402.96 PA. Those outputs and the failed IL/aging gates are retained.

| Schedule cohort | Method | n | MAE | Bias | RMSE |
| --- | --- | --- | --- | --- | --- |
| H_anchor_2020 | baseline | 86 | 168.21 | -18.88 | 200.35 |
| H_anchor_2020 | selected | 86 | 183.05 | -124.59 | 226.47 |
| H_anchor_2020 | past_only | 86 | 143.77 | 19.84 | 181.54 |
| H_anchor_2019 | baseline | 101 | 232.52 | 232.52 | 254.39 |
| H_anchor_2019 | selected | 101 | 207.54 | 204.40 | 249.60 |
| H_anchor_2019 | past_only | 101 | 208.43 | 206.33 | 249.40 |
| P_anchor_2020 | baseline | 146 | 30.50 | -8.41 | 39.03 |
| P_anchor_2020 | joint_selected | 146 | 29.08 | -20.17 | 40.82 |
| P_anchor_2020 | joint_calendar | 146 | 26.60 | -10.83 | 36.43 |

For the same 86 positive 2020-anchor hitters, PA MAE is 168.21 baseline,183.05 prior raw candidate,152.02 earlier bounded candidate and 143.77 new calendar/past-only. New bias+19.84 remains material. Calendar capacity/workload features normalize 2020 by 162/60, while actual talent rates and raw demonstrated professional capacity are not annualized. Completed 2020 targets can be used with confidence weight 60/162; future 2020 shortened outcomes are not retrospectively assumed known at 2019 prediction time. Positive 2020-anchor pitching favors the calendar sensitivity 26.60 vsbaseline 30.50 and initial raw joint 29.08; however the calendar pitching variant did not win the development objective. There is no test-selected pandemic-only production switch.

## Horizons, values and remaining gates

| Role | Horizon | n | As-of cohort reference MAE | Past-only pooled model MAE | New bias |
| --- | --- | --- | --- | --- | --- |
| H | 2 | 289 | 175.30 | 143.37 | 5.14 |
| H | 3 | 196 | 166.84 | 146.41 | 17.98 |
| H | 4 | 196 | 171.75 | 138.12 | 26.90 |
| H | 5 | 101 | 163.90 | 137.49 | 23.23 |
| H | 6 | 101 | 153.31 | 133.99 | 24.28 |
| SP | 2 | 134 | 55.87 | 50.56 | -6.73 |
| SP | 3 | 89 | 57.58 | 52.62 | -10.68 |
| SP | 4 | 89 | 50.44 | 44.45 | -6.57 |
| SP | 5 | 42 | 56.35 | 47.71 | -5.47 |
| SP | 6 | 42 | 45.39 | 41.23 | -2.98 |
| RP | 2 | 370 | 22.07 | 19.94 | -3.70 |
| RP | 3 | 252 | 19.77 | 17.62 | -4.34 |
| RP | 4 | 252 | 19.27 | 16.93 | -4.67 |
| RP | 5 | 107 | 20.77 | 19.67 | -6.43 |
| RP | 6 | 107 | 19.76 | 17.63 | -7.15 |

These fixed pooled-horizon fits use chronological anchors 2019/2021/2023 and completed targets through 2025. They are new comparisons to an as-of cohort reference, not a byte-identical saved multi-year baseline. At 2019 there are 803 pitching horizon 6 training rows and zero horizon 7/8 rows. Current fits can train on completed 2013–2025 pairs at horizons 7/8, but no corresponding past-anchor forecast can both train and be scored through 2025 at those horizons. Years 7/8 therefore lack chronological validation. Role/workload attrition is learned directly by horizon; the old cohort workload multiplier is replaced once, while frozen rate aging remains.

The full sensitivity accounts for all 2546 assets:841 H,273 SP and 786 RP supported MLB projections;645 picks/prospects/unresolved or unsupported assets andone two-way combined valuation remain unchanged. Baseline value recomputation matches exactly. Both frozen full-prior and corrected past-only sensitivity outputs are saved. In the past-only principal case, median neutral change=-1.13, mean=-1.76, maximum absolute change=28.00;1141 supported assets move by more thanone value point.

| Diagnostic player | Work | Baseline year 1 | Prior year 1 direction | Joint year 1 | Blend year 1 | Neutral eight-year value | Neutral rank |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Matt Olson | PA | 600.55 | 628.66 | 639.42 | 639.42 | 32.88 → 38.07 | 123 → 76 |
| Freddie Freeman | PA | 543.00 | 513.53 | 537.38 | 537.38 | 28.63 → 26.07 | 159 → 184 |
| Jose Ramirez | PA | 529.78 | 510.91 | 508.65 | 508.65 | 42.27 → 33.19 | 72 → 113 |
| Aaron Judge | PA | 469.41 | 287.43 | 402.96 | 402.96 | 71.40 → 43.39 | 16 → 56 |
| Jacob Misiorowski | IP | 129.07 | 159.53 | 124.50 | 147.11 | 93.41 → 102.41 | 7 → 3 |
| Nolan McLean | IP | 120.13 | 149.32 | 117.96 | 135.30 | 42.90 → 42.98 | 66 → 59 |
| Paul Skenes | IP | 165.32 | 154.79 | 132.86 | 145.67 | 94.91 → 79.27 | 5 → 9 |
| Zack Wheeler | IP | 142.43 | 155.26 | 110.47 | 133.29 | 53.01 → 62.62 | 39 → 19 |
| Cade Smith | IP | 61.03 | 63.69 | 61.59 | 60.33 | 39.23 → 39.08 | 84 → 70 |

The prior pitching comparison here is the linear-SP sensitivity, not the earlier development-selected future_role_caps. H uses its earlier development-selected candidate. New first-year means use the separate one-year model; years 2–8 use the pooled-horizon model. Values pass the resulting eight-year stats through the preserved surplus, nonlinear utility, discounting and competitive-fit evaluator. Strategy-specific competitive fit is saved separately for all existing modes. Rates, leverage growth guard, prospects, mixture weights and existing MLB low/base/high state amplitudes remain frozen. Category/count coherence passed 40,368 H state checks and 101,664 leverage checks. No injury or attrition factor is applied twice.

**The valuation uncertainty gate fails.** The new absent/RP/SP mixture is collapsed into a yearly mean, then evaluated inside inherited contribution-state paths. It is not a calibrated, correlated joint role/availability path distribution across eight years. Missing mixtures, two-way overlap and horizon 7/8 extrapolation can drive large future-value/rank changes; for example the blend puts Misiorowski first by the existing neutral evaluator. This is a disclosed model sensitivity, not a ranking recommendation or a player-specific target. Paired historical bootstrap diagnostics quantify MAE differences, not dynasty-value intervals.

Remaining work: obtain independently verified provider links for 11 unresolved identities; add calendar-verified historical foreign/independent capacity where available; improve continuing-SP and RP→SP starts without increasing absence/transition bias; resolve RP QA3 without treating mixed innings as verified component data; develop comprehensive prior-IL and durable-player opportunity forecasts; implement and validate correlated role/availability/category paths and two-way overlap; score untouched prospective outcomes and longer horizons. No proposed numerical projection or value change is deployed or approved by this checkpoint.

## Saved evidence

`PROTOCOL.md`, `PROTOCOL_AMENDMENT.md`, `Development_Selection.json`, `Hitter_Development.json`; initial joint/principal/past-only case and validation files; `Minor_Role_Ablation*`; `Diagnostics.json`; `Prior_IL_Followup.json`; `Coverage_Followup.json`; `Foreign_Workload_Evidence.json`; both original and past-only horizon files; `League_Impact*` and `Past_Only_League_Impact*` (all asset/year/category/component/value/rank details); all fitted model files; source scripts; `Integrity.json`; `PROSPECTIVE_CONFIRMATION.md`; and the piece/hash recovery manifest. Earlier experiments remain at their original paths and commits.

