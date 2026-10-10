# Website production verification — October 10, 2026

User explicitly authorized production deployment of website changes only.

Live: https://bangalangin-pipeline-zeta.vercel.app/#afl
Production commit: 1aff0ef81f82b997e41337ac30461a4352df2332
Feature commit: af9ff011ddf34e32395521377c24cf2a479e16e8
Vercel production deployment: dpl_JDrBxmN9miGMMWChncbCBBBXzTJ9 — READY.

## Checks
- 60 tests passed; build passed.
- Diff against prior production changes only AFL hero, International profiles/search/navigation, tests, website documentation and responsive review generator. No projection or dynasty calculation/data files changed.
- Desktop live AFL at 1363 px: both hero panels exactly 362.65625 px tall.
- Refresh clicked; MLB feed timestamp updated; game tracker, source links and all 251 roster profiles retained.
- Mobile rendering through the existing review iframe at 390 and 320 px: panels stack vertically and document has no horizontal overflow.
- Pérez Acuña and Oda profiles rendered at desktop and 320 px. Both mobile profiles have no page overflow.
- International search: accentless Sebastian Perez returns one of thirteen players; Oda returns one of thirteen. Profile links work.
- Global search: Japanese 織田翔希 routes to Oda; accentless Sebastian Perez routes to Pérez Acuña; exercised on desktop and mobile.
- Pérez remains an unranked 2027 J15 watch with reported NYY verbal agreement, official organization and measurements unverified.
- Oda remains an unranked Japanese amateur, destination unknown, official organization unverified, official 186 cm / 81 kg listing preserved.
- All eleven original international records remain exactly equivalent to their prior values.

Screenshots: qa/afl-desktop-after-live.jpg and qa/afl-mobile-after-live.jpg. Mobile screenshot shows the live 390 px iframe, not physical-device emulation.

Responsive review: https://bangalangin-pipeline-zeta.vercel.app/ui-review.html
The review frame renders the same public production application and exposes no additional research/model assets. Deployment protection was not changed.

Research sources and unresolved claims remain in the earlier dated preview report and each profile's source section. Its preview access status is a historical record superseded by this production verification.
