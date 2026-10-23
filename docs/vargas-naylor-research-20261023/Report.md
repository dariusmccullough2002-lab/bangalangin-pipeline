# Vargas and Naylor: underlying-trend research

October 23, 2026. Research only; no production valuation changes.

## Finding

The concern is supported: Vargas's recent power and overall offensive-quality indicators are substantially stronger than Naylor's. His improvement also has a visible swing-speed mechanism. The current forecast retains a large historical batting-average advantage for Naylor and heavily regresses Vargas's power. That is a model assumption requiring validation, not an established conclusion that Naylor is the better contender asset.

Naylor's decline is not universal: his contact and strikeout indicators improved, he retained a batting-average advantage and stole 30 bases. More importantly, the Mariners reported wrist surgery after the season and expected spring-training recovery. A recovery scenario has a factual basis; the probability and size of the resulting power rebound remain unknown. Poor expected power while injured does not establish permanently diminished healthy talent.

## Source comparison

Fresh public Kodo player responses reconcile with Savant's 2026 xBA, xSLG, xwOBA, exit velocity, barrels, hard-hit rate, strikeout and walk rates. Both Kodo statistical rows are dated October 1. Kodo lists Savant among its upstream sources: agreement is reconciliation within one evidence family, not two independent votes.

| Indicator | Vargas 2025 → 2026 | Naylor 2025 → 2026 |
|---|---:|---:|
| Expected AVG | .237 → .263 | .267 → .269 |
| Expected SLG | .407 → .496 | .432 → .381 |
| Expected wOBA | .319 → .378 | .332 → .310 |
| Barrel rate | 9.4% → 13.0% | 6.7% → 4.4% |
| Hard-hit rate | 40.5% → 43.8% | 41.9% → 35.6% |
| Average exit velocity | 89.7 → 90.1 mph | 89.2 → 87.0 mph |
| Walk rate | 9.8% → 14.3% | 7.9% → 6.9% |
| Strikeout rate | 17.6% → 17.9% | 13.7% → 12.2% |
| Chase rate | 21.5% → 20.9% | 37.1% → 37.8% |
| Whiff rate | 20.6% → 21.0% | 22.1% → 16.9% |

Savant's year-to-year comparison puts Vargas's bat speed at 70.6 → 73.9 mph. Kodo's full-2026 swing summary independently reconciles to approximately 73.91 mph across 1,096 competitive swings. That supports a real change in his power mechanism. His walk rate improved while his strikeout/whiff rates stayed broadly stable.

Naylor's Kodo monthly samples show average bat speed about 69.98 mph in April and 69.51 in September, while attack angle moved from about 11.58° to 3.21°. These observations establish changing contact geometry, not its cause. They do not diagnose injury effects or prove recovery. Kodo health fields were null/UNKNOWN and `on_il` was false; those fields miss the subsequently documented surgery and cannot establish full health.

## What the category test says

I normalized both players to **600 PA** to remove an opportunity advantage. The same frozen league category normalizers and replacement rule were used. A second set preserves each player's inherited forecast PA. Picks, ownership and lineups do not enter this diagnostic.

| Equal-600-PA scenario | Vargas category surplus | Naylor category surplus |
|---|---:|---:|
| Inherited projection | 2.937 | 3.850 |
| 2026 observed rates repeated | 6.782 | 1.251 |
| 2026 rates, substituting xBA/xSLG | 7.648 | 2.052 |

These are **underlying category-surplus units**, not trade-price points, expected category wins or a 2027 forecast. The expected-quality scenario substitutes expected H and TB, retains the same season's actual HR/R/RBI/SB/walk rates, and enforces coherent counts. It does not infer HR from xSLG. Actual future workload and run/RBI context can differ.

The latest-evidence sensitivity clearly favors Vargas despite Naylor's steals. That establishes why the forecast deserves scrutiny; repeating the latest season is not a validated prediction. The adjusted live forecast still projects roughly .235 AVG for Vargas versus .265 for Naylor, whereas their 2026 xBA difference is only .006. The historical average advantage is therefore a major assumption behind the remaining contender ordering.

## Held-out testing beyond these two players

Protocol was frozen before the completed backtest. Complete official annual hitter components were joined to Savant expected-stat exports by MLBAM/year. The fixed four-year estimator uses nominal .1/.2/.3/.4 season weights and the original-style 100-PA prior from qualified 2010–2012 hitters. This tests talent rates **before cohort aging and workload**.

Vargas and Naylor were excluded from training and evaluation. There were **934 training player-seasons** (2019–2023 targets, excluding shortened 2020) and **775 held-out player-seasons across 381 players** (2024–2026 targets). Eligibility requires at least 150 PA in the latest observed season and at least 250 PA in the next season.

Fixed quality weights 0%, 10%, 25%, 50%, 75% and 100% were compared. Effective weight is shrunk by latest PA/(latest PA+100). A single 25% weight was selected using training AVG/SLG MAE relative to the training baseline. It was not chosen from held-out results or either named player.

| Held-out error | Four-year estimator | Training-selected 25% blend | Reduction |
|---|---:|---:|---:|
| AVG mean absolute error | .021498 | .020777 | 3.36% |
| SLG mean absolute error | .046866 | .046366 | 1.07% |

The nominal 10% blend had AVG MAE .021161 and SLG MAE .046591. Thus 25% improved only modestly on the existing family-weight concept: about 1.82% in AVG and 0.48% in SLG. This is a rate-model comparison, not validation of the live scalar contribution bridge or its cap.

Paired player-cluster bootstrap intervals for selected-minus-baseline MAE were [-.000957, -.000489] for AVG and [-.001071, +.000068] for SLG. The AVG improvement was more stable; the SLG interval crossed zero. These intervals describe this retrospective sample only.

The predeclared breakout group (last-year xSLG rose at least .050, at least 200 PA in both observed years) contained **90 held-out player-seasons**. The 25% blend made SLG MAE worse: .047817 → .052129, about **9.0% worse**, and increased positive bias. The decline group had **95 player-seasons** and improved SLG MAE .051720 → .049188, about **4.9% better**. Automatically extrapolating every breakout is not supported by this test.

Join exclusions were eight prior-season discrepancies (five PA, three rates), reported in `Backtest.json`; 905 otherwise-eligible observations lacked a >=250-PA next season and are excluded. That latter restriction creates survivorship selection. Historical expected stats were downloaded retrospectively, not from archived publication-day vintages. No claim of a fully prospective or injury-conditioned test is made.

## Model implications

1. Keep neutral dynasty prices anchored to dynasty rankings, as requested. This research provides no reason to replace those prices with category-surplus sums.
2. Treat the present Naylor-over-Vargas contender ordering as assumption-sensitive. Vargas's recent power improvement is supported, and expected batting average does not support anything close to the full .030 gap in the current forecast.
3. A modest shared quality blend has useful held-out AVG evidence, but a larger blanket breakout bonus fails the subgroup check. Rebuilding the shared rate forecast is preferable to enlarging the current percentage adjustment until a named comparison flips.
4. Distinguish sustained skill change from injury-limited performance. Naylor needs explicit continued-low-power and recovery scenarios; neither a permanent decline penalty nor a certain full rebound is justified. Calibrated recovery probabilities require additional historical injury evidence.
5. Validate HR/R/RBI/SB, availability and full annual utility paths before claiming an end-to-end trade-value improvement. xBA/xSLG alone do not establish those components.

## Reproduce and resume

Python standard library only; network downloads use curl. Frozen inputs are included.

```sh
python fetch_sources.py   # only downloads missing public inputs
python analyze.py        # runs offline from the frozen inputs
```

`freeze_model.py` extracts the two baseline rows and scale constants from the repository when producing a new research snapshot; the supplied frozen copies make that extraction unnecessary for rerunning this bundle. `Backtest_Cases.json` retains every eligible case and prediction. `Category_Scenarios.json` retains all rate/weight scenarios. `Profiles.json`, `Source_Manifest.json`, `Model_Manifest.json` and `Checks.json` preserve identities, dates, hashes, source comparisons and blocked work. All 67 data/consistency checks passed after the final complete-data run; these are implementation checks, not 67 proofs of predictive accuracy.

The requested research is complete. No production model was changed in this research turn. The next substantive step is a separately validated shared rate forecast with injury/recovery scenarios and component-level outcomes.

## Sources

- [Vargas Baseball Savant profile](https://baseballsavant.mlb.com/savant-player/miguel-vargas-678246)
- [Naylor Baseball Savant profile](https://baseballsavant.mlb.com/savant-player/josh-naylor-647304)
- [Savant expected-stat leaderboard and methodology](https://baseballsavant.mlb.com/leaderboard/expected_statistics)
- [Vargas Kodo player endpoint](https://kodoanalytics.com/api/v1/players/678246)
- [Naylor Kodo player endpoint](https://kodoanalytics.com/api/v1/players/647304)
- [Kodo source/methodology description](https://kodoanalytics.com/about)
- [MLB, October 5: wrist procedure and expected spring-training availability](https://www.mlb.com/news/cal-raleigh-josh-naylor-undergo-offseason-surgeries)
- [MLB, October 7: Naylor's season and injury context](https://www.mlb.com/news/josh-naylor-dealt-with-injuries-amid-2026-offensive-struggles-for-mariners)
- Official MLB annual-component URLs and complete response counts are preserved in `Source_Manifest.json`.
