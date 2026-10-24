# Calendar production versus eight-year strategy fit

October 24, 2026. Request: investigate Bregman versus Wrobleski plus a prospect, separate next-season help from future value, and test more than the named trade.

## What the uploaded file contains

The supplied JSON is Wrobleski + Felnin Celesten for Bregman. The prior screenshot used Ethan Holliday. Both cases are tested independently by stable Fantrax ID; neither player's identity is substituted.

## Findings

The eight-year calculations reconcile to the saved annual paths. There is no addition error. Their description as a win-now verdict was incorrect. Normalized .75 annual timing weights still credit all eight years, while the rebuild view uses .94. The neutral ranking-led price is a separate ledger.

| Shea receives Bregman, sends… | Original contender fit | Next-season production difference | Dynasty value difference |
|---|---:|---:|---:|
| Wrobleski + Celesten (uploaded) | −11.1185 | +0.64493 annual utility units | +1.83766 |
| Wrobleski + Holliday (screenshot) | −12.1499 | +0.64493 annual utility units | +0.69580 |

Annual utility units are not dynasty points, category wins, or guaranteed active-lineup gains. The current shared quality adjustment is already in these figures. Prospect first-year zeros come from the supported calendar scenario (regular contribution starts in 2029), not from assigning prospects no asset value or guaranteeing no early debut.

Bregman's 2027 utility is 2.86198 versus Wrobleski's 2.21705. On the eight-year contender display scale, the first year contributes 11.2445 to Bregman and 8.71064 to Wrobleski. Later years contribute 13.4944 and 16.5185, respectively. Those later years make Wrobleski's total 25.2291 exceed Bregman's 24.7389. The source forecast classifies Wrobleski as SP despite saved RP eligibility; it projects 100.48 IP, 84.20 K and 8.74 QA3. The saved 2026 history records 140 IP and 22 starts. An RP eligibility label does not establish a reliever-only forecast.

This trace does not validate the expected longevity, workload or cross-position replacement scale. It does not establish a new player value, justify changing coefficients to favor Bregman, or demonstrate improved forecast accuracy.

## Released correction

A separate 2027 production outlook is shown above each multi-year score. The old number is explicitly labeled “8-year strategy fit change.” Contender prose follows the calendar comparison and identifies any opposing longer-term signal. Missing production or prospect timing blocks the short-term comparison, rather than entering zero. Prospect paths use the same supported published-ETA scenario as the existing fit calculation; the inherited path is never substituted. Picks receive no direct MLB-production credit before a player is selected, while keeping their dynasty and multi-year asset values.

The full numbers, both horizons, per-player assumptions and caveats remain behind “For more details.” Exports include the structured horizon trace. Dynasty prices, existing eight-year fits, projection inputs, quality weights, roster-space calculations and draft rules are unchanged.

## Broad checks and limits

- 300 deterministic new packages: 100 each of 1-for-1, 2-for-1 and 3-for-1, rotating across hitters, SP, RP, prospects and picks. These are synthetic mathematical stress cases, not observed trade outcomes or a representative accuracy sample.
- Both teams evaluated; all complete next-season comparisons reverse symmetrically.
- 45 packages have different signs for next-season production and the contender's eight-year fit. That supports separating horizons, not picking the horizon that gives a preferred trade verdict.
- Four saved historical packages also replayed.
- 5,757 MLB/hybrid asset-mode scores reconstruct from the annual paths; maximum floating-point residual 4.27e-14.
- No daily schedule, waiver-access optimization or weekly category-win forecast. Static lineup opportunity remains a separate diagnostic.
- Future injury recovery and role retention are not newly modeled. Cross-position replacement levels remain provisional; no empirically validated replacement-scale revision is ready here.
- Prospect arrival scenarios have no calibrated probabilities. No forward-season actual outcomes exist for accuracy validation.
- 39 targeted tests pass, including calendar alignment, missing-evidence handling, picks, symmetric comparisons, unchanged shared forecasts and conditional timing safeguards.

## Reproduction and checkpoint

Frozen inputs include the compact production catalog, timing scenarios, saved packages and exact uploaded trade JSON. Source hashes and per-case results are in Results.json (checked in as Results.json.gz; replay writes the readable JSON). Run from the repository root:

```
node scripts/audit-contribution-horizons.mjs
node --test tests/contribution-horizon.test.js tests/trade-explanation.test.js tests/shared-forecast.test.js tests/conditional-prospect-fit.test.js tests/prospect-timing.test.js
npm run build
```

The freeze flag is only for deliberately capturing a new input snapshot. Normal replay reads Frozen_Inputs.json.gz and needs no network. No production data or pricing writes occur during audit replay. Failed checks are explicit in Results.json; limitations are listed as blocked checks. This is horizon and explanation validation, not evidence the underlying model is fully calibrated.
