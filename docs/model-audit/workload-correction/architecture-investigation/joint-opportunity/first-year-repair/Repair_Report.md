# First-year repair: implemented, partially improved, not release-ready

Continue from9b411d231e895fb43dd99906158c564ec8879766 on `review/capacity-opportunity-attrition-20261009`. Four bounded engineering iterations were implemented before new benchmark selection/scoring. Production is unchanged. The repair is incomplete: the original-starter gate fails and high-RBI signed bias remains too high.

## Implemented change

The first iteration predicts unconditional starts/relief appearances and hitterPA, including zero-outcome seasons. The second adds regularized cohort interactions for capacity, recent workload, age, stability and interrupted seasons. The third tests fixed equal-weight ensembles. Those revisions fail development starter stability; their code/results are retained. The fourth changes loss/factorization: robust directIP, active-conditionalIP and shrunk conditional cohort specialists. Development selects active-conditional opportunity for currentSP and robust directPA for H. The stronger existing principal-RP model remains the RP expert.

Capacity is evidence, not guaranteedMLB opportunity. Role/absence probabilities are explicit. Conditional opportunity is reconciled to bounded state components; innings retain starts/relief/depth accounting. H forecasts become an exact regular/part-time/absent mixture rather than an inconsistent separately fitted active-hurdle total. No extra workload aging or attrition multiplier follows the replacement forecast. A universal zero-baseline handling correction prevents positive predictedIP from disappearing in stat scaling. Inherited-state QA3 scaling was corrected for valuation. A full weighted-category replay also found an inherited leverage inconsistency (up to2.22HLD): SV/HLD caps now apply inside the conditional opportunity mixture, so reported mean categories equal state-weighted counts without creating leverage opportunities. No named-player patch or workload floor is used.

`FirstYearForecastEngine` is callable and replayed against8 named players. Fit artifacts and scripts reproduce all experiments. New expert fits use IDs1/2/3 only and completed targets through the anchor. Current fits end at2025; current input features use the2026 snapshot, forecasting2027. ID4 chooses architectures before ID0 scoring. These benchmarks were previously exposed; this is retrospective safety evidence, not independent confirmation. Inherited category-rate/aging normalizers remain comparison inputs, not newly certified talent models.

## Accuracy and gates

| Benchmark | Strong preserved comparison | Revised | Result |
|---|---:|---:|---|
| Expanded1084 pitching IP MAE | Direct linear25.92; joint26.05 | 26.00 | Within predeclared0.5 tolerance |
| Expanded288 currentSP IP MAE | Direct linear46.38; joint46.54 | 46.35 | Pass |
| Original94 IP MAE | Joint23.00 | 23.67 | Within1.0 tolerance |
| Original27 currentSP IP MAE | Joint35.88 | 38.23 | **Fail**; maximum36.88 |
| Young111 currentSP IP MAE | Joint41.91 | 43.12 | Within1.5 tolerance |
| Stable rotation87 IP MAE | Joint51.86 | 48.31 | Improve3.54 |
| Combined1215 H PA MAE | Joint116.08 | 111.73 | Improve4.36 |
| Preserved682 H PA MAE | Prior workload129.81; joint132.06 | 127.33 | Improve2.48 versus strongest |
| Durable24 H PA MAE | Joint94.97 | 84.13 | Improve; small cohort |
| Interrupted188 H PA MAE | Joint135.59 | 126.34 | Improve; paired interval overlaps0 |
| Comparable high-RBI62 RBI MAE | Production20.70; joint20.82 | 20.50 | Small improvement |
| Comparable high-RBI62 signed bias | Production−9.92; joint+0.37 | +4.53 | **Fail**; magnitude maximum3 |

Player-cluster95% intervals for MAE change against joint: H combined−6.99 to−1.83PA; stable rotation−6.75 to−0.19IP; original27 starters−2.91 to+7.84IP. The original regression is uncertain but exceeds the predefined critical tolerance; aggregate gains do not waive it. Seasonal checks identify no >10% clearly positive paired regression. The broader64-case high-RBI definition has+3.09 bias; the earlier comparable62-case definition is also retained and controls the explicit continuity diagnostic. Both bias failures remain visible.

The robust rate expert uses verified individualRBI/PA, HR, TB, BB, R, H, age and tenure. Development gains only0.05RBI against a required0.2 and does not authorize replacement. Its retrospectively better testRBI MAE is not used to reverse that decision. Thus reported counting-stat changes come from workload repair. Frozen annual inputs lack historical batting order, team environment, baserunners and lineup continuity; the code records their absence instead of fabricating context. No Soto-specific uplift is applied.

## Current forecasts and value effects

These are **rejected-candidate outputs**, not recommended player projections.

| Player | Workload | Production | Revised | Production neutral | Revised neutral |
|---|---|---:|---:|---:|---:|
| Skenes | IP | 165.32 | 113.11 | 94.91 | 87.76 |
| Misiorowski | IP | 129.07 | 138.00 | 93.41 | 94.33 |
| McLean | IP | 120.13 | 123.38 | 42.90 | 42.62 |
| Wheeler | IP | 142.43 | 133.69 | 53.01 | 51.67 |
| Judge | PA | 469.41 | 253.08 | 71.40 | 60.43 |
| Ramírez | PA | 529.78 | 546.51 | 42.27 | 42.74 |
| Olson | PA | 600.55 | 661.14 | 32.88 | 33.58 |
| Soto | PA | 640.17 | 598.57 | 87.93 | 86.38 |
| Freeman | PA | 543.00 | 587.79 | 28.63 | 29.59 |

Soto's RBI becomes82.39 through598.57PA at the retained rate; Olson86.06, Judge39.44, Ramírez64.78. These outputs expose remaining failure rather than establish appropriate totals. Recent observed exposure and pooled conditional opportunity still suppress several demonstrated high-workload players. Modelled absence, opportunity reduction and rate aging are shown separately; only rate aging remains an inherited category multiplier.

All1900 supported MLB assets (841H/273SP/786RP) have complete before/after first-year counting-stat tables. All2546 entries have mode values and ranks;646 forecast/value entries remain frozen. Primary bounded first-year sensitivity changes mean neutral value by−0.56, median−0.38, maximum absolute10.97;1065 catalog entries trigger a >10-value or >50-rank review flag, including induced ranking movement. Conditional-state expected utility and future-role replacement are supplied separately. All1900 later utility paths are verified unchanged. All1900 supported forecast-stat mixtures are coherent;64 inherited valuation amplitudes need bounding, explicitly counted.

A selected public2026Steamer sample matches10 of11 names. Mean2027Pipeline gap is−29.49IP for production,−42.29 for prior joint and−37.64 for this revision. It is not the full original comparison and has unverified source revision dates. Arithmetic conditional-opportunity/absence/role terms reproduce each gap; forecast-year, age and injury causation cannot be identified from this cross-year sample. The gap remains a blocker, not validation or a numerical target.

## Remaining executable work

1. On development data, replace the single pooled currentSP active opportunity expert with a jointly regularized **role-conditioned** opportunity model using continuous demonstrated rotation stability rather than tenure-only cohort boundaries. Fit all future roles/zero outcomes, calibrate role and workload together, and require original-starter preservation in the predeclared confirmation design. The original27 failure table identifies affected cases without authorizing test-label tuning.
2. Audit full-season versus censored snapshot exposure using verified reporting dates; add observed exposure completeness to the availability model only when supported. Current Judge/Skenes outputs must not be repaired with player patches. Test capacity and recent-season weights on development interruption/young-transition cohorts.
3. Couple H counting-stat rate/opportunity calibration on development high producers. Acquire historically dated lineup/team/baserunner inputs before any context fit; reserve IDs/seasons not repeatedly exposed for confirmation. Preserve the rejected individual-rate results.
4. Obtain a dated completeSteamer export and matched independent2027 reference to distinguish population composition, forecast horizon and explicit injury information. The small indexed sample cannot support causal attribution.

`Engineering_Blockers.json` specifies model/data tasks and acceptance evidence. The candidate is **not ready for release review**; no numerical changes were deployed. This session delivers an implemented replacement framework, measurable H/stable-rotation gains, saved failures and reproducible artifacts, not a completed universal repair.
