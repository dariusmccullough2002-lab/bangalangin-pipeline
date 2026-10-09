# V2.3C recovery continuation and conditional starter experiments

## Recommendation

Keep numerical changes offline. The interrupted session saved substantially more work than its last progress message: the role/MLB-ability candidate improves both aggregate pitcher benchmarks, the universal affiliated debut ledger is complete for all owned MLB-pitching assets, and the pandemic and current-value audits are saved. This continuation adds three general conditional-SP experiments, additional chronological transition scores, and current sensitivities for 1,059 pitchers. None consistently clears the remaining starter and schedule gates. No numerical candidate is accepted for release.

## Recovery and preservation

Recovered checkpoint: `2710377f77f570bb2f11b2002e8471662272732c` on `review/capacity-opportunity-attrition-20261009`, continuing `cc80da73` and `485d0f27`. The repository's main head was `ca15ab54`, and its deployed header correction is `d757773e`. No application, production, header, or other website file was edited.

The checkpoint contains 369 audit artifacts. This session materialized and verified 365 against their exact Git blob hashes, including cached sources, historical cases, protocols, scripts, failed experiments, and superseded outputs. Four artifacts exceed the connected file reader's content limit and remain preserved at their exact Git blob SHAs in the existing checkpoint: the two large primary current-impact archives and two large material-impact CSVs. Empty transfer placeholders were removed. This is a local retrieval limitation, not loss or deletion of checkpoint work. The recovery manifest names all four. The smaller quality-aware current-impact archive was verified and reused directly for the new current comparisons.

The original `BangaLangin_V23C_Verified_Recovery_Package.zip` was recovered and unpacked. Its embedded catalog reproduces SHA256 `aadad4dc7763510da7eba928aae5018af1bc48cfacd8b5f510ca5f5cd0995235`. The preserved training code loaded 7,504 hitter, 3,727 SP and 10,338 RP training records. Completed collection and prior experiment fitting were not rerun. New fits use the recovered training helpers and cached source evidence.

## Results saved before the interruption

| Evaluation | Frozen baseline | Initial selected model | Role + MLB-ability model |
|---|---:|---:|---:|
| Pitcher IP MAE, 1,084 cases | 29.42 | 27.03 | 26.23 |
| Original 94 pitcher IP MAE | 24.97 | 25.96 | 23.77 |
| Original 94 current-SP IP MAE | 39.10 | 45.06 | 36.94 |
| Expanded current-SP IP MAE | 51.75 | 48.78 | 47.35 |
| Hitter PA MAE, 682 cases | 155.62 | 129.81 | unchanged |
| Durable hitter PA MAE, 18 cases | 150.30 | 97.26 | unchanged |

Thus the initial model's failure in the 94 cases was already partially addressed by the saved role/MLB-ability model. It was not a reason to discard all prior research. The remaining distinction is important: pitchers classified as SP at the forecast date improve, while pitchers observed to be SP next season still have weak conditional workload forecasts.

## Universal debut evidence

The preserved ledger audits 1,287 pitching or secondary-pitching assets. It retains MLB innings, affiliated MiLB innings, combined workload, component roles, and source provenance separately. It has 1,190 verified affiliated debut queries: 959 positive and 231 verified no-recorded-affiliated cases. There are 958 combined-workload corrections. All 266 owned MLB-pitching assets have verified affiliated coverage.

The universal request is not fully finished across every identity: 11 free-agent identities remain unresolved, and 86 assets lack a recorded MLB pitching debut. These remain explicit missing/ambiguous states. Foreign and independent professional workload coverage is incomplete. No missing record was converted into a fabricated zero, and no player-specific override was introduced. This continuation reused the ledger rather than collecting the same debut innings again. Ambiguous Fantrax identities require independent disambiguation before adding career records; matching a familiar name alone is insufficient.

## New fixed conditional-SP experiments

All three variants retain the existing absent/RP/SP classifier and frozen MLB-only performance rates. They change conditional workloads or caps only. Names never enter fitting.

1. **Future-role caps:** bound each role's conditional innings by that future role's historical cap, rather than bounding the entire mixture by the current role's cap. This tests the RP-to-SP clipping mechanism separately.
2. **Linear SP:** replace only the SP conditional regression with standardized ridge regression, alpha 100, using the existing workload, capacity, role, age, and MLB-rate features. RP conditional regression remains unchanged.
3. **Pooled linear SP:** use the same ridge model, pooling training records from both current roles among observed future starters. This tests whether more transition evidence helps the conditional workload fit.

Development selection uses the preserved ID-modulo-4 group and anchors 2016–2018, 2021–2022, while fitting excludes modulo groups 0 and 4. The fixed objective averages role-normalized MAE plus one-quarter absolute bias. Among these new alternatives it selects future-role caps, not either linear model. This selection is not an endorsement over the prior incumbent, which was not included in this three-way selection. The selected alternative slightly worsens the incumbent's aggregate test error. The incumbent is retained for research comparison; no new model is accepted.

Test identities and all 1,084 cases are preserved. Final historical fitting excludes ID-modulo-0 test identities and requires training outcome year no later than the forecast anchor. Future role is a training target and scoring label, never a feature known at prediction time. Previously exposed outcomes make these exploratory tests, not pristine prospective confirmation.

| IP MAE | Baseline | Saved role/ability | Future-role caps | Linear SP | Pooled linear SP |
|---|---:|---:|---:|---:|---:|
| Expanded all, 1,084 | 29.42 | 26.23 | 26.27 | 25.92 | 25.93 |
| Expanded current SP, 288 | 51.75 | 47.35 | 47.36 | 46.38 | 46.33 |
| Expanded current RP, 796 | 21.34 | 18.58 | 18.64 | 18.52 | 18.55 |
| Expanded observed next-season SP, 219 | 51.07 | 50.79 | 50.75 | 49.39 | 49.60 |
| Expanded first MLB season, 253 | 24.24 | 22.11 | 22.19 | 21.95 | 22.17 |
| Expanded second MLB season, 159 | 26.53 | 24.96 | 24.96 | 24.13 | 24.15 |
| Original 94 all | 24.97 | 23.77 | 23.91 | 23.77 | 24.17 |
| Original 94 current SP | 39.10 | 36.94 | 36.94 | 37.55 | 38.09 |
| Original 94 observed next-season SP, 22 | 32.81 | 35.53 | 35.37 | 34.98 | 36.11 |

Full K/QA3 errors, signed biases, RMSE, date manifests, and subgroup results are in `Conditional_SP_Validation.json`. Per-case forecasts are preserved separately. The original 94 baseline retains inherited full-source preprocessing; the expanded baseline uses past-only preprocessing. They are not claimed to be identical baseline constructions.

## Why a blanket starter increase remains inappropriate

The saved role/ability model underprojects observed next-season starters by 22.77 IP on average. However, the 111 cases with forecast starter probability at least 0.8 have mean predicted starter probability 0.927 versus observed frequency 0.865, and expected innings bias +7.79 IP. The linear-SP variant increases this group's bias to +8.67 IP. Conversely, the 777 cases with probability below 0.2 have predicted starter frequency 0.017 versus observed 0.037.

These are complementary calibration problems. Conditioning evaluation on realized survival/role exposes workload shortfalls but does not justify removing absence probability from expected production. The role classifier overstates some high-confidence assignments and misses some low-probability transitions. Conditional workload flexibility helps selected cohorts, but neither a global increase nor a global shrinkage reduction solves both. Probability calibration and conditional workload calibration must be evaluated together, using forecast-date cohorts and completed historical training targets.

## Pandemic and cold-start follow-up

No model was selected on these extra anchors. The preserved 2020→2021 hitter schedule-aware result remains 152.02 PA MAE versus 168.21 baseline and 183.05 raw-feature primary. Olson's specific reduction still has no COVID cause.

| SP IP MAE | Baseline | Earlier primary | Future-role caps | Linear SP | Pooled linear SP |
|---|---:|---:|---:|---:|---:|
| 2015 cold-start, 36 | 63.97 | 65.99 | 68.70 | 64.50 | 63.89 |
| 2020→2021, 38 | 58.10 | 51.13 | 52.82 | 52.00 | 52.62 |

New 2021 SP biases remain −30.93, −31.56 and −34.18 IP respectively. All three beat the raw baseline in MAE, but each loses to the earlier primary and retains substantial underprojection. Their RP cold-start and 2021 errors improve, while RP 2021 bias remains approximately −11.8 IP. This does not establish a universally calibrated schedule-aware engine.

## Current projections and dynasty sensitivities

New current comparisons cover the same 1,059 quality-aware pitchers. The complete outputs include all three alternatives, baseline, prior quality-aware candidate, neutral value, and every competitive-fit mode. The CSV has 3,055 material method/player rows using the existing threshold of at least 1 IP or 1 neutral-value point. No aggregate gain was used to hide unfavorable individual outcomes.

| Diagnostic | Baseline IP | Saved role/ability IP | Linear-SP IP | Linear-SP neutral |
|---|---:|---:|---:|---:|
| Misiorowski | 129.07 | 104.62 | 159.53 | 98.83 |
| McLean | 120.13 | 116.99 | 149.32 | 45.41 |
| Skenes | 165.32 | 120.52 | 154.79 | 93.46 |
| Wheeler | 142.43 | 104.37 | 155.26 | 54.79 |
| Cade Smith | 61.03 | 63.68 | 63.69 | 39.48 |

These are general-model diagnostics, not player overrides or recommended production values. The large changes demonstrate material model uncertainty despite modest aggregate MAE differences. The earlier hitter candidate still projects Olson at 628.66 PA versus 600.55 baseline, neutral 33.38 versus 32.88. Its durable subset remains small, and no new hitter fit was necessary to recover the already completed 682-case and schedule tests.

Current sensitivities change year one only. Years 2–8 and prospect distributions remain preserved. No additional cohort attrition multiplier is attached to the direct expected-workload prediction. Pitcher counting categories retain frozen MLB rates; more innings never creates saves/holds, while less innings scales those opportunities down. Exact QA3 remains unchanged. Assertions verify baseline reproduction, proportional counts, no added leverage, all 1,084 historical cases, all 1,059 current pitcher comparisons, and training target dates. These checks do not certify eight-year distributions or market prices.

## Remaining work

* Independently resolve the 11 free-agent identities and complete relevant non-affiliated professional evidence before claiming literally universal verified coverage.
* Calibrate role/absence probabilities jointly with conditional starter workload, preserving failed alternatives and using development-only decisions. Reserve untouched chronological confirmation before release.
* Forecast starts, relief appearances, and innings per start to address the remaining exact-QA3 subgroup weaknesses. No new joint appearance model was completed here.
* Consolidate schedule handling into shared training features and test a broader set of veteran and promotion transitions. The new starter alternatives still fail a robust pandemic-bias gate.
* Extend verified pre-2010 covariates for affected veterans, calibrate uncertainty and years 2–8, and finish two-way overlap and leverage opportunity validation.
* Current dynasty deltas are first-year sensitivities, not validated multi-year trade economics. No production projection or valuation deployment is authorized or performed.

The requested recovery and additional experiments are saved. The numerical audit remains open with specific failed gates, rather than being represented as complete or release-ready.
