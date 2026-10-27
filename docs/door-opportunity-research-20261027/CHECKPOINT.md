# Knocking on the Door: opportunity research, October 27, 2026

User correction implemented: only the homepage rotates. Player watchlist uses a three-column desktop grid, two columns on tablet and one on mobile. No player swipe controls. Group/filter by roster path, MLB organization and hitter/pitcher. Homepage carousel retained.

## Frozen evidence

- Official MLB roster captures for all 30 clubs, condensed to player identity/status and team-matching MLB regular-season hitting, pitching and fielding usage. Source URLs retained. Nine clubs used for these 13 editorial cases.
- Official people records checked October 27: none of the 13 has a recorded MLB debut.
- Separate, frozen October 6 league player inputs preserve identity, ownership, rank, counts and level samples. Later roster/transaction captures are not represented as October 6 evidence.
- Editorial research links nine original FanGraphs scouting articles with original dates. These were read October 27. Weaknesses are reported observations; checkpoints and proposed monitors are editorial interpretations.

## What changed

Removed the initial top-32-derived eligibility screen. Included Fischer (#90), Burke (#144) and Adams (#147), plus Doyle (#54), and retained higher prospects only with an explicit roster case. This remains a researched shortlist, not a probability-ranked or exhaustive all-baseball selection model. More organizations can be added through the same evidence requirements.

Each case names incumbents, an organizational need or absence of one, a conditional role, development checkpoint, dated scouting finding and unmeasured follow-up metric. Need signals use actual club OPS/usage where relevant; OPS alone is not a park-adjusted comparison or defensive evaluation. Clubs with several competing prospects do not receive multiple imaginary vacancies. Thin AAA samples (Walcott/Sirota nine PA) and Willits' 17 AA PA are explicitly flagged. Catchers need receiving trust and workload readiness, not only offensive results.

## Reproduce

`python scripts/build-door-watch.py` rebuilds the public dataset offline from the three frozen inputs plus Editorial_Research.json.

`python scripts/research-door-rosters.py` refreshes the public official roster and people captures (network required). This does not change editorial conclusions automatically. Review dates, roster moves and debut status before rebuilding. It intentionally does not infer contract/free-agency status from roster membership.

Roster extraction excludes non-MLB/nonmatching-team splits and never adds combined totals to team splits. Fielding games do not imply future assignments. The full original hydration response is local intermediate data; the reproducible, source-linked condensed extract is committed.

## Checks

PASS: source module syntax; production build; all 13 unique identities; no recorded MLB debut; every named incumbent matches the frozen club roster; every player has AA/AAA sample evidence; three players outside league top 75; ordering differs from league rank.

PASS (live production 20a2ffe): desktop 1363px renders three cards on the first row and the fourth on the next. 390px and 320px iframe reviews render one column with no grid overflow; 320px document width and scroll width both 305px after the scrollbar. Tablet 768px renders two columns. All 13 cases render. MIL filter returns four players; MIL plus rotation returns zero with the empty-state message; rotation plus pitchers across clubs returns two. Fischer evidence disclosure shows the dated report, exact named incumbents and source links. Homepage carousel reaches slide two; its CTA opens the watchlist. Mobile Menu → Resources → Knocking on the Door opens the same watchlist. Browser warnings observed were extension metadata messages, not application errors.

PASS: offline rebuild is byte-for-byte reproducible from the frozen inputs. Production deployment dpl_EiDEssUMZwuuSgje5fWyMcgcnaXD reported READY. Public URL: https://bangalangin-pipeline-zeta.vercel.app/#knocking-on-door.

Proof screenshot: knocking-door-research-grid-20261027.jpg, captured from the live desktop three-card row. No model/trade valuation code was changed.

## Limitations / blocked measurements

No independently collected current pitch-level Prospect Savant data. No numeric whiff, zone-contact, pitch-shape or command changes are invented; historical source figures are dated. No instruction to increase changeup movement without shape evidence. This is a conditional 2027 watch, not a calibrated prediction or an Opening Day lineup. October roster snapshots do not resolve future transactions, contracts, recovery or club promotion decisions. A debut does not guarantee regular fantasy playing time. ETA labels are contextual only; FanGraphs organizational ETAs can follow Rule 5 protection timing.
