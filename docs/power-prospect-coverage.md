# Power Translation Lab: expanded player directory and source coverage

Snapshot: November 20, 2026. Search is no longer restricted to the 178-player league-board audit.

## What is indexed

The directory contains 10,360 unique MLBAM identities from the 2026 MLB season player registries for sport IDs 11, 12, 13, 14 and 16 (AAA, AA, High-A, A and Rookie/DSL/complex), plus source-observed 2024–2026 hitters and existing board identities. Registered players can include pitchers, veterans and rehabbing MLB players; search inclusion is not prospect eligibility or an official prospect ranking. This is a dated directory, not a claim to cover every unsigned amateur, foreign player or future signee.

The observed panel has 23,748 distinct player/year/tracking-environment/provider records. Of these, 2,047 records across 1,305 players pass the four-metric sample guard. Another 15,188 records have partial metrics and 6,513 have complete rates with insufficient or unknown sample counts. All of these remain selectable. Current plot-ready records are AAA and FSL A. Known rates in partial complex records can be inspected, but unknown tracking denominators do not pass the plotting guard.

## Public sources and availability

- MLB Stats API season registries supply stable MLBAM identities, primary positions and birth dates. Official names and provider names are retained as aliases. Name alone is never used to join measurements.
- Prospect Savant's public leaderboard JSON, used by its free leaderboard page, supplies 2024–2026 hitter observations at AAA, AA, High-A, A and Rookie. No PS Plus export, authenticated route, private feature or account is used.
- Already-reviewed official Baseball Savant regular-season snapshots supply complete AAA/FSL components for all source hitters, expanding beyond the previously filtered board records.

Prospect Savant's page states that AA and High-A have no Statcast impact measurements. Other Single-A records outside the FSL and DSL records lack Statcast impact; complex records have partial tracking. Its backend sometimes fills unavailable fields with zero. The importer applies the same source/level masks as the public UI:

| Source environment | Chase / Whiff | Hard-Hit / Barrel |
| --- | --- | --- |
| AAA | When observed | When tracked |
| AA / High-A | When observed | Missing, never zero-filled |
| A with `aball_src=fsl` | When observed | When tracked |
| Other A with `aball_src=agg` | When observed | Missing |
| Rookie with `rk_src=dsl` | When observed | Missing |
| Rookie with `rk_src=cpx` | When observed | Partial observations, when positive-EV tracking is present |

A genuine observed zero Barrel rate is retained when its tracking context is known. A zero used as an unavailable-data placeholder is masked. A zero Chase value without an outside-zone denominator is not certified as an observed zero. Nonzero source-reported Chase/Whiff rates remain visible even when their raw denominator counts are not exposed; the missing counts still prevent plotting. No plate-discipline value is inferred from K% or BB%; no impact metric is inferred from scouting prose or surface results.

## Provenance, samples and selections

All four components of a record come from a single provider/environment. When an official record duplicates a Prospect Savant player/year/environment, the official record takes priority; component rates are never blended. This matters because the snapshots can differ in PA totals and coverage. Retrieval date does not guarantee that a source is complete through that date. Source URLs and retained-source JSON SHA-256 hashes are in the catalog manifest. Official CSV snapshot manifests remain in `power-translation-minor.json`.

Plotting requires all four observed component rates plus 100+ source PA, 100+ swings, 100+ outside-zone pitches and 50+ tracked BBE/provider BIP. Unknown counts fail the guard. The selected panel labels the denominator as tracked BBE or provider BIP and displays unknown counts honestly. Partial records remain useful for viewing Chase, Whiff, K%, BB%, ISO, wOBA, Zone Contact, Zone Swing and EV90 where actually available; those extra measurements do not replace missing inputs to the frontier.

No seasons or levels are aggregated by this tool. Provider-published same-level league aggregates retain explicit environment labels. The selector defaults to the latest observed year and highest observed level, including partial records, rather than silently substituting an older complete sample. Users can select each other record. Historical age, when available, is calculated from the official birth date at June 30 of the observed season and rounded to one decimal; it does not enter the model.

Search includes aliases and MLB IDs. Existing Pipeline profile links are retained; other provider-observed players link to Prospect Savant. Pitchers remain findable, with no batting measurements invented for them. If the expanded files cannot load, the existing league-board view remains available with an explicit fallback message.

The investigation table defaults to the league board and offers all tracked hitters as a separate universe. Ownership is still the dated October 6 league snapshot, not a live ownership feed. Broadening search does not change any main ranking, grade, trade value, Decision Lab or FYPD recommendation. No new translation coefficient or model probability is assigned.

## Reproduction

Run `python scripts/build-power-prospect-universe.py`. The script uses a scratch cache specified by `POWER_SOURCE_CACHE` or a sibling `prospect-source-cache` directory. Both catalogs are published as `.json.gz` to keep transfers to approximately 1.7 MB total rather than 17.5 MB of uncompressed JSON. The existing supported-browser gzip loader decodes them locally. Source availability masks and identity/sample guards are tested in Python and JavaScript.

This release is a fixed snapshot. It does not set up recurring refreshes or imply validated age/level/park/competition translation. The four-component MLB reference, its coefficients and its experimental status are unchanged.

## TJ Stats integration — November 20, 2026

All 15 public regular-season batter leaderboard snapshots for 2024–2026 and AAA, AA, High-A, A and Rookie were queried using the same unauthenticated summary route as the free TJ Stats leaderboard. This adds 10,640 separate source records and 38 identities. No paid tools, subscription exports or credentials are used. TJ Stats is attributed on every record and linked from the selected panel. The season / level / source menu retains both providers rather than blending rates.

TJ rates arrive as fractions and are multiplied by 100 once. A null remains null. Known zero Barrel rates remain zero when an observed exit-velocity context exists. No level-wide zero mask is applied to TJ observations: a small tracked 2024 AA subset remains available. 2026 High-A and AA have no reported impact; Neyens High-A has null Hard-Hit, Barrel and Chase in TJ, with Whiff 43.52%. The public summaries do not provide verified swing/outside-zone counts or tracked EV/LA denominators. Provider BIP is displayed separately and cannot substitute for tracked BBE. Therefore TJ summary records do not bypass the existing plotting guard, even when all four rates exist.

The public source has no 2024/2025 Rookie rows and 529 Rookie rows for 2026, with a maximum of 77 listed PA at retrieval. These are partial observations, not full-season coverage. Its Rookie and A aggregates can include different tracking environments. No claim is made that every prospect has observed Hard-Hit or Barrel data. Exact repeated rows are collapsed; conflicting rows for the same player/season/level are excluded and recorded as `conflictingPlayerIdsExcluded` in the source manifest. Source hashes and returned row counts remain in the downloadable directory. No rates are averaged to resolve conflicts.

TJ's live public website was used rather than its public Hugging Face archive, whose latest repository update was April 5, 2026. The latter is not a current-season substitute. Source: https://tjstats.ca/leaderboard/ . This update adds source ingestion and records; it does not schedule automatic refreshes or change rankings, grades, model coefficients or probabilities.
