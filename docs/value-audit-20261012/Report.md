# BangaLangin Pipeline — valuation audit and review candidates

Base: `4607c1619458be18aa884a106eb1be2ac7bd13ee`. Audit date: October 12, 2026.

## Recommendation

Adopt the **10% spacing policy** after review. It removes broad isotonic plateaus without individual price overrides, keeps supplied prospect ranks dominant, and retains existing supported deviations and debut continuity. Keep contribution forecasts unchanged.

Treat the **overall-ranking extension as a review candidate**, not a proven model correction. It supplies the requested dominant overall anchor, but should not be adopted automatically: it materially moves elite starters, boosts some relievers despite weak league scarcity, has incomplete source coverage, and has no transaction-price calibration. Review these cohort effects and source vintage before choosing it.

No valuation changes have been deployed. The recovered actual model reproduces Bradish, Soriano and Keith exactly. No confirmed arithmetic or SP/RP routing defect explains those three values. A metadata correction now identifies the active estimator parameters separately from inherited career diagnostics; it changes neither forecasts nor fundamental values.

## Recovery and production status

Remote `main` was fetched and points to `4607c16`. The live Trade Analyzer HTML is byte-identical to that commit's local HTML (`Live_Verification.json`). Earlier release commits `975ab6e`, `ce326ae`, `f0388d8` and `2f2b392` are ancestors. The prior workspaces and untracked research were left intact; this work uses an isolated branch.

This verifies Git and live release state. It does **not** establish whether the other conversation is still actively executing; no cross-conversation running-task monitor is available.

## Before and after

| Player | Deployed | Spacing only | Overall extension |
|---|---:|---:|---:|
| Kyle Bradish | 10.529154 | 10.529154 | 24.567273 |
| Jose Soriano | 11.347823 | 11.347823 | 20.497113 |
| Colt Keith | 24.136977 | 24.136977 | 14.682165 |
| Ramon Marquez | 20.144739 | 20.131313 | 14.893662 |
| Taitn Gray | 20.144739 | 20.111665 | 14.682769 |
| Franklin Primera | 20.144739 | 20.102118 | 14.676756 |
| Emmanuel Rodriguez | 20.144739 | 20.028340 | 14.587068 |
| Ethan Holliday | 20.144739 | 20.039940 | 14.623808 |

All figures are internal trade-value points. Six decimals here support reproducibility; the interface can retain ordinary rounded displays. These are valuation policy outputs, not empirically established market prices.

## 1. Prospect spacing correction

The original fixed decreasing isotonic curve pools conflicting source-rank/fundamental pairs into identical values. The fix uses **90% of that fixed pooled curve plus 10% of a positive decreasing power curve fitted across its rank domain**. The power component is normalized to preserve the mean across the original 500-point curve. This imposes a modest ordinal-distance prior rather than player-specific prices or tiny uniqueness epsilons. Both components decrease, so the resulting curve declines strictly. Linear interpolation is continuous; source tiers do not trigger extra value jumps.

The 10% choice is the smallest predeclared sensitivity examined (10%, 20%, 30%). It is a conservative policy judgment, not a parameter selected from transaction outcomes. The biggest change is Sebastian Walcott, **54.2757 → 57.4834 (+3.2077)**. This upper-tail effect must be reviewed even though aggregate value barely changes.

The existing effective ranks, evidence strengths, source weights and adjacent-tier deviation bounds stay fixed for all 265 players. Rodriguez's effective rank remains **80.4082116**; unlike the old plateau, the new curve responds to that supported deviation. Debut metadata never refits the curve or removes source membership.

- Exact tie groups: **16 → 0** among the 265 affected prospects.
- One-decimal tie groups: **16 → 28**. Previously distinct plateau groups fan out into several rounded groups; this increase does not mean more exact plateaus. `Tie_Diagnostics.json` separately reports exact values and distinct values within each rounded group.
- Sum of affected prospect values: **4712.239422304 → 4712.013752428**, a **-0.225669876** change.
- Every rank-curve interval declines; there are no remaining flat curve sections. No attempt is made to make every rounded display unique.
- All tier boundaries and adjacent-rank changes appear in `Tier_Boundaries.csv`. Tier bounds can still saturate supported deviations; that is a disclosed rank-deviation policy, not a price discontinuity.

| Largest spacing changes | Before | After | Change |
|---|---:|---:|---:|
| Sebastian Walcott | 54.2757 | 57.4834 | +3.2077 |
| Jesus Made | 53.1740 | 54.6537 | +1.4796 |
| Josuar Gonzalez | 38.0242 | 38.6317 | +0.6075 |
| Josue De Paula | 51.6122 | 52.1596 | +0.5474 |
| Josh Adamczewski | 29.9544 | 29.5141 | -0.4404 |
| Angel Genao | 29.9544 | 29.5144 | -0.4400 |
| Arjun Nimmala | 29.9544 | 29.5405 | -0.4139 |
| Zyhir Hope | 29.9544 | 29.5681 | -0.3863 |
| Bryce Rainer | 25.8509 | 25.5180 | -0.3330 |
| Kaelen Culpepper | 25.8509 | 25.5316 | -0.3193 |

The five reported tied players now separate modestly: Marquez 20.1313, Gray 20.1117, Primera 20.1021, Rodriguez 20.0283, Holliday 20.0399. Rodriguez's supported negative adjustment places him below Holliday. Their displayed values may still round together.

## 2. Actual production pitcher audit

### Identity, coverage and roles

José Soriano is Fantrax **04c0o**, MLBAM **667755**, linked through the preserved crosswalk and career profile. Kyle Bradish is **04pq4 / 680694**; Colt Keith is **05jrh / 690993**. Source-table team labels are snapshots and are not used to override stable identity. No ambiguous name-only match is used.

The values here are the current verified *website snapshot* values. The 2026 inputs are the preserved Fantrax regular-season export; 2022–2025 inputs are the cached official MLB records. They are not newly fetched 2026 statistics. Historical QA3 counts use the preserved game-level calculation, not conventional quality starts.

| Bradish season | Routed role | IP | Appearances | Starts | QA3 |
|---|---|---:|---:|---:|---:|
| 2022 | SP | 117.666667 | 23 | 23 | 9 |
| 2023 | SP | 168.666667 | 30 | 30 | 19 |
| 2024 | SP | 39.333333 | 8 | 8 | 5 |
| 2025 | SP | 32.000000 | 6 | 6 | 4 |
| 2026 | SP | 155.000000 | 29.0 | 29.0 | 16.0 |

| Soriano season | Routed role | IP | Appearances | Starts | QA3 |
|---|---|---:|---:|---:|---:|
| 2023 | RP | 42.000000 | 38 | 0 | 0 |
| 2024 | SP | 113.000000 | 22 | 20 | 11 |
| 2025 | SP | 169.000000 | 31 | 31 | 17 |
| 2026 | SP | 177.333333 | 32.0 | 32.0 | 15.0 |

All listed seasons have positive observed innings. Bradish has no missing post-debut calendar year within this series. Soriano's 2023 relief season is preserved but excluded from the current SP rate/workload fit. His 2024–2026 start shares support the SP route. A short relief debut never independently establishes a permanent bullpen role.

**Zero/missing limitation:** SV/HLD zeros are zeros in the preserved normalized records; absent years and absent component keys are recorded separately. The inherited normalization uses `.get(field, 0)` in places, so raw-field presence cannot be independently proven for every historical zero from these normalized artifacts. This audit does not relabel an absent record as a verified zero or silently repair forecasts without original evidence. Both pitchers' positive-season IP, GP and GS are supported; their tiny smoothed SV/HLD contributions are not material to the discrepancy.

### Talent versus workload

The active recent estimator uses weights 0.1/0.2/0.3/0.4 for 2023–2026, renormalized across positive matching-role seasons. The rate pseudocount is **30 IP** for pitchers, **100 PA** for hitters. Rate shrinkage is not an extra subtraction from final value.

Bradish: recent weighted workload **96.333333 IP**, healthy top-two median **161.833333**, historical SP prior **171**, prior weight **1/7**. Base workload = `(6/7) × (0.7 × 96.333333 + 0.3 × 161.833333) + (1/7) × 171` = **123.842857 IP**. His 2024–2025 interrupted seasons therefore lower future baseline workload despite 155 observed 2026 IP. Projected rates are K/IP **0.961869**, ER/IP **0.412560**, BB/IP **0.378459**, H/IP **0.929719**, QA3/IP **0.106514**.

Soriano: matching SP seasons 2024–2026; recent workload **160.259259**, healthy median **173.166667**, prior **171**, prior weight **1/6**. Base workload **165.276235 IP**. Rates: K/IP **0.896406**, ER/IP **0.440265**, BB/IP **0.409212**, H/IP **0.900520**, QA3/IP **0.093210**. His low value is not mainly a very short projected baseline workload.

The first future cohort multiplier produces **101.751448 IP** for Bradish and **135.392894 IP** for Soriano. Their subsequent aging/attrition paths are substantially shorter than Keith's age-25 hitter path. Historical cohort support: Bradish 77 anchors/52 players; Soriano and all representative cohorts are recorded in `inputs/model-evidence.json`.

Yes, short/interrupted seasons enter long-term baseline capacity. That is a confirmed mechanism, but not by itself evidence that replacing them with a healthy ceiling improves forecasting. Starting workload already reflects recent availability; applying a generic future cohort can compound conservative availability assumptions. There is **no duplicated explicit injury haircut**, but calibration of that interaction remains unresolved. The model does not separately forecast cause-specific injury recovery or future role retention.

### Numerical value decomposition

Signed category score includes HR/R/RBI/SB/AVG impact/OPS impact for hitters; negative raw ER/K/SVH7/QA3/K-to-walk impact/WHIP impact for pitchers. The preserved SVH7 vector is `3×SV + 2×HLD`; the model uses raw earned runs, not ERA as an independent category. QA3 is at least 5 IP and at most 2 ER, **or** at least 6 IP and at most 3 ER. Ratios are exposure-weighted impacts relative to frozen references, not predicted head-to-head wins.

Replacement = role floor × exposure / role reference workload. Floors: H **4.614672**, SP **−0.348355**, RP **0.113167**; workloads: H **509 PA**, SP **171 IP**, RP **56.666667 IP**. A negative SP floor means the SP replacement deduction below is negative: it slightly **adds** surplus. It is not a large SP penalty. Floors are inherited historical structural proxies, not a newly validated estimate of this league's free-agent acquisition scarcity.

Value = **2.6501808806 × Σ (0.88^t × expected state utility)**, for 2027–2034. Utility truncates negative surplus at zero and retains the frozen convex upper tail. Three states carry 0.25/0.50/0.25 probabilities; utility is computed within states before averaging. Neutral risk-preference deduction, additional injury penalty and explicit role-retention penalty are **all zero**. Future cohort workload/rate multipliers already include historical loss and aging; no second external discount is applied.

| Bradish | IP | Gross score | Replacement deduction | Expected utility | Time discount | Value contribution |
|---|---:|---:|---:|---:|---:|---:|
| 2027 | 101.751448 | 1.356347 | -0.207285 | 1.563632 | 1.000000 | 4.143907 |
| 2028 | 85.992289 | 0.970626 | -0.175181 | 1.145807 | 0.880000 | 2.672203 |
| 2029 | 79.805631 | 0.755630 | -0.162577 | 0.918207 | 0.774400 | 1.884437 |
| 2030 | 53.481420 | 0.478435 | -0.108951 | 0.587385 | 0.681472 | 1.060832 |
| 2031 | 27.760186 | 0.090733 | -0.056552 | 0.147285 | 0.599695 | 0.234080 |
| 2032 | 16.379088 | 0.173174 | -0.033367 | 0.206541 | 0.527732 | 0.288865 |
| 2033 | 13.262823 | 0.086826 | -0.027019 | 0.113845 | 0.464404 | 0.140115 |
| 2034 | 7.486348 | 0.081433 | -0.015251 | 0.096684 | 0.408676 | 0.104715 |

Total **10.5291542146**.

| Soriano | IP | Gross score | Replacement deduction | Expected utility | Time discount | Value contribution |
|---|---:|---:|---:|---:|---:|---:|
| 2027 | 135.392894 | 1.169473 | -0.275818 | 1.445291 | 1.000000 | 3.830283 |
| 2028 | 105.755226 | 0.881441 | -0.215441 | 1.096882 | 0.880000 | 2.558104 |
| 2029 | 81.115971 | 0.565534 | -0.165247 | 0.730781 | 0.774400 | 1.499781 |
| 2030 | 67.970781 | 0.566428 | -0.138468 | 0.704896 | 0.681472 | 1.273058 |
| 2031 | 52.852022 | 0.305397 | -0.107668 | 0.413065 | 0.599695 | 0.656485 |
| 2032 | 45.292472 | 0.585709 | -0.092268 | 0.677977 | 0.527732 | 0.948209 |
| 2033 | 34.830231 | 0.204039 | -0.070955 | 0.274994 | 0.464404 | 0.338451 |
| 2034 | 28.355053 | 0.167017 | -0.057764 | 0.224781 | 0.408676 | 0.243452 |

Total **11.3478234055**.

| Keith | PA | Gross score | Replacement deduction | Expected utility | Time discount | Value contribution |
|---|---:|---:|---:|---:|---:|---:|
| 2027 | 525.779368 | 6.573222 | 4.766797 | 1.806425 | 1.000000 | 4.787354 |
| 2028 | 508.333246 | 6.941641 | 4.608627 | 2.333014 | 0.880000 | 5.440960 |
| 2029 | 464.423307 | 6.303489 | 4.210533 | 2.092956 | 0.774400 | 4.295373 |
| 2030 | 400.279345 | 5.704149 | 3.628994 | 2.075155 | 0.681472 | 3.747779 |
| 2031 | 368.863767 | 4.861135 | 3.344176 | 1.516959 | 0.599695 | 2.410904 |
| 2032 | 291.976214 | 3.623615 | 2.647101 | 0.976514 | 0.527732 | 1.365738 |
| 2033 | 259.099065 | 3.339841 | 2.349032 | 0.990809 | 0.464404 | 1.219443 |
| 2034 | 210.690423 | 2.712899 | 1.910152 | 0.802747 | 0.408676 | 0.869427 |

Total **24.1369769967**. Keith's long tail, rather than an overall ranking advantage, drives the deployed result. Annual category components and exact state paths for 14 representative players are included in `Annual_Decomposition.csv` and `inputs/model-evidence.json`: established starters, young/partial-season starters, relievers, mixed-role histories and hitters.

### Diagnostic workload sensitivities — not proposed forecast fixes

These counterfactuals hold rates, aging curves, state probabilities, utility, replacement and discounting fixed and change only initial workload. They show sensitivity; they are not evidence to promote a workload forecast.

| Player | Initial-workload assumption | Workload | Value |
|---|---|---:|---:|
| Kyle Bradish | recent_baseline | 123.8429 | 10.5292 |
| Kyle Bradish | latest_observed | 155.0000 | 13.1781 |
| Kyle Bradish | healthy_observed | 161.8333 | 13.7591 |
| Kyle Bradish | historical_role_reference | 171.0000 | 14.5385 |
| Jose Soriano | recent_baseline | 165.2762 | 11.3478 |
| Jose Soriano | latest_observed | 177.3333 | 12.1757 |
| Jose Soriano | healthy_observed | 173.1667 | 11.8896 |
| Jose Soriano | historical_role_reference | 171.0000 | 11.7408 |

### Confirmed metadata correction

The audit object inherited career-estimator fields such as 100-IP rate strength and exponential recency weights even when the active V2.3 recent estimator uses 30 IP and fixed season weights. Those fields are misleading when read as active inputs. The candidates add `active_forecast_inputs` for **1919** records with this estimator, while retaining the inherited career diagnostic separately. This is an explanatory metadata correction, with **zero forecast or price effects**. It does not claim all inherited fields were numerically applied twice.

## 3. Ranking coverage and proposed extension

The deployed registry covers listed prospects only. Bradish, Soriano and Keith are absent, so all three retain contribution-fundamental values. The same coverage boundary explains why the overall table has no direct effect on Soriano.

Overall source: recovered `Dynasty_Dugout_Overall.tsv`, 500 unique stable Fantrax IDs, received **2026-10-08**; publication date **not independently established**. Prospect source: the separately supplied 500-player prospect snapshot received **2026-10-12**; publication date unknown. These are distinct source scopes, not interchangeable ranks. The source filenames/tabs, dates, tiers, Fantrax and available MLBAM IDs appear in `Source_Registry.json`.

The extension fits an overall rank curve from **486 supported listed players' contribution fundamentals** on the existing display scale; existing ranking-led values are **excluded** from this fit. It blends the overall pooled curve with the same 10% fitted power spacing prior. Direct overall ranks take precedence when available. Prospect-only identities absent from the overall list use a disclosed monotone scope bridge fitted from **117 shared stable IDs** and evaluated on the **single overall value curve**. This is not overall rank = prospect rank, and not two summed value anchors.

MLB deviations use at most 25% evidence weight, scaled by career exposure, and are bounded to ±10% of source rank. Unsupported roles/samples retain the source-only anchor. Existing prospect talent deviations are retained with explicit scope translation; they do not use damaged short-season workload to erase prospect standing. Source weights remain greater than 50% for all supported identities. These are bounded policy choices, not historically fitted market-price coefficients.

- Direct overall coverage: **486**; absent catalog source rows: **14**, explicitly unsupported.
- Prospect-only bridged coverage: **162**; total candidate coverage: **648** assets.
- Other catalog assets retained unchanged: **1,898**; omission never means zero value.
- Final curves have no flat rank sections. Five exact asset-level ties remain because different supported deviations arrive at the same effective rank; no artificial separation is added. Full identities and rounded ties are in `Tie_Diagnostics.json`.
- Contribution forecasts and competitive-fit values remain untouched across all **2,546** assets. Pick values and Rounds 1–5 eligibility remain unchanged; Rounds 6–20 are never introduced as assets.

| Largest extension effects (relative to spacing candidate) | Deployed | Extension | Extension minus spacing |
|---|---:|---:|---:|
| Payton Tolle | 76.8050 | 45.5091 | -31.2959 |
| Paul Skenes | 94.9067 | 65.0988 | -29.8079 |
| Daylen Lile | 52.4261 | 24.6312 | -27.7949 |
| Sam Antonacci | 48.9292 | 24.9563 | -23.9729 |
| Cole Carrigg | 48.5458 | 24.5780 | -23.9678 |
| Samuel Basallo | 12.1674 | 35.7981 | +23.6308 |
| Braxton Ashcraft | 59.2660 | 35.6949 | -23.5711 |
| Logan Gilbert | 69.3203 | 45.8902 | -23.4301 |
| Pablo Lopez | 43.6497 | 21.0383 | -22.6113 |
| Bryan Woo | 67.4906 | 45.4764 | -22.0142 |

**League-context limit:** the inherited contribution engine uses common pitching-category dispersion, role-specific replacement proxies, no arbitrary RP penalty, and no scarcity premium. It preserves 35-IP weekly eligibility context and optional RP deployment, but does not independently quantify this league's replacement acquisition cost. Source-led reliever increases (for example Mason Montgomery) therefore remain material adoption concerns. Dominant overall rankings cannot be represented as validated league-specific market prices. Do not force hitter/pitcher equality or tune Bradish/Soriano/Keith individually.

## 4. Trade arithmetic and validation

`Prospects_All_265.csv` compares every affected prospect. `Population_Comparison.csv` supplies every candidate-covered identity. `Saved_Trade_Comparisons.json` recalculates every saved package. Representative packages:

| Package comparison | Deployed sides | Spacing sides | Extension sides |
|---|---|---|---|
| Kyle Bradish vs Colt Keith | 10.5292 / 24.1370 | 10.5292 / 24.1370 | 24.5673 / 14.6822 |
| Jose Soriano vs Colt Keith | 11.3478 / 24.1370 | 11.3478 / 24.1370 | 20.4971 / 14.6822 |
| Ramon Marquez + Taitn Gray + Franklin Primera vs Emmanuel Rodriguez + Ethan Holliday | 60.4342 / 40.2895 | 60.3451 / 40.0683 | 44.2532 / 29.2109 |
| Kyle Bradish + Jose Soriano vs Eury Perez | 21.8770 / 32.7334 | 21.8770 / 32.7334 | 45.0644 / 35.9326 |

All packages sum player/pick policy values directly. Neutral trade values are strategy-invariant. Competitive fit remains a separate forecast timing quantity, so changing a ranking anchor does not rewrite expected contribution or imply a trade is a guaranteed competitive improvement. Policy ranges are ±15% sensitivity envelopes, not confidence intervals.

No forecasting changes are promoted here, so no new forecast-accuracy claim is made. Previously inspected chronological evidence is preserved and labeled **development evidence**: recent-debut mean shifts had worse low-PA error; prior full-workload candidates failed forecast gates; the separate reliever opportunity candidate improved cached first-year checks but is not merged into this policy audit or described as independent new validation. No fresh historical data collection or recycled holdout certification occurs.

Regression checks cover production byte isolation, all 265 matches, curve monotonicity/continuity, 44 debuted identities, distinct source scopes/no stacking, bounded deviations, omitted identity retention, forecast/scenario separation, exact 14-player model reconstruction and routing, one cohort application/discount per annual path, active estimator metadata, and saved trade-package arithmetic. These tests establish implementation consistency, not calibration of ordinal ranks to actual transactions or future injury recovery. They do not resolve potential implicit availability conservatism.

## Preview and reproduction

Two review calculators reuse the deployed shell, AFL links, scenario displays, historical pitching-stat renderer and removal of doubles/triples columns:

- `/value-audit-preview/spacing/`: spacing-only prospect policy plus corrected explanatory metadata.
- `/value-audit-preview/overall/`: the proposed overall dynasty extension.

`/value-audit-preview/` provides a comparison table and quick additive trade comparison. Open the downloadable complete preview package by extracting it, running `python3 -m http.server 8080` in its folder, then opening `http://localhost:8080/value-audit-preview/`. Local calculators require serving rather than opening individual HTML files because they reuse root-relative deployed assets. The review table itself is self-contained.

Regenerate from committed frozen inputs: `python docs/value-audit-20261012/build_candidate.py`, then `python docs/value-audit-20261012/render_review.py`; run `npm test` and `npm run build`. Exact source model files and hashes are retained for inspection. `export_model_evidence.py <recovered-model-root>` reconstructs diagnostic evidence if the preserved model checkpoint is available; normal candidate regeneration requires only committed frozen evidence and source tables.

Browser interaction has not been verified in this session; the available managed environment lacks the required browser-control skill. Numerical/catalog regressions and the build verify the candidates, with that browser QA limit explicit. No production approval or deployment is implied by a successful preview build.
