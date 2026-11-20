# Power Survival Frontier — historical research V1

November 20, 2026 · Research for review · No website deployment

## Main finding

The historical first pass supports evaluating impact quality in context, but **does not validate the proposed Hard-Hit formula or establish a publishable universal survival boundary**. Barrel rate supplies information that Hard-Hit alone misses. A fixed Chase/Whiff penalty underperforms even a Hard-Hit-only comparator. A separate next-year test does not establish incremental prediction over ordinary prior-season performance statistics.

This study is completed for the obtained Savant panel and the explicitly named V1 endpoints below. It is incomplete for the requested wRC+ endpoint, EV90, Pull-Air, minor-league translation, age-related improvement and causal development questions. Those limitations change what can be claimed.

## What was actually obtained and audited

- Official Baseball Savant CSV: **5,300 hitter-seasons, 1,354 distinct MLBAM IDs, 2015–2026**, minimum 100 PA.
- Main sample: **1,655 qualified seasons from 529 hitters**. Qualification is operationalized as at least 502 PA, or 186 in 2020. This is not an independently reproduced official batting-title eligibility list; exemption rules are not applied.
- Sensitivity samples: 4,049 seasons with at least 200 PA; all 5,300 with at least 100 PA; qualified samples excluding 2020 or 2015.
- Unique `player_id + year` keys; zero duplicates; no missing values in the selected 19 raw columns. No name-based joins, missing-to-zero conversions or averaged team-split rates.
- Zone Contact = 100 minus the exported Zone Swing & Miss %. Its denominator is in-zone swings. Whiff is per swing; Chase is swings per out-of-zone pitch; Hard-Hit is per batted ball.
- A case-study name collision was caught: Max Muncy (571970) and Max Muncy (691777) are different players. The requested Dodgers case uses 571970 only. The full panel already used IDs and was unaffected.
- The data includes numeric 2015 Hard-Hit/Barrel fields, despite a separate Savant context page describing those context metrics as 2016-present. We retained the obtained values and ran an explicit exclude-2015 sensitivity rather than silently asserting identical historical tracking quality.
- Dataset checksum: `863efa0edae9cafa83104b5ee5c7fe2d8eb51469b1a3112d3e708d203d70173f`. The original bytes and exact source URL are included.

The raw export was obtained through the live Download CSV control after direct requests were denied. FanGraphs could not be retrieved: direct requests timed out and browser verification remained unresolved. We did not bypass verification or invent a wRC+ join.

## Outcome definitions — a material deviation from the requested primary endpoint

**The requested ISO ≥ .200 AND wRC+ ≥ 110 endpoint has NOT been tested.** wOBA is not wRC+; it is not park adjusted and an absolute .330 does not mean 110 wRC+ in every season. The following cutoffs were declared in the first-pass code before fitting and were not optimized to make the hypothesis look good:

| Endpoint | Operational definition | Qualified holdout events / n |
| --- | --- | --- |
| successful_v1 | ISO ≥ .200 AND raw wOBA ≥ .330 | 102 / 409 |
| viable_v1 | ISO ≥ .150 AND raw wOBA ≥ .320 | 220 / 409 |
| impact_v1 | ISO ≥ .250 AND raw wOBA ≥ .370 | 18 / 409 |
| xslg450 | xSLG ≥ .450 | 155 / 409 |

These are sensitivity endpoints, not player badges or validated prospect categories. The impact tier has only 18 positive holdout cases. xSLG shares exit-velocity/launch-angle ingredients with the predictors, so its strong same-season fit is partly structural; it is not independent evidence of future projection skill. Even observed ISO and wOBA come from the same season, so the main study is explanatory/associational.

## Models and separation of fitting from evaluation

For same-season models: train on 2015–2021 (982 seasons), choose logistic penalty on 2022–2023 (264), refit through 2023, and evaluate once on 2024–2026 (409). Each season is equally weighted. No class balancing changes the base rate. Standardization and spline knots are learned inside fitting pipelines. Candidate logistic penalties are C=.1, 1, 10, chosen by validation log loss. The forest uses fixed depth 4, minimum leaf 25 and 400 trees. Seed: 20261120.

Candidate families: Hard-Hit only; the proposed margin; additive Chase/Whiff/Hard-Hit; Chase×Whiff; all pairwise interactions; additive cubic splines; an exploratory random forest; richer impact (Barrel and average EV plus pairwise terms); and a passivity/control bundle (Swing, Zone Swing, Zone Contact and BB plus pairwise terms). The spline model is additive, not a full tensor-product GAM. There is no gradient-boosting claim.

Repeated seasons from the same hitter can occur on both sides of the temporal split. To assess this, a second sensitivity holds out identities with MLBAM ID modulo 5 = 0, excludes all their earlier seasons from training/validation, and tests their 2024–2026 seasons. That test has only 78 seasons/28 events: additive AUC .809; richer-impact AUC .881. It is useful robustness evidence, not a prospect-translation validation.

## Main held-out results

AUC measures ranking discrimination (higher is better); Brier score and log loss measure probability error (lower is better). Numbers describe only the stated endpoint/sample.

| model | auc | brier | log_loss |
| --- | --- | --- | --- |
| hard_hit_only | 0.8219 | 0.183 | 0.5375 |
| hypothesis_margin | 0.7718 | 0.1854 | 0.5462 |
| additive | 0.8306 | 0.178 | 0.5263 |
| chase_whiff | 0.83 | 0.178 | 0.5265 |
| all_pairs | 0.8304 | 0.1789 | 0.5284 |
| spline | 0.8275 | 0.1825 | 0.5341 |
| forest | 0.8211 | 0.1845 | 0.5435 |
| rich_impact | 0.9104 | 0.1337 | 0.4087 |
| passivity | 0.8386 | 0.1546 | 0.4658 |

The richer-impact model improves AUC by .080 over the three-variable additive model and lowers Brier error by .044. A 500-replicate player-cluster bootstrap of the fixed test predictions gives AUC improvement interval [.045, .117] and Brier improvement interval [.027, .062]. These are uncertainty intervals conditional on the fitted models, not a fully nested model-selection bootstrap.

The Chase×Whiff term has essentially unchanged Brier error. Its AUC-improvement interval crosses zero (approximately −.0018 to +.0007). This is **no demonstrated additional interaction benefit in V1**, not proof that the biological interaction is absent. The passivity bundle improves Brier score, but its AUC-improvement interval crosses zero. It bundles four variables and interactions, so that result cannot be attributed specifically to excessive passivity.

## Which impact information mattered?

| model | auc | brier | chase_logodds_per_pp | whiff_logodds_per_pp |
| --- | --- | --- | --- | --- |
| core | 0.8306 | 0.178 | -0.0254 | 0.0226 |
| plus_barrel | 0.9137 | 0.131 | 0.0133 | -0.1754 |
| plus_average_ev | 0.8353 | 0.173 | -0.0244 | 0.0242 |
| core_plus_bb | 0.8375 | 0.1714 | 0.087 | 0.0008 |
| core_plus_zone_swing | 0.8284 | 0.1758 | -0.0445 | 0.0118 |
| core_plus_zone_contact | 0.8278 | 0.1758 | -0.0204 | -0.0137 |
| core_plus_swing | 0.8306 | 0.1777 | -0.0179 | 0.0237 |

The additive +Barrel model reaches .914 AUC, versus .835 for adding average EV alone. It is at least as competitive here as the more elaborate impact composite. Hard-Hit and Barrel correlate about .759 in the full panel: related but not identical. There is no reason yet to publish an arbitrary weighted Impact Score. Z-scoring correlated variables does not remove double counting; penalization, ablation and independent evaluation are still required.

An important warning: the three-variable model's Whiff coefficient is slightly positive conditional on Hard-Hit. After adding Barrel, the Whiff coefficient becomes negative. Chase also changes sign in some expanded specifications. These sign reversals are a warning about omitted launch quality, correlated predictors and survivor selection—not evidence that missing pitches helps hitting or chasing is beneficial. They prevent a defensible statement that Whiff is exactly X times worse than Chase.

## The proposed formula did not survive this first test

Required HH = 40 + .7×max(0,Chase−30) + .9×max(0,Whiff−25).

At 28 Chase / 25 Whiff, its required HH is 40.0%; at 34 / 31 it is 48.2%; at 40 / 37 it is 57.8%. These are arithmetic outputs of an unvalidated hypothesis, not learned thresholds. The margin was converted to a probability only by fitting a separate logistic calibration on historical development data; those calibrated results are the `hypothesis_margin` row above. The original zero-margin rule was separately checked: accuracy .648 and balanced accuracy .680 on 409 test seasons. Always predicting the more common non-event gives .751 accuracy, illustrating why accuracy alone is misleading.

The simplest fitted additive model yields the following 50% response levels. They are shown to diagnose the hypothesis, **not offered as required-impact recommendations**:

| chase | whiff | estimated_hh_for_50pct | bootstrap_2p5 | bootstrap_97p5 | nearby_n | supported_at_point |
| --- | --- | --- | --- | --- | --- | --- |
| 28 | 25 | 44.06 | 42.91 | 45.68 | 242 | True |
| 34 | 31 | 44.17 | 42.63 | 45.91 | 104 | True |
| 40 | 37 | 44.29 | 41.31 | 47.81 | 15 | False |

Intervals use 150 player-clustered refits of the development data at a fixed selected penalty. A 50% probability level is a visualization convention, not a learned decision threshold. The almost-flat fitted response does not reproduce the proposed steep penalty. The 40/37 estimate has too little support and must not be used even though a mathematical root exists.

## Is either high-risk weakness survivable?

For an explicitly exploratory region (Chase ≥34%, Whiff ≥31%, Hard-Hit ≥45%), 14 qualified seasons meet the entry conditions and 5 meet the raw-wOBA/ISO endpoint. Across all 100+ PA seasons, the region contains 42 seasons and 10 endpoint hits. These small, selected denominators are descriptive, not long-term survival probabilities.

Examples include 2021 Salvador Perez (44.8 Chase, 33.7 Whiff, 56.2 Hard-Hit, 16.3 Barrel, .271 ISO, .359 wOBA) and 2021 Javier Báez (44.6, 40.6, 45.2, 13.4, .229, .344). Thus, no blanket impossibility rule is justified. Conversely, 2024 Jesús Sánchez had 51.3% Hard-Hit yet .165 ISO/.317 wOBA, and 2026 Jordan Walker had 49.9% Hard-Hit yet .197 ISO/.344 wOBA. Walker narrowly misses the chosen ISO cutoff: calling him a career failure would be incorrect. These are season-level endpoints, not verdicts on careers.

## Named MLB archetypes

The full season histories, including K/BB, xwOBA and zone contact, are in `results/archetypes_all_seasons.csv`. Below is the 2026 export. Judge has fewer than qualifying PA, so he is a case-study observation rather than a member of the qualified test sample.

| name | pa | chase | whiff | z_contact | z_swing | hard_hit | barrel | iso | woba |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Muncy, Max | 561 | 25.8 | 29.2 | 81.0 | 65.7 | 45.8 | 12.9 | 0.238 | 0.361 |
| Judge, Aaron | 285 | 26.4 | 32.8 | 78.0 | 64.0 | 57.5 | 20.9 | 0.27 | 0.372 |
| Olson, Matt | 698 | 27.9 | 25.4 | 80.8 | 66.8 | 52.0 | 14.2 | 0.251 | 0.351 |
| Devers, Rafael | 633 | 30.0 | 29.0 | 74.9 | 66.4 | 51.6 | 12.5 | 0.267 | 0.367 |
| Schwarber, Kyle | 701 | 26.1 | 33.1 | 77.5 | 66.4 | 49.3 | 15.6 | 0.271 | 0.368 |
| Ohtani, Shohei | 618 | 30.0 | 31.7 | 77.2 | 66.0 | 52.1 | 16.4 | 0.237 | 0.377 |
| Crow-Armstrong, Pete | 726 | 34.2 | 26.3 | 82.8 | 68.6 | 48.6 | 13.3 | 0.29 | 0.4 |
| Wood, James | 623 | 21.3 | 30.1 | 81.8 | 56.8 | 58.9 | 18.6 | 0.238 | 0.383 |

Most of these stars are not simultaneously extreme in both Chase and Whiff. Several pair large impact with restrained chase or useful walk rates. They cannot establish the high-Chase/high-Whiff frontier by themselves. Crow-Armstrong's defense and speed may affect overall value, but they are not included in the modeled offensive endpoint. Here are all obtained Joey Gallo seasons, retaining both stronger and weaker years:

| year | pa | chase | whiff | hard_hit | barrel | iso | woba | successful_v1 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 2015 | 123 | 27.4 | 50.0 | 51.0 | 17.4 | 0.213 | 0.305 | 0 |
| 2017 | 532 | 28.2 | 43.4 | 52.2 | 24.0 | 0.328 | 0.364 | 1 |
| 2018 | 577 | 29.5 | 40.8 | 49.5 | 24.7 | 0.292 | 0.343 | 1 |
| 2019 | 297 | 20.5 | 41.6 | 53.1 | 29.8 | 0.345 | 0.401 | 1 |
| 2020 | 226 | 19.0 | 37.4 | 43.9 | 14.2 | 0.197 | 0.297 | 0 |
| 2021 | 616 | 19.0 | 38.8 | 45.8 | 18.7 | 0.259 | 0.348 | 1 |
| 2022 | 410 | 27.5 | 40.6 | 50.5 | 17.6 | 0.197 | 0.286 | 0 |
| 2023 | 332 | 26.1 | 44.3 | 52.9 | 19.3 | 0.263 | 0.32 | 0 |
| 2024 | 260 | 21.9 | 39.6 | 43.4 | 13.1 | 0.175 | 0.276 | 0 |

## Separate next-year prediction test

Join only consecutive seasons on MLBAM ID + year. Predictors require a qualified feature season; the next season must have at least 200 PA. Of 1,520 eligible pre-2026 feature seasons, 1,361 retain a next-year outcome and 159 do not. Missing/under-200-PA outcomes are not coded as failure. This makes prediction conditional on receiving that much MLB opportunity; injury, demotion and attrition remain selection issues.

Train on feature years 2015–2020 (outcomes 2016–2021); validate on feature years 2021–2022; test on feature years 2023–2025 (outcomes 2024–2026). Holdout: 382 pairs, 90 events.

| model | auc | brier | log_loss |
| --- | --- | --- | --- |
| hard_hit_only | 0.7606 | 0.1794 | 0.5383 |
| hypothesis_margin | 0.7295 | 0.181 | 0.5436 |
| additive | 0.7629 | 0.1774 | 0.5335 |
| chase_whiff | 0.7604 | 0.1783 | 0.5355 |
| all_pairs | 0.7564 | 0.1796 | 0.5376 |
| spline | 0.7578 | 0.1794 | 0.5371 |
| forest | 0.7363 | 0.1844 | 0.5467 |
| rich_impact | 0.8087 | 0.1537 | 0.4751 |
| passivity | 0.792 | 0.1479 | 0.461 |

The necessary performance-baseline comparison is:

| model | auc | brier | log_loss |
| --- | --- | --- | --- |
| core | 0.7629 | 0.1774 | 0.5335 |
| plus_barrel | 0.8188 | 0.1555 | 0.4808 |
| plus_average_ev | 0.7666 | 0.1726 | 0.5224 |
| core_plus_bb | 0.7826 | 0.1658 | 0.507 |
| core_plus_zone_swing | 0.7658 | 0.1763 | 0.5311 |
| core_plus_zone_contact | 0.7627 | 0.177 | 0.5325 |
| core_plus_swing | 0.7609 | 0.1763 | 0.5309 |
| prior_woba_iso | 0.8233 | 0.1388 | 0.4392 |
| prior_woba_iso_k_bb | 0.8293 | 0.1365 | 0.4343 |
| rich_plus_prior_stats | 0.8323 | 0.1381 | 0.4371 |

Prior wOBA/ISO/K/BB reaches .829 AUC and .1365 Brier, versus .809/.1537 for richer impact alone. Adding the richer predictors to performance raises AUC only to .832 while worsening Brier to .1381. **V1 has not demonstrated useful incremental prediction beyond the simpler performance baseline.** These results do not predict whether a teenager reaches MLB.

## Passivity and the two developmental cases

With consistent pitch definitions, let Z be the fraction of pitches in-zone, ZS the in-zone swing rate, C the chase rate, ZC in-zone contact and OC out-of-zone contact. Then Swing = Z×ZS + (1−Z)×C, and Whiff = [Z×ZS×(1−ZC)+(1−Z)×C×(1−OC)] / Swing. Also SwStr = Swing×Whiff when all use the same pitch universe. These are denominator identities, not fitted baseball findings. They explain why low SwStr alone does not establish bat-to-ball skill, and why changing zone aggression can change total Whiff through pitch mix even without a contact-skill improvement.

MLB reported Rodriguez's zone-swing rate rising from 63.3% in 2025 to 69.6% early in 2026; contact remained an issue. That dated report is not a controlled pre/post estimate and is not the same sample as his later MLB season line. The later Savant MLB table has only 178 pitches; it must not be pooled with the Triple-A rates to manufacture a development trajectory.

For Neyens, MLB Pipeline describes substantial power, mechanical/contact concerns and occasional passivity. We did not obtain the reviewed, dated level-by-level tracking panel necessary to quantify his zone-swing or zone-contact improvement requirement. Low chase alone does not establish elite recognition: passivity can also lower chase. Neither prospect receives a model score or label.

## Visualizations and support

`results/frontier_slices.png` shows separate Chase slices, Whiff horizontally and Hard-Hit vertically. Keeping Chase separate avoids hiding different hitter types inside an arbitrary weighted risk index. Contours are exploratory all-pairs logistic same-season responses. Historical points are included, and predictions are blanked outside the development-data convex hull or when fewer than 25 development seasons fall within ±5 percentage points on all three axes. The 25-neighbor rule is a transparency guard, not an empirically validated reliability cutoff. Point overlays include all years; fitted surface/support use development years only. The high-risk corner is visibly sparse. These are not ready-to-deploy frontier contours.

`results/impact_bands.png` shows the requested five Hard-Hit bands. Cell counts and empirical region summaries are in CSV; rates do not account for confounding or repeated seasons. No 3D chart was needed.

## Answers to the outstanding questions

| Question | Current defensible answer |
| --- | --- |
| How much extra HH compensates? | No publishable increment. The hand formula fails the comparison; the HH-only response is specification-sensitive. |
| Is Whiff worse than Chase? | No stable causal ratio established. Coefficients change when Barrel/BB/zone variables enter. |
| Nonlinear Chase×Whiff penalty? | No clear incremental holdout benefit in V1. Splines/forest also do not improve the core three-metric result. |
| Almost-impossible combinations? | No defensible cutoff; extreme cells lack support and some historical exceptions exist. |
| Can impact compensate for both? | Some season-level examples meet the endpoint. Hard-Hit alone is not sufficient; not a career-survival estimate. |
| EV90 versus HH? | Untested. EV90 is unavailable; average EV/EV50 is not a substitute. |
| Barrel adds value? | Yes for these same-season tests; +Barrel also improves the conditional next-year core model. |
| Pull-Air adds value? | Untested; not in the obtained export. Do not multiply marginal Pull% by Air% to invent the joint rate. |
| BB beyond Chase? | The BB ablation reduces error. It does not prove a causal mechanism; BB also directly contributes to wOBA. |
| Passivity independently harmful? | The multivariable bundle helps probability error, but zone-swing alone does not establish that claim. |
| Zone Contact versus Whiff? | Adding zone contact has little discrimination gain here. A proper matched substitution study remains pending. |
| How much contact improvement is needed? | Not determined by these MLB season-level associations. |
| Do young hitters improve enough? | Not tested; age and longitudinal minor-league tracking are absent. |
| At what age/level does risk harden? | Not tested. |
| Age-adjusted prospect version? | Not yet. `prospect_stress_test_status.csv` keeps all requested candidates unscored with missing inputs blank. |

## Review gates before calling this a metric

Obtain the requested wRC+ panel and audit MLBAM joins/park/season context; add EV90 and true joint Pull-Air with tracked BBE coverage; assess era/tracking changes and within-season out-of-time prediction; quantify attrition rather than dropping it silently; compare richer predictors with performance baselines on fresh unseen data; and fit a separate age/level prospect panel before considering development labels. More model searches on the already inspected holdout would require another untouched test set.

Any future margin must be conditional on an explicitly defined outcome, probability level, opportunity sample and covariates. It may not be monotonic or identifiable everywhere. Defense and speed can sustain a roster role without meeting an offensive power endpoint; overall player value is a separate target. **No score, badge, ranking adjustment or player-profile feature was deployed.**

## Sources

1. [Official custom leaderboard export](https://baseballsavant.mlb.com/leaderboard/custom?year=2026%2C2025%2C2024%2C2023%2C2022%2C2021%2C2020%2C2019%2C2018%2C2017%2C2016%2C2015&type=batter&filter=&min=100&selections=pa%2Ck_percent%2Cbb_percent%2Cslg_percent%2Cisolated_power%2Cxslg%2Cwoba%2Cxwoba%2Cexit_velocity_avg%2Cbarrel_batted_rate%2Chard_hit_percent%2Cz_swing_percent%2Cz_swing_miss_percent%2Coz_swing_percent%2Cwhiff_percent%2Cswing_percent&chart=false&x=pa&y=pa&r=no&chartType=beeswarm&sort=xwoba&sortDir=desc) — original data; retrieval November 20, 2026.
2. [Savant CSV field documentation](https://baseballsavant.mlb.com/csv-docs) — IDs, pitch/batted-ball measurements and expected-stat fields.
3. [Savant metric context](https://baseballsavant.mlb.com/statcast-metrics-context) — definitions and stated context-window coverage.
4. [Savant expected-stat methodology](https://baseballsavant.mlb.com/expected_statistics) — explains shared EV/launch-angle ingredients and inclusion of actual noncontact events.
5. [FanGraphs wRC+ definition](https://library.fangraphs.com/offense/wrc/) — why raw wOBA is not a park/league-adjusted substitute.
6. [MLB's dated Rodriguez development report](https://www.mlb.com/news/emmanuel-rodriguez-boasts-consistent-production-healthy-spring).
7. [Rodriguez official Savant record](https://baseballsavant.mlb.com/savant-player/emmanuel-rodriguez-691181).
8. [Neyens official Savant / Pipeline record](https://baseballsavant.mlb.com/savant-player/xavier-neyens-815832).

## Reproduction and completed files

The companion package contains the original CSV, normalized panel, model code, chronological holdout predictions, evaluation metrics, calibration bins, bootstrap results, boundary diagnostics, correlation matrix, full archetype histories, supported contour grids, figures, prospect missing-data register and validation script. See README for run order. The program has no publishing or site-writing code.
