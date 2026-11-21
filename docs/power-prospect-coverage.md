# Power Translation Lab: expanded player directory and source coverage

Snapshot: November 20, 2026. Search is no longer restricted to the 178-player league-board audit.

## What is indexed

The directory contains 10,322 unique MLBAM identities from the 2026 MLB season player registries for sport IDs 11, 12, 13, 14 and 16 (AAA, AA, High-A, A and Rookie/DSL/complex), plus source-observed 2024–2026 hitters and existing board identities. Registered players can include pitchers, veterans and rehabbing MLB players; search inclusion is not prospect eligibility or an official prospect ranking. This is a dated directory, not a claim to cover every unsigned amateur, foreign player or future signee.

The observed panel has 13,108 distinct player/year/tracking-environment records. Of these, 2,047 records across 1,305 players pass the four-metric sample guard. Another 8,597 records have partial metrics and 2,464 have complete rates with insufficient or unknown sample counts. All of these remain selectable. Current plot-ready records are AAA and FSL A. Known rates in partial complex records can be inspected, but unknown tracking denominators do not pass the plotting guard.

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
