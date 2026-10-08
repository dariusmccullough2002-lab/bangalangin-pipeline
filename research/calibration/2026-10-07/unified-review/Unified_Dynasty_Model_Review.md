# Unified Dynasty Asset Model — Offline Review

October 7, 2026 · BangaLangin Pipeline · No deployment or repository changes

## Decision

Recommend the **U2 architecture: a common distribution of future fantasy contribution, valued above available league replacement, with nonlinear utility applied to outcome states before taking expectations**. Combine it with roster optimization; the smooth capacity curve below is only an interim proxy.

**Do not approve these numerical coefficients for production yet.** The experiments compare coherent architectures, but incomplete inputs prevent a calibrated dynasty-market estimate. U3's risk overlay produces pathological zero values for some prospects, and even U2 remains vulnerable to one-year MLB outliers and unobserved prospect replacement. None was fitted to trade equality. The previous package-only Candidate A remains undeployed; “U1” below is a new unified linear experiment, not that Candidate A.

The live compact two-sided UI is unchanged. Main remains commit `cba5e8095a91e9ef5c3fe776ec9d7d78b8005013`, verified read-only at the end of this review. No Fantrax data was recollected.

## Three clocks: THEN, NOW, REALIZED SO FAR

| View | Question | Inputs allowed | Status in this review |
| --- | --- | --- | --- |
| THEN | What did each asset plausibly offer on the trade date? | Only evidence published and available by that date; contemporaneous projections, health, ranks, contracts, slots and ownership | Not estimated: reliable trade-date snapshots are missing |
| NOW | What are the same original assets worth with current information? | October snapshot, with source dates exposed | All numerical historical comparisons below |
| REALIZED SO FAR | What actually happened after the trade? | Dated game production, injuries, promotions, prospect development, picks exercised and later transfers | Not estimated: season aggregates cannot isolate post-trade outcomes |

Trade agreement is not a fairness label. No parameters are optimized against the transaction prices, number of winners, or closeness to zero. The Guerrero and Acuña results are NOW stress tests, not judgments about their February/March prices. NOW includes information that would be leakage in a THEN model; it is explicitly not used to train THEN.

A future historical ledger should preserve immutable Fantrax IDs, original sides, trade timestamps and evidence timestamps. A pick becomes a selected prospect in the realized ledger: count the descendant once, not the pick plus the player. Separate production of the original asset after the trade from production actually received by an owner after subsequent transfers. Full-season totals are neither measure.

## Evidence audit

The snapshot contains 10,616 unique player IDs and 180 unique pick IDs. There are 9,795 free agents, including 147 with at least 150 AB and 251 with at least 30 IP. **Zero of the 260 Pipeline-evaluated prospects is currently unowned.** This permits an MLB replacement estimate but not an observed ranked-prospect replacement estimate.

The domestic draft file contains 112 profiles; 110 have Pipeline class ranks. Only one matches the baseline through MLBAM ID, and that player is owned. There are no recorded actual FYPD selections. Thus the draft file cannot tell us which ranked players are truly available after Round 5. No name-only crosswalk is used.

The league-rules attachment lists a 17-round draft and five tradable rounds. The Rule 5 proposal describes a **five-round FYPD**, apparently a separate event, and explicitly says its temporary expansion is illustrative. This supports testing a five-round FYPD, but does not establish its final cutdown, waiver access, adoption of Rule 5, or actual post-draft pool. The prototype's “after 60 selections” assumption is not presented as an observed pool.

The August Top 30 workbook and old Shea-only roster are historical material, not current October evaluations or a league-wide replacement census. No uploaded file was edited. Current values use the persisted October roster snapshot, prospect ranks/ETAs and dated scouting observations. Fantrax IDs remain primary keys, including duplicate-name players; pick identity is year + round + original owner.

The baseline supplies only 2026 production. Verified 2023–2025 regular-season batting lines were added for Acuña and Guerrero as a limited methodology demonstration. Other MLB players use explicitly marked single-season fallbacks. No current 2027 projection feed, league-wide contract audit, medical prognosis, career eligibility census or measured weekly matchup distribution was fabricated.

## One underlying economy

For every asset, first infer a distribution over yearly MLB category contributions and availability. A prospect is a distribution of future MLB careers; a pick is a distribution of prospects selected from an eligible draft pool. Neither receives an independent points curve.

For outcome `s`, year `t` and owner `o`:

`asset utility = Σ_t horizon_weight[o,t] × E_s[utility(category surplus[s,t])]`

`trade net = utility received − utility surrendered + change in roster opportunity cost`

Replacement surplus is measured before the utility transform. The same transform and category units apply to all three classes. A constant contribution stream has the same total value under each owner mode; preferences change the timing, not the class conversion rate. Neutral is a patient market reference; Balanced is a distinct owner timing preference. The live model uses Balanced as Neutral, which is disclosed in the before columns.

### MLB forecast design

Use multi-year rate estimates with recency, sample-size regression and a projection ensemble. Forecast talent, playing time and health separately. A healthy-state star can retain high ability during a missed season while expected availability declines. Replacement fill-in can cover missed time; no extra generic injury discount should repeat that reduction. Contract/free agency is evidence about role and playing time, not a direct salary penalty in this no-salary league.

Forecast workload, lineup position, starts, save/hold opportunities, role competition, recovery and age-dependent rates. Use empirical aging by skill and role; speed, power and pitcher workload should not share one decay rate. Defensive real-life WAR is not a fantasy utility unit.

Evaluate C/MI/CI/OF eligibility and pitcher roles through feasible lineup assignment against actual free agents. Do not add a generic scarcity bonus on top of a position-specific replacement adjustment. A position's extra value is the improvement over the next feasible alternative.

Ratios must be recalculated on the whole projected roster: hits/AB, OBP components and slugging, K/BB, and baserunners/IP. QA3 requires game-level probability of ≥5 IP and ≤2 ER or ≥6 IP and ≤3 ER. SVH7 is 3SV + 2HLD. The weekly 35-IP minimum is a constraint; low ER from too little pitching cannot be rewarded as a successful strategy. Use the Fantrax zero-walk adjustment when calculating whole-roster K/BB, not summed pitcher ratios.

### Prospect distributions and superstar probability

Use five outcomes: minimal/bust, regular, above-average fantasy regular, star and superstar. Separately estimate arrival time, probability of reaching useful MLB play, healthy workload and conditional ceiling. Pitchers and hitters need different outcome priors, with pitchers' attrition and role changes represented.

Rank/tier is a prior, not complete identity. Scouting tools, age relative to level, approach/contact, power/speed, role, performance translated by level and athleticism can update that prior. Use structured sourced evidence, not unsourced narrative sentiment. FV/rank already encode some of these traits: do not multiply rank, FV, tools, age and an elite premium independently. Apply residual evidence once, or build a single joint model.

The prototype demonstrates a narrow tool-based shift toward the upper tail while holding rank-based MLB contribution probability fixed. That residual shift is **unvalidated and may still double-count rank evidence**; the rank-only ablation is included. Age presently affects future aging, ETA affects access, and tools affect the tail; performance, tier and athleticism are not numerically inferred from incomplete prose.

An elite-prospect scarcity premium and superstar probability are not automatically separate bonuses. Superstar probability changes the outcome distribution. Scarcity enters through the common nonlinear value of superstar outcomes, also used for MLB stars. Add a further prospect liquidity premium only if independent league demand supports it; none is added here.

For example, equally likely outcomes 3/5 and 0/8 have the same mean annual surplus of 4. Under a linear utility they are equal. With a 1.35 exponent, the wider upper-tail distribution is worth about 25% more before owner risk preferences. This demonstrates the mechanism, not any player's measured probabilities.

### Pick translation

At each possible slot, simulate the eligible remaining pool and selection policy. Translate the chosen player's outcome distribution through the same prospect → MLB machinery. Average over the slot range; carry class quality uncertainty, signing/eligibility, selection risk and years of delay. Unknown 2028/2029 classes stay neutral with broad uncertainty, not an invented research premium. Preserve existing ownership, including unchanged 2029 original ownership.

The prototype averages twelve class-rank slots per round, with early/late four-slot scenarios. The 2027 proxy uses saved domestic class ranks and DD overall ranks when available; unranked profiles use a disclosed weaker prior. Future classes reuse this distribution as a hypothetical template. This is not a realistic full draft-choice simulation: ranks mix sources and do not establish fantasy outcome probabilities. No 2028/2029 class research is claimed.

Pick value subtracts an assumed post-FYPD access option on the same latent scale. This is **exclusivity over a free acquisition opportunity**, not roster cost. Roster cost covers future occupied capacity. Those are economically distinct, but the option must disappear or change if those players cannot actually be acquired for free. A future implementation should value draft decisions and retention jointly, eliminating overlap rather than stacking opaque discounts.

## Candidate experiments and coefficients

All three experiments share an eight-season 2027–2034 horizon, 0.88 annual discount, the same observed MLB surplus distribution, player identity and draft translation. This longer horizon prevents a 2029 debut from having almost no value solely because of a three-year cutoff. No terminal value is included; horizon sensitivity exposes that limitation.

U1 uses linear annual surplus. U2 uses `10 × (surplus / observed owned-player 90th-percentile surplus)^1.35`, applied to each outcome before expectation. U3 adds an illustrative certainty-equivalent risk deduction to U2: Neutral 0, Contender .30, Balanced .15 and Rebuild .06 times forecast dispersion. These are experimental preferences, not inferred owner behavior.

The category units are observed dispersion among qualified owned players. AVG/OPS and pitcher ratios use marginal numerator proxies at .250 AVG, .720 OPS, K−3BB and a 1.25 WHIP baseline. That is more consistent than class-specific points, but remains an annual proxy, not measured category-win probability. Raw ER uses its own dispersion. The full weekly optimization is still required.

Rates shrink toward qualified-player cohort rates with 100 PA / 30 IP prior strength. Acuña/Guerrero histories use .1/.2/.3/.4 weights for 2023–2026; all others use 2026 only. Healthy reference workloads are 600 PA, 170 SP IP and 65 RP IP, with observed exposure limiting expected workload. Decline beyond 29 is 4.5%/year for hitters and 7% for pitchers: transparent priors, not fitted curves. Replacement is the median of the best five same-position/role free agents at observed workload, not a guaranteed full season extrapolated from a small sample.

Prospect outcomes are anchored to owned MLB surplus percentiles 30/60/85/98 in the relevant role. These labels are provisional: some pitching “regular” anchors equal zero surplus. Rank contribution probability is `.22 + .58 exp(-(rank−1)/160)` (bounded .12–.88), with conditional superstar probability `.015 + .20 exp(-(rank−1)/35)` and star probability `.07 + .25 exp(-(rank−1)/100)`. Arrival ramps over two seasons. An unobserved rank-400/2030 prospect is the default free-prospect proxy; 250/600 are sensitivities. These probabilities are hypotheses, **not measured historical success rates**.

Owner timing multipliers before equal-total normalization: Contender 3/1.5/.7/.25 thereafter; Balanced 1.2 for the first three years/.85 thereafter; Rebuild .2/.5/1.2 thereafter; Neutral 1 throughout. No class-specific future multiplier is added. This retains two-sided utility: receiver and sender apply their own timing to the same asset distribution.

## Smooth consolidation

The target is a before/after constrained roster optimizer: choose starts, reserves and minors, respect career eligibility, IR and weekly innings, and retain the best feasible portfolio. Extra assets displace actual bench alternatives. Strong additions remain valuable; weak overlapping assets can have little marginal utility. An open roster can accept a large package without an arbitrary package-size penalty.

The offline substitute is a smooth capacity-cost function `C(x) = λτ log(1 + exp(x/τ))`, with change `C(net load − free slots) − C(−free slots)`. Default λ=3, τ=2, two free spots. Every player occupies one proxy slot. Picks carry discounted future draft-year occupancy, **not an immediate current slot**; there is no separate package diminishing multiplier or flat pick fee. This fractional future-load approximation is not a true calendar capacity optimizer. Replacement quality and actual team occupancy do not yet set λ or free spots.

A negative cost is a freed-capacity credit. It is bounded by previously occupied capacity in the proxy, not a large bonus for any 1-for-many trade. Both owners' costs are calculated separately; net values need not sum to zero because capacity is scarce.


| Net extra incoming players | Capacity cost (two open spots) |
| --- | --- |
| 0 | 0.0 |
| 1 | 1.0 |
| 2 | 2.3 |
| 3 | 4.0 |
| 4 | 6.0 |
| 5 | 8.3 |
| 6 | 10.9 |
| 7 | 13.6 |
| 8 | 16.4 |
| 9 | 19.3 |


For literal 2-for-1/3-for-1/5-for-1/9-for-1 player packages, net additions are 1/2/4/8. Costs are 1.0/2.3/6.0/16.4. The curve has no behavioral switch at three assets. Pick-heavy packages differ according to arrival years, not just count.

## Required stress tests — raw asset totals before consolidation

Left/right is **assets sent by the two named owners**, not an assumed winner. Each historical row uses October information. Different candidates have different scales: compare ratios and net direction, not the absolute point difference between Live and U2. Rounding is presentation only. Neutral Live equals its Balanced calculation.


### Josuar negotiation · 2026-10-07

Left: **Shea Stadiums** sends Felnin Celesten, Jack Wenninger, 2027 R5 · Shea Stadiums, 2027 R5 · Young Guns, 2028 R2 · Shea Stadiums.

Right: **The Sandlot Sluggers** sends Josuar Gonzalez.

Negotiation; not completed.


| Perspective | Live left / right | U1 left / right | U2 left / right | U3 left / right |
| --- | --- | --- | --- | --- |
| Neutral | 86.5 / 46.7 | 17.1 / 23.0 | 14.7 / 23.3 | 14.7 / 23.3 |
| Contender | 72.3 / 30.0 | 15.1 / 11.4 | 12.9 / 11.4 | 5.2 / 2.8 |
| Balanced | 86.5 / 46.7 | 17.2 / 21.9 | 14.8 / 22.1 | 9.7 / 17.8 |
| Rebuild | 100.7 / 66.9 | 17.8 / 28.4 | 15.4 / 28.8 | 12.9 / 27.1 |


U2 owner summaries (each row assumes both owners use that perspective; actual mixed preferences follow below):


| Perspective / owner | Surrendered | Received | Roster adjustment | Final net |
| --- | --- | --- | --- | --- |
| Neutral / Shea Stadiums | 14.7 | 23.3 | 1.5 | 10.1 |
| Neutral / The Sandlot Sluggers | 23.3 | 14.7 | -5.0 | -13.6 |
| Contender / Shea Stadiums | 12.9 | 11.4 | 1.5 | 0.0 |
| Contender / The Sandlot Sluggers | 11.4 | 12.9 | -5.0 | -3.5 |
| Balanced / Shea Stadiums | 14.8 | 22.1 | 1.5 | 8.9 |
| Balanced / The Sandlot Sluggers | 22.1 | 14.8 | -5.0 | -12.4 |
| Rebuild / Shea Stadiums | 15.4 | 28.8 | 1.5 | 14.9 |
| Rebuild / The Sandlot Sluggers | 28.8 | 15.4 | -5.0 | -18.4 |


### trade-export-005 · 2026-07-27

Left: **How Lowe Can You Go?** sends Leo De Vries.

Right: **Shea Stadiums** sends Casey Schmitt, 2027 R4 · Shea Stadiums, 2028 R4 · Shea Stadiums, 2027 R2 · Shea Stadiums.

NOW stress test; THEN and REALIZED unestimated.


| Perspective | Live left / right | U1 left / right | U2 left / right | U3 left / right |
| --- | --- | --- | --- | --- |
| Neutral | 65.7 / 96.5 | 30.9 / 32.9 | 31.4 / 30.5 | 31.4 / 30.5 |
| Contender | 54.2 / 88.5 | 26.7 / 31.9 | 26.8 / 30.1 | 18.1 / 27.9 |
| Balanced | 65.7 / 96.5 | 30.8 / 32.7 | 31.2 / 30.4 | 26.9 / 27.4 |
| Rebuild | 77.2 / 104.3 | 32.5 / 33.4 | 33.2 / 30.7 | 31.4 / 28.8 |


U2 owner summaries (each row assumes both owners use that perspective; actual mixed preferences follow below):


| Perspective / owner | Surrendered | Received | Roster adjustment | Final net |
| --- | --- | --- | --- | --- |
| Neutral / How Lowe Can You Go? | 31.4 | 30.5 | -3.1 | -4.0 |
| Neutral / Shea Stadiums | 30.5 | 31.4 | 1.3 | 2.1 |
| Contender / How Lowe Can You Go? | 26.8 | 30.1 | -3.1 | 0.2 |
| Contender / Shea Stadiums | 30.1 | 26.8 | 1.3 | -2.1 |
| Balanced / How Lowe Can You Go? | 31.2 | 30.4 | -3.1 | -3.9 |
| Balanced / Shea Stadiums | 30.4 | 31.2 | 1.3 | 2.1 |
| Rebuild / How Lowe Can You Go? | 33.2 | 30.7 | -3.1 | -5.6 |
| Rebuild / Shea Stadiums | 30.7 | 33.2 | 1.3 | 3.8 |


### trade-export-029 · 2026-03-03

Left: **How Lowe Can You Go?** sends Jacob Misiorowski, Munetaka Murakami, Eury Perez, Kyle Bradish, Luis Robert Jr., Emil Morales, Eli Willits.

Right: **Shea Stadiums** sends Ronald Acuna Jr..

NOW stress test; THEN and REALIZED unestimated.


| Perspective | Live left / right | U1 left / right | U2 left / right | U3 left / right |
| --- | --- | --- | --- | --- |
| Neutral | 273.9 / 51.7 | 175.4 / 45.3 | 175.2 / 48.2 | 175.2 / 48.2 |
| Contender | 247.3 / 52.4 | 164.5 / 48.3 | 164.6 / 52.5 | 137.9 / 49.6 |
| Balanced | 273.9 / 51.7 | 175.1 / 45.9 | 174.8 / 49.1 | 161.5 / 47.6 |
| Rebuild | 303.0 / 50.1 | 180.4 / 43.9 | 180.0 / 46.2 | 174.6 / 45.7 |


U2 owner summaries (each row assumes both owners use that perspective; actual mixed preferences follow below):


| Perspective / owner | Surrendered | Received | Roster adjustment | Final net |
| --- | --- | --- | --- | --- |
| Neutral / How Lowe Can You Go? | 175.2 | 48.2 | 1.8 | -125.1 |
| Neutral / Shea Stadiums | 48.2 | 175.2 | -10.9 | 116.0 |
| Contender / How Lowe Can You Go? | 164.6 | 52.5 | 1.8 | -110.3 |
| Contender / Shea Stadiums | 52.5 | 164.6 | -10.9 | 101.2 |
| Balanced / How Lowe Can You Go? | 174.8 | 49.1 | 1.8 | -124.0 |
| Balanced / Shea Stadiums | 49.1 | 174.8 | -10.9 | 114.8 |
| Rebuild / How Lowe Can You Go? | 180.0 | 46.2 | 1.8 | -131.9 |
| Rebuild / Shea Stadiums | 46.2 | 180.0 | -10.9 | 122.8 |


### trade-export-039 · 2026-02-19

Left: **The Sandlot Sluggers** sends Vladimir Guerrero Jr..

Right: **TheMissingSox** sends Carter Jensen, Ryan Clifford, Hunter Gaddis, Adrian Morejon, Emmanuel Rodriguez, Jasson Dominguez, 2027 R1 · TheMissingSox, 2028 R1 · TheMissingSox, 2028 R2 · TheMissingSox.

NOW stress test; THEN and REALIZED unestimated.


| Perspective | Live left / right | U1 left / right | U2 left / right | U3 left / right |
| --- | --- | --- | --- | --- |
| Neutral | 39.6 / 262.9 | 36.4 / 78.9 | 31.9 / 68.5 | 31.9 / 68.5 |
| Contender | 39.1 / 241.9 | 38.1 / 71.1 | 33.9 / 60.9 | 32.0 / 50.6 |
| Balanced | 39.6 / 262.9 | 36.8 / 77.4 | 32.4 / 67.0 | 31.4 / 56.1 |
| Rebuild | 40.0 / 283.5 | 35.7 / 82.3 | 31.0 / 71.9 | 30.7 / 67.4 |


U2 owner summaries (each row assumes both owners use that perspective; actual mixed preferences follow below):


| Perspective / owner | Surrendered | Received | Roster adjustment | Final net |
| --- | --- | --- | --- | --- |
| Neutral / The Sandlot Sluggers | 31.9 | 68.5 | -14.8 | 21.8 |
| Neutral / TheMissingSox | 68.5 | 31.9 | 1.8 | -34.8 |
| Contender / The Sandlot Sluggers | 33.9 | 60.9 | -14.8 | 12.2 |
| Contender / TheMissingSox | 60.9 | 33.9 | 1.8 | -25.1 |
| Balanced / The Sandlot Sluggers | 32.4 | 67.0 | -14.8 | 19.9 |
| Balanced / TheMissingSox | 67.0 | 32.4 | 1.8 | -32.8 |
| Rebuild / The Sandlot Sluggers | 31.0 | 71.9 | -14.8 | 26.0 |
| Rebuild / TheMissingSox | 71.9 | 31.0 | 1.8 | -39.0 |


### trade-export-003 · 2026-08-07

Left: **Shea Stadiums** sends Yohandy Morales.

Right: **The Sandlot Sluggers** sends 2028 R2 · The Sandlot Sluggers.

NOW stress test; THEN and REALIZED unestimated.


| Perspective | Live left / right | U1 left / right | U2 left / right | U3 left / right |
| --- | --- | --- | --- | --- |
| Neutral | 18.2 / 24.6 | 4.5 / 1.3 | 4.7 / 1.1 | 4.7 / 1.1 |
| Contender | 18.0 / 21.0 | 4.6 / 0.3 | 4.7 / 0.3 | 4.5 / 0.0 |
| Balanced | 18.2 / 24.6 | 4.5 / 1.1 | 4.7 / 0.9 | 4.5 / 0.0 |
| Rebuild | 18.3 / 28.3 | 4.5 / 1.7 | 4.6 / 1.5 | 4.6 / 0.8 |


U2 owner summaries (each row assumes both owners use that perspective; actual mixed preferences follow below):


| Perspective / owner | Surrendered | Received | Roster adjustment | Final net |
| --- | --- | --- | --- | --- |
| Neutral / Shea Stadiums | 4.7 | 1.1 | 0.2 | -3.4 |
| Neutral / The Sandlot Sluggers | 1.1 | 4.7 | -0.2 | 3.3 |
| Contender / Shea Stadiums | 4.7 | 0.3 | 0.2 | -4.3 |
| Contender / The Sandlot Sluggers | 0.3 | 4.7 | -0.2 | 4.2 |
| Balanced / Shea Stadiums | 4.7 | 0.9 | 0.2 | -3.6 |
| Balanced / The Sandlot Sluggers | 0.9 | 4.7 | -0.2 | 3.5 |
| Rebuild / Shea Stadiums | 4.6 | 1.5 | 0.2 | -3.0 |
| Rebuild / The Sandlot Sluggers | 1.5 | 4.6 | -0.2 | 2.9 |


### trade-export-004 · 2026-07-27

Left: **How Lowe Can You Go?** sends Casey Mize.

Right: **The Sandlot Sluggers** sends Curtis Mead, 2027 R5 · The Sandlot Sluggers.

NOW stress test; THEN and REALIZED unestimated.


| Perspective | Live left / right | U1 left / right | U2 left / right | U3 left / right |
| --- | --- | --- | --- | --- |
| Neutral | 9.3 / 49.6 | 0.6 / 30.4 | 0.1 / 30.7 | 0.1 / 30.7 |
| Contender | 12.5 / 48.2 | 0.6 / 30.7 | 0.1 / 31.3 | 0.1 / 29.5 |
| Balanced | 9.3 / 49.6 | 0.6 / 30.4 | 0.1 / 30.8 | 0.1 / 29.9 |
| Rebuild | 5.0 / 50.8 | 0.5 / 30.2 | 0.1 / 30.4 | 0.1 / 29.9 |


U2 owner summaries (each row assumes both owners use that perspective; actual mixed preferences follow below):


| Perspective / owner | Surrendered | Received | Roster adjustment | Final net |
| --- | --- | --- | --- | --- |
| Neutral / How Lowe Can You Go? | 0.1 | 30.7 | -0.8 | 29.7 |
| Neutral / The Sandlot Sluggers | 30.7 | 0.1 | 0.6 | -30.0 |
| Contender / How Lowe Can You Go? | 0.1 | 31.3 | -0.8 | 30.3 |
| Contender / The Sandlot Sluggers | 31.3 | 0.1 | 0.6 | -30.5 |
| Balanced / How Lowe Can You Go? | 0.1 | 30.8 | -0.8 | 29.9 |
| Balanced / The Sandlot Sluggers | 30.8 | 0.1 | 0.6 | -30.1 |
| Rebuild / How Lowe Can You Go? | 0.1 | 30.4 | -0.8 | 29.5 |
| Rebuild / The Sandlot Sluggers | 30.4 | 0.1 | 0.6 | -29.7 |


### trade-export-013 · 2026-06-04

Left: **The Sandlot Sluggers** sends Ben Brown.

Right: **Young Guns** sends Jack Leiter, Travis Sykora.

NOW stress test; THEN and REALIZED unestimated.


| Perspective | Live left / right | U1 left / right | U2 left / right | U3 left / right |
| --- | --- | --- | --- | --- |
| Neutral | 24.9 / 45.5 | 9.7 / 6.9 | 7.4 / 5.7 | 7.4 / 5.7 |
| Contender | 24.6 / 38.2 | 10.4 / 6.0 | 8.1 / 4.9 | 7.3 / 0.9 |
| Balanced | 24.9 / 45.5 | 9.9 / 6.9 | 7.5 / 5.7 | 7.2 / 3.7 |
| Rebuild | 25.1 / 52.8 | 9.4 / 7.3 | 7.1 / 6.0 | 6.9 / 5.2 |


U2 owner summaries (each row assumes both owners use that perspective; actual mixed preferences follow below):


| Perspective / owner | Surrendered | Received | Roster adjustment | Final net |
| --- | --- | --- | --- | --- |
| Neutral / The Sandlot Sluggers | 7.4 | 5.7 | -1.0 | -2.7 |
| Neutral / Young Guns | 5.7 | 7.4 | 0.7 | 2.4 |
| Contender / The Sandlot Sluggers | 8.1 | 4.9 | -1.0 | -4.2 |
| Contender / Young Guns | 4.9 | 8.1 | 0.7 | 3.9 |
| Balanced / The Sandlot Sluggers | 7.5 | 5.7 | -1.0 | -2.8 |
| Balanced / Young Guns | 5.7 | 7.5 | 0.7 | 2.5 |
| Rebuild / The Sandlot Sluggers | 7.1 | 6.0 | -1.0 | -2.0 |
| Rebuild / Young Guns | 6.0 | 7.1 | 0.7 | 1.7 |


### trade-export-018 · 2026-05-01

Left: **Shea Stadiums** sends Hurston Waldrep.

Right: **Yoho and a Bottle of Rum** sends Elian Pena.

NOW stress test; THEN and REALIZED unestimated.


| Perspective | Live left / right | U1 left / right | U2 left / right | U3 left / right |
| --- | --- | --- | --- | --- |
| Neutral | 5.8 / 12.7 | 0.0 / 5.9 | 0.0 / 5.3 | 0.0 / 5.3 |
| Contender | 5.8 / 8.0 | 0.0 / 1.9 | 0.0 / 1.7 | 0.0 / 0.0 |
| Balanced | 5.8 / 12.7 | 0.0 / 5.3 | 0.0 / 4.7 | 0.0 / 2.0 |
| Rebuild | 5.8 / 20.3 | 0.0 / 8.0 | 0.0 / 7.0 | 0.0 / 6.0 |


U2 owner summaries (each row assumes both owners use that perspective; actual mixed preferences follow below):


| Perspective / owner | Surrendered | Received | Roster adjustment | Final net |
| --- | --- | --- | --- | --- |
| Neutral / Shea Stadiums | 0.0 | 5.3 | -0.0 | 5.3 |
| Neutral / Yoho and a Bottle of Rum | 5.3 | 0.0 | -0.0 | -5.3 |
| Contender / Shea Stadiums | 0.0 | 1.7 | -0.0 | 1.7 |
| Contender / Yoho and a Bottle of Rum | 1.7 | 0.0 | -0.0 | -1.7 |
| Balanced / Shea Stadiums | 0.0 | 4.7 | -0.0 | 4.7 |
| Balanced / Yoho and a Bottle of Rum | 4.7 | 0.0 | -0.0 | -4.7 |
| Rebuild / Shea Stadiums | 0.0 | 7.0 | -0.0 | 7.0 |
| Rebuild / Yoho and a Bottle of Rum | 7.0 | 0.0 | -0.0 | -7.0 |


### trade-export-019 · 2026-03-26

Left: **How Lowe Can You Go?** sends Jake Mangum.

Right: **Shea Stadiums** sends Tanner Scott.

NOW stress test; THEN and REALIZED unestimated.


| Perspective | Live left / right | U1 left / right | U2 left / right | U3 left / right |
| --- | --- | --- | --- | --- |
| Neutral | 32.3 / 25.0 | 14.6 / 18.7 | 10.1 / 13.1 | 10.1 / 13.1 |
| Contender | 35.5 / 27.8 | 15.9 / 21.1 | 11.2 / 15.4 | 10.6 / 13.9 |
| Balanced | 32.3 / 25.0 | 14.9 / 19.1 | 10.3 / 13.5 | 10.0 / 12.7 |
| Rebuild | 27.7 / 21.2 | 14.1 / 17.6 | 9.6 / 12.1 | 9.5 / 11.8 |


U2 owner summaries (each row assumes both owners use that perspective; actual mixed preferences follow below):


| Perspective / owner | Surrendered | Received | Roster adjustment | Final net |
| --- | --- | --- | --- | --- |
| Neutral / How Lowe Can You Go? | 10.1 | 13.1 | -0.0 | 3.0 |
| Neutral / Shea Stadiums | 13.1 | 10.1 | -0.0 | -3.0 |
| Contender / How Lowe Can You Go? | 11.2 | 15.4 | -0.0 | 4.2 |
| Contender / Shea Stadiums | 15.4 | 11.2 | -0.0 | -4.2 |
| Balanced / How Lowe Can You Go? | 10.3 | 13.5 | -0.0 | 3.2 |
| Balanced / Shea Stadiums | 13.5 | 10.3 | -0.0 | -3.2 |
| Rebuild / How Lowe Can You Go? | 9.6 | 12.1 | -0.0 | 2.5 |
| Rebuild / Shea Stadiums | 12.1 | 9.6 | -0.0 | -2.5 |


### trade-export-025 · 2026-03-04

Left: **Cafécitos de Spokane** sends Luis Garcia Jr., Ryan Weathers.

Right: **How Lowe Can You Go?** sends Wilyer Abreu.

NOW stress test; THEN and REALIZED unestimated.


| Perspective | Live left / right | U1 left / right | U2 left / right | U3 left / right |
| --- | --- | --- | --- | --- |
| Neutral | 88.2 / 54.9 | 66.0 / 29.0 | 63.7 / 23.4 | 63.7 / 23.4 |
| Contender | 87.1 / 54.3 | 68.1 / 30.3 | 66.3 / 24.9 | 62.4 / 23.5 |
| Balanced | 88.2 / 54.9 | 66.5 / 29.3 | 64.3 / 23.7 | 62.3 / 23.1 |
| Rebuild | 89.0 / 55.4 | 65.1 / 28.4 | 62.5 / 22.8 | 61.7 / 22.5 |


U2 owner summaries (each row assumes both owners use that perspective; actual mixed preferences follow below):


| Perspective / owner | Surrendered | Received | Roster adjustment | Final net |
| --- | --- | --- | --- | --- |
| Neutral / Cafécitos de Spokane | 63.7 | 23.4 | 0.7 | -39.6 |
| Neutral / How Lowe Can You Go? | 23.4 | 63.7 | -1.0 | 39.3 |
| Contender / Cafécitos de Spokane | 66.3 | 24.9 | 0.7 | -40.8 |
| Contender / How Lowe Can You Go? | 24.9 | 66.3 | -1.0 | 40.5 |
| Balanced / Cafécitos de Spokane | 64.3 | 23.7 | 0.7 | -39.9 |
| Balanced / How Lowe Can You Go? | 23.7 | 64.3 | -1.0 | 39.6 |
| Rebuild / Cafécitos de Spokane | 62.5 | 22.8 | 0.7 | -39.1 |
| Rebuild / How Lowe Can You Go? | 22.8 | 62.5 | -1.0 | 38.8 |


## Current negotiation — actual mixed owner preferences

Shea uses Contender; Sandlot uses Rebuild. The same incoming and outgoing assets are evaluated independently under each owner’s preference.


| Model / owner | Surrendered | Received | Roster adjustment | Net |
| --- | --- | --- | --- | --- |
| Live / Shea Stadiums (contender) | 72.3 | 30.0 | 0.0 | -42.3 |
| Live / The Sandlot Sluggers (rebuild) | 66.9 | 100.7 | -8.0 | 25.8 |
| U1 linear / Shea Stadiums (contender) | 15.1 | 11.4 | 1.5 | -2.2 |
| U1 linear / The Sandlot Sluggers (rebuild) | 28.4 | 17.8 | -5.0 | -15.6 |
| U2 upper-tail / Shea Stadiums (contender) | 12.9 | 11.4 | 1.5 | 0.0 |
| U2 upper-tail / The Sandlot Sluggers (rebuild) | 28.8 | 15.4 | -5.0 | -18.4 |
| U3 risk overlay / Shea Stadiums (contender) | 5.2 | 2.8 | 1.5 | -0.9 |
| U3 risk overlay / The Sandlot Sluggers (rebuild) | 27.1 | 12.9 | -5.0 | -19.3 |


## Individual assets — common-scale U2 values

These are illustrative posterior values, not validated market prices. “MLB” uses the numerical exposure threshold in the prototype, not Fantrax minors eligibility. Pick identity is embedded in its stable ID.


| Asset / ID | Class | Live neutral | U2 Neutral | Contender | Balanced | Rebuild |
| --- | --- | --- | --- | --- | --- | --- |
| Felnin Celesten / 05mx9 | prospect | 29.0 | 11.4 | 10.7 | 11.6 | 11.6 |
| Jack Wenninger / 06f1c | prospect | 18.8 | 1.9 | 1.9 | 2.0 | 2.0 |
| 2027 R5 · Shea Stadiums / pick-2027-6-5 | pick | 7.0 | 0.1 | 0.0 | 0.1 | 0.2 |
| 2027 R5 · Young Guns / pick-2027-11-5 | pick | 7.0 | 0.1 | 0.0 | 0.1 | 0.2 |
| 2028 R2 · Shea Stadiums / pick-2028-6-2 | pick | 24.6 | 1.1 | 0.3 | 0.9 | 1.5 |
| Josuar Gonzalez / 06ps2 | prospect | 46.7 | 23.3 | 11.4 | 22.1 | 28.8 |
| Leo De Vries / 067yc | prospect | 65.7 | 31.4 | 26.8 | 31.2 | 33.2 |
| Casey Schmitt / 05jp4 | MLB | 47.1 | 27.8 | 29.5 | 28.1 | 27.0 |
| 2027 R4 · Shea Stadiums / pick-2027-6-4 | pick | 11.0 | 0.6 | 0.1 | 0.5 | 0.8 |
| 2028 R4 · Shea Stadiums / pick-2028-6-4 | pick | 9.3 | 0.4 | 0.1 | 0.3 | 0.5 |
| 2027 R2 · Shea Stadiums / pick-2027-6-2 | pick | 29.0 | 1.8 | 0.4 | 1.5 | 2.4 |
| Jacob Misiorowski / 061yu | MLB | 79.2 | 83.6 | 84.9 | 83.9 | 83.0 |
| Munetaka Murakami / 05y3u | MLB | 54.0 | 38.0 | 39.5 | 38.3 | 37.3 |
| Eury Perez / 05aoc | MLB | 23.3 | 4.5 | 4.5 | 4.5 | 4.5 |
| Kyle Bradish / 04pq4 | MLB | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 |
| Luis Robert Jr. / 047l7 | MLB | 22.3 | 5.9 | 6.5 | 6.0 | 5.6 |
| Emil Morales / 06ibo | prospect | 48.9 | 20.3 | 17.9 | 20.3 | 21.2 |
| Eli Willits / 06n8y | prospect | 46.2 | 22.9 | 11.3 | 21.8 | 28.4 |
| Ronald Acuna Jr. / 03wha | MLB | 51.7 | 48.2 | 52.5 | 49.1 | 46.2 |
| Vladimir Guerrero Jr. / 03ojr | MLB | 39.6 | 31.9 | 33.9 | 32.4 | 31.0 |
| Carter Jensen / 05vy5 | MLB | 56.5 | 43.1 | 43.2 | 43.1 | 43.0 |
| Ryan Clifford / 05ge1 | prospect | 11.1 | 5.7 | 6.1 | 6.0 | 5.4 |
| Hunter Gaddis / 05143 | MLB | 18.0 | 0.0 | 0.0 | 0.0 | 0.0 |
| Adrian Morejon / 043ia | MLB | 28.6 | 6.1 | 6.7 | 6.2 | 5.8 |
| Emmanuel Rodriguez / 054p6 | MLB | 13.0 | 0.6 | 0.6 | 0.6 | 0.6 |
| Jasson Dominguez / 050c3 | MLB | 22.3 | 1.4 | 1.4 | 1.4 | 1.4 |
| 2027 R1 · TheMissingSox / pick-2027-9-1 | pick | 48.0 | 6.3 | 1.5 | 5.2 | 8.4 |
| 2028 R1 · TheMissingSox / pick-2028-9-1 | pick | 40.8 | 4.3 | 1.0 | 3.5 | 5.7 |
| 2028 R2 · TheMissingSox / pick-2028-9-2 | pick | 24.6 | 1.1 | 0.3 | 0.9 | 1.5 |
| Yohandy Morales / 05js4 | MLB | 18.2 | 4.7 | 4.7 | 4.7 | 4.6 |
| 2028 R2 · The Sandlot Sluggers / pick-2028-8-2 | pick | 24.6 | 1.1 | 0.3 | 0.9 | 1.5 |
| Casey Mize / 04mlf | MLB | 9.3 | 0.1 | 0.1 | 0.1 | 0.1 |
| Curtis Mead / 05ahe | MLB | 42.6 | 30.5 | 31.2 | 30.7 | 30.2 |
| 2027 R5 · The Sandlot Sluggers / pick-2027-8-5 | pick | 7.0 | 0.1 | 0.0 | 0.1 | 0.2 |
| Ben Brown / 04o2w | MLB | 24.9 | 7.4 | 8.1 | 7.5 | 7.1 |
| Jack Leiter / 04y9o | MLB | 3.8 | 0.0 | 0.0 | 0.0 | 0.0 |
| Travis Sykora / 05ycl | prospect | 41.7 | 5.7 | 4.9 | 5.7 | 6.0 |
| Hurston Waldrep / 0603p | MLB | 5.8 | 0.0 | 0.0 | 0.0 | 0.0 |
| Elian Pena / 06m0g | prospect | 12.7 | 5.3 | 1.7 | 4.7 | 7.0 |
| Jake Mangum / 05135 | MLB | 32.3 | 10.1 | 11.2 | 10.3 | 9.6 |
| Tanner Scott / 03dfa | MLB | 25.0 | 13.1 | 15.4 | 13.5 | 12.1 |
| Luis Garcia Jr. / 0414g | MLB | 63.5 | 55.7 | 57.8 | 56.1 | 54.7 |
| Ryan Weathers / 04mnw | MLB | 24.7 | 8.0 | 8.5 | 8.1 | 7.8 |
| Wilyer Abreu / 060x1 | MLB | 54.9 | 23.4 | 24.9 | 23.7 | 22.8 |


## Prospect outcome hypotheses used in these cases

Probabilities below sum to 100%; their precision reflects arithmetic, not measurement. No player-specific coefficient was edited to balance a trade.


| Prospect | Minimal/bust | Regular | Above-average | Star | Superstar |
| --- | --- | --- | --- | --- | --- |
| Felnin Celesten | 43.9% | 31.3% | 14.0% | 9.9% | 0.8% |
| Jack Wenninger | 52.9% | 28.0% | 11.8% | 6.4% | 0.9% |
| Josuar Gonzalez | 22.1% | 18.8% | 19.5% | 23.8% | 15.8% |
| Leo De Vries | 20.7% | 16.9% | 19.8% | 25.0% | 17.6% |
| Emil Morales | 30.2% | 28.0% | 17.4% | 17.7% | 6.7% |
| Eli Willits | 22.5% | 19.2% | 19.4% | 23.5% | 15.4% |
| Ryan Clifford | 62.0% | 24.2% | 9.5% | 3.9% | 0.4% |
| Travis Sykora | 34.8% | 29.8% | 16.3% | 14.8% | 4.4% |
| Elian Pena | 48.7% | 29.6% | 12.8% | 7.9% | 1.0% |


## Sensitivity tests

Each cell is U2 final net for left owner / right owner. These are NOW results. The full Neutral/Contender/Balanced/Rebuild grid is in results.json. No sensitivity is selected because it makes a trade equal.


| Assumption | Josuar | De Vries | Acuña | Guerrero |
| --- | --- | --- | --- | --- |
| Default | 10.1 / -13.6 | -4.0 / 2.1 | -125.1 / 116.0 | 21.8 / -34.8 |
| Linear tail gamma 1 | 7.4 / -10.9 | -1.1 / -0.7 | -128.3 / 119.2 | 27.7 / -40.6 |
| Gamma 1.6 | 11.8 / -15.3 | -6.1 / 4.3 | -125.6 / 116.4 | 19.4 / -32.4 |
| 3-year horizon | 2.2 / -5.7 | -3.4 / 1.6 | -57.9 / 48.8 | -2.3 / -10.7 |
| 5-year horizon | 6.4 / -9.9 | -3.8 / 1.9 | -91.3 / 82.2 | 6.6 / -19.6 |
| Discount .80 | 6.9 / -10.4 | -3.5 / 1.6 | -95.8 / 86.7 | 11.7 / -24.6 |
| Discount .95 | 13.9 / -17.4 | -4.5 / 2.7 | -159.8 / 150.6 | 34.3 / -47.3 |
| Prospect success -25% | 8.5 / -12.0 | 2.9 / -4.8 | -112.9 / 103.8 | 15.5 / -28.5 |
| Prospect success +20% | 9.8 / -13.3 | -7.2 / 5.3 | -133.2 / 124.1 | 26.2 / -39.1 |
| Superstar tail x.5 | 7.2 / -10.7 | 0.8 / -2.7 | -119.6 / 110.5 | 20.4 / -33.4 |
| Superstar tail x1.5 | 12.7 / -16.2 | -8.8 / 7.0 | -130.7 / 121.5 | 23.2 / -36.2 |
| Rank only; no tool residual | 8.7 / -12.2 | -3.1 / 1.2 | -124.4 / 115.3 | 21.9 / -34.9 |
| Replacement best FA | 10.1 / -13.6 | -14.9 / 13.1 | -125.5 / 116.4 | 7.3 / -20.3 |
| Replacement top10 median | 10.1 / -13.6 | 5.4 / -7.3 | -146.1 / 137.0 | 40.7 / -53.6 |
| No open roster spots | 11.8 / -16.0 | -5.8 / 3.5 | -123.0 / 112.8 | 18.3 / -32.6 |
| Six open roster spots | 8.8 / -9.8 | -1.5 / 1.1 | -126.6 / 123.0 | 30.2 / -36.3 |
| No capacity cost | 8.6 / -8.6 | -0.9 / 0.9 | -126.9 / 126.9 | 36.6 / -36.6 |
| Capacity cost 1 | 9.1 / -10.2 | -1.9 / 1.3 | -126.3 / 123.3 | 31.7 / -36.0 |
| Capacity cost 6 | 11.6 / -18.6 | -7.1 / 3.4 | -123.4 / 105.1 | 7.0 / -32.9 |
| Capacity cost 12 | 14.6 / -28.6 | -13.4 / 6.0 | -119.8 / 83.4 | -22.6 / -29.3 |
| Prospect replacement rank250 | 10.8 / -14.3 | -4.3 / 2.4 | -123.4 / 114.3 | 19.4 / -32.4 |
| Prospect replacement rank600 | 10.0 / -13.5 | -4.3 / 2.5 | -125.9 / 116.8 | 22.4 / -35.4 |
| Future class -20% | 10.3 / -13.8 | -4.1 / 2.2 | -125.1 / 116.0 | 20.7 / -33.7 |
| Future class +20% | 9.9 / -13.3 | -3.9 / 2.1 | -125.1 / 116.0 | 22.9 / -35.8 |
| Expected early slot | 9.0 / -12.5 | -2.3 / 0.5 | -125.1 / 116.0 | 25.8 / -38.8 |
| Expected late slot | 10.3 / -13.8 | -4.9 / 3.0 | -125.1 / 116.0 | 18.0 / -31.0 |
| Postdraft proxy after84 | 9.6 / -13.1 | -3.6 / 1.7 | -125.1 / 116.0 | 22.2 / -35.1 |
| No supplemental star history | 10.1 / -13.6 | -4.0 / 2.1 | -138.9 / 129.8 | 47.9 / -60.9 |


Health sensitivity multiplies already-estimated availability while holding healthy-state ability fixed. It is a hypothetical additional availability change, not a medical assessment or claim of full health.


| Player / availability multiplier | Neutral | Contender | Balanced | Rebuild |
| --- | --- | --- | --- | --- |
| Ronald Acuna Jr. / 0.6 | 28.9 | 31.5 | 29.5 | 27.7 |
| Ronald Acuna Jr. / 0.8 | 38.6 | 42.0 | 39.3 | 37.0 |
| Ronald Acuna Jr. / 1 | 48.2 | 52.5 | 49.1 | 46.2 |
| Vladimir Guerrero Jr. / 0.6 | 19.2 | 20.3 | 19.4 | 18.6 |
| Vladimir Guerrero Jr. / 0.8 | 25.5 | 27.1 | 25.9 | 24.8 |
| Vladimir Guerrero Jr. / 1 | 31.9 | 33.9 | 32.4 | 31.0 |


## What these tests establish — and what fails


- **Josuar negotiation:** Live left/right 86.5/46.7; U2 14.7/23.3. This is a NOW comparison, not a THEN fairness estimate.

- **trade-export-005:** Live left/right 65.7/96.5; U2 31.4/30.5. This is a NOW comparison, not a THEN fairness estimate.

- **trade-export-029:** Live left/right 273.9/51.7; U2 175.2/48.2. This is a NOW comparison, not a THEN fairness estimate.

- **trade-export-039:** Live left/right 39.6/262.9; U2 31.9/68.5. This is a NOW comparison, not a THEN fairness estimate.


U2 reduces the unidentified 2028 R2's apparent equivalence to Celesten by valuing expected drafted outcomes and delayed access, rather than an independent 29-point round curve. However, the default also drives R5 close to zero under the speculative post-draft option. That is a warning about unobserved replacement and draft choice, not proof late picks are worthless.

The Acuña package still exceeds Acuña in every candidate. That is allowed: current production includes a very strong Misiorowski season and several separate sources of MLB output. It does **not** establish the package was worth more on March 3. Misiorowski's single-year extrapolation is a particularly important unresolved risk. Raising Acuña manually or multiplying all stars until that trade balances would conceal this weakness.

Guerrero remains below the package before capacity costs. His multi-year baseline improves the ability estimate compared with using only 2026, but the report does not assume an elite-name floor or restore earlier performance as a certainty. Bench constraints can change the economic result; the sensitivity grid exposes that dependence.

Controls reveal important instability: some MLB assets fall to zero projected surplus under certain replacement estimates, and MLB/prospect classification at an exposure threshold is not a finished development model. A production design must blend observed MLB evidence with development outcomes rather than abruptly switch at a PA/IP threshold. U3 also clips some prospect values to zero because its static dispersion deduction ignores timing and diversification. Reject U3 as currently coded; use owner-specific roster simulations to measure downside instead.

## Recommendation and next evidence gate

Choose U2's **architecture**, not these constants. Fit MLB ability/availability and prospect outcome distributions using baseball evidence, never trade equality. For prospects, use historical cohorts with source-date snapshots, censoring and survival/arrival analysis; hold out prospect classes and later years. Convert outcome production into this league's categories instead of importing real-life WAR dollars. A remaining scarcity term needs independent demand evidence, not the fact that a player is highly ranked.

Replace fixed power utility with empirically estimated incremental category-win/playoff utility once weekly roster and matchup data supports it. Until then show an interval and the linear/nonlinear sensitivity, not a confident “fair trade” verdict. A contender and rebuild can rationally disagree about the same distribution; they should not receive different underlying factual forecasts without an explicitly different scenario.

Before any formula deployment, acquire or validate: league-wide multi-year/projection inputs, injuries and expected roles; current Fantrax position/career eligibility and actual active/reserve/minor/IR usage; rated available prospects; final FYPD/Rule 5/cutdown rules and actual draft availability; historical draft classes with outcomes; and any reliable trade-date projection/rank snapshots for THEN. User screenshots are optional evidence, not a prerequisite to designing this architecture. THEN stays unavailable when the record cannot support it.

Release gates: no leakage by evidence timestamp; meaningful MLB multi-year coverage; credible available-player replacement; scenario-calibrated prospect tails; continuous development blending; future-capacity allocation without duplicate pick fees; stable controls and surfaced uncertainty. Stress trades can retain unequal outcomes. Owner utility, raw base value and capacity adjustment must remain separately visible in the existing UI.

## Verification and reproducibility

The prototypes ran on isolated copies, with tests for unique identities, constant-stream equality across owner modes, upper-tail utility at equal means, package-order invariance, smooth costs and separation of roster cost from asset value. These are structural tests, not validation of probabilities, injury forecasts or market prices. All tests passed. The before-values are a saved evaluation of the unchanged production formula under default scenarios; user local-browser overrides are not included.

`prototype.py` reruns with Python's standard library: `python prototype.py`, then `python make_report.py`. Inputs, verified star history, production formula snapshot and values, full numerical output, source links, hashes and this report are included in the review bundle. No data collector, deployment step, Git push or website mutation is included.

## Research sources

- [FanGraphs: How to Use Depth Charts](https://library.fangraphs.com/how-to-use-fangraphs-depth-charts/) — separates projected rates from playing-time estimates. This informs architecture, not a claim that the prototype downloaded current Depth Charts forecasts.
- [FanGraphs: Prospect Grades and Future Outcomes](https://blogs.fangraphs.com/how-do-prospect-grades-translate-to-future-outcomes/) — outcome distributions can carry information a single grade obscures. Real-life WAR outcomes require a fantasy-category translation.
- [FanGraphs: New Prospect Valuation Methodology](https://blogs.fangraphs.com/the-details-of-our-new-prospect-valuation-methodology/) — historical prospect cohorts and noncontributors matter. No FanGraphs probability table was copied into the prototype.
- [Acuña regular-season history](https://www.fangraphs.com/players/ronald-acuna-jr/18401/stats/batting) and [Guerrero regular-season history](https://www.fangraphs.com/players/vladimir-guerrero-jr/19611/stats/batting) — verified 2023–2025 inputs only; 2026 comes from the saved league export. Postseason and old preseason forecasts were excluded.

Scouting source URLs and source dates remain in each saved Pipeline prospect record. They are dated observations, not newly researched October grades. No Dynasty Dugout proprietary formula or software was adopted.
