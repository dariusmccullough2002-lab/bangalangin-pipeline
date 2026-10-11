# Pitching history display correction

Preview only. Full-season scenario adapter and sidecar remain unchanged.

## Exact identity and source trace

Jacob Misiorowski: Fantrax 061yu, MLBAM 694819, FanGraphs 31623. The affected row is **2026 MLB**, not a minor-league row or the 2025 debut season.

The preserved Fantrax 2026 regular-season export maps into `career_history_cache.json` (asOf 2026-10-08), then the embedded `assets[].career_profile.seasons[]` publication record. The frozen row contains GP30, GS30, IP174 2/3, K252, HR14, ER35, QA3 26. This is verification against the preserved source snapshot, not a newly obtained official 2026 statistic. The complete snapshot remains preserved in research; its relevant row is included in `pitching-history-evidence.json`.

The separately cached official 2025 MLB record has IP66, K87, HR allowed8 (skills.homeRuns), GP15, GS14. `prototype.py:collect_cached_seasons` maps K from strikeOuts. `career_forecast.py:estimate` reads each stat field directly; `prototype.py:vector` explicitly uses K for strikeout and K/BB valuation contributions. Neither reads the table's HR/K fallback. The 2026 history cache already has K252, so this defect does not expose projections or valuation inputs to HR14 as K. No model or data numbers were modified.

## Root cause and affected scope

The embedded detail renderer used `fmt(z.stat.HR ?? z.stat.K ?? 0)` under the shared `HR / K` heading. Because 2026 pitchers have HR allowed populated, HR won. A separate shared expression selected R before ER. Column counts aligned mechanically but their meanings did not. Absent values defaulted to zero rather than unavailable.

There are 5,225 pitching history rows; 812 have HR populated and were vulnerable to HR selection instead of K. Representative frozen 2026 records: Skenes K200/HR20; Wheeler K193/HR21; Iglesias K64/HR6; Jansen K51/HR7. This is a shared Trade Analyzer MLB-history renderer defect. Minor-league performance cards in `profile-context.js:prospectMetrics` already read group.strikeOuts and split.k explicitly and do not use this fallback.

## Correction

`trade-analyzer-beta/history-display.js:historyTables` supplies separate hitter/pitcher tables with explicit keys. Pitchers show GP, GS, IP, K, HR allowed, ER, QA3, SV, HLD, plus year/level/role. Missing measurements say unavailable; observed zero remains zero. Official skills.strikeOuts and skills.homeRuns are same-stat source fallbacks, never interchangeable statistics. Hitter values remain unchanged where supplied.

This display does not reaggregate annual totals or combine MLB with MiLB. All 5,225 existing MLB pitching rows have unique player/year/level identities; therefore no duplicate totals are introduced. All 80 cached minor-league pitching profiles have aggregate K equal to the sum of distinct team/level splits. Representative multilevel examples: MLBAM815825 K118=68+50; 800537 K144=78+66; multiteam/multilevel809254 K141=47+60+34. These are cached October6 records. This audit confirms publication-record consistency, not a new collection of every original raw MiLB API response.

## Verification

Regression tests assert the verified Misiorowski source record K252 differs from HR14, correct ER35 differs from R43, header alignment, missing K, observed K0, official-source mappings, all existing pitching records, annual uniqueness, and all cached MiLB split sums. The starter-isolation verifier checks exact packed catalog bytes and unchanged valuation code, permitting only the two documented display hooks. The starter sidecar, formulas, workload candidates, dynasty calculations, rankings, replacement values, years2–8 and Trade Analyzer inputs are unchanged. Production remains unchanged.
