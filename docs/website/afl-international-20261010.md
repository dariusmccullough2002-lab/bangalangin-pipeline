# AFL and international profile preview — 2026-10-10

Preview: https://bangalangin-pipeline-itefwh1kl-shea-stadiums.vercel.app/#afl
Website commit: af9ff011ddf34e32395521377c24cf2a479e16e8
Branch: preview/afl-international-20261010
Production was not deployed.

## Implemented
- Cream editorial AFL tile with lime accent, modest diamond linework, season marker and evidence footer. Desktop grid stretches both panels equally; existing mobile stack is retained.
- AFL refresh, game tracker, resources and statistics remain in their existing components.
- Two unranked International profiles use existing routes, source panels and search architecture. Search accepts accents, aliases and Japanese characters.
- All 11 existing International player objects are byte-for-byte equivalent after JSON parsing; rankings are unchanged.
- No projection, workload or dynasty calculation files changed.

## Research
Pérez Acuña: Venezuelan catcher and 2027 international class reported by Sports Illustrated on February 15, 2026. Yankees verbal pre-agreement remains reported, not an official signing. Offensive impact and receiving are attributed scouting opinions, not tool grades. Measurements, birth date and signing bonus remain unverified.
https://www.si.com/es-us/mlb/quien-sebastian-acuna-prospecto-preacuerdo-yankees-2027
https://www.pinstripealley.com/yankees-news/176173/mlb-yankees-news-ben-rice-neck-gerrit-cole-2027-ifa-chase-hampton

Oda: Samurai Japan verifies Yokohama affiliation, U18 selection, right-handed throwing/batting and listed 186 cm / 81 kg measurements. Sporting News documents birth date and a reported 157 km/h peak (97.6 mph). Developmental scouting lists fastball, curve, slider and changeup; older velocity and measurements are explicitly dated. September 12 official game coverage records six innings, three hits and seven strikeouts. Public scouting attendance is reported interest, not an agreement. October 7 Nikkan coverage schedules a career announcement for October 15; that event had not occurred at this research cutoff. No MLB organization assigned.
https://i.japan-baseball.jp/jp/profile/202607004.html
https://i.japan-baseball.jp/jp/team/18u/2026/asianchampionship/player.html
https://i.japan-baseball.jp/jp/news/press/20260912_1.html
https://www.hb-nippon.com/articles/10940
https://www.sportingnews.com/jp/high-school-baseball/news/shoki-oda-tsn-baseball-player-profile/84f8e1b8fb7fd2366b9712e8
https://column.sp.baseball.findfriends.jp/?id=001-20260928-20&pid=column_detail
https://www.nikkansports.com/baseball/highschool/news/202610070001426.html?mode=all

## Validation
- npm test: 60 passed, zero failed.
- npm run build: passed.
- New record tests enforce no invented rankings, MLB IDs, signed organizations, bonuses, grades or projections.
- Original International records checked for exact equality.
- Vercel deployment READY, preview target (not production).
- Public desktop before screenshot captured. Desktop after and mobile screenshots and browser interaction QA are pending authenticated preview access. They must not be represented as completed.
- Protected preview offers ui-review.html with 320, 390, 768 and desktop widths, AFL and both profile routes for responsive verification.

## Access limitation
Automatic approval review rejected a seven-day deployment share link because it would alter access controls. Protection remains unchanged. Secure Vercel authentication was attempted, but the browser remains at sign-in as of this validation record.
