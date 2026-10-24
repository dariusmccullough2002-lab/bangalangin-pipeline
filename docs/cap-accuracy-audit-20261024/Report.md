# Cap accuracy audit — October 24, 2026

## Result

The 0%, 10%, 20% and 30% candidates do not change any player projection. They only bound the departure of a strategy-adjusted asset value from its neutral price. No cap can be selected as a more accurate player forecaster from these tests.

Across all 2,546 catalog entries, projected components and all annual utility paths have the same SHA-256 fingerprint before and after all four candidate caps. The nonzero caps change 4,898 supported asset-mode values, but zero forecasts. There are 7,467 supported asset-mode values and 171 blocked asset-mode values across balanced/contender/rebuild; missing evidence is not assigned zero.

## Historical check actually available

The existing pitcher-case file has 1,084 records, targeting 2017–2019 and 2022–2025. Of these, 781 have finite baseline and actual components for IP, K and ER (241 SP, 540 RP). The remaining records are not imputed. This is a previously inspected inherited-forecast sample with positive target-season selection, not a fresh held-out test of the current production forecast or a test of zero-innings/injury outcomes.

| Valuation cap | Usable historical cases | IP MAE | K MAE | ER MAE | Player forecasts changed |
|---|---:|---:|---:|---:|---:|
| 0% | 781 | 29.6294 | 28.9830 | 14.0270 | 0 |
| 10% | 781 | 29.6294 | 28.9830 | 14.0270 | 0 |
| 20% | 781 | 29.6294 | 28.9830 | 14.0270 | 0 |
| 30% | 781 | 29.6294 | 28.9830 | 14.0270 | 0 |

The equality is expected: the cap is outside the forecast calculation. It is not evidence that the four trade-value policies are equally accurate, nor new validation of the forecast itself. The script also records RMSE, bias, role splits, later-period diagnostics and SV/HLD/QA3 where finite.

## What remains blocked

Historical valuation/policy accuracy cannot be measured with the current files:

- None of the historical pitcher records contains a dated neutral dynasty price or an eight-year annual contribution forecast.
- The 680 historical ranking snapshots are FanGraphs prospect rankings. They do not reconstruct contemporaneous overall-dynasty values and the active strategy production paths for MLB players.
- The current catalog forecasts 2027–2034 and was frozen after the 2026 season. Testing it against 2026 or older actual results would use future information and evaluate the wrong forecast year.
- Correlation between the current cap-adjusted value and older production would not repair this information leakage.

A valid test needs historical evaluation dates, the overall dynasty ranks/neutral values and full forecasts available on each date, followed by a defined outcome: next-season lineup/category benefit, two-season benefit, or subsequent market value. Those are different objectives and should be evaluated separately. Historical rosters would help lineup evaluation but cannot substitute for missing historical ranking and forecast vintages. Current roster uploads do not fix this gap.

Reconstructing a new historical forecaster from incomplete components would also change the forecasting method, confounding a test intended to isolate the caps. No retrospective 2026 ranks, invented historical prices, revised post-outcome forecasts or named-trade target answers are used.

## Decision and reproducibility

No cap selected or deployed. The 10% cap previously discussed is a conservative valuation preference, not an accuracy-validated winner. Previous synthetic-package results measure preservation of the ranking-led neutral anchor and sensitivity; they are not held-out forecast accuracy.

Run from repository root:

```
node scripts/audit-cap-forecast-accuracy.mjs
```

The script uses frozen repository files, records every input SHA-256, compares forecast fingerprints, recomputes saved-case errors and lists the missing data checks in Results.json. It needs no network and does not change production values. It is saved with the offline strategy-settings research for resumption.
