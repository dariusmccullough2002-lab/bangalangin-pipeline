# DD baseline plus research layer — October 13, 2026

**Status: offline research candidate; production unchanged.**

The candidate applies 377 numerical adjustments across the 648 ranked assets: 217 hitters, 132 starters and 28 relievers. The other 271 retain their current values. All 100 repository checks pass. These verify implementation and preservation, not empirical trade-price accuracy.

## Findings

The screenshot group spans 24.52–24.61 in production. The research-only candidate spans 24.18–24.64. Four players still cluster near 24.6. More source data does not automatically solve a compressed baseline curve. Alternative curve shapes were evaluated separately; wider spacing can move unrelated elite values substantially and is not justified as a research premium.

Carrigg’s MLB label is correct: he debuted in June 2026. His single MLB season limits confidence. Kodo lists .352 wOBA versus .316 xwOBA, .250 xBA and .407 xSLG: these temper his observed .279/.341/.477 line. The FanGraphs Steamer row has just 1 PA and is excluded from numerical use; ZiPS provides a usable rate benchmark.

Bradish’s dated 2026 Kodo record lists 155 IP, 142 K, 70 BB, 4.12 ERA, 4.46 FIP and 4.48 xERA. The expected-stat evidence does not justify a bullish override. His injury and “backup” depth labels are contextual, not an additional numerical discount. FanGraphs Steamer’s 154.145 IP and ZiPS’ 100 IP are provider workload scenarios; neither replaces the Pipeline availability model or supplies a verified 2027 workload.

Pasquantino’s .338 xwOBA is modestly above .331 observed wOBA, while Bauers’ .371 xwOBA is modestly below .381 observed. Bauers also has a 13.9% barrel rate, but barrel rate is not added as another bonus on top of the expected-quality family. Rodón’s 2.67 ERA versus 3.89 xERA argues against extrapolating the raw ERA. These are dated facts and model interpretations, not permanent player labels.

## Representative values

| Player | Live | DD baseline | Research candidate | Change vs live |
|---|---:|---:|---:|---:|
| Carlos Rodon | 24.61 | 24.55 | 24.61 | +0.00 |
| Vinnie Pasquantino | 24.58 | 24.53 | 24.59 | +0.00 |
| Cole Carrigg | 24.58 | 24.47 | 24.58 | +0.00 |
| Kyle Bradish | 24.57 | 24.67 | 24.18 | -0.38 |
| Jake Bauers | 24.52 | 24.62 | 24.64 | +0.12 |
| Jose Soriano | 20.50 | 20.96 | 20.61 | +0.12 |
| Mason Montgomery | 24.97 | 24.97 | 24.45 | -0.51 |

## Method

DD remains the source anchor. The research blend uses Pipeline talent rates, one FanGraphs Steamer/ZiPS ensemble and one Kodo expected-quality family. Missing sources return their share to Pipeline rather than becoming zero. The 65/25/10 research-input blend is a provisional policy, not a historically trained coefficient; it is distinct from DD’s final weight.

Talent is compared at the inherited role-specific reference exposure, not blanket 650 PA or 200 IP. Hitter counts are reconciled; QA3 retains the Pipeline’s actual-definition rate. Provider conventional QS is excluded. Provider SV/HLD do not replace the inherited forecasts, and no new long-term bullpen extrapolation is created. Ranking research compares players within H/SP/RP cohorts and maps that order onto their own DD ranks; this does not give relievers hitter or starter prices.

Final research influence is capped at 25% and shrinks with MLB reliability, short debut exposure, provider disagreement and projection-date uncertainty. Rank-equivalent departures remain within the inherited 10% boundary. A common fitted rank-value elasticity lets supported departures survive locally pooled curve sections. The exact elasticity and caps are valuation policy assumptions, not transaction-price calibration.

This replaces the existing overall MLB research adjustment rather than adding another copy of it. DD baseline reset, new research adjustment and change versus live are separate fields. Large differences from live can reflect removal of an old adjustment as well as fresh evidence. All non-adjusted assets—including protected prospects—retain their exact existing values.

The calculator’s actual statistical forecasts, availability, annual paths, competitive-fit scores and prospect distributions remain byte-for-byte unchanged. Updated research talent lines are audit inputs only. Saved neutral packages recompute on the candidate scale.

## Evidence and limitations

- FanGraphs: 329 adjusted players have both systems. Raw API rows lack explicit publication dates and season fields; they are weak rate benchmarks with halved freshness confidence, not certified next-season forecasts.
- Kodo: player pages retrieved for all 407 eligible ranked MLB identities; 345 adjusted players pass numerical expected-quality checks. IDs, names, MLB level, 2026 season, source dates and observed exposure must agree with the preserved catalog. Missing or incompatible fields remain contextual.
- Kodo’s current-week hitter projections are empty after the season; its bulk pitcher feed has no xERA data. Individual player endpoints supply the dated expected metrics used here. Remaining-season zero innings and one-game recent lineup snippets are not dynasty opportunity forecasts.
- Steamer and ZiPS are one projection family; Kodo expected stats, whiff and barrel diagnostics are one underlying-data family. Supporting metrics are visible but not separate stacked bonuses.
- No additional market-price claims, arbitrary RP haircut, manual player values or gaps to make every display unique.
- No new chronological out-of-sample test of this composite is available. The current source snapshots cannot honestly be presented as archived preseason forecasts. Production release is not recommended from implementation tests alone.

## Review recommendation

Keep the live release as the baseline while reviewing this candidate. The added layer provides reproducible research departures but does not fully resolve compression. Do not adopt the wider curve variants merely to increase spacing: their largest whole-catalog shifts are materially greater. Current missing confidence and chronology information limits how aggressively external projections should move DD.

## Sources

- [FanGraphs projection tables](https://www.fangraphs.com/projections)
- [Kodo Bradish profile](https://kodoanalytics.com/players/680694)
- [Kodo Carrigg profile](https://kodoanalytics.com/players/694249)
- [Kodo Pasquantino profile](https://kodoanalytics.com/players/686469)
- [Kodo Bauers profile](https://kodoanalytics.com/players/641343)
- [Kodo Rodón profile](https://kodoanalytics.com/players/607074)
- [Kodo Soriano profile](https://kodoanalytics.com/players/667755)

Reproduce: run `python docs/research-layer-20261013/build.py` and `npm test` from the repository root. The candidate calculator and full 648-row comparisons are in this directory; raw evidence is excluded from the production publication allowlist.
