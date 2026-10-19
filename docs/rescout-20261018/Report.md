# Current-profile adequacy audit — October 18, 2026

The current site has 695 dataset entries covering 649 identity-matched players across October Pipeline, AFL, DSL, the domestic draft, J15 and international professionals. Every entry was checked, including canonical redirects. The revised request calls for adequate, relevant information on each page rather than a new independent scouting report for everyone.

The completed audit retains 557 players' existing substantive descriptions, makes targeted repairs for 80 players, and includes the 12 previously researched rewrites. No adequacy gaps remain in the checklist. These categories describe 649 unique people, not 695 separate reports. Archived August narratives remain historical.

The targeted work expands 70 thin domestic-draft entries and replaces generic context for ten AFL players lacking a saved regular-season aggregate. The latter distinguish rehabilitation, prior-year evidence and first professional appearances. Tekoah Roby's canonical October profile receives the same update. The AFL renderer loads the report catalog on player pages and displays each repair's sources and review date.

The earlier individual rewrites cover Sebastian Walcott, Jesús Made, Leo De Vries, Theo Gillen, Rainiel Rodriguez, Ryan Sloan, Josuar Gonzalez, Eli Willits, Eduardo Quintero, Mike Sirota, Franklin Arias and Emil Morales. Published observations, statistical facts and conditional development analysis are kept distinct. The review does not assign new tool grades or claim every retained profile has fresh external research.

Coverage.json records each identity, all dataset locations, resolved canonical profiles, relevant source URLs, specific context, development context and check results. scripts/audit-profile-adequacy.py regenerates that checklist and rejects empty or fragment-only narratives, unfinished placeholders, missing development context, unresolved redirects and broken source IDs. These are structural safeguards supporting the content review, not a substitute for scouting judgment. An explained unknown such as Oda's unsigned-amateur ETA remains valid information.

Adequacy_Repairs.json preserves the domestic-draft replacement text. AFL_Repair_Evidence.json retains the official fall rows and source references used for the ten repairs. Official_Season_Evidence.json preserves the retrieved 2026 rows supporting the earlier twelve rewrites. Existing statistical snapshot and publication dates remain in force; adequacy review does not make older evidence current.

Rankings, ownership, ETAs, scouting-grade tables, regular-season statistical tables, AFL roster/stat snapshots, calculator values and August archives are preserved. The ETA test now checks independently sourced display evidence instead of requiring stale October metadata to match it; no ETA value is changed.

Validation: 649 identities / 695 entries pass the audit; all 133 automated tests pass; the production bundle builds successfully. The targeted domestic-draft changes preserve all non-narrative player fields except source references and the explicit review context/date.
