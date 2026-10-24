# Strategy-setting audit — October 24, 2026

## Main finding

The user's concern is a confirmed mismatch with the requested valuation behavior. The current strategy view does not start with the displayed, ranking-led neutral value and adjust it. It replaces that value with a separate production-based quantity, then applies an eight-year timing preference. Those are different measures. This is not an arithmetic error or proof that the forecasts themselves are wrong.

For Shea receiving Bregman for Wrobleski + Celesten:

| Stage | Displayed balance for Shea |
|---|---:|
| Ranking-led neutral asset value | +1.8377 |
| Separate production baseline, balanced timing | −16.7423 |
| Current contender production fit | −11.1185 |

The baseline replacement changes the displayed number by −18.5799. The contender preference then moves it +5.6238 toward Bregman. Thus the contender timing preference moves in the expected direction in this case; it starts from a much less favorable production baseline. It is incorrect to attribute the entire neutral-to-contender difference to time weighting.

Bregman's neutral price is 33.2269, balanced production fit 19.9200 and contender fit 24.7389. Wrobleski's corresponding values are 18.1065, 23.2540 and 25.2291. Celesten's neutral price is 13.2828, conditional balanced production fit 13.4083 and conditional contender fit 10.6283. Prospects use the same supported published-ETA scenarios as the served model, not withdrawn inherited fit fields.

The screenshot's Holliday version reproduces the same pattern: +0.6958 neutral, −18.0826 production baseline, −12.1499 contender. Its timing preference improves the displayed balance +5.9327.

## What the current contender window means

The contender algorithm uses normalized .75^t weights over 2027–2034. Its first-year share is 27.78%; the first two years receive 48.62%, the first three 64.24%, and later years 35.76%. These are weight shares, not predicted production shares. A large prospect contribution starting in the third year can still outweigh a veteran. Shortening the comparison to one or two years changes the Bregman packages' production direction; the three-year sums favor the package once the selected prospect arrival scenario begins. None is a weekly category-win forecast.

## Population tests

Frozen catalog: 2,546 assets. Supported neutral and strategy comparisons: 2,271 after excluding 180 hypothetical numbered slots. Cases use canonical identity to block duplicate assets. Historical ownership, acquisition price and roster legality are not assumed for synthetic packages.

Tested the prior 300 broad packages, four saved packages, both Bregman variants and Vargas–Naylor, plus 3,000 additional packages matched using neutral prices alone: 1,000 each of 1-for-1, 2-for-1 and 3-for-1. Incoming single-asset price must be within 10% of the outgoing package. Fixed seed; no strategy scores or named trades used to select matches.

Among the 3,000 deliberately near-even neutral packages:

- 811 have opposite signs between neutral value and the current balanced production baseline, before contender timing is applied.
- 1,219 have opposite signs between neutral value and current contender fit.
- 642 flip signs between balanced production and contender production.
- The 90th-percentile absolute displayed difference from neutral to balanced production is 15.82; balanced to contender is 5.97.
- First-year production and current contender fit disagree in 536 cases; first-two-year production disagrees in 423.

These are structural stress tests, not accuracy measurements. Near-even packages can reasonably change direction with small preferences, so a sign flip by itself is not a model error. The test demonstrates substantial baseline substitution separately from timing adjustments.

No universal pitcher-only inflation was established. Among ranking-led records, the median balanced-production/neutral-price ratio is .909 for hitters, .936 for starters and .825 for relievers. Each group has a wide spread; Wrobleski/Bregman cannot justify a blanket pitcher haircut.

## Offline policy candidates

Candidate definition:

```
strategy value = neutral asset price × clamp(
    current strategy production fit / balanced production fit,
    1 − cap, 1 + cap
)
```

Caps 0%, 10%, 20% and 30% were specified before evaluating results. Balanced always equals neutral price. Production rates, annual paths and ETA scenarios are unchanged. Every asset uses the same rule; no named-player coefficients. Unsupported evidence blocks a value. If both production quantities are zero, the neutral asset price is retained with explicit no-timing-information status; no production is invented.

This is a candidate valuation policy, not a trained projection or measured trade-market preference. It may double count aging already embedded in rankings, and a cap has not been empirically selected.

| Shea receives Bregman, sends… | Neutral | Current contender | 10% candidate contender | 20% candidate contender |
|---|---:|---:|---:|---:|
| Wrobleski + Celesten | +1.84 | −11.12 | +4.95 | +9.60 |
| Wrobleski + Holliday | +0.70 | −12.15 | +3.92 | +8.69 |

The counterpart's rebuild result under the 10% candidate is +1.89 for Celesten, +3.15 for Holliday. Different strategies need not sum to zero; using the same strategy on both sides does.

Across neutral-matched packages, the 10% candidate reduces median departure from neutral to .59 and the 90th-percentile departure to 3.58. It changes the neutral sign in 649 cases versus 1,219 under current contender fit. This follows the desired neutral anchor more closely by construction; it is not proof of better trading outcomes.

An important countercheck: the 10% candidate disagrees with first-season production in 877 cases, versus 536 for the current contender production score. Even the 20% candidate disagrees in 682. Neutral anchoring and pure immediate-production alignment are different objectives; one blended score cannot be claimed to optimize both from these tests. Keep the explicit next-season comparison alongside any strategy-adjusted asset-price policy.

## Recommendation and release decision

The supported direction is to preserve ranking-led neutral value as the asset-price anchor, apply a modest, disclosed strategy preference, and continue showing next-season production separately. A two-year production view is a useful additional sensitivity for a competitive window; do not silently substitute it as an empirically optimal horizon.

Do not deploy a universal pitcher penalty, a Bregman boost, a package discount, or an asserted calibrated cap based on this audit. The 10% candidate is a reviewable conservative policy sensitivity, not an accuracy-validated replacement. This task runs the requested tests; production values and settings have not changed.

## Verification and resume checkpoint

Six candidate tests pass: neutral preservation, bounded/monotone factors, missing-evidence blocking, scale invariance, calendar-window isolation, and preventing substitution of raw contribution for neutral price. Population checks found no failures in balanced-price preservation or asset caps.

Frozen model inputs and their SHA-256 are referenced from `docs/horizon-audit-20261024/Frozen_Inputs.json.gz`; the canonical-identity sidecar is tied to the same source HTML hash. Complete results are checked in as Results.json.gz. Replay writes the readable JSON and compressed result. No network or production writes occur:

```
node scripts/audit-strategy-settings.mjs
node --test tests/strategy-setting-candidates.test.js
```

Offline candidate code is in policy-candidates.mjs. Package matching, assumptions and failed/blocked checks are recorded in results. No future observed outcomes, transaction-price labels, daily lineup optimization or new injury/role model were available. Continue strategy-policy implementation only with explicit acknowledgement that the adjustment is a chosen preference, not newly proven forecast accuracy.
