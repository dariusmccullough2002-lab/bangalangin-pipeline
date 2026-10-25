# Neutral-anchored strategy release — October 25, 2026

The former headline compared independent projected-production totals. That could turn a nearly even dynasty-price exchange into a large apparent contender loss before strategy preferences were considered. This release changes the executable value function and sums, not only their labels.

The headline now starts from each asset's saved neutral price. Balanced preserves that price exactly. Contender and rebuild apply the tested smooth timing response with a maximum 10% adjustment per asset. A normalized contender bell places 74.8% of preference weight in the next two years; the broad rebuilding bell places 24.0% there. Timing ratio r is the strategy-weighted annual path divided by the neutral-weighted path. Adjusted value = neutral price × [1 + .10 × tanh(log(r)/.5)]. All curves span 2027–2034. Curve widths, response scale and cap are explicit policy choices, not empirically learned prices.

Ranked players retain their ranking-led neutral prices. Production-only neutral prices remain provisional and retain the coverage warnings. No blanket common-scale conversion, graduation premium, bench coefficient or package penalty was introduced. This policy does not resolve the remaining unranked-price coverage problem.

Supported published-ETA annual paths determine prospect timing. Missing or zero timing signal retains the neutral price with an explicit status; it does not invent an ETA or erase asset value. Future picks use their saved conditional selected-player conversion paths, receive no immediate player slot or direct lineup-production credit, and retain the disclosed later-class proxy limitation. Predraft production or invalid paths cause neutral-price retention.

The point totals, selected-asset figures, details, plain-language explanation, uncertainty display and downloads use the same runtime value function. Each card separates neutral change from timing adjustment. Ranges combine saved neutral-price ranges with the entire permitted ±10% timing sensitivity; they are policy envelopes, not confidence intervals. Exports expose strategy_values and move raw competitive production quantities into production_values/production_range. Withdrawn inherited prospect trajectories remain redacted. Production forecasts are supporting diagnostics inside details, rather than the main trade score.

| Side receiving the named player | Neutral | Old contender score | New contender score |
|---|---:|---:|---:|
| Bregman for Wrobleski + Celesten | +1.8377 | -11.1185 | +4.9777 |
| Bregman for Wrobleski + Holliday | +0.6958 | -12.1499 | +3.9483 |
| Vargas for Naylor | +11.0457 | -1.4686 | +10.7026 |

Counterparty rebuild for the Celesten example: old +19.0749 → new -0.3601. Different strategy preferences need not sum to zero; neutral value remains conserved.

## Verification

Build passed. 63 targeted checks passed, including actual built val/stats hooks, full-population caps and neutral preservation, missing-data retention, prospect timing, pick timing, exports, evidence safeguards and shared forecasts. The release audit evaluated 1,000 neutral-price-matched packages (200 each of 1-, 2-, 3-, 4-, 6-for-1) with fixed seed 20261025 and canonical duplicates excluded, plus four saved and three named cases. No cap or balanced-preservation violations were found. All 2,546 source prices and forecasts are unchanged by the valuation accessor.

Reproduce:

```sh
node scripts/build.js
node scripts/audit-strategy-release.mjs
node --test tests/strategy-values.test.js tests/model-safeguards.test.js tests/shared-forecast.test.js tests/trade-explanation.test.js tests/contribution-horizon.test.js tests/prospect-timing.test.js tests/valuation-review.test.js
```

Verification.json records hashes, exact before/after figures and coverage; Packages.json.gz contains all sampled packages. The input catalog, shared-forecast evidence, timing evidence and their build scripts are already versioned in this repository. No fresh roster capture or medical information is part of this release.

Live_Verification.json records completed production browser, balanced-toggle, player-detail and download checks. No historical price-accuracy or category-win improvement is claimed.
