# Pitcher Opponent Hitting Quality (OQI)

One descriptive opponent-quality metric for every AFL pitcher with a completed matchup. Scope is regular season plus postseason; the Fall Stars Game and other exhibitions are excluded. The daily CBS+ workflow regenerates the pitcher scores from the same games. The hitter CBS+ calculation and existing scores are unchanged in this release.

## Formula and safeguards

For target pitcher A, exclude ALL A outcomes from each opposing hitter's PA, AB, H, total bases, BB, HBP, SF and SH. Also exclude A from the team and league offensive reference counts. Calculate each OPS from the resulting raw counts. No CBS+, PQI, pitcher ERA/K rate, season-wide fitted coefficient or cross-pitcher z-score normalization enters the formula.

For opposing hitter h, independent-sample reliability is PA_without_A / (PA_without_A + 40). Quality = 1 + reliability × [0.65 × (OPS_h_without_A / OPS_league_without_A − 1) + 0.35 × (OPS_h_without_A / OPS_team_without_A − 1)]. If a team reference is unavailable/zero, use the independent league reference. If the hitter has no usable independent sample or the league reference is unavailable, assign neutral quality 1. Weight hitter quality by completed matchup PA against A; OQI = 100 × that weighted average.

Weights and 40-PA shrinkage are transparent editorial choices, not fitted or empirically validated talent coefficients. 100 is neutral; higher means tougher independent hitting opposition. This ratio scale is not interchangeable with hitter OQI's 100 + 10z scale. It is not a pitching-performance score or a projection. No pitcher is penalized for striking out opponents in his own OQI.

All 157 pitchers have scores. Default leaderboard qualification is 20 matched BF; all smaller samples can be shown and remain available on profiles. Matchup BF follows the completing pitcher in the play feed, consistent with the existing CBS+ convention, not a claim that partial-PA inherited-walk accounting is identical to official pitcher BF. Two-strike pinch-hit strikeouts follow official charged-batter attribution. Defensive-shift violation awards are PA without AB, unlike ordinary fielding errors. These event distinctions allow all eight offense count fields to reconcile with official hitter lines.

## Website

- AFL page links to #afl/pitcher-oqi.
- Search, AFL-team filter, OQI/BF/name sort and an include-small-samples checkbox.
- Pitcher profiles and canonical inline AFL cards display OQI and matchup BF, with independent methodology and sample labels.
- Missing scores display a dash, never a fabricated 100; neutral 100 is used only when a real matchup lacks independent offensive evidence.
- Own ERA, strikeouts and walks are retained only as descriptive source fields; they do not feed OQI.

## Validation

35 focused tests pass, covering own-result invariance, team/league baseline leakage, neutral fallback, independent-sample shrinkage, sparse samples, scoring distinctions, filters, existing CBS+, combined postseason stats and current player/profile behavior. Production build passes.

The real-data audit checks all 157 pitchers twice: replacing every result against each target with a strikeout, then a home run, while preserving opponents, team identity and BF. All 314 own-OQI invariance checks pass. Other pitchers may correctly change because those results are independent evidence for them. Cross-pitcher ranks can change; the invariant applies to the target's own numeric OQI.

86 completed games, 6,862 PA, 107 official hitter counting lines reconciled, 157 pitcher scores, 148 qualified. See pitcher-oqi-audit-20261112.json for source checksum and results. The earlier broader-suite ProspectRank verification test remains a known pre-existing failure; that unrelated source registry is untouched.
