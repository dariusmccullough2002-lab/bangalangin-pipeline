# BangaLangin Pipeline

Phase 1 of an independent dynasty prospect publication, intended for GitHub + Vercel.

## Run

Node 22+ and Python 3 are sufficient; there are no npm dependencies.

```
npm test
npm run build
npm run dev
```

Open http://localhost:8080. Deploy on Vercel by importing a new GitHub repository, selecting Other, build command `npm run build`, output `dist`. No environment variables are required.

## Checkpoints

Keep `main` deployable. Use a feature branch per increment, require tests and build in a PR, and tag known-good releases. Never replace the simulator repository. Review Vercel previews before merging. Roll back by reverting a commit or promoting a previous Vercel deployment.

## Data boundary

- `data/players.json`: persistent identities and attributed August source metadata. Age and MLB affiliation are historical, not live.
- `data/organizations.json`: 12 organization identities and prototype publication state.
- `data/editions/august-2026.json`: immutable August organizational ranks, league ranks, tiers, source notes, and historical ownership.
- `data/ownership.json`: single-team supplied roster, unidentified export date. Not authoritative league-wide ownership.

The organization sheets contain 355 prospects; the league sheet contains 361. Only organizational rows were imported in this first checkpoint. The six additional league records must be reconciled before the League Top 100 release. Shea's entire original Top 30 is preserved, including players absent from its later roster export. No current rankings or new farm grades were computed.

Future data files should separate scouting reports and metrics from identities. Every metric should include playerId, season, level, sample, source, asOf, unit, and value. Every report should carry author, sources, evaluation date, and publication status. IDs must survive trades and name changes; prefer a verified Fantrax/MLB ID crosswalk over automatic name matching. Do not merge players on names alone.

## Ownership import contract

Use a full-league export with organization and persistent player IDs. Require a verified export timestamp and reject older snapshots. Build an import preview, resolve unmatched identities, and save an append-only transaction snapshot before promoting current ownership. A transfer alters the next edition's assignment, never a historical edition. Prospect eligibility requires league-rule verification separately from ownership.

## Editorial workflow

Research → evidence review → finalized edition → interface publication. The interface never computes new prospect ranks. The August workbook's consensus formula and calibrated farms are historical, and the underlying deep-research report was not supplied. A future farm methodology must be documented and evaluated before assigning scores. Missing metrics and movement remain absent.

## Next increments

1. GitHub repository and Vercel deployment; review prototype.
2. Full-league ownership import and reconciliation; research organizational pages.
3. Finalized Top 100, farm methodology, profiles and filters.
4. Multiple editions, movement and comparisons.


## October 2026 working consensus

`data/editions/october-2026.json` preserves the ownership snapshot, source dates and coverage, source ranks, MLBAM identity, eligibility evidence, prior rank references, model output, research queue and every exclusion. It never rewrites August. User's revised eligibility policy: **non-debuted prospects only**, regardless of remaining rookie eligibility. All 827 roster identities are accounted for.

DD controls the baseline at 60%; supporting weights are PL 15%, FG 10%, JB 10%, BA 5%. `scripts/ranking-model.js` reproduces the bounded log-rank score. Missing evidence stays neutral; the 501 DD boundary is explicitly censored, not a published DD rank. The original 215 consensus entries preserve their relative order. The 45 previously uncovered candidates now have disclosed supplemental editorial placements; their source ranks remain null. BA coverage is limited to publicly verified ranks 1–36. No full independent scouting reassessment is claimed.

The October interface is isolated in `october.js`. Routes: `#october`, `#october-org/{id}`, `#october-player/{fantrax-id}`, `#october-method`, `#october-review`. Historical routes remain available. Never change rankings for presentation.

## October expanded research checkpoint

All 260 non-debuted candidates have placements and two-paragraph conditional projections. 240 have reliably matched, dated published grades; 256 have usable 2026 regular-season minor-league statistics. Never label retrieved older grades as October scouting. The archived August edition remains byte-for-byte unchanged.

`data/research/october-2026-supplement.json` records the 45 editorial placements, comparison peers and individual reasons. `data/research/october-2026-evidence.json` holds selected tool grades, season totals, team/level splits and provenance. The edition materializes these records for rendering. Missing DD ranks remain missing. Editorial placement scores belong to Pipeline, not DD.

`profile-context.js` renders sourced grades, projections and performance evidence. `farms.js` renders system ranks and the complete scoring methodology. `scripts/farm-model.js` reproduces the eight-component model; run `node scripts/update-farms.js` after changing an edition's evaluations. Farm index sets the leader to 100, is not a 20–80 grade, and never sums organization ranks. Routes: `#october-farms` and `#october-farm-method`. Organization views default to all eligible prospects; league Top 100 filters explicitly explain their scope.

Validation: `npm test` checks all roster identities, non-debuted eligibility, source-vs-editorial separation, season split aggregation, profile coverage, archive integrity and farm-model reproducibility. `npm run build` copies each isolated UI module. Keep ranking changes in structured data, then verify presentation separately.
