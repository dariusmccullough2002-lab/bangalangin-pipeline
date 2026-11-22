# Contact versus damage — broad-coverage research view

Snapshot: November 21, 2026. This view compares observed Whiff% against directly reported ISO. It requires neither exit velocity nor invented Hard-Hit/Barrel values. The existing Statcast view and Pipeline rankings/grades remain separate.

## What the chart means

X is Whiff% (misses per swing). Y is ISO (SLG minus AVG, equivalent to extra bases per at-bat). The four quadrants compare these rates with fixed 2021–2022 development means. ISO already includes strikeout at-bats; adding K or Whiff can be redundant, which is tested rather than penalized twice by hand. Pulled-air, K%, BB%, PA, provider BIP and age are displayed when available. No percentages are imputed. ISO on contact was considered but not calculated from rounded rates: exact AB and K counts are absent from the live TJ summary.

The background contains up to 25 observed 2025 MLB examples, or 25 same-season/same-level TJ examples. MLB points are visual references only: neither axes nor the selected prospect are MLB-equivalent translations. Search covers all identities in the existing directory, including pitchers and players without an observed hitter record. Partial observations stay selectable. Levels, seasons and providers are never pooled by the interface.

## Frozen study design

- Public TJ Stats regular-season summary records for 2021–2023 at Single-A, High-A, AA and AAA.
- Eligible index record: age 16–26, 150+ provider PA, 50+ provider BIP, observed Whiff, ISO, K% and BB%. Pulled-air is not a fitting requirement because early coverage is sparse.
- MLB Stats API identities establish whether an MLB debut occurred before or during the index season. Those players are excluded, avoiding rehabbing veterans. Debut dates and later outcomes are never input features.
- One index record per player: earliest eligible season in this study window, then highest eligible level. This is not necessarily the first professional season.
- Target: within the following two seasons, at least one MLB regular season with 250+ PA, ISO >= .200 and TJ wOBA >= .330. It combines opportunity and performance. No attainment within this window is not career failure; later development remains possible.
- Non-debuted players remain in the study rather than dropping everyone without MLB playing time. Two unresolved follow-up identities were excluded; conflicting provider rows are audited, not averaged.
- 2021: 523 players, 13 events. 2022: 289 players, 4 events. 2023: 331 players, **0 events**. Player IDs are disjoint across cohorts. Follow-up ends in 2025.

Candidate logistic models use standardized inputs. Context is age, log(PA), and level indicators. Candidates are context alone; ISO + context; Whiff + ISO + context; and Whiff + ISO + K + BB + context. Each selects C from 0.1, 1, 10 using 2022 validation log loss. Select the best candidate by that same validation loss, refit on 2021–2022, and inspect 2023 once. The compressed study file holds full-precision coefficients, scales, source hashes and evaluation metrics.

## Result and interpretation

**ISO + context was the best validation candidate.** Validation log loss was approximately .05676, versus .05689 for Whiff + ISO and .05701 after also adding K and BB. These differences are tiny and based on four validation events; they establish no general superiority. Whiff is retained as an interpretable chart axis, not forced into the selected prediction formula. No compensating power requirement is invented.

The held-out player cohort contains no positive endpoint events. Consequently AUC, average precision and AUC improvement cannot be estimated; they are null, never zero or a fabricated accuracy score. Test log loss and Brier score are reported, but a model predicting nearly zero for everyone can perform well on those in an all-negative sample. This is **not evidence of validated MLB translation**. Only 17 development events support the fit, so coefficients and calibration are fragile.

The optional fitted reference is off by default. It holds the selected record's age, level and PA fixed and solves for ISO at the development cohort event-rate reference (17/812), not a 50% probability. Because the selected model does not include Whiff, the line is flat. It is an exploratory model slice, not a pass/fail frontier. No individual probability or score is displayed. The line is suppressed for missing context, under 150 PA/50 BIP, marginal features outside development ranges, or Rookie/DSL/complex. Marginal range checks are not proof of joint support.

## Limitations and follow-up

The source snapshots were retrieved retrospectively. Although IDs are disjoint and features precede each player's target window, training and validation target windows overlap calendar years. This is not a strict as-of deployment simulation. The earliest-eligible, disjoint-player design makes the later cohort younger/newer, and the two-year endpoint leaves many developing prospects without an event. Preserve this negative result; a future broader-horizon study must be declared exploratory and tested on fresh follow-up rather than silently changing this endpoint.

There is no park or league-specific adjustment. A level indicator cannot remove park effects. Age in TJ and approximate season age in other providers use different conventions and remain labeled by source. Whiff denominators and provider PA may reflect tracking differences. Rows missing raw stats do not receive substituted means. Rookie observations are descriptive because the model was fitted only at full-season A through AAA.

Next research should extend the historical window and follow-up, assess calibration with enough positive cases, test an independent future cohort, and obtain stable league/park context and exact contact denominators. The data does not currently justify a prospect forecasting grade or a universal “power compensates for misses” slope.

## Reproduction and sources

Run `python scripts/build-contact-damage.py` with numpy and scikit-learn installed. Missing public snapshots and MLB identities are downloaded to the external source cache (`POWER_SOURCE_CACHE` overrides the default); existing cache bytes are reused. Retain the cache to reproduce the exact published snapshot: a fresh download can differ after provider revisions. The current broader plotting observations reuse the reviewed Prospect Savant/official source panel without mixing its four-metric records.

- https://tjstats.ca/leaderboard/
- https://tjstats.ca/glossary/
- https://statsapi.mlb.com/api/v1/people
- https://www.mlb.com/glossary/advanced-stats/isolated-power

Download `contact-damage-study.json.gz` for source manifests and metrics, `contact-damage-cohort.json.gz` for the one-player cohort audit, and `contact-damage-records.json.gz` for the plotting panel. This is a dated build, not an automatic refresh.
