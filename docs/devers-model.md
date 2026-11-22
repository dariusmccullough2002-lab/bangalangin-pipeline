# DEVERS V1 — impact relative to Chase and Whiff risk

Snapshot: November 21, 2026. DEVERS is an experimental 0–100 relative profile index. It is not an MLB-success probability, MLB-equivalent translation, official prospect grade or a replacement for Pipeline rankings. A score of 82 describes a larger fitted profile margin than 50; it does not mean an 82% chance of success.

## Models and tier selection

**Tier A — full four-metric.** Chase%, Whiff%, Hard-Hit% and Barrel/BBE%. Preserve the original model specification and chronological fitting: qualified MLB source seasons through 2021 fit candidates; 2022–2023 choose regularization C from .1, 1, 10 by log loss; refit through 2023; inspect 2024–2026 (409 seasons, 102 same-season endpoint events). Endpoint: ISO >= .200 AND wOBA >= .330. The reproduced full-model AUC is .91368. This is same-season discrimination, not future prospect validation.

**Tier B — observed three-metric fallback.** Compare Chase + Whiff + Barrel against Chase + Whiff + Hard-Hit on the same split. Validation log loss favors Barrel (.43339 versus .58495). Inspected holdout AUC is .91330 for Barrel and .83062 for Hard-Hit. Barrel is the preferred fallback when available; the observed Hard-Hit model remains available when it is the only impact measurement. Current source panels commonly provide both impact rates or neither, so there may be no current Tier B rows. That does not justify fabricating a missing input.

**Tier C — experimental broad impact proxy.** Use Chase + Whiff with the selected proxy mapped into the Barrel-reference model. Proxy components are HR per non-strikeout at-bat, pulled-air rate and air-ball rate. They predict a Barrel reference target with learned ridge coefficients; no manual power-minus-contact weights are used. The displayed raw Hard-Hit and Barrel fields stay blank when unobserved. Internal proxy reference units are never presented as measured Barrel% or as a validated MLB translation.

**Tier D — insufficient inputs or cohort.** No score. Missing Chase, Whiff, proxy components, sufficient normalization peers or the 100-PA display minimum cannot be replaced by zero, an invented mean, scouting prose or another provider's measurement. All indexed players remain searchable.

Measured impact requires at least 50 source-tracked batted-ball events; unknown or smaller tracking samples cannot produce Tier A/B scores. Such rows can use Tier C if complete proxy components and 50+ same-source non-strikeout at-bats are available; otherwise they remain Tier D. Raw observed impact values stay visible even when too thin to use. Full/Moderate/Experimental badges describe input coverage. They are not calibrated confidence levels or proof of sample stability. One hundred PA is a display guard, not an empirically established stabilization threshold.

## Impact proxy research

Common comparison cohort: MLB TJ summaries at 250+ PA with all tested candidate fields. Exact AB/K/HR count inputs come from same-year MLB Stats API totals only when MLBAM ID, PA and HR counts match TJ exactly and the official player row is unique. Counts are never reconstructed from rounded rates. Many traded/mismatched players are excluded (1,217 otherwise eligible TJ rows), which is a selection limitation.

- Train: 2021–2023, 351 records.
- Choose alpha (.1, 1, 10, 100) and candidate using 2024 validation, 90 records.
- Held-out proxy test: 2025, 92 records.
- Additional inspected sensitivity: 2026, 158 records.

Candidates: ISO alone; pulled air + air; ISO + pulled air + air; HR/contact + pulled air + air; contact ISO + pulled air + air; EV90 + pulled air; EV90 + pulled air + ISO; EV90 + max EV + pulled air; average EV + pulled air. Each is evaluated against actual Barrel and actual Hard-Hit, with R², MAE, Spearman rank correlation and predicted-decile calibration. EV and xSLG cannot be silently filled at AA/High-A; an EV + xSLG candidate is not fitted because current common-source summaries do not expose xSLG. All results, both targets and sensitivity metrics are in `devers-research.json.gz`.

The broad deployment candidate excludes ISO and contact ISO. Among the two non-ISO, broad candidates, choose the simplest within 5% of the lowest 2024 validation MAE. Require validation R² >= .25 and rank correlation >= .50 before displaying the experimental proxy. These are research display rules, not a guarantee of minor-league validity. EV versions are compared but do not solve AA/High-A EV absence.

The selected **HR/contact + pulled air + air** proxy predicts Barrel on held-out 2025 MLB records with R² **.65524**, MAE **1.75458 percentage points**, and rank correlation **.85265**. Validation values were R² .74581, MAE 1.34630 pp and rank correlation .87555. The 2025 calibration deciles show systematic underprediction through much of the distribution; no post-test correction is fitted. Repeated players across years and the small PA-aligned sample limit uncertainty claims.

HR/contact = 100 × HR / (AB − K). It is **not HR/BIP**. For PS prospects those counts come from the same PS record. Air rate uses the provider's air-ball categories; source-specific differences remain. Normalization occurs within each provider/environment before aligning proxy inputs to the MLB training reference distribution. Negative conditional regression coefficients (for example pulled air after HR/contact is controlled) are not causal skill penalties.

The proxy is still outcome- and environment-dependent. It does not restore missing exit-velocity measurements. MLB held-out accuracy does **not** establish AA, High-A, complex or DSL transfer accuracy. Those scores remain Tier C / Experimental.

## Relative normalization

Use 100+ PA records in the same season × level/tracking environment × provider. Use an age band (18 and under, 19–20, 21–22, 23–24, 25+) only with at least 50 rows and at least 30 observed values for every required input; otherwise use the entire same-environment pool and show age as context. Each scored input requires at least 30 observed peers. Ties receive midrank percentiles.

Align each component's percentile to the corresponding historical qualified MLB development distribution. For proxy inputs, align to the proxy's MLB training feature distribution before predicting reference impact. This creates a **relative profile coordinate system**. It does not remove league difficulty or park effects, estimate an MLB-equivalent rate, or validate a future-outcome relationship. Age context uses the provider/season-age convention retained in the source, not an invented future-development bonus.

Do not combine metrics across providers, seasons or levels. An AA PS record retains PS Chase, Whiff and proxy components even if a different TJ record has a similar PA count. Original measured Hard-Hit and Barrel values are preserved separately from the aligned model inputs.

## Frontier, score and comparability

For a selected tier, let each centered fitted component be coefficient × (aligned input − MLB development mean).

- X = negative sum of centered Chase and Whiff contributions.
- Y = sum of centered impact contributions (Hard-Hit + Barrel for A, the available single impact component for B, the proxy reference component for C).
- Baseline = model intercept + coefficients × development means.
- Margin = baseline + Y − X.
- Fitted frontier: Y = X − baseline. It is derived algebraically from the fitted model, never drawn by hand.
- **DEVERS = 50 + 50 × tanh(margin / (2 × development margin SD)).**

The smooth 0–100 display scaling is a convention, not a fitted probability calibration. Margin zero maps exactly to 50. Descriptive bands are very high relative margin (85+), high (70+), above reference (55+), near reference (45–54), below reference (30–44), low (under 30). These are not validated scouting thresholds. The zero margin originally corresponds to the model's same-season MLB endpoint boundary; applying percentile alignment does not turn it into a prospect success threshold.

Chase and Whiff have separate fitted coefficients. Their conditional coefficients can have unintuitive signs in correlated models; risk is a fitted burden, not an assertion that every extra point of Chase causally hurts by a fixed amount. The preceding Phase 2 nonlinear audit did not support promoting a curved replacement. No universal compensation slope or no-survival cutoff has been established.

Tier scores share a display convention but are not proven interchangeable. The leaderboard offers tier filters for close comparisons. For Tier C, propagate ±one held-out proxy MAE through the index as a sensitivity range; it is not a confidence interval and omits minor-league transfer uncertainty. Full-tier scores also have sampling error even though this V1 does not publish calibrated intervals.

## Leaderboard and graph

The default leaderboard contains non-debuted hitters according to the retrieved MLB people snapshot; it is not a complete rookie-eligibility determination. Unknown debut status is excluded, not assumed to mean non-debuted. Other views show the league board or all indexed hitters. Search remains broad.

One player row per selected year: choose the highest observed level, then best available tier, then largest source PA. Do not choose an older/lower-level record merely because its score is higher. Tier D is unscored, not a score of zero. Filter by year, level, tier, minimum PA and name; export all filtered rows as CSV. These are research view orders, not main Pipeline ranks.

The graph keeps 25 MLB reference seasons, including recognizable landmarks and low-impact/non-endpoint seasons. Earlier qualified fallbacks are explicitly dated. Reference points are recomputed for the selected model tier; prospects use percentile-aligned components. Distances use the selected tier's standardized components against actual historical MLB seasons, with three distinct players from each endpoint group. “Endpoint not met” is a season classification, never a failed career label. These are relative-component neighbors, not equivalent talent or age/level-matched developmental paths.

Extreme-profile tables retain Whiff/Chase thresholds 30/30, 30/35 and 35/35, with Barrel and Hard-Hit bands and explicit sample sizes. Development and previously inspected holdout samples are separate. These show associations only; tiny groups cannot establish rescue effects or impossibility thresholds.

## Reproduction and deployment

Run `python scripts/build-devers.py` with numpy, scipy and scikit-learn. It reuses the reviewed MLB source, prospect panel and directory in this repository, and downloads missing public TJ/PS/MLB cache inputs. Preserve `POWER_SOURCE_CACHE` to reproduce exact published source bytes; a fresh provider response may differ. Hashes of the reviewed repository inputs and cached source responses are retained in the research download.

No paywall, private feature, authenticated export or credentials are used. No main Pipeline rankings, scouting grades, recommendations or player profiles consume DEVERS. This is a dated publication, not an automatically refreshing service.
