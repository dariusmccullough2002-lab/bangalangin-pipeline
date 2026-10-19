# 2026 draft outcomes — October 19, 2026

All 112 players on the site's domestic draft board receive a dedicated section containing an individual ceiling, qualitative median, floor and explained risk level. This covers the entire board, not only one fantasy organization's roster. Research confidence and direct source links appear separately from development risk.

Research checked all 112 official player records. Full MLB Pipeline scouting text was available on Baseball Savant for 103. The other nine use identified alternatives: original scouting from The Prospect Porch (Ferraro), Yankees Farm Report (Potestio and Armstrong), Three Quarter Slot (LaFavor), Perfect Game firsthand showcase evaluations (Roberson, Bland and Kemp), Baseball Prospect Journal's firsthand interview/profile (Moore), and an explicitly limited indexed Baseball America excerpt (Plunkett). Dates of retrieval do not substitute for missing publication dates. Amateur showcase looks are not represented as new professional measurements.

Each assessment was written individually from the player's carrying skills, contact or command problems, defensive or pitching role, health history when published, and saved professional evidence. No ranking-based probability formula or automatic promotion from a short debut is used. Median means an editorial central development path, not the 50th percentile of a calibrated model and not an outcome conditional on reaching MLB. Reserve, relief, organizational-depth and no-established-role outcomes remain represented. Ceilings are plausible favorable branches, not guarantees; floors include failure to establish a major-league role.

Risk is relative to other draft prospects. The distribution is 12 moderate, 67 high and 33 very high; no player receives a low-risk label. Moderate risk still includes failure to establish an MLB career. Research confidence is moderate or limited, independent of the risk label. Pitching outcomes explicitly distinguish starters from relievers; bullpen success neither guarantees saves/holds nor implies premium fantasy trade value.

Six older summaries were reconciled where new report text supplied a materially different basis: Rose's defensive risk, Gracia's labrum surgery, Bumila's separate elbow procedures, Giles's hit-oriented foundation, Levu's raw-power foundation and Rabe's repertoire/command. Medical histories are attributed context, with no current clearance or recovery date inferred. Broader existing source/stat dates are preserved.

Evidence.json records the 112 identities, which player pages contained reports, the actual source used, source limitations, the retrieved player-page hash and each final assessment hash. It does not reproduce full proprietary scouting reports. Full source pages were used as temporary research material, not shipped in the site bundle.

The new section uses four labeled cards, a two-column desktop layout and a single column on smaller screens. It is inserted in the draft profile's scouting overview, with no section added to J15 profiles. Existing rankings, consensus scores, draft selections, grades, statistical tables, player identities, ownership, ETAs, August archives and calculator inputs remain unchanged.

Validation covers complete identity/source mapping, individual assessment coverage, medical/role distinctions, HTML escaping, every draft route's rendered section, exclusion from international routes, and the publication asset allowlist, alongside the full existing test suite and production build.

## Numerical season illustrations

The ceiling, central and floor cards now include individually selected numerical MLB-season illustrations for all 112 players (336 lines). They describe a future mature season at the specified role, not 2027, a calibrated statistical median, a probability-weighted career projection or a guaranteed amount of MLB opportunity. The underlying qualitative assessments, risks and source limitations remain in place.

Hitters show PA, AVG/OBP/SLG, OPS, HR, runs, RBI and steals. Pitchers show IP, starts, earned runs/ERA, WHIP, strikeouts/walks, K/BB, QA3, saves/holds and weighted SVH7. Catcher playing time, power/contact versus speed-led offense, starting versus relief roles, short MLB trials and uncertain bullpen usage receive different assumptions. Runs and RBI depend on lineup context. Saves and holds represent a hypothetical usage branch, not a future closer or setup assignment.

Stat_Line_Inputs.json records the individual numeric assumptions. scripts/build-draft-stat-lines.py creates consistent underlying batting counts and pitching totals from those inputs. AVG/OBP/SLG derive from the same counts; displayed OPS adds displayed OBP and SLG. ERA, WHIP and K/BB derive from consistent innings, earned runs, hits, walks and strikeouts. Decimal ties use half-up rounding. QA3 counts are individually selected feasible qualifying-appearance totals, not mechanically inferred from season ERA. SVH7 is three times saves plus twice holds. No playing-time or risk inputs in the trade calculator are changed.

A floor trial is explicitly conditional on receiving limited MLB exposure. Every floor card also presents the complete-bust alternative: zero MLB PA or IP and undefined rate statistics. The positive trial line does not assert that even the weakest prospect must reach MLB.
