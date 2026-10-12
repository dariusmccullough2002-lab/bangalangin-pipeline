# Ranking-led valuation of debuted rookies

## Result and recommendation

**Use the supplied fantasy prospect ranking as the dominant dynasty-value anchor, retain that anchor after debut, and make small, disclosed model adjustments from supported talent-rate evidence.** Keep this policy value separate from the model's expected category contribution. A short debut is not evidence that a player's future capacity is only that short season.

The reference sensitivity on the existing calculator scale gives **Josue De Paula 51.6**, **Leo De Vries 50.9**, **Kaelen Culpepper 25.9**, **Walker Jenkins 38.0**, and **Kade Anderson 38.0**. These are **proposed ranking-policy values**, not calibrated transaction prices or a newly validated eight-year forecast. Production remains unchanged. All44 supplied debuted prospects are covered.

The research supports the architecture and removal of the first-appearance valuation cliff. It does **not** establish an optimal weighting strength. The limited chronological test favors combining ranking and rate information, but its uncertainty and different historical provider prevent an accuracy claim for the uploaded ranking or these particular prices. The reference600PA/170IP uses inherited reliability scales as a conservative comparator, not a newly discovered optimum.

## What is valued, and how

1. **Ranking anchor.** Join the uploaded500-player table by exact stable Fantrax ID. Fit a decreasing isotonic rank-to-value curve using221 currently modeled, non-debuted pure prospects and their deployed neutral values. Exclude all rookies from fitting. This places the new ranking on the existing calculator's internal scale and prevents damaged rookie means from setting the scale. It is internal-scale calibration, not market-price or outcome calibration. Piecewise-flat values are intentional: ordinal rank differences do not establish precise value gaps.
2. **Independent model disagreement.** Use production-regressed talent rates at fixed historical role-reference workloads. Hitter signals use HR, SB, AVG and OPS components; omit R/RBI context and known RBI-rate bias. Pitcher signals use ER, K, K/BB and WHIP components; omit saves, holds and relief QA3 opportunities. No full-season workload is substituted into projected contribution. Own-model injury, age, ETA or level premiums are not added without independent, validated inputs.
3. **Dominant ranking.** In log-rank space, effective_rank=exp[(1−w)log(source_rank)+w log(model_rank_signal)]. Model weight w=.5×career_exposure/(career_exposure+K), so the source carries more than half the weight while listed. Half is the user's ranking-dominance policy constraint, not a fitted coefficient. Strength sensitivities are150/300/600/1200PA and42.5/85/170/340IP. Bound movement to immediately neighboring source tiers. Tier bounds and population-percentile mapping are disclosed policy assumptions, not calibrated posterior probabilities.
4. **Evidence required.** Hitters receive rate-based deviations where production rates exist. Pitchers need at least ten verified appearances and a supported pure-relief or strong-starting role before a deviation; a brief relief debut cannot establish a future bullpen assignment. All19 supplied debuted pitchers fall below the supported role criterion in this snapshot and retain their source anchors. All25 supplied debuted hitters receive bounded deviations:14 move down in effective rank and11 move up. Nineteen pitchers retain rank; plateaued curves can leave a value unchanged even when effective rank moves.
5. **Continuous transitions.** The source registry persists by identity after firstPA/IP and after eligibility changes. Load a fixed, versioned value curve; do not refit it just because a player debuts. A later source omission alone is not proof of graduation or zero value. For explicitly confirmed graduation, a separate engineering prototype saves the last policy value and exposure, then transitions toward a supported MLB estimate using only *new* exposure, delta/(delta+K). This graduation-price rule is unvalidated and not deployed; it is documented separately as a post-scoring continuity amendment.

The current source publication date/provider is not established. The snapshot already marks44 players debuted and may incorporate the same statistics as our model. This is a disagreement ensemble, not independent Bayesian updating; a model adjustment must not be presented as fresh information that the source has never seen.

## Player results

|Player|Source rank|Deployed value|Source-only anchor|Reference policy value|Source weight|Strength sensitivity range|
|---|---:|---:|---:|---:|---:|---:|
|Josue De Paula|3|20.04|52.02|51.61|96.7%|49.35–51.82|
|Leo De Vries|4|50.87|50.87|50.87|100%|50.87|
|Walker Jenkins|8|14.56|38.02|38.02|93.3%|33.30–38.02|
|Kade Anderson|9|11.45|38.02|38.02|100%|38.02|
|Kaelen Culpepper|41|15.80|25.85|25.85|91.2%|21.71–25.85|
|Emmanuel Rodriguez|76|6.75|20.14|20.14|96.3%|17.38–20.14|

Sensitivity ranges span the four fixed strengths. They are **not confidence intervals** or estimated market-price ranges.

De Paula's42PA can nudge his effective rank from3 to3.36 in the reference version, rather than replacing his prospect standing with an MLB-only value. Culpepper's128PA moves41 to48.15; the internal-scale curve is flat in that region, leaving25.85. Their first-year expected projections remain exactly those of production. The stronger ranking anchor accounts for the major value change; it does not forecast more playing time or assert better first-year statistical accuracy.

The largest positive reference changes include De Paula(+31.57), Angel Genao(+28.17), Kade Anderson(+26.58) and Jenkins(+23.46). These are consequences of the explicit source policy and source updates, not independently measured intrinsic-value gains.

## Historical check: a different, longer target

The prior unsuccessful repairs tried to improve *next-season expected contribution*. This research instead checks whether rankings plus a bounded rate signal discriminate **three-year discounted realized league contribution**, including subsequent absent seasons. It does not compare these current prices against historical transaction prices.

Use dated, preserved FanGraphs rankings, never the2026 supplied list. Ranks must precede or share the first MLB year and be no more than two years old at forecast. Include first/second positive MLB seasons, career exposure<=600PA or170IP, and three fully observed future years. All predictors use forecast-date information. Fixed league components, ratio formulas, replacement floors, utility and.88 discount are preserved; no pitcher/hitter equalization or RP penalty.

There are167 chronological player-origin cases:113 development origins2013–2015 and54 later origins2016–2017, representing45 later players. The freshness and first/second-season requirements leave no later2018–2022 cases. These previously inspected cases are **not a fresh independent holdout**. Historical ranking files are incomplete, so the historical model-rank proxy uses a generic top100 percentile mapping rather than the current full500-list family mapping. No current-source price curve is used in historical predictions. Same-year source independence is verified at season granularity, not an exact in-season timestamp.

|Later within-origin pair ordering accuracy|All54 cases|Small-debut24 cases|
|---|---:|---:|
|Dated ranking alone|51.6%|62.8%|
|Model-only talent-rate rank proxy|66.7%|57.9%|
|Faster ranking-led sensitivity|59.7%|66.9%|
|Medium sensitivity|58.3%|65.4%|
|Reference600PA/170IP|55.2%|63.9%|
|Slower sensitivity|53.7%|63.2%|

Small debut means below250PA or50IP. Across54 cases, source-only Spearman is.070 and reference is.189; across the24 small-debut cases, they are.407 and.428. Later role coverage is31 hitter cases,19 starter cases and only4 reliever cases; the latter cannot support RP-specific conclusions. Pair counts are dependent comparisons, not732 independent player observations.

The identity-cluster bootstrap95% interval for reference minus source pair accuracy is approximately **−0.6 to+9.9 percentage points**, including no improvement. Faster adjustments outperform the conservative reference in this exposed sample, but no strength is declared an optimal calibrated choice. Model-only rate ranking is strongest overall, while rankings alone outperform it among the small-debut subset: this supports retaining the source early and allowing stronger MLB evidence to matter as players establish themselves. The source-dominance preference is still a user policy constraint, not the empirically best unconstrained forecast.

## Trade-scale implications

On the reference policy, De Paula51.61 sits close to deployed Wheeler53.01, rather than far below him at20.04. Culpepper25.85 remains below Olson32.88. Jenkins38.02 moves above Langeliers31.07. Kade Anderson38.02 moves well above Brash12.75. Established-player values are unchanged in these comparisons. These are illustrative package arithmetic on the calculator scale, **not claims that those trades are fair market exchanges**. See Trade_Scale_Examples.csv.

## Coverage and limitations

-500 supplied records and500 unique IDs;265 modeled catalog matches;235 unsupported outside the current modeled catalog. Unsupported players receive no fabricated value. All44 supplied debuted players match and receive policy comparisons. Existing supported assets outside the list are preserved.
-221 non-debuted pure prospects set the internal-scale curve. Their existing model uncertainties, weak upper-tail calibration, provider mapping and provisional replacement inputs are inherited. The new curve does not resolve them.
-Current and historical talent percentiles compare different populations from the external prospect ranking. They are *proxy signals*, not independently calibrated equivalent prospect ranks. Modern run environments can also differ from frozen2010–2012 references.
-Source ranking likely already incorporates age, ETA, health, skill and some MLB evidence. No blanket extra age/ETA/injury discount or additive upside bonus was applied. No validated new MiLB skill translations were available for numerical deviations; their absence is not negative evidence.
-Role certainty, prospect-list omissions, scouting-source updates and confirmed graduation need explicit provenance. No future bullpen assignment was inferred. Talent rates remain unchanged.
-No independent eight-year dynasty-price validation, completed current-rookie future outcomes or completed league transaction-price data support the point values. Three-year discrimination cannot establish those prices or eight-year forecast accuracy.

## Reproduce and integrate for review

```sh
python research/ranking-led-rookies-20261012/run.py ../model-recovered
python research/ranking-led-rookies-20261012/finalize.py
python research/ranking-led-rookies-20261012/test_policy.py
```

Recover the preserved verified V2.3C model package; do not rerun old collectors or overwrite its inputs. Initial protocol was committed locally before scoring at `f3e5fff` and signal details at `6fb1cc2`. Continuity_Amendment.json records the later engineering addition without pretending it was prescore or retuning outcomes.

Outputs include every current comparison, all44 debuted examples, unsupported IDs, largest changes,167 historical cases/results, versioned rank-value curve, stable policy registry, transition checks and a read-only integration adapter. Six regression tests verify all265 current policy values, all44 rookie IDs, source dominance, zero-to-positive continuity, fixed calibration, and graduation/omission behavior. Production's projection, valuation, ranking and trade files retain their original hashes.

**Recommended next model design:** expose ranking-policy trade values alongside contribution fundamentals; use the versioned source registry and fixed curve so debut metadata cannot erase scouting value. Treat the conservative reference and faster variants as reviewable policy alternatives. Do not overwrite expected forecasts or claim an optimal calibrated price until the updated ranking provider and long-horizon/transaction evidence support it.

## External context

- [MLB rookie eligibility](https://www.mlb.com/glossary/rules/rookie-eligibility): eligibility involves at-bats, innings and active-roster time; debut alone does not determine graduation. Eligibility is not used as this policy's price switch.
- [FanGraphs2026 prospect methodology](https://blogs.fangraphs.com/2026-top-100-prospects/): scouting grades matter more than precise ordinal positions. This motivates disclosing source-tier bounds rather than treating adjacent ranks as exact price differences. The supplied fantasy list is not represented as that FanGraphs list.
