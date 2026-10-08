# Unified Dynasty Asset Model: Phase 1 historical calibration

**Review checkpoint, 2026-10-08. Recommendation: continue offline calibration; do not implement or deploy this formula.**

This extends the preserved U2 architecture and replacement review at research/calibration/2026-10-07. It supplies first historical contribution and prospect probability components, not a replacement Trade Analyzer or a completed full-league valuation model. No current trades were treated as fair or used as fitted targets. No production application files were edited. Phase 2 and the full roster optimizer have not started.

## What this checkpoint establishes

1. A cached primary-source dataset, explicit identity exceptions and reproducible temporal tests.
2. Actual-workload MLB forecasts with age, role and attrition, and signed replacement surplus separate from intrinsic contribution.
3. Five-window prospect outcome probabilities from historical ranking cohorts, with uncertainty and matched age/trajectory experiments.
4. Preliminary evidence of better forecasts than constant production; insufficient evidence for precise superstar probabilities or trustworthy hitter/pitcher exchange rates.

## Data coverage and provenance

MLB.com historical preseason top-100 lists for 2012, 2013, 2017 and 2018 supply 400 ranking records. Official MLB StatsAPI regular-season aggregates cover 2010–2023: 28 cached group/year responses and 19,049 primary-role player-seasons. All returned split counts were checked against totalSplits; IDs within each season/group were checked for duplication. Bio responses supply stable birth dates only; present-day status, evaluations and current ages never enter historical features.

399 rankings were resolved to MLBAM IDs. Brody Colvin (2012) is explicitly excluded because the searched official identity source did not resolve him; he is not silently assigned zero production. Explicit overrides distinguish Josh Bell born 1992 from the older namesake, and Luis Ortiz born 1995 from the younger pitcher. Alias evidence is saved. Exact season names were normalized only for initial resolution; production/outcome matching thereafter uses MLBAM IDs.

The four archive articles were republished in December 2018 and carry later update metadata. Historical preseason labels and list membership are usable retrospective evidence, but the pages alone do not prove every field was frozen at its original publication date. A strict point-in-time archive audit is still required. Parser corrections are documented: missing separator for Mike Olt in 2012; organization/position order for Jarred Cosart and Xander Bogaerts in 2012; duplicated rank 32 for José De León in 2017 corrected to 33 by sequence. 2018 ranks follow ordered-list position.

Sources: sources.json has URLs, hashes and season row counts. raw-data.zip retains the retrieved pages, parsed lists, MLB responses and identity evidence. FanGraphs 2017 historical prospect reports/Board contain FV and tool information; they were located but not assembled into a time-consistent training corpus here. SABR Lahman is an independent outcome cross-check resource, not an additional fitted dataset in this checkpoint. No uncollected source is counted as model coverage.

Primary source inventory:

- MLB archives: [2012](https://www.mlb.com/news/2012-top-100-mlb-prospects-list-c301610610), [2013](https://www.mlb.com/news/2013-top-100-mlb-prospects-list-c301609842), [2017](https://www.mlb.com/news/2017-top-100-mlb-prospects-list-c301608460), [2018](https://www.mlb.com/news/2018-top-100-mlb-prospects-list-c301606192).
- MLB season and identity API URLs are recorded in sources.json; game-level QA3 would require additional collection.
- Candidate scouting source: [FanGraphs 2017 report](https://blogs.fangraphs.com/2017-top-100-prospects/) and [historical Board](https://www.fangraphs.com/prospects/the-board/2017-prospect-list).
- Independent outcome cross-check: [SABR Lahman](https://sabr.org/lahman-database/).

## Contribution scale and the pitcher anchor

The first component sums standardized category contributions, with dispersions estimated only from qualified 2010–2012 player-seasons. Hitters use HR, R, RBI, SB, H − .250×AB, and (OPS − .720)×AB. Pitchers use K, (4.2/9)×IP − ER, 3×SV + 2×HLD, K − 3×BB, and 1.25×IP − H − BB. Baseball innings notation is converted to outs/3; starts ≥5 define SP, otherwise RP. An occasional two-way row is assigned its dominant exposure role, which is a limitation for genuine two-way assets.

These are **first-order category proxies, not category-win probabilities**. OPS/AVG/WHIP/K-BB contributions depend on the surrounding roster denominators. The ER term assumes fixed innings exchanged against a reference rate; it does not reproduce the league's raw-ER incentive for arbitrary changes in innings. The league's zero-walk K/BB convention is not exactly represented. The historical score omits QA3 entirely because season aggregates do not establish the custom ≥5 IP/≤2 ER OR ≥6 IP/≤3 ER game-level condition. Standard quality starts are not a substitute. Six hitter versus five pitcher components therefore make cross-role exchange rates provisional. No multiplier was fitted to make hitters and pitchers equal.

U2 extrapolated small samples to full seasons, used separate role denominators, subtracted very strong free-agent references, and clipped surplus at zero. Its first SP/RP outcome anchors were both zero. This checkpoint removes that clipped-surplus anchor from intrinsic labels. It retains actual workloads, uses shared SP/RP category dispersions, and records signed surplus in a separate ledger. That fixes the conflation; it does **not** establish that a low-surplus pitcher is valuable or finish the missing-QA3 calibration.

Historical replacement references are the median next-24 scores after hitter rank156 and pitcher rank108 in each 2010–2012 season. These are explicit 12-team roster-depth proxies, not verified historical Fantrax free agents, positional alternatives, or current acquisition evidence. The pitcher cutoff assumes the maximum nine active pitcher slots; reserve/minor ownership and variable weekly pitching are not reconciled. They must not be interpreted as validated league replacement access.

| Role | Intrinsic annual q30 | q60 | q85 | q98 | Signed surplus q30 |
|---|---:|---:|---:|---:|---:|
| H | 7.40 | 10.67 | 13.96 | 20.00 | 1.16 |
| SP | -0.56 | 2.57 | 6.00 | 11.86 | -3.62 |
| RP | 1.05 | 3.11 | 5.63 | 8.74 | -2.00 |

These descriptive quantiles include all workload-qualified players; they are not replacement-adjusted regular/star outcome constants. A negative score reflects harmful ratio/reference production, not a negative raw number of statistics. Intrinsic production is stored before subtraction. Acquisition scarcity is left unestimated. A low or negative replacement surplus is allowed without forcing intrinsic contribution to zero.

## Forecast design and pitcher/hitter diagnostics

The one-year ridge component predicts next-year intrinsic score from current score, workload, age, a post-age-30 hinge and SP/RP indicators. Missing next-year MLB production is zero, preserving attrition. Training transitions end with outcomes in 2017. Held-out transitions start in 2018, 2021 and 2022; transitions involving the COVID season are excluded from this one-year test. The fixed regularization parameter is alpha10, not selected on holdout. The same players may appear in MLB training and test years; this is a temporal forecast test, not an unseen-player test. Errors are dependent within players and years.

| Role | Held-out transitions | Forecast MAE | Carry-forward MAE | Bias | No next-year MLB row |
|---|---:|---:|---:|---:|---:|
| H | 1173 | 3.019 | 3.183 | -0.017 | 8.0% |
| SP | 677 | 2.536 | 2.944 | -0.033 | 10.0% |
| RP | 732 | 1.750 | 2.071 | 0.223 | 15.7% |

Signed residual quantiles are saved in validation.json. They describe held-out errors; they are not prospectively calibrated prediction intervals. RP forecasts have positive bias. No injury diagnoses were available in the feature corpus; attrition includes injury, demotion, retirement and role loss, and cannot identify their separate causal effects. The age hinge is a fitted conditional association, not an identified biological aging curve.

Separate one/three/five-year forecasts use fixed Contender/Balanced/Rebuild illustrative horizons (discount .88 for multi-year horizons). All training windows start in 2010–2012 and end by 2017; held-out starts are 2017/2018 and end by 2023. Actual COVID production remains in multi-year outcomes. All role/horizon MAEs improve over constant-production extrapolation in this sample; detailed figures and RP bias are in diagnostics.json. Horizon preferences are not optimized owner utility and do not replace U2's existing eight-year strategy weighting. The component forecasts conditional means; a full correlated future-contribution distribution and calibrated durability intervals remain unfinished.

## Prospect outcome definitions

Labels concern the **five calendar seasons beginning with the historical preseason evaluation**, not completed careers. A missing MLB row is zero production during that window. Class0 means fewer than two seasons with ≥250 AB or ≥40 IP; it is minimal realized contribution within five years, not a lifetime bust declaration. A young prospect can be class0 and become excellent later. Classes1–4 require the same participation condition. The mean of the two largest annual intrinsic scores in the window determines the upper tiers: regular below q60, above-average at q60, star at q85, superstar at q98. Thresholds are pooled from positive workload-qualified 2010–2012 annual scores; they are pragmatic fantasy proxy definitions, not independently validated baseball superstar labels. In particular annual thresholds applied to a two-year mean and missing QA3 require sensitivity testing.

Thresholds q60/q85/q98: 6.828 / 11.615 / 17.598. No late-career outcomes are used to redefine those five-year labels.

First appearances from the 2012/2013 lists yield 148 unique development players; labels are available by the end of 2017. The 2018 holdout excludes any development player, leaving 99 distinct prospects; labels cover 2018–2022. The 2017 list supplies a prior ranking for a separate trajectory experiment, not training labels for the primary model. No current Josuar, Acuña, Guerrero or De Vries trade result enters fitting. Normalization, replacement and thresholds use 2010–2012 only. This is temporal and player-disjoint validation, conditional on archive accuracy; it is not a claim that the 2012 training predictions themselves were issued in 2012.

A multinomial logistic model with fixed C=.3 uses log(rank) and pitcher/hitter status. Age is a separate additive experiment. The trajectory experiment trains on 2013 with 2012 history and tests 2018 with 2017 history, compared against exactly the same 2013-only age/rank model. It does not borrow the unmatched holdout trajectory into the primary model. Historical tool/FV changes, levels, minor-league performance and injury changes were not modeled because a comparable dated training corpus is absent. They are promising sources to assemble, not demonstrated predictors here.

| Model | Holdout log loss ↓ | Multiclass Brier ↓ | Superstar Brier ↓ |
|---|---:|---:|---:|
| rank_role_logistic | 1.184 | 0.646 | 0.0091 |
| training_frequency_baseline | 1.268 | 0.671 | 0.0101 |
| U2_rank_prior | 1.267 | 0.663 | 0.0120 |
| rank_role_age | 1.154 | 0.628 | 0.0089 |
| 2013_matched_rank_role_age | 1.158 | 0.621 | 0.0100 |
| 2013_matched_plus_trajectory | 1.173 | 0.628 | 0.0100 |

Primary paired Brier difference versus U2: -0.0171; bootstrap95% interval -0.0442 to 0.0105. The interval crosses zero; superiority is not established. Age improves this single test; trajectory slightly worsens the matched metrics. More independent years are necessary.

Development class counts minimal/regular/above/star/superstar: [61, 46, 27, 12, 2]; holdout: [52, 20, 17, 9, 1]. Only two development and one holdout superstar support the primary tail. Class-conditional rarity and class imbalance make a low superstar Brier insufficient proof of accurate superstar calibration.
| MLB Pipeline rank / role | Minimal | Regular | Above | Star | Superstar | Superstar bootstrap90% range |
|---|---:|---:|---:|---:|---:|---:|
| 5 / H | 22.8% | 27.9% | 21.0% | 22.6% | 5.7% | 1.2–23.3% |
| 25 / H | 38.8% | 23.9% | 21.9% | 13.5% | 2.0% | 0.9–5.1% |
| 50 / H | 46.2% | 21.2% | 21.2% | 10.2% | 1.2% | 0.5–2.6% |
| 90 / H | 52.5% | 18.7% | 20.1% | 7.9% | 0.7% | 0.3–1.7% |
| 5 / P | 18.6% | 54.0% | 14.9% | 9.0% | 3.5% | 0.8–11.8% |
| 25 / P | 31.6% | 46.2% | 15.6% | 5.4% | 1.2% | 0.6–2.4% |
| 50 / P | 38.2% | 41.6% | 15.3% | 4.2% | 0.7% | 0.4–1.4% |
| 90 / P | 44.1% | 37.3% | 14.8% | 3.3% | 0.5% | 0.2–0.9% |

These probabilities are fitted research estimates, not probabilities licensed for any current player. Bootstrap ranges condition on fixed definitions and training resamples containing all classes;171/200 fits survive that filter. They omit source, class-definition and distribution-shift uncertainty. For decisions, use broad scenarios rather than the displayed decimals. Empirical holdout rank/role bins with Wilson intervals are saved. The Pipeline app's 260 league prospects are not automatically equivalent to these MLB.com national top100 ranks.

Threshold ±20% and COVID exclusion checks are saved. Merely changing the threshold changes the holdout superstar count from0 to7; annualizing 2020 in an earlier checkpoint changed the primary count from1 to4. Final results use actual 2020 output, with annualized calculations retained as checkpoint-v1-annualized-covid.json. No invented full-season 2020 production enters the final primary labels. Checkpoint-v0 documents the earlier clipped-surplus label approach. These methodology diagnostics inspected the holdout; therefore this is preliminary temporal validation, **not a pristine final confirmation set**. Freeze a full definition now and reserve additional historical years before claiming a statistically defensible final calibration.

## Unified architecture and trade comparisons

Keep four distinct ledgers: intrinsic contribution distribution; replacement difficulty/signed opportunity loss; acquisition scarcity (verified alternatives and asking prices); owner-specific timing/nonlinear utility. Nonlinear utility applies once per asset's outcome distribution. Summing a package and then raising the total to a convex power creates an artificial package-size premium. Synthetic elite-MLB, elite-prospect, hitter/SP, prospect/MLB, pick-package and large-consolidation stresses demonstrate this failure and the per-asset alternative. They do not supply an optimized roster or empirical current pick distributions. No arbitrary capacity or scarcity bonus was added.

saved-U2-comparisons.json copies the already completed Live/CandidateA/U2 comparisons without rerunning or altering them. The selected current negotiations and historical trades remain stress cases, never training targets. The following table reproduces earlier neutral first-side net results; units differ across models and these are **not new calibrated fairness conclusions**.

| Preserved case | Production snapshot | Candidate A | U2 | Phase1 new trade score |
|---|---:|---:|---:|---|
| Josuar negotiation | -39.84 | 7.39 | 10.08 | Not estimated |
| trade-export-005 | 30.79 | -1.10 | -3.99 | Not estimated |
| trade-export-029 | -222.21 | -128.30 | -125.14 | Not estimated |
| trade-export-039 | 183.31 | 27.68 | 21.80 | Not estimated |

The underlying dates, sides and all owner modes are retained in the JSON. Acuña and Guerrero packages contain injured pitchers/uncertain roles; the missing injury and role-specific horizon evidence prevents new reliable rankings. Josuar/De Vries and fifth-round selections lack a validated dated prospect/draft-slot input mapping. Historical THEN must use only transaction-date rankings, health and production; NOW may use present evidence; REALIZED SO FAR records outcomes separately. This checkpoint does not train THEN values using eventual outcomes of those trades. A historical trade's recorded completion is not a fairness observation.

## Remaining weaknesses and next steps

Before a next implementation stage:

1. Complete game-level QA3 with custom thresholds, league weekly category distributions and combined-roster ratio math. Re-test SP/RP/hitter scales including 35-IP weekly eligibility; do not equalize role means.
2. Verify archive snapshots, expand non-overlapping earlier cohorts and reserve untouched later evaluation years. Add full fantasy outcome definitions, delayed arrivals/right censoring and competing-risk or hierarchical tail models. Validate reliability plots and uncertainty coverage with enough stars/superstars.
3. Assemble dated FV/tools/level, minor-league production and injury reports for both training and holdout. Separate scouting changes from ranking movements; test incremental predictive benefit on matched cohorts.
4. Cross-check player identity/missing production independently, validate genuine two-way roles, fit multi-year durability distributions and position-specific historical replacements. Roster-depth cutoffs are proxies only.
5. Only after foundational review, proceed to user-approved Phase2: verified Fantrax available prospects, FYPD historical outcomes/class strength, real roster/IR/eligibility/opening obligations. Keep the corrected 20-round rule: Rounds 1–5 are the only tradable picks; Rounds 6–20 are acquisition access, never standalone trade assets. Do not assume 15 usable openings.
6. Joint before/after roster optimization remains deferred. It must count each replacement opportunity and nonlinear superstar benefit once, with acquisition feasibility and legal roster capacity, not gross incoming-slot bonuses.

**Readiness: not ready for live implementation, a replacement production formula, or unrestricted Phase2 application.** The architectural correction and cached historical components merit continued offline calibration after review. No calibrated current-asset ranking, acquisition-scarcity price, full-league pitcher/hitter exchange rate, FYPD forecast or roster benefit is claimed.

## Reproduction and saved checkpoints

Python scripts run only in this research directory. Extract raw-data.zip here, install requirements.txt, then run `python diagnostics.py` and `python verify.py`. diagnostics.py imports analyze.py and writes its results; do not run both just to reproduce once. make_report.py rebuilds this review. collect.py optionally refetches missing primary sources; reproduction uses cached data and hashes. resolve.py is the identity research aid; explicit reviewed overrides are already cached. The reference U2 source is the adjacent 2026-10-07 research directory, with a local-workspace fallback for this session only. No script imports, writes or activates the production analyzer.

Artifacts: methodology report; sources.json; raw-data.zip; results/validation.json; diagnostics.json; cohort.json; identity-unresolved.json; saved-U2-comparisons.json; two earlier diagnostic checkpoints; production-before.json; scripts and dependency versions. Hash manifest covers files inside the package; the final preservation receipt is recorded separately. Production model hash before preservation matches the frozen U2 input. Phase1 remains an offline research checkpoint; Phase2 has not started.
