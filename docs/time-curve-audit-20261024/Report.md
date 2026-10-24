# Ranking-anchored time-curve experiment — October 24, 2026

The time-curve idea works as an explicit strategy preference. It should adjust the existing neutral dynasty price, rather than replace that price with an unrelated sum of projected production. These experiments change no production website files.

## How the curve works

For each player, distribute their neutral value across eight forecast seasons (2027–2034) according to their saved annual contribution path and neutral discount weights. The pieces sum to exactly the original neutral value. A strategy curve then changes the importance of those years. All preference curves have area one: a narrow curve does not automatically mean a player has less total value.

There are two distinct objects: the player's contribution/value distribution and the team's timing-preference curve. A player need not have a bell-shaped career. The tested bell curves describe the team's preferences; multiplying them by the player's trajectory captures when that player is useful.

Baseline annual weights are proportional to 0.88^t. Gaussian season weights are integrated over each year's interval using Simpson integration (200 subdivisions), truncated to eight years and normalized. Policy parameters were fixed before evaluating results:

| Preference | Center, years from forecast start | Width | Weight in first two years |
|---|---:|---:|---:|
| Current contender discount | — | — | 48.6% |
| Front-loaded contender bell | 0.5 | 1.5 | 74.8% |
| Gentler contender bell | 0.5 | 2.0 | 62.2% |
| Broad rebuilding bell | 3.5 | 4.0 | 24.0% |

These shares are preference weights, not shares of any particular player's expected production. Rebuild emphasizes later seasons without making immediate contributors worthless.

Let P be neutral price, u_t annual contribution, b_t normalized neutral weights and s_t normalized strategy weights. Compute r = sum(u_t*s_t)/sum(u_t*b_t).

Two bounded policies were tested at c=0.10 and c=0.20:

- Hard cap: adjusted price = P * clamp(r, 1-c, 1+c).
- Smooth response: adjusted price = P * [1 + c*tanh(log(r)/0.5)]. The response scale 0.5 is an explicit sensitivity assumption, not fitted to trade outcomes. A zero ratio uses its limiting response of -1.

The smooth response is separate from smoothing the time curve. Its purpose is to avoid giving many different players the same maximum adjustment. Neutral timing preserves price. Multiplying a player's entire contribution path by a constant does not change their relative timing adjustment.

## Scope and results

Frozen input: `../horizon-audit-20261024/Frozen_Inputs.json.gz`. SHA-256 is recorded in Results.json. Supported prospect timing uses the supported ETA-aligned annual path; inherited unaligned prospect paths are not used.

Reused 3,000 neutral-price-matched hypothetical packages (1,000 each of 1-, 2-, and 3-for-1), plus 400 new neutral-price-matched packages (200 each of 4- and 6-for-1), fixed seed 20261024. New package selection uses price within 10%, never strategy results or named-player preferences. Canonical duplicate assets are excluded. The three previously discussed examples are reported separately and do not select parameters.

2,309 assets are supported after excluding 180 hypothetical duplicate pick slots; 57 assets remain blocked. For the Gaussian candidates, 180 owned picks retain neutral price with an explicit pick-specific timing limitation. A zero direct-player-production curve must not erase a pick's value. All 3,400 sampled packages have supported values. This sample therefore does not test trades involving the blocked assets.

| Contender policy | Median absolute trade-value change from neutral | 90th percentile | Assets at the cap, within numerical tolerance |
|---|---:|---:|---:|
| Existing timing, hard 10% | 0.77 | 3.95 | 1,742 |
| Existing timing, hard 20% | 1.56 | 6.28 | 800 |
| Front-loaded bell, hard 10% | 0.36 | 3.18 | 1,886 |
| Front-loaded bell, hard 20% | 1.25 | 6.53 | 1,723 |
| Front-loaded bell, smooth 10% | 0.49 | 2.17 | 6 |
| Front-loaded bell, smooth 20% | 0.99 | 4.34 | 6 |
| Gentler bell, smooth 20% | 0.82 | 3.54 | 0 |

The six smooth cases numerically near the cap are not evidence of a discontinuity. They have extremely low contender-to-neutral timing ratios. Broad rebuilding bell with smooth 20%: median absolute change 0.46, 90th percentile 1.86, zero assets near the limit.

A larger cap doubles the adjustment under the smooth formula, not the whole player value. A cap per player does not bound the percentage change in a near-zero package difference. Sign changes among near-even trades are not accuracy measures.

## Named examples

Numbers below are changes for the side receiving the player in the first column. Positive favors that side under the specified preference. Rebuilding results in Results.json use this same direction; reverse the sign for the counterparty. Both teams' differing preferences need not sum to zero, while neutral value remains conserved.

| Receives / sends | Neutral | Existing timing, hard 10% | Existing timing, hard 20% | Front-loaded bell, smooth 10% | Front-loaded bell, smooth 20% |
|---|---:|---:|---:|---:|---:|
| Bregman / Wrobleski + Celesten | +1.84 | +4.95 | +9.60 | +4.98 | +8.12 |
| Bregman / Wrobleski + Ethan Holliday | +0.70 | +3.92 | +8.69 | +3.95 | +7.20 |
| Vargas / Naylor | +11.05 | +12.02 | +9.42 | +10.70 | +10.36 |

The Vargas example retains his higher neutral price, while the smooth contender adjustment slightly reduces that advantage under the saved production trajectory. It does not force Vargas to be the better immediate producer. No named trade was used to tune the curves or limits.

## Recommendation and limits

Prefer the smooth bounded response over a hard clip if adopting time curves. A 20% outer limit offers more strategy expression; a 10% limit keeps prices closer to neutral. The 75% first-two-year curve matches the requested contender emphasis; the 62% version is a less aggressive sensitivity alternative. Neither is empirically established as the right preference.

All 12 unit tests passed, and population cap/area-preservation checks reported zero failures. This supports the arithmetic and policy behavior, not historical forecast accuracy or proof of fair market pricing. The inputs include production-only assets as well as ranking-led assets; anchoring existing neutral prices does not resolve missing dynasty-ranking coverage.

Annual forecasts still influence timing, especially uncertain prospect arrival dates and longevity. No curve repairs an incorrect trajectory. Aging may already be reflected in dynasty prices, so further timing adjustments can double count it. Picks require their own conversion/timing evidence. No new roster optimizer, replacement additions, positional opportunity, package-consolidation model, or weekly category simulator was introduced. Roster-space costs remain separate.

## Reproduce and resume

Run from repository root:

```
node scripts/audit-time-curves.mjs
node --test tests/time-curve-candidates.test.js tests/strategy-setting-candidates.test.js
```

`Results.json.gz` is the frozen result checkpoint; the runnable script regenerates readable Results.json using existing frozen catalog and prior package inputs. `curve-candidate.mjs` contains all formulas. No network is needed for reproduction after checkout.

Next step, if authorized: choose a documented strategy policy and integrate it consistently into all runtime value totals, uncertainty displays, reasoning and exports. Preserve raw production estimates as separate diagnostics. Do not deploy this audit as though it were a validated forecast improvement.
