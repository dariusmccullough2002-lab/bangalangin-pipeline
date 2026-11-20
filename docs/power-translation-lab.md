# Power Translation Lab — research preview V1

Route: `#power-translation-lab`; Resources/Explore menu. This module is read-only and isolated from ranking, grade and profile source-of-truth logic.

The displayed model reproduces `plus_barrel` from the November 20 study: standardized additive logistic regression, C selected on 2022–2023 log loss, refitted through 2023. Test AUC 0.9136807817589576 on 409 qualified 2024–2026 hitter-seasons. It is a same-season ISO/wOBA classifier, not a prospect forecast. No MLBAM identities are joined by ambiguous names; Dodgers Max Muncy is 571970.

## Reproduce

With Python, numpy, pandas, scipy and scikit-learn installed:

```
python scripts/build-power-translation.py
node --test tests/power-translation.test.js
```

The exporter verifies the unchanged official source CSV hash, reproduces the prior holdout AUC, serializes coefficients/scaling, and constructs supported conditional slices. No fitting happens in the browser. Raw source and metadata are downloadable. The source is a fixed snapshot, not an automatic-refresh feed.

## Interpretation

Risk coordinate: mean of standardized Chase and Whiff. This is a display projection only. Y is Hard-Hit; point size encodes Barrel. The frontier fixes Barrel and sets Chase and Whiff to equal z-scores. Its 50% line is conditional and cannot define the probability of arbitrary plotted players; individual displayed probabilities use all four actual metrics.

Sparse regions are blank under a documented four-dimensional convex-hull/local-neighbor guard. The guard and 25/75 bands are not calibrated uncertainty estimates. Probabilities are suppressed for under-qualified players and outside support. Both met-endpoint and not-met-endpoint neighbors are retained, with four nearest seasons per group. Neighbors are metric similarity, not career comparisons. No rejected compensation formula is implemented.

The minor view contains 178 non-debuted November board hitters in the coverage audit, zero qualified lab records, and no scores, estimated metrics or raw MLB-equivalent overlays. This records an ingestion gap, not universal unavailability of tracking data. A proper source-reviewed MiLB panel and age/level/league/park/competition translation remain future research.

## Validation

Five automated tests cover identity/duplicate/missing-data guards, endpoint parity, browser/Python AUC parity, supported-grid shape, component-sort immutability, same-name identities, probability suppression and both nearest-neighbor groups. Browser checks cover benchmark selection, historical search, coverage search, and mobile page-width containment. Only new research assets plus app routing, navigation and the deployment allowlist are changed.
