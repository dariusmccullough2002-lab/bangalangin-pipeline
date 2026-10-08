import json,hashlib,zipfile
from pathlib import Path
R=Path(__file__).resolve().parent
r=json.load(open(R/'results.json'));out=[]
def add(s):out.append(s)
def f(x):return '—' if x is None else f'{x:.2f}'
def table(h,rows):add('| '+' | '.join(h)+' |\n| '+' | '.join(['---']*len(h))+' |\n'+'\n'.join('| '+' | '.join(str(x).replace('|','/') for x in row)+' |' for row in rows)+'\n')
add('''# Task 1 — Replacement Difficulty and Acquisition Access

BangaLangin Pipeline · October 7, 2026 · Offline refinement of the completed U2 work

## Conclusion

Replacement difficulty **materially improves the explanation and the evidence**, but is not yet an identified market-price adjustment. Actual available candidates can replace the hypothetical rank-400 identity as the basis for an alternative-player sample. Their future fantasy distributions still require modeling; observed availability is not an observed career outcome or a guaranteed December acquisition.

Preserve U2's outcome distributions, nonlinear superstar utility and owner windows. Keep replacement and acquisition diagnostics separate. Do not add another elite bonus. Do not subtract available-player value again from an intrinsic value that already uses a replacement reference. The eventual owner utility should come from a joint before/after roster optimization, not intrinsic totals plus a collection of unrelated scarcity bonuses.

The current negotiation is **not a clear win for Shea** in this experiment. Retaining U2's intrinsic assumptions while correcting late-pick access gives a modest negative Contender estimate for Shea and a negative Rebuild estimate for Sandlot. That supports Sandlot keeping Josuar under these assumptions, not a confident real-market recommendation: late-class outcomes, prospect probabilities, post-FYPD room and counterpart asking prices remain uncertain. No coefficients were chosen to balance this trade.

The previously completed U2 inputs, scripts, results and report passed 11 preservation hash checks. Repository main remains `cba5e8095a91e9ef5c3fe776ec9d7d78b8005013`, checked read-only. No commit, deployment, website edit, transaction recollection or Fantrax transaction request was performed.

## Corrected league rules — authoritative user clarification

- The formal draft has **20 rounds**.
- Rounds **1–5** are FYPD and the only tradable picks.
- Rounds **6–20** open the available Fantrax pool. They are an acquisition mechanism, never tradable assets or draft-capital value.
- Reported stopping around Rounds **10–17** is capacity-driven behavior, not the formal endpoint.
- No owner is assumed to have 15 free post-FYPD spots. Existing keepers, traded FYPD rights, eligibility, IR and cutdowns affect usable capacity.

This supersedes the older attachment's 17-round setting. The Rule 5 proposal's temporary expansion is not treated as an adopted rule. Later selections can acquire useful players, but their player outcomes are not standalone values for the nontradable selections themselves.

## Four separate ledgers

| Concept | Meaning | Measurement in this review | What it does not imply |
| --- | --- | --- | --- |
| Intrinsic value | Expected future category contribution and outcome distribution on a common reference scale | Retained U2 probability/aging/utility machinery; separated from the old hypothetical prospect and FYPD-access deductions | An observed market price or certainty of production |
| Replacement difficulty | Ability to recreate most of a lost asset's role, contribution and upper tail through feasible low-cost channels | Actual unowned IDs; quality/depth screens; finite-slot and competition scenarios | That all free agents are useful, or one substitute can fill multiple losses |
| Acquisition scarcity/price | Access to an equivalent owned asset and the compensation its owner demands | Known modeled owned alternatives and owner concentration; actual asks remain unobserved | That two assets summing to 60 can purchase an asset valued at 60 |
| Owner utility | Timing and marginal contribution to a legal roster | Contender/Balanced/Rebuild horizons; bilateral capacity sensitivities | Automatic benefit from consolidation or a flat penalty on every pick |

The intrinsic ledger is still a **U2 proxy**, not an absolute forecast: its MLB outcome anchors already measure category surplus above its reference MLB replacement estimate. This task removes the extra hypothetical rank-400 prospect deduction and speculative post-Round-5 FYPD exclusivity deduction into separate diagnostic concepts. It does not refit U2's category scale, superstar probabilities, pitching anchors or aging curves.

## What is actually observed

The October 7 saved Fantrax export contains 10,616 unique IDs and 9,795 free agents. Qualified free-agent MLB evidence is available for 147 hitters with ≥150 AB and 251 pitchers with ≥30 IP. The other zero-stat or small-sample players remain unknown; they are not assumed worthless.

The previous report correctly found zero free agents among the 260 *Pipeline-rated* prospects, but that was a **coverage limit**, not evidence that no good prospects were available. This refinement screened a dated external scouting list against the full saved ownership pool, using name, organization, age and position family, and preserved the resulting Fantrax ID as the key. No ranked-list number was assigned as a new Pipeline rank.

The screening resolved 103 of 111 records: 90 owned, 13 unowned; eight organization mismatches remain unresolved. Six of the unowned records belong to the saved 2026 FYPD class and are excluded from immediate free-agent replacement access. The remaining seven form a small researched prospect cohort. These counts are not a census of every available prospect or an assertion that the July grades remain current.

For the matched seven, official MLB player identities provide secondary MLBAM IDs. The export does not expose a direct Fantrax→MLBAM link: the multi-attribute crosswalk is a research match, not a production identity migration. Raw ownership is checked against each Fantrax ID, with October 7 provenance; **no live Fantrax ownership claim** is made. A pending waiver or later roster move can change availability.

Duplicate-name protection matters: Sebastian Rojas has separate ATH and STL Fantrax IDs; the DSL Cardinals record cannot be matched by name alone. Ramon Ramirez's young KC catcher identity is separated from other same-name players by organization, age and position. Existing Juan Sanchez IDs remain separate. No data was merged by name alone.

### Screened non-FYPD prospect candidates

All seven are `Free agent` in the saved October 7 Fantrax ownership export. The scouting snapshot is July 23; identity and current-quality limitations remain. The table is a shortlist, not advice to add them.
''')
table(['Player','Fantrax ID','MLBAM ID','Role / org','External FV / ETA','Ownership date'],[(c['name'],c['fantraxId'],c['mlbamId'],c['position']+' / '+c['org'],str(int(c['fv']))+' / '+str(c['eta']),c['ownershipAsOf']) for c in r['FA_cohort']])
add('''Sources: [FanGraphs scouting snapshot](https://blogs.fangraphs.com/2026-pre-trade-deadline-top-100-prospects-update/) plus each official MLB identity URL retained in the bundle. Ownership comes from the user's league export, not from those public sites.

### Empirical alternative distribution — observed identities, modeled outcomes

For each available prospect, use matched owned prospects with the same provider/FV and broad role, age within three years and ETA within two years. Sparse groups fall back to the same-FV/role cohort. Negotiation players are excluded from these donor groups. The resulting prior combines those peers' retained U2 distributions, then uses the available player's own age and sourced ETA. No generic rank 400 is assigned.

This produces a distribution of **model-implied alternative quality** conditional on actual available identities. It is not an empirical distribution of realized MLB success. Donor ranks are league-conditioned, older grades can be stale, owned peers are selected and fantasy role differs from real-life FV. The hitter and pitcher U2 anchors are themselves uncalibrated; in particular the pitching “regular” anchor can equal zero surplus. That can make available pitchers appear artificially inexpensive.
''')
table(['Candidate','Donor count','Rebuild P25','Median','P75','Modeled superstar probability'],[(c['name'],c['peer_count'],f(c['values']['rebuild']['p25']),f(c['values']['rebuild']['median']),f(c['values']['rebuild']['p75']),f(100*c['elite_probability_mean'])+'%') for c in r['FA_cohort']])
add('''Qualified MLB free agents provide a separate observed-player sample evaluated using U2's unchanged single-season extrapolation. Full distributions for all 398 are in results.json. Those forecasts do not certify upside equivalence to a young prospect. An older pitcher can replace near-term innings without replacing a prospect's future role, age profile or tail.

## Replacement difficulty is profile-specific

Default diagnostic: an alternative must recreate at least **80% of expected intrinsic utility** in the same broad hitting/pitching family. A second screen also requires at least 80% of the modeled superstar probability. A strict-position screen requires the same listed position. Thresholds of 60%/95% and donor P25/P75 are sensitivities, not measured owner preferences.

Expected utility alone can be recreated across positions; exact role and upside may not. All counts below refer only to the seven screened available prospects, not to the unmodeled pool. Future Fantrax eligibility is not fully known. Lack of a observed comparable means “none in this sample,” not “impossible anywhere.”
''')
table(['Lost asset','Broad mean-value alternatives','Broad mean + tail alternatives','Same-position mean + tail alternatives'],[(name,*(next(x['observed_comparables'] for x in r['replacement_ladder']['rebuild'][label] if x['name']==name) for label in ['Functional mean >=80%','Functional mean and superstar probability >=80%','Same position, mean and tail >=80%'])) for name in ['Jack Wenninger','Felnin Celesten','Josuar Gonzalez']])
add('''Wenninger has two screened SP alternatives: Hardin and Keyner Martinez. That is evidence for partial replaceability, not a claim they are identical or certainly available in December. Celesten has broad hitting alternatives—including Hayden Alvarez—but no same-position shortstop in this screened cohort. The idea that Celesten must be much harder to replace than all available hitters is not supported by this small sample; the SS requirement materially changes that conclusion. Josuar has no observed alternative passing the default mean-and-tail screen.

The sampled scouting frontier has no resolved, non-FYPD free agent in its highest rank bands. This supports a thin upper rung, conditional on dated source coverage. It does not identify a price premium. A package can have high total expected contribution while lacking any *single* distributional replacement for an elite asset. Conversely, several independent prospects can improve the chance of eventually developing at least one star; that possibility must not be suppressed to make consolidation look attractive.

### Existing owned alternatives and counterparties

These are modeled compatible prospects owned by other teams, not advertised trade availability. Counts use broad role, 80% mean utility and 80% superstar probability; the lost asset is excluded. A player being owned does not make its owner willing to sell. No owner asking price is estimated from completed trades.
''')
table(['Lost asset / Rebuild','Modeled owned alternatives','Distinct owners','Observed asking price'],[(next(a['name'] for a in r['assets'] if a['id']==x['target_id']),x['owned_compatible_prospect_count'],len(x['owners']),'Unobserved') for x in r['owned_reacquisition_ladder']['rebuild']])
add('''Nonlinear acquisition should therefore be shown as an **access frontier and uncertainty**, not a multiplier on intrinsic value. No arithmetic rule forces a seller to exchange one scarce asset for several lower-rung assets. Nor does scarcity prove the buyer should accept any consolidation offer.

## Re-run of the Josuar negotiation

Shea receives Josuar Gonzalez. Sandlot receives Felnin Celesten, Jack Wenninger, 2027 #56, 2027 #58 and the unknown-slot 2028 second. The two R5 rights retain their existing IDs/original owners; the slot pair follows the user clarification and supplied fixed-order context. Nothing is assigned a Round 6–20 asset ID.

A known slot is not a known selected player. The corrected experiment averages a ±12-class-rank choice window around #56/#58 to represent uncertain remaining players and owner preferences. Narrow/broad windows and a deterministic rank=slot diagnostic are included. No named draftee is asserted to be available at those selections. The 2028 class remains a hypothetical template, not newly researched class quality.

The corrected intrinsic calculation removes only the old hypothetical prospect deduction and assumed access to the residual FYPD class. It leaves the retained U2 outcome, utility and horizon parameters unchanged. Later free-agent access belongs in the capacity-aware counterfactual, not a zero value automatically assigned to R5.

### Asset values
''')
table(['Asset','Frozen U2 Neutral','Corrected Neutral','Contender','Balanced','Rebuild'],[(a['name']+(' / #'+str(a['slot']) if a['slot'] else ''),f(a['values']['neutral']['frozen_U2']),*[f(a['values'][m]['corrected_intrinsic']) for m in ['neutral','contender','balanced','rebuild']]) for a in r['assets']])
add('### Bilateral owner summaries — same retained capacity proxy\n\nEach row uses that owner’s stated perspective for both incoming and outgoing assets. Default capacity remains λ=3, two free proxy spots; this is held constant to isolate the input correction, not asserted as the actual draft room.\n')
table(['Perspective / owner','Surrendered','Received','Capacity adjustment','Net'],[(m.title()+' / '+['Shea','Sandlot'][i],f(v['surrendered'][i]),f(v['received'][i]),f(v['capacity_adjustment'][i]),f(v['net'][i])) for m,v in r['corrected_same_capacity'].items() for i in [0,1]])
add('### Actual selected strategies — Shea Contender, Sandlot Rebuild\n')
table(['Experiment / owner','Surrendered','Received','Capacity adjustment','Net'],[(label+' / '+['Shea Contender','Sandlot Rebuild'][i],f(v['surrendered'][i]),f(v['received'][i]),f(v['capacity_adjustment'][i]),f(v['net'][i])) for label,d in [('Frozen U2',r['frozen']),('Corrected intrinsic/access separation',r['corrected_same_capacity'])] for i,m in [(0,'contender'),(1,'rebuild')] for v in [d[m]]])
add('### Why Sandlot originally showed −18.4\n\nThe original score contains **zero explicit measured acquisition-scarcity premium**. Its high Josuar value reflects U2’s rank/tool-driven outcome hypotheses and nonlinear utility, not an observed inability to buy another Josuar. The following attribution is exact within the retained arithmetic. It is not an estimate that those terms were empirically justified.\n')
d=r['decomposition']['rebuild']
table(['Component','Effect / points'],[('Frozen package intrinsic proxy minus Josuar',f(d['intrinsic_received_minus_given'])),('Frozen capacity adjustment',f(-d['old_smooth_capacity_cost'])),('Frozen Sandlot net',f(d['Sandlot_frozen_net'])),('Remove hypothetical prospect deduction — bilateral effect',f(d['remove_hypothetical_prospect_floor_effect'])),('Remove speculative post-R5 FYPD-access deduction',f(d['remove_assumed_postR5_FYPD_exclusivity_floor_effect'])),('Condition on #56/#58 with selection uncertainty',f(d['exact_56_58_slot_effect'])),('Corrected net, same capacity',f(d['corrected_net_same_capacity']))])
add('''Thus the hypothetical prospect floor has a small *net* effect because its hitting deduction appears on both sides. Correcting draft access explains most of the reduction in Sandlot's modeled loss. The remaining negative result should not be relabeled “proven Josuar scarcity.” It still depends on U2's unvalidated superstar probability and projected draft outcomes.

### Superstar lottery — not just the sum of point values

The retained U2 hypotheses assign different upper tails. The package can generate several outcomes, but occupies several slots and includes delayed draft selections. At-least-one probabilities below assume independent outcomes; real class, injury and evaluation risks can be correlated. These are model hypotheses, not measured success frequencies or trade prices.
''')
table(['Side','Expected number of superstar outcomes','Probability ≥1 if independent'],[(label,f(v['expected_number_of_superstars']),f(100*v['prob_at_least_one_if_independent'])+'%') for label,v in r['superstar_lottery'].items()])
add('## Capacity audit and post-FYPD access\n\nOctober 6 roster statuses were reconciled to October 7 ownership by ID. Known IR is excluded from the 63-player count; unmatched current statuses are conservatively treated as non-IR. Status changes, eligibility, moves, injuries and future cutdowns remain uncertain.\n')
rosters=[x for x in r['rosters'] if x['team'] in ['Shea Stadiums','The Sandlot Sluggers']]
table(['Owner','Owned now','Known IR','Conservative current openings','2027 FYPD rights before trade','Unknown statuses'],[(x['team'],x['owned'],x['known_ir'],x['current_total_openings_conservative'],x['2027_fypd_rights'],len(x['unknown_status_ids'])) for x in rosters])
add('''Under a **no-expansion, all-current-players-retained** bookkeeping scenario, Shea's five current openings versus nine existing 2027 rights already require at least four cuts to exercise all those rights. After the trade, Shea gains one player opening and sends two 2027 rights: six openings versus seven rights, at least one cut. Sandlot's one current opening versus three 2027 rights becomes zero openings versus five rights after the trade: at least five cuts. These are mechanical scenario counts, not forecasts that every pick is used or that any specific player should be dropped. The 2028 second adds a separate later decision.

Minors/reserve eligibility can tighten these constraints further. No claim is made that the prior day's status allocation establishes current legality. IR recoveries or adopted expansion could change totals. The simplified numerical capacity-cost curve remains uncalibrated; actual post-FYPD room is tested rather than inferred from today's openings.

Existing first-round rights are a potentially important source of future high-end outcomes for both organizations. They are **already owned** and cannot be added again as trade gains. Their use consumes real capacity and competes with late free-agent selections. A future joint optimizer must evaluate those rights and free-agent opportunities together.

### Finite post-FYPD acquisition simulations

The sampler uses the seven screened prospects plus positive-model qualified MLB free agents, selection without replacement, 11 rival owners and turns only in R6–20. Rival capacities of 5/8/12 correspond to stopping after R10/R13/R17 if they use every turn; 15 tests the formal R20 endpoint. Focal capacities of 0/1/3/6 are scenario openings, not assumed league entitlements.

Opponent policies and persistence of this October pool are assumed. General competition uses weighted modeled utility; a need-directed focal owner seeks a comparable pitcher first. Targeted rivals can intentionally take the same scarce alternatives before the focal turn. The outputs are **conditional simulations**, not empirical acquisition probabilities. Player utility acquired below is the expected quality of selected players, not draft-capital value for later-round selections.
''')
selected=['capacity0_competition8','capacity1_competition8','capacity3_competition8','capacity6_competition8','One earlier owner targets comparable pitchers','Two earlier owners target comparable pitchers','Four earlier owners target comparable pitchers','Focal not need-directed','36 early claims']
table(['Scenario','Focal openings','Rival openings each','Mean modeled player utility acquired','Model-implied chance of screened Wenninger substitute'],[(k,v['focal_post_fypd_capacity'],v['competitor_capacity_each'],f(v['mean_harvest']),f(100*v['prob_obtaining_tail_screened_prospect_comparable_to_wenninger'])+'%') for k in selected for v in [r['draft_access_scenarios'][k]]])
add('''The near-100% results under broad utility-weighted competition are **not reliable access estimates**: the inherited U2 scale makes these SP alternatives cheap relative to many hitters. Two earlier targeted rivals reduce access to those screened pitching substitutes to zero in the scenario. This is the practical distinction between pool availability and owner-specific access. Current claimability also differs from waiting until the draft: these names may disappear before December. Claims, waiver priority and actual competitor intentions are not observed.

### Bilateral regeneration — shared capacity, no reused substitute

The loss-specific experiment asks how much of the player portion could be covered with 0/1/2 slots and assumed 25/50/75% per-candidate access. One free agent cannot cover two lost players. Strict-position and broad-production variants are separate. It is a **partial recovery bound**, not a bonus to add to trade net: before-trade owners may already be able to acquire the same alternatives.

The three surrendered pick rights retain intrinsic value. No R6–20 selection recreates their tradable rights, early FYPD exclusivity or future class option. Their future production may have substitutes, but that is different from recovering the draft capital. Pick occupancy is charged once in the retained capacity proxy; no extra pick diminishing-returns fee is added.
''')
table(['Owner’s lost player assets','Role screen','Usable slots','Assumed access per candidate','Expected recovery bound','Unrecreated intrinsic value'],[('/'.join(next(a['name'] for a in r['assets'] if a['id']==i) for i in x['lost_ids']),'Exact listed position' if idx%2 else 'Broad contribution',x['capacity'],str(int(x['per_candidate_access_assumption']*100))+'%',f(x['joint_recreation_bound']),f(x['not_recreated'])) for idx,x in enumerate(r['joint_regeneration']['rebuild']) if x['capacity'] in [0,1,2] and x['per_candidate_access_assumption']==.5])
add('''This is bilateral: Shea's lost player portfolio has some potentially regenerable production; Sandlot's lost Josuar distribution has no screened equivalent. That explains a possible consolidation rationale but does not establish Shea can harvest the replacements after its FYPD commitments, or that Sandlot should surrender the scarce asset. Intrinsic package value, draft rights, timing and capacity remain relevant.

## Sensitivities — no preferred outcome selected

The following are final net under Shea's Contender and Sandlot's Rebuild preferences. Default replacement diagnostics themselves do not modify intrinsic totals. Late-class and future-class factors are hypothetical outcome-quality changes, not fitted coefficients. Their purpose is to show how much unmeasured draft quality matters.
''')
table(['Assumption','Shea Contender net','Sandlot Rebuild net'],[(label,f(v['contender']['net'][0]),f(v['rebuild']['net'][1])) for label,v in r['sensitivities'].items()])
add('''With default corrected intrinsic assumptions and no capacity cost, Sandlot remains negative. Doubling modeled late-FYPD outcomes and removing capacity cost changes that sign; that combination is a sensitivity, **not a recommendation or evidence late picks are twice as good**. Capacity and late-pick quality remain capable of changing the decision.

Removing the unvalidated U2 scouting residual tests potential double-counting of characteristics already reflected in rank. It changes the result but does not resolve the underlying outcome calibration. U2's upper-tail transform is retained exactly once. Available-substitute count and acquisition scarcity never multiply it again.

## Acuña, Guerrero and De Vries — NOW stress tests only

The same structural intrinsic/access separation is applied generally, with unknown historical pick slots remaining unknown. No trade-date fairness claim or historical-price target is used. Acuña and Guerrero's own MLB intrinsic proxies are unchanged by this task; package prospect/pick deductions are separated. Their one-year and projection weaknesses remain as identified in U2.
''')
for c in r['stress_tests']:
 add('### '+c['id']+'\n\nLeft owner: '+c['teams'][0]+'; right owner: '+c['teams'][1]+'.\n\nLeft sends: '+', '.join(c['sends'][0])+'.\n\nRight sends: '+', '.join(c['sends'][1])+'.\n')
 table(['Perspective','Frozen left/right intrinsic proxies','Separated left/right intrinsic','Separated left/right net'],[(m.title(),f(c['frozen'][m]['surrendered'][0])+' / '+f(c['frozen'][m]['surrendered'][1]),f(c['gross'][m]['surrendered'][0])+' / '+f(c['gross'][m]['surrendered'][1]),f(c['gross'][m]['net'][0])+' / '+f(c['gross'][m]['net'][1])) for m in ['neutral','contender','balanced','rebuild']])
add('''## THEN / NOW / REALIZED SO FAR remains intact

Every historical numerical result here is **NOW**, using October information and dated scouting. THEN is not estimated without trade-date projections, ranks, injuries, availability, ownership and draft knowledge. July/October information cannot train a February/March trade-date model. REALIZED SO FAR is not calculated from full-season aggregates. No completed trade is assumed fair, and no candidate is fitted to equality.

## What is measured, assumed and still missing

Measured: exported ownership by unique Fantrax ID, qualified season counts, dated available-player scouting, cohort membership, existing tradable rights, reconciled prior-day statuses and formal 20-round access rules supplied by the user.

Modeled: future ability, aging, tails, same-FV donor translation, eligibility-compatible substitution, class-rank selection windows, discounting and year weights. The new available-player distribution removes a fictitious generic identity but does not magically validate U2's outcome priors.

Assumed in sensitivities: post-FYPD usable capacity, cuts/expansion, persistence of current free agents, rival priorities, claims, future class quality and access probabilities. No empirical counterpart asking price, transaction friction or price premium is inferred.

Still needed for a calibrated economic model: a broader ID-linked available-prospect census with current scouting/performance; league-wide multi-year/projection data; actual FYPD and late-round selections/passes/cutdowns; current eligibility and statuses; waiver/claim timing; and voluntary asking-price or offer evidence. Completed trades can stress the model, not label fair prices.

## Recommended next design

Keep the four ledgers visible. Use real alternative-player samples with uncertainty intervals instead of a hard-coded rank-400 subtraction. Price late picks by their eligible draft outcome distributions, then evaluate the opportunity cost of exercising them in the owner's full roster/draft plan. Treat R6–20 as finite selection opportunities only.

Implement a joint counterfactual optimizer `utility(after trade, feasible acquisition plan) − utility(before trade, feasible acquisition plan)`. The same free agent cannot be counted twice, and opportunities already available before the trade are not new trade gains. Include finite slots, position/eligibility, current FYPD rights, rival depletion and future retention decisions. This is how replacement difficulty should affect consolidation without adding an arbitrary elite premium or double-charging picks.

This refinement is a stronger **diagnostic foundation** for U2. It is not yet a justified acquisition-price formula or deployable roster optimizer. The default proxy would not support Sandlot accepting this package, and Shea's small negative Contender estimate is not enough to establish a meaningful market overpay. There is no demonstrated both-owner benefit under the default case.

## Reproducibility and verification

Run `python refinement.py`, then `python make_report.py` with Python's standard library. Inputs include immutable U2 copies, the actual export, dated available-player cohort, aggregate scouting-coverage audit and reconciled status snapshot. results.json contains all four perspectives, 22 intrinsic/capacity sensitivities, 27 acquisition scenarios, both-side recovery bounds and historical NOW stress tests.

Checks verify exact reproduction of the previous U2 negotiation; all seven candidate IDs free in the export; no FYPD-restricted candidate admitted to immediate access; unique IDs; R6 trade-value requests rejected; zero capacity yields zero acquisitions; no draft turn beyond R20; no substitute reused; and empty access changes only the diagnostic, not intrinsic values. All passed. These checks verify structural separation, not the empirical validity of forecasts or access probabilities.

Source articles were used for limited factual scouting/identity inputs, not copied in full. Scouting dates and official identity URLs remain in cohort records. All original work remains intact; no new production formula is approved or deployed.
''')
(R/'Task1_Replacement_Access_Review.md').write_text('\n\n'.join(out))
(R/'README.txt').write_text('OFFLINE ONLY. Run python refinement.py, then python make_report.py. No deployment, commit, transaction collection or website modification is included. Rounds 6–20 are acquisition turns, never tradable assets. All probabilities and access scenarios are provisional; see the report.\n')
files=[p for p in R.rglob('*') if p.is_file() and p.suffix!='.zip' and '__pycache__' not in p.parts and p.name!='manifest.json']
(R/'manifest.json').write_text(json.dumps({str(p.relative_to(R)):hashlib.sha256(p.read_bytes()).hexdigest() for p in files},indent=2))
with zipfile.ZipFile(R/'Task1_Replacement_Access_Bundle.zip','w',zipfile.ZIP_DEFLATED) as z:
 for p in files+[R/'manifest.json']:z.write(p,p.relative_to(R))
print('Report created:',len(r['sensitivities']),'sensitivities;',len(r['draft_access_scenarios']),'access scenarios;',len(r['invariants']),'structural checks')
