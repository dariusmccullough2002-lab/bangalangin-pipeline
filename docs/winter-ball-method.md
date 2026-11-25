# Winter Ball Watch — WPS-v1

Public developmental research, separate from fantasy ownership and strategy. Official MLB Stats API snapshots for LIDOM (131), LMP (132), LBPRC (133), LVBP (135). LMP identity checked against the official `/leagues?sportId=17&season=2026` registry on every refresh. Initial season: 2026–27, API season 2026.

## Scope

V1 covers **regular-season statistical appearances**, not roster-only registrations. Postseason, exhibitions and all-star games are excluded explicitly with `gameType=R`. It does not claim to show a prospect who has only registered on a roster. Daily game logs, rolling windows, notifications and scouting enrichment remain future work.

## Publication

`scripts/winter-ball.py` fetches all pages of official hitting/pitching counts for each league, validates counts/identities/season, and hydrates official DOB, position and organization. Official 2026 regular-season records across MLB/AAA/AA/High-A/Single-A/Rookie identify highest affiliated level. This includes rehab appearances; the highest appearance is an experience indicator, not a durable assignment. MLB debut or MLB-level evidence excludes a player from the prospect dashboard. Age ≤25, known prior level, and an affiliated appearance or Pipeline match are required. All players remain available in the full leaderboard.

Pipeline matching uses MLBAM IDs from existing public profile datasets, including `data/players.json`. Unique normalized-name matches are lower confidence and never override a conflicting known ID. Unknown metadata stays null. Private fantasy owners, strategy and league-specific valuations are never exported.

Source requests use `/stats?stats=season&group=hitting|pitching&season=2026&sportIds=17&leagueIds=ID&gameType=R&playerPool=ALL`, plus `/people`, `/teams`, and affiliated `/stats` with sport IDs 1,11,12,13,14,16. Full source URLs are saved per league. No browser calls to live stats endpoints.

Every league must validate for an initial publication. On later runs a failed league retains its complete last good data, timestamp and signal, marked stale, while successful leagues can publish. If all leagues fail, the prior JSON is untouched and the job fails. Context-refresh failure retains previous context with a stale flag; initial missing context fetch aborts rather than inventing data. Publication uses an atomic file replace after validation. Per-league last-success dates and a global last-fully-successful date remain separate.

Validation rejects empty/truncated pagination, wrong leagues or seasons, malformed integer counts, duplicate MLBAM IDs within league/group, impossible components/percentages and invalid baseball IP. Prior identities/counts cannot regress unexpectedly. Mass loss >15% or disappearance >max(2,5%) triggers stale retention. Official count corrections require a reviewed workflow-dispatch override; it does not bypass malformed-response checks.

The hourly GitHub workflow runs at minute 15 of every hour during October–February. Scheduled runs may be delayed by GitHub Actions; timestamps show when official data was actually retrieved. It runs tests and a production build before committing. A season archive guard stops API retrieval after every configured league end date has passed and a clean final refresh succeeds. A February 8 hard stop prevents indefinite retrieval if an official feed fails to mark completion. The page remains readable as an archive. Advancing to a new season requires an explicit reviewed configuration/route update, not silent reuse of the prior season.

## Derived rates

Hitting: K/PA; BB/PA; BB/K; ISO=SLG−AVG; HR/PA; SB/(SB+CS). AVG=H/AB; SLG=TB/AB; OBP=(H+BB+HBP)/(AB+BB+HBP+SF); OPS=OBP+SLG. Zero denominators are null, displayed —. No synthetic tracking metrics.

Pitching: outs are authoritative; IP is baseball thirds. ERA=27 ER/outs; WHIP=3(H+BB)/outs; K/BF; BB/BF; (K−BB)/BF; K/9=27 K/outs; BB/9=27 BB/outs. Missing advanced data is not inferred.

## Transparent descriptive signal

League baselines are aggregate counts/rates, separately for hitters/pitchers. No pooling of leagues. Hitting performance=(OPS−league OPS)/.180. Pitching performance=.70×(K−BB%−league K−BB%)/.12+.30×(league ERA−ERA)/1.50. Constants are editorial scale choices, not fitted translation coefficients.

Sample weights: PA/(PA+60), BF/(BF+80). Age bonus=min(.9,max(0,(23−age)×.18)); experience bonus=min(.8,gap×.22). Experience units: Rookie/DSL=0, A=1, High-A=1.5, AA=2, AAA=3, MLB=4. Approximate winter context: LIDOM=3.5, others=3. These ordinal values are not official MiLB equivalencies. Bonuses apply only at performance≥−.25. Order=weight×(performance+applicable bonuses). Below 40 PA/BF, positive order is capped at .5 so small heaters cannot lead the established strong-signal tier. Age≤21 and gap≥1.5 bounds negative input at −.5 to avoid severe judgments on extremely young, overmatched players.

Veterans/MLB evidence: descriptive veteran label. Under 40 PA/BF: small-sample labels only. At 40+: exceptional requires order≥1.1, age≤22 and gap≥1; strong requires ≥.55. Holding own requires performance≥−.25, age≤22 and gap≥1. Struggling-young requires performance<−.5, age≤21 and gap≥1. Other negative performance is labeled below current league baseline, otherwise neutral. Context-incomplete records get no prospect classification.

The order is a readable screening heuristic, **not a confidence interval, probability, prospect grade, stock movement or validated predictive model**. Within-league baseline adjustment does not control for parks, opposing pitchers, schedule or lineup quality. Winter performance remains additional evidence; no changes feed main rankings, trades, draft models or TEO.


## MLB-affiliated prospect profiles

`scripts/winter-profiles.py` independently audits all 30 official MLB organization full rosters, then checks recent official transactions for absent/ambiguous candidates. Explicit minor-league signings and non-roster invitations provide separately labeled organization evidence; winter-team membership alone does not. Free agents and unconfirmed current affiliations stay in the full winter leaderboard without being promoted as currently affiliated prospects. This audit can correct the earlier historical-affiliation-based screen.

Verified non-debuted players under 26 receive a saved catalog entry even if no 2026 affiliated stat line is available. The narrower Winter Signal cohort still requires verified previous-level context. Existing canonical Pipeline profiles, including AFL, are reused by MLBAM ID; a unique name-and-organization fallback is lower confidence and cannot override a known conflicting ID. New profiles use `#winter-player/MLBAM_ID`; they include official bio, dated 2026 affiliated lines, live saved winter results, and performance-derived development questions. They do not fabricate tool grades, repertoire, injuries, ETA, published rankings or independently authored scouting. New identities automatically receive profiles when the hourly refresh's audit verifies them. Prior pages persist if affiliation later becomes unconfirmed, and their verification state is explicit. Regular-season lines retain their original retrieval date instead of being relabeled as new research.

The global player search and Winter Ball Watch tables/details/featured jerseys use these canonical links. All changes stay within public prospect coverage; no rankings, private fantasy strategies or simulator values are generated.
