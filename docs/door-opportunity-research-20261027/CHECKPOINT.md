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


## Expansion and interaction update — October 27, later revision

Current coverage supersedes the initial 13-player list: 30 unique, non-debuted players across 22 MLB organizations, arranged as ten desktop rows of three. Seventeen additions are preserved separately in Expansion_Research.json. All 30 official player identities/debut records were refreshed together on October 27; no recorded debut. Frozen October 6 performance/ownership inputs now include all 30. Named incumbents must match the frozen club roster or the offline build fails.

New cases include prospects outside the top 100, defensive reserve routes, starting-depth routes, and explicitly conditional health/workload cases. Aidan Miller (11 AA PA), Jarlin Susana (2.2 AAA IP), Jamie Arnold (5 AAA IP) and Brandon Clarke (4 AA IP) are not presented as having demonstrated higher-level mastery. Small pitching samples now receive the same visible warning as small hitting samples. Pitching labels cover both starter and relief possibilities.

Player nameplates are now the profile links, with a directional arrow and keyboard focus treatment; bottom Full profile links are removed. Homepage portraits of Walcott, Made and Sloan were published in b68b469, with official source URLs saved in Homepage_Portraits.json. Profile ribbons follow current watchlist membership automatically, so expansion also adds ribbons to the new members.

Validation before release: source syntax/build; 30 unique IDs; all no-debut records; named-incumbent matching; frozen highest-level splits; grouped rather than league-rank order. Browser verification follows publication.


### Live verification of expansion

Production 9dbce7c, deployment dpl_9G57KuevcrmkHBaBn2KH9JtDTjk3: READY. Browser measured 30 cards, 10 distinct desktop row positions, three columns, 30 linked nameplates and zero footer profile links. Desktop viewport/scroll width matched. Clicking Jamie Arnold's nameplate opened his profile, where the watchlist ribbon was visible and returned to the watchlist.

At mobile 390px, all three homepage images loaded; the portrait row measured 220px and the page had no horizontal overflow. At mobile 320px, all 30 watchlist cards and links rendered in one column; grid client/scroll width both 275px and document client/scroll width both 305px. The homepage CTA opened the expanded watchlist. Each portrait is a link to the matching profile. Offline membership checks confirmed ribbons for all 30 current members and no ribbon for a non-member.

Proof images: knocking-door-home-portraits-20261027.jpg and knocking-door-30-players-verified-20261027.jpg. Source module syntax, publication build and image decoding checks passed. No trade-model or ranking values changed.


## Homepage jerseys and gold title — verified production

Production commits d068e5e (design) and 944d914 (scoped header-layout correction), October 27, 2026. The homepage second slide now features organization-color jersey SVGs for Franklin Arias, Jesús Made and Ryan Sloan, replacing portraits; Walcott remains on slide one. Surnames and verified 2026 affiliate numbers 16, 12 and 26 are shown. These are concept MLB organization jerseys using affiliate numbers, not future MLB number assignments. Frozen sources: Homepage_Jerseys.json.

The watchlist title uses the same gold color and folded corner as the profile ribbon. Explicit display:block prevents global header grid rules from squeezing the title. Build passed. Production Vercel deployment dpl_AusfE1Fp4C2pSp6aBGciU8uWn2rA READY. Live browser verified desktop gold title, all 30 cards, homepage three jerseys and Arias profile destination. Responsive review at 320px: homepage and watchlist document width 305px and scrollWidth 305px, title width 275px, no horizontal overflow. Screenshots saved in scratch: door-gold-title-20261027.jpg and door-home-jerseys-20261027.jpg.

Follow-up research leads, separate from this design task: secondary September reports mention De Vries shoulder surgery and Arnold facial/eye injuries. Obtain primary club/MLB confirmation before updating health language; these leads were not treated as verified evidence or model inputs.


## Five-slide homepage — implementation checkpoint

Added shared home-highlights.js and jerseys.js. Five slides: October #1 Walcott (pine/lime), debut watch (olive/gold), 2026 draft class (navy/ice), AFL featured performers (clay/apricot), #1 farm Yoho and a Bottle of Rum with Ryan Sloan (slate/lilac). All share one layout, type scale, jersey system and controls. Featured draft players derive from current Pipeline ranks; farm leader and premier prospect derive from October farm data.

AFL jerseys select up to three unique qualified active players, including hitters and pitchers, using the same featuredAflPlayers rules as the AFL board. Live MLB counts refresh on homepage load and every five minutes; complete snapshots are validated before replacing saved counts. Failure keeps visibly dated saved results. Registry data/homepage-jerseys.json stores official 2026 affiliate/AFL number sources. Future participants without verified numbers get no invented number. Team marks from https://www.mlbstatic.com/team-logos/{MLB-team-ID}.svg are saved under assets/jersey-marks. Jerseys show team-specific road/alternate colors, outlined twill-style lettering, sleeve marks, seams and cuff treatment; hover/focus reveals a front with club wordmark and placket. These remain stylized organization concepts, not a claim of assigned MLB uniforms.

Removed only the requested draft-listing consensus notice; international notice, draft methodology and ranking data remain. Existing 16 AFL/home-search tests plus new active/qualified/unique cross-role homepage selector test pass. Build and JS syntax checks pass. Browser verification pending deployment.


### Five-slide live verification

Production ce14a6d6d821f63cd43461d0faf87a02fb273e97; Vercel dpl_GwqP6KpBik9iiHTAzzEyRB9BB6Uq READY. Desktop shows five slides and correct 01–05 counters. Visually reviewed Walcott, draft, AFL and farm designs. The draft CTA opens 112 rows with the requested notice absent. AFL live feed succeeded; homepage O’Dowd / Reid / Francisca match the AFL page’s six featured performers, including a pitcher. Farm CTA opens the power rankings; Yoho is the October #1 and Sloan its saved premier prospect. Watchlist jersey routes match current profiles. At 320px outer review width, document clientWidth and scrollWidth both305; all five slide heights match at851px, with readable wrapped names and no document horizontal overflow. Three-pixel SVG rotation overhang remains inside hero padding. Browser extension metadata errors were observed; they originate from chrome-extension content scripts rather than site code.

Proofs: /workspace/scratch/pipeline-home-walcott-20261027.jpg, pipeline-home-draft-20261027.jpg, pipeline-home-afl-20261027.jpg. Responsive review was temporary. Existing saved watchlist research and rankings remain unchanged.


## Diamond layout correction — October 27

Replaced all five homepage arch graphics with baseball diamonds, bases and home plate. Labels sit in a centered, width-limited inner text box. Single-player slides (Walcott and #1 farm/Sloan) now use two separate columns with a15px desktop gap and12px phone gap, without negative margins or overlap. Group jerseys sit below their diamond with positive spacing. Removed sleeve image marks from both jersey faces. The #1 farm name remains in its separate linked caption; the diamond says POWER RANKINGS rather than squeezing in a long team name.

Production 2516c79893db36c09fd517027ce1a82f9dc2d7db, Vercel dpl_6zgU61SLBq5YHArsmJAehBS22R8N READY. Live desktop: five diamonds, zero jersey image elements, both single-player gaps15px. At320px review: document305px/client and305px/scroll; both single-player gaps12px, diamond128.7px, jersey85.8px; inner copy height82px and scrollHeight82px. JS syntax, homepage selection test and build passed. Final typography raises desktop diamond labels while retaining phone-specific sizing.


## AFL warm-tint theme

Added route-scoped afl-mode to the AFL board only. Its background is faint sand, panels warm cream, header a pale apricot wash, resources/game tracker dark clay matching the homepage AFL slide, and links/badges peach. Navigation retains the site's green branding. The class clears on navigation away; profile routes keep their current theme. Color-only treatment: no data, screening criteria or live refresh behavior changes. JS syntax and static publication build passed; Live production verification passed on commit8977853744735e208c9e028166f01de1df8fea29 / READY deployment dpl_3uFemskn81KRCgNymc5qNRRFx2rk: sand background rgb(248,242,235), clay resources rgb(75,48,45), six featured cards and successful MLB feed. Navigating Home clears afl-mode. Screenshot: /workspace/scratch/pipeline-afl-warm-tint-20261027.jpg.


## Individual debut-watch profile chapters and view toggle

Added a Knocking on the Door chapter only for the exact30 watchlist members. Canonical shareable URLs: #october-player/{Fantrax-ID}/knocking-on-door. Gold ribbons (including archive ribbons) link to the matching current profile chapter. The current profile keeps its nameplate, sidebar and existing tabs. Tab selection uses a profile subpath; source-entry and development-checkpoint lookups normalize the first two path segments so deep links retain context. Unknown/nonmember chapter requests fall back to scouting with no empty watch tab. Only October tabs change URL; other profile types keep their previous behavior.

The hub has Tiles and List buttons, shared filters and a persisted view preference. Both render the same30-player data. Tile initials replaced with jerseys; list rows include name/profile and direct Read breakdown links. The individual chapter and hub reuse the same why/need/opportunity/checkpoint paragraphs and dated evidence, preventing separate copies from drifting. Current affiliate jersey numbers were verified for all30 players via official MLB people data; Clarke37 came from the full-season FCL Cardinals roster. Existing dated number choices remain preserved.

Softened AFL theme: near-neutral warm paper, faint cream/apricot header, muted beige badges/buttons, and a resources panel closer to the site's forest green with a faint warm wash. Data and featured rules unchanged.

Validation: JS syntax and build pass;11 targeted profile/history/homepage/member-gating checks pass, including all30 matching profile identities and direct ribbon URLs plus nonmember exclusions. Broader development-checkpoint coverage test fails because seven pre-existing AFL profiles lack saved checkpoint entries: Felix Arronde, Williams Salazar, Elian Soto, Angel Perez, Anthony Santa Cruz de Oviedo, Kaleb Freeman and Luke Scherrer. Neither AFL roster data nor checkpoint data changed in this work; all30 watchlist players already have checkpoint entries. This unrelated evidence gap is retained rather than filled with invented research. Browser integration review follows deployment.
