# J15 / FYPD editorial ranking update — October 10, 2026

Base production: 1aff0ef81f82b997e41337ac30461a4352df2332.

| Player | Pipeline comparison place | Interpretation |
|---|---:|---|
| Shoki Oda | 2* of 13 | Conditional MLB international-route comparison; Japanese amateur, no confirmed J15 class year or MLB destination |
| Sebastián Pérez Acuña | 8 of 13 | 7th among the twelve J15 candidates; provisional editorial placement |
| Anthony Potestio | 70 of 112 | Domestic MLB-draft FYPD board; editorial insertion |
| Tyce Armstrong | 95 of 112 | Domestic MLB-draft FYPD board; editorial insertion |

These are Pipeline judgments, not discovered outside numerical rankings. No verified DD or BA FYPD rank was found for either newly placed domestic player. Consensus fields remain null for them. BA indexed snippets were found but article access returned 403; inaccessible content was not used. No numbered international publication rank is asserted for either international addition.

The exact placement is intentionally provisional. Each profile states the comparative rationale and evidence confidence. The original 110 domestic players and eleven international candidates retain their relative order; display numbers shift at the two insertions. Neither international player enters the domestic FYPD board: the league's December pool remains 2026 MLB draftees.

Sources:
- https://www.yankeesfarmreport.com/post/early-look-at-2026-draft-prospects — Aaron Lichstrahl, September 8, 2026, original scouting analysis; sample-sensitive interpretation.
- https://www.pinstripealley.com/yankees-mlb-draft/196988/yankees-mlb-draft-2026-day-2-picks-top-prospects-rounds-11-15 — July 12, 2026, Potestio's draft and college context.
- https://www.pinstripealley.com/yankees-mlb-draft/197032/yankees-mlb-draft-2026-picks-top-prospects-all-star-break — July 12, 2026, Armstrong's draft and college context.
- https://www.hb-nippon.com/articles/10940 — January 29, 2026, Oda evaluated as the leading high-school right-hander and a first-round NPB candidate; distinct from an international or fantasy rank.
- https://www.pinstripealley.com/yankees-news/176173/mlb-yankees-news-ben-rice-neck-gerrit-cole-2027-ifa-chase-hampton — February 15, 2026, attributed Romero scouting and reported Pérez destination.
- Official Samurai Japan U18 profile/game coverage, Sporting News velocity coverage, Nikkan October 7 career-status reporting and Pérez SI coverage remain linked in the profiles.

Reproduce: `node scripts/rank-editorial-additions.js`. The script uses stable IDs, the preserved domestic consensus order, and explicit editorial insertion positions. Re-running produces the same data. No statistical fitting, workload forecasts, dynasty valuations, tool grades, player IDs or performance counts change.

Validation before publication: 61 tests pass; build passes. Direct comparison with base verifies identical player IDs, source ranks, consensus ranks/scores, season counts, signing facts, measurements and class years. The new menu/page label is J15 Candidates. Oda's #2* condition is displayed in the list, profile and methodology.
