# Player position audit — November 17, 2026

Checked 925 MLB-linked display records representing 797 distinct MLBAM identities across the draft, DSL, international, November rankings, AFL and Knocking on the Door datasets. All 797 IDs returned an official MLB player record.

Corrected or clarified 30 display fields for 17 identities across five published datasets. Rankings, roster ownership and stored fantasy eligibility were not recalculated.

## Review method

Compare official primary positions by MLBAM identity, treating OF and specific outfield positions, pitching-handedness labels and valid multi-position lists as compatible. Inspect conflicting current MLB/MiLB scouting and assignment coverage before correcting a label. A primary-position mismatch alone is not a correction: for example, the official primary record still calls Bo Lowrance a shortstop, while current scouting supports third base. Likewise, Jonathon Long's primary API record says 3B while current scouting supports the site's existing 1B.

The initial raw 120-field mismatch count includes broad/specific labels, fantasy roster slots and legitimate defensive usage; it is not an error count. Historical archive labels and source-rank transcriptions remain historical.

## Reviewed corrections

| Player | Display position | Evidence |
|---|---|---|
| Bo Lowrance | 3B | [Official source](https://www.mlb.com/milb/prospects/2026/draft/bo-lowrance-836574/) — Draft listing was SS; current scouting identifies 3B. |
| Josh Adamczewski | LF | [Official source](https://baseballsavant.mlb.com/savant-player/josh-adamczewski-815304) — Current scouting identifies left field rather than shortstop. |
| Ike Irish | OF/1B | [Official source](https://www.mlb.com/milb/prospects/orioles/ike-irish-702610) — Transitioned from catching to outfield/first base. |
| Ethan Petry | 1B/OF | [Official source](https://www.mlb.com/milb/prospects/2026/nationals/ethan-petry-701337) — Current Pipeline lists both first base and outfield. |
| Billy Amick | 3B | [Official source](https://www.milb.com/player/billy-amick-701771) — Official current assignment is third base. |
| Mitch Voit | SS/2B | [Official source](https://www.mlb.com/milb/prospects/2026/mets/mitch-voit-702491/) — Current Pipeline retains shortstop and second base. |
| Henry Godbout | SS/2B | [Official source](https://www.mlb.com/player/henry-godbout-804995) — Official assignment lists SS; retain the existing second-base designation as a secondary role. |
| Xavier Isaac | 1B | [Official source](https://www.mlb.com/milb/prospects/rays/xavier-isaac-800060) — UT was a fantasy slot, not his defensive position. |
| Eduardo Beltre | OF | [Official source](https://www.milb.com/player/eduardo-beltre-815924) — Current official position is OF; DH was a roster label. |
| Jeancer Custodio | OF | [Official source](https://www.mlb.com/player/jeancer-custodio-836586) — Official assignment is outfield, not a DH-only defensive role. |
| Caleb Bonemer | 3B/SS | [Official source](https://www.mlb.com/milb/prospects/whitesox/caleb-bonemer-815352) — Current Pipeline lists 3B/SS; AFL OF label is incorrect. |
| Jack O'Dowd | 1B | [Official source](https://www.milb.com/player/jack-o-dowd-691942) — Official AFL assignment lists first base, not catcher. |
| Dalton Wentz | 3B/2B | [Official source](https://www.mlb.com/milb/prospects/2026/draft/dalton-wentz-807275) — Existing researched draft profile and official primary position support 3B/2B rather than AFL SS. |
| Cole Mathis | 3B/1B | [Official source](https://www.milb.com/player/cole-mathis-695573) — Official assignment lists 3B; retain first-base usage as secondary. |
| Cade McGee | C/3B | [Official source](https://www.mlb.com/cardinals/news/cardinals-prospect-cade-mcgee-talks-versatility-in-arizona-fall-league) — Official AFL catcher listing plus documented infield versatility. |
| Sammy Hernandez | C | [Official source](https://www.milb.com/player/sammy-hernandez-803679) — Official catcher; AFL second-base label is incorrect. |
| Brandon Eike | 1B/3B | [Official source](https://www.mlb.com/rangers/news/2026-arizona-fall-league-rosters) — Official AFL roster lists both first and third base. |

## Limits and retained records

The international amateur list contains 41 profiles without an MLBAM ID, and the international professional list contains five without an MLBAM ID. Their existing sourced positions were retained, not marked independently reverified by this MLB API check. The 355-row August catalog is historical and has no MLBAM field; it was inspected for scope but not overwritten with current roles.

Matos and Salio retain their sourced third-base display despite a shortstop primary API label. Existing utility/two-way projections, multi-position use and legitimate AFL game assignments were not automatically discarded. Fantasy eligibility and current defensive projection are separate concepts.

## Exact changed fields

- Bo Lowrance: `data/draft/2026.json/players/12/position`: SS → 3B
- Caleb Bonemer: `data/editions/october-2026.json/rankings/14/position`: SS → 3B/SS
- Caleb Bonemer: `data/editions/october-2026.json/rankings/14/rankingPosition`: 3B,SS → 3B/SS
- Josh Adamczewski: `data/editions/october-2026.json/rankings/25/rankingPosition`: SS → LF
- Ike Irish: `data/editions/october-2026.json/rankings/78/position`: RF → OF/1B
- Ike Irish: `data/editions/october-2026.json/rankings/78/rankingPosition`: C,1B → OF/1B
- Mitch Voit: `data/editions/october-2026.json/rankings/102/position`: SS → SS/2B
- Mitch Voit: `data/editions/october-2026.json/rankings/102/rankingPosition`: 2B → SS/2B
- Henry Godbout: `data/editions/october-2026.json/rankings/166/position`: SS → SS/2B
- Henry Godbout: `data/editions/october-2026.json/rankings/166/rankingPosition`: 2B → SS/2B
- Ethan Petry: `data/editions/october-2026.json/rankings/196/position`: 1B → 1B/OF
- Ethan Petry: `data/editions/october-2026.json/rankings/196/rankingPosition`: OF → 1B/OF
- Billy Amick: `data/editions/october-2026.json/rankings/203/position`: 1B → 3B
- Billy Amick: `data/editions/october-2026.json/rankings/203/rankingPosition`: 1B → 3B
- Xavier Isaac: `data/editions/october-2026.json/rankings/216/rankingPosition`: UT → 1B
- Eduardo Beltre: `data/editions/october-2026.json/rankings/246/position`: DH → OF
- Eduardo Beltre: `data/editions/october-2026.json/rankings/246/rankingPosition`: DH → OF
- Jeancer Custodio: `data/editions/october-2026.json/rankings/254/position`: DH → OF
- Jeancer Custodio: `data/editions/october-2026.json/rankings/254/rankingPosition`: DH → OF
- Caleb Bonemer: `data/afl/full-2026.json/players/8/position`: OF → 3B/SS
- Jack O'Dowd: `data/afl/full-2026.json/players/56/position`: C → 1B
- Cole Mathis: `data/afl/full-2026.json/players/99/position`: 1B → 3B/1B
- Dalton Wentz: `data/afl/full-2026.json/players/134/position`: SS → 3B/2B
- Brandon Eike: `data/afl/full-2026.json/players/174/position`: 3B → 1B/3B
- Cade McGee: `data/afl/full-2026.json/players/176/position`: 3B → C/3B
- Ike Irish: `data/afl/full-2026.json/players/184/position`: OF → OF/1B
- Sammy Hernandez: `data/afl/full-2026.json/players/200/position`: 2B → C
- Caleb Bonemer: `data/afl/2026.json/players/2/position`: OF → 3B/SS
- Ike Irish: `data/afl/2026.json/players/16/position`: OF → OF/1B
- Caleb Bonemer: `data/knocking-door-2027.json/players/10/position`: 3B,SS → 3B/SS
