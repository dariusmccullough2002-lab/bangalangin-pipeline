# Separate MLB arrival and playing-time model — October 13, 2026

## Result and release status

Built a reproducible annual research model with separate first-MLB-arrival probabilities, conditional post-arrival workload paths, annual expected PA/IP, MLB activity probabilities, and the probability of reaching a regular-role milestone. It produces forecasts for all 267 prospect-only assets and separate observed-debut diagnostics for 233 recently debuted catalog assets. Published ETAs are displayed as independent evidence. They are not assumed to mean a full season, half season, or established MLB role.

The new panel is a research diagnostic. Dynasty values, active MLB forecasts, and existing MLB fit calculations remain unchanged. Prospect competitive-fit scores remain withheld. The joint production-value calculation has not been rebuilt: multiplying these arrival probabilities into old unconditional prospect outcome paths would double-count non-arrival/bust risk.

## Research on the user's suggestions

A one-year transition is common, but far from universal. In a unique-player descriptive cohort of 98 ranked hitters with five complete ordinary-year seasons after debut, 16 reached the playing-time milestone in their debut year, 29 the following calendar year, 28 in years two through four, and 25 did not reach it within five years. This is a calendar-season study, not a claim about exactly twelve months. It conditions on observed MLB arrival; it does not describe all signed minor leaguers.

In the later chronological evaluation, 91 hitter forecast cases with an observed ordinary-year debut averaged 184 PA, with a median 109 PA; 13.2% reached the regular-role milestone immediately. These are forecast cases, with repeated historical snapshots, not 91 independent players. The descriptive 98-player cohort uses earlier, unique identities, so its percentages differ.

The hitter model's debut-year PA MAE is 128.3 versus 161.9 for a conditional half-season reference (509/2 = 254.5 PA) and 335.6 for a full-role reference. A fixed half-season assumption is consequently an informative sensitivity, but not the adopted forecast. Debut month is not separately modeled: the distribution of first-calendar-year volumes captures early call-ups, late call-ups and brief appearances empirically. Exact monthly timing would need more historical game/date inputs.

Within realized debut-year MLB roles, a half-season reference outperformed the candidate's pitcher debut-volume forecasts: starters 29.7 versus 40.4 IP MAE; relievers 16.3 versus 35.1 IP. These role-conditioned comparisons use the eventual MLB role as an evaluation subgroup and reference, not as a pre-debut predictor. They do not establish a deployable rule that knows a pitcher's future role. No fixed half-season pitcher forecast is silently substituted. Future starter/reliever conversion and missing current MiLB GP remain material limits.

The published-ETA study also contradicts guaranteed playing time in the ETA year. Among 105 hitter snapshot cases (83 players), 70.5% had arrived by the published ETA; workload in that year averaged 153 PA and had a median of 60 PA. For 46 pitcher cases (41 players), 67.4% had arrived by ETA; volume averaged 47.1 IP, median 24.3 IP. COVID volume year 2020 is excluded from this descriptive comparison. These are historical FanGraphs estimates, not proof every provider's ETA has the same meaning.

Bolte illustrates the early-arrival/large-workload branch. MLB identifies his debut as May 13, 2026. The preserved full-season Fantrax export records 473 PA and .764 OPS; the user's approximately 430 PA/.770 OPS example is compatible with an earlier snapshot. He is already above the model's 400-PA regular-role milestone, so the post-debut model treats arrival and achievement of that milestone as known. It does not impose another development year.

Sources checked October 13:
- https://www.mlb.com/athletics/video/henry-bolte-s-great-day-in-mlb-debut — dated May 13, 2026.
- https://www.mlb.com/news/henry-bolte-growing-with-athletics-in-breakout-rookie-season — debut and opportunity context.
- https://blogs.fangraphs.com/how-to-use-the-board-a-tutorial-2022/ — ETA commonly follows a 40-man roster timetable, with manual exceptions. It is not a guaranteed regular-role date.

## Definitions and architecture

Arrival is the first calendar season with positive MLB PA for hitters or IP for pitchers. Prior MLB arrivals are excluded from the pre-debut training population; pre-2010 arrivals are recognized using the preserved Chadwick first-MLB-year crosswalk.

Regular role is an operational exposure milestone: 400 PA for hitters, 300 PA for catchers, 80 IP for starters or 40 IP for relievers. It does not guarantee positive fantasy contribution, and does not certify roster eligibility or a lasting everyday role. Pitching roles for outcome measurement use observed starts. Future pitching role is not known in advance.

The arrival component is role-specific discrete-time logistic survival, using snapshot age, prior/saved level, time since the snapshot, and a global FanGraphs rank where traceable. A separately selected rank-free age/level model handles missing global ranks. Pipeline and Dynasty Dugout ranks are not converted into FanGraphs ranks. Published ETA is excluded from the fitted predictor: the recovered pre-2019 development snapshots do not contain published ETA fields. Current ETA evidence remains visible for comparison, rather than being given an unvalidated numerical weight.

Conditional playing-time paths use weighted historical neighbors by age, level and independently traceable rank; pre-debut MiLB GS/GP is an additional pitcher feature when present. They retain zero MLB years after debut. Later unobserved years are right-censored, not assigned zero. A weighted survival calculation measures the first regular-role milestone, with a monotone calibration transform fitted only on development forecasts. Arrival masses and conditional workload are combined once: expected calendar-year exposure sums each possible arrival year's probability times its post-arrival workload. Annual activity, arrival, and ever reaching a regular role remain different quantities.

Observed-debut diagnostics condition on the recorded first-season PA/IP and known MLB role. Donors match whether the player has already reached the regular-role milestone. Bolte's achieved milestone remains 100%; Culpepper's MLB arrival is 100%, but his future regular-role probability is estimated separately. No new debut penalty is applied. These diagnostics do not overwrite active forecasts.

## Recovery, chronology and validation

Recovered 680 dated FanGraphs ranking snapshots (512 stable MLBAM identities), 4,176 MLB role-seasons through 2025, complete annual source coverage, and prior-year MiLB level/starting-share evidence. Historical inputs come from preserved foundational ZIPs and the verified historical-coverage checkpoint. Corrected official hitting exports replace previously truncated/misaggregated inputs where recovered. No broad new collection or reserved 2021 prospect-cohort evaluation was performed.

Hyperparameters use 2014/2015 forecast origins, training strictly before each origin, and development outcome labels ending in 2018. Later evaluation uses 2019 and 2020 forecast origins with training through 2018 and 2019 respectively. All outcome inspection ends in 2025. The earlier model cohorts were already inspected; these are new-model chronological evaluations on exposed history, not an untouched final holdout. Protocol_Amendment.json records the additional rank-free validation, pitcher feature, and calibration changes made after initial inspection. Do not portray repeated inspection as independent confirmation.

Across 1,397 player-horizon cases (162 players), ranked arrival Brier is .1144 versus .1434 for a role/lag empirical baseline. Lower is better. By family: hitters .1166 versus .1519; pitchers .1097 versus .1256. Player-block bootstrap intervals for the improvement exclude zero in both families. The separately evaluated rank-free variant also improves on that arrival baseline.

Regular-role Brier is .2216 versus .3740 for immediate regular playing time and .3110 for an imposed one-calendar-year delay. Those simple rules are benchmarks, not calibrated alternatives. The candidate remains overconfident about regular roles in the later cohorts. Ordinary-year hitter workload MAE is 186 PA with +35 PA bias; rank-free hitter workload has larger positive bias. This is not sufficient to restore a reliable central trade-fit forecast.

Post-debut next-season workload MAE improves only slightly over repeating the first season: hitters 151.8 versus 154.3 PA; starters 41.8 versus 41.9 IP. Relievers are worse, 31.6 versus 11.6 IP. These gains are not declared a validated replacement for active MLB forecasts. RP post-debut sample size is only ten players. All post-debut outputs remain exploratory.

Model contracts verify probability conservation, monotone arrival/regular-role curves, regular-role and annual-activity probabilities bounded by arrival, correct source-year coverage, chronology, zero versus censoring treatment, source identity uniqueness, and unchanged neutral catalog. UI tests cover source limitations and observed-debut behavior. Reproduce with the pinned dependencies, then run model.py, post_debut.py, research_checks.py, validate.py, npm test, and npm run build.

## Morales and the original comparison

Morales's forecast uses verified April 1, 2027 age 20.5, saved A+ level, and independently traceable FanGraphs preseason global rank 61. The candidate gives approximately 22% probability of MLB debut during 2027, 6% probability of having reached regular playing time by year-end, and 40 expected MLB PA in 2027. Conditional on arriving that year, the debut-year workload expectation is about 183 PA; the unconditional 40 PA includes non-arrival. Its year-by-year arrival distribution can differ from FanGraphs's 2030 ETA and MLB Pipeline's 2029 estimate. A published ETA is not treated as a deterministic cutoff.

Culpepper already debuted and recorded 128 PA. The post-debut diagnostic estimates about 271 PA for 2027 and 27% probability of reaching the regular-role milestone by year-end. Bolte already recorded 473 PA and reached that milestone; his post-debut diagnostic estimates about 483 PA in 2027. These numbers are research diagnostics with the stated weak post-debut validation, not new active valuation inputs.

## Remaining release requirements

To restore prospect competitive fit, integrate mutually coherent arrival, conditional playing time and talent/count outcomes, preserving the star utility calculation once and avoiding a second bust/availability discount. Improve regular-role calibration and pitcher role/opportunity prediction, evaluate category contribution and trade outcomes on chronological data, and quantify sparse/longer-horizon uncertainty. The separate timing model is built and exposed for review; central trade-fit adoption has not passed those gates.
