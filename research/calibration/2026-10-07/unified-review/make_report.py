import json,math,hashlib,zipfile
from pathlib import Path
R=Path(__file__).resolve().parent
r=json.load(open(R/'results.json'))
lines=[]
def add(s):lines.append(s)
def table(headers,rows):
 add('| '+' | '.join(headers)+' |\n| '+' | '.join(['---']*len(headers))+' |\n'+'\n'.join('| '+' | '.join(str(x).replace('|','/') for x in row)+' |' for row in rows)+'\n')
def f(x):return f'{x:.1f}'
labels={'Live':'Live','A':'U1 linear','B':'U2 upper-tail','C':'U3 risk overlay'}
add('''# Unified Dynasty Asset Model — Offline Review

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
''')
table(['Net extra incoming players','Capacity cost (two open spots)'],[(x['net_incoming_players'],f(x['cost'])) for x in r['smooth_curve']])
add('''For literal 2-for-1/3-for-1/5-for-1/9-for-1 player packages, net additions are 1/2/4/8. Costs are 1.0/2.3/6.0/16.4. The curve has no behavioral switch at three assets. Pick-heavy packages differ according to arrival years, not just count.

## Required stress tests — raw asset totals before consolidation

Left/right is **assets sent by the two named owners**, not an assumed winner. Each historical row uses October information. Different candidates have different scales: compare ratios and net direction, not the absolute point difference between Live and U2. Rounding is presentation only. Neutral Live equals its Balanced calculation.
''')
for c in r['cases']:
 add(f"### {c['id']} · {c['date']}\n\nLeft: **{c['teams'][0]}** sends {', '.join(c['sends'][0])}.\n\nRight: **{c['teams'][1]}** sends {', '.join(c['sends'][1])}.\n\n{c['status']}.\n")
 table(['Perspective','Live left / right','U1 left / right','U2 left / right','U3 left / right'],[(m.title(),*[f(z['surrendered'][0])+' / '+f(z['surrendered'][1]) for z in c['comparisons'][m].values()]) for m in ['neutral','contender','balanced','rebuild']])
 add('U2 owner summaries (each row assumes both owners use that perspective; actual mixed preferences follow below):\n')
 table(['Perspective / owner','Surrendered','Received','Roster adjustment','Final net'],[(m.title()+' / '+c['teams'][i],f(v['surrendered'][i]),f(v['received'][i]),f(v['roster_adjustment'][i]),f(v['net'][i])) for m,d in c['comparisons'].items() for v in [d['B']] for i in [0,1]])
add('## Current negotiation — actual mixed owner preferences\n\nShea uses Contender; Sandlot uses Rebuild. The same incoming and outgoing assets are evaluated independently under each owner’s preference.\n')
c=r['cases'][0]
table(['Model / owner','Surrendered','Received','Roster adjustment','Net'],[(labels[k]+' / '+c['teams'][i]+' ('+m+')',f(v['surrendered'][i]),f(v['received'][i]),f(v['roster_adjustment'][i]),f(v['net'][i])) for k in ['Live','A','B','C'] for i,m in [(0,'contender'),(1,'rebuild')] for v in [c['comparisons'][m][k]]])
add('## Individual assets — common-scale U2 values\n\nThese are illustrative posterior values, not validated market prices. “MLB” uses the numerical exposure threshold in the prototype, not Fantrax minors eligibility. Pick identity is embedded in its stable ID.\n')
table(['Asset / ID','Class','Live neutral','U2 Neutral','Contender','Balanced','Rebuild'],[(a['name']+' / '+a['id'],a['type'],f(a['values']['neutral']['Live']),*[f(a['values'][m]['B']) for m in ['neutral','contender','balanced','rebuild']]) for a in r['assets']])
add('## Prospect outcome hypotheses used in these cases\n\nProbabilities below sum to 100%; their precision reflects arithmetic, not measurement. No player-specific coefficient was edited to balance a trade.\n')
table(['Prospect','Minimal/bust','Regular','Above-average','Star','Superstar'],[(a['name'],*[f(100*p)+'%' for p in a['probabilities']]) for a in r['assets'] if a['type']=='prospect'])
add('## Sensitivity tests\n\nEach cell is U2 final net for left owner / right owner. These are NOW results. The full Neutral/Contender/Balanced/Rebuild grid is in results.json. No sensitivity is selected because it makes a trade equal.\n')
table(['Assumption','Josuar','De Vries','Acuña','Guerrero'],[(label,*[f(v[c['id']]['neutral'][0])+' / '+f(v[c['id']]['neutral'][1]) for c in r['cases'][:4]]) for label,v in r['sensitivity'].items()])
add('Health sensitivity multiplies already-estimated availability while holding healthy-state ability fixed. It is a hypothetical additional availability change, not a medical assessment or claim of full health.\n')
table(['Player / availability multiplier','Neutral','Contender','Balanced','Rebuild'],[(name+' / '+h,*[f(v[m]) for m in ['neutral','contender','balanced','rebuild']]) for name,d in r['star_health_sensitivity'].items() for h,v in d.items()])
add('## What these tests establish — and what fails\n')
for c in r['cases'][:4]:
 live=c['comparisons']['neutral']['Live']['surrendered'];b=c['comparisons']['neutral']['B']['surrendered']
 add(f"- **{c['id']}:** Live left/right {f(live[0])}/{f(live[1])}; U2 {f(b[0])}/{f(b[1])}. This is a NOW comparison, not a THEN fairness estimate.")
add('''
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
''')
(R/'Unified_Dynasty_Model_Review.md').write_text('\n\n'.join(lines))
manifest={str(p.relative_to(R)):hashlib.sha256(p.read_bytes()).hexdigest() for p in R.rglob('*') if p.is_file() and p.suffix not in ['.zip'] and p.name!='manifest.json'}
(R/'manifest.json').write_text(json.dumps(manifest,indent=2))
with zipfile.ZipFile(R/'Unified_Dynasty_Model_Review_Bundle.zip','w',zipfile.ZIP_DEFLATED) as z:
 for p in R.rglob('*'):
  if p.is_file() and p.suffix!='.zip':z.write(p,p.relative_to(R))
print('Saved review; cases',len(r['cases']),'sensitivities',len(r['sensitivity']),'invariants',r['invariants'])
