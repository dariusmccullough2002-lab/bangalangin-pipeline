# Detailed debut-watch breakdowns — release checkpoint

October 27, 2026. Deployed and verified in production.

- Removed requested introductory strip. Research Watch badge remains absent.
- All 30 tiles retain jersey/name/profile link, role, highest-level metrics and a direct Read breakdown link. Long case paragraphs and evidence disclosure now exist only in individual profile chapters. List view and shared filters are preserved.
- Added expandable plain-language explanations beside filters, plus a live selected-path explanation. All paths = everyone; pitching = starts/relief opportunity; needs a lane = plausible candidate without clear position/opening; development = skill/health/workload hurdle.
- Deep_Research.json contains 30 distinct conditional assessments, likely first roles and two specific follow-up checkpoints each. Source_Updates.json contains 26 concise primary-source notes, with publication dates checked against article bodies where available. Four players retain their existing detailed scouting sources instead of inventing a later update: Walcott, Velazquez, Harber, Rainiel Rodriguez.
- Corrected health/role paths for De Vries, Arnold, Miller, Susana, Bonemer and Lagrange. Added current saved center-field competition for Bonemer and bullpen competition for Lagrange. Duno’s October catching outlook supersedes an assumption that Stephenson is a permanent blocker.
- Distinguishes reporting from editorial interpretation, affiliate statistics from MLB competition, historical injury context from current clearance, and a first appearance from an everyday role. No collected pitch-level measurements or numeric debut probabilities were added.

Reproduce: python scripts/expand-door-research.py; python scripts/build-door-watch.py. Editorial_Research.json and Source_Updates.json are frozen edited inputs. Public output: data/knocking-door-2027.json.

Validation: node syntax passed; 12 targeted tests passed across door-profile, profile-polish, profile-history, home-highlights. Static publication build and git diff --check passed. New interaction test covers all 30 compact tiles, no long research on hub, all three contextual filter definitions, list links and all 30 expanded member-only chapters. Existing unrelated seven-player AFL checkpoint coverage gap remains documented in CHECKPOINT.md; no fabricated additions.

Production: research/UI commit 5405a1af1c05bd2f403efe32811b9ae1e815858c; source-note semantic fix 084c9c40032c38ce020f3a95b36d953ecef732da. Vercel production dpl_BMJ9m76LDzTkJcYrYwWobumf2ws9 READY. Public hub https://bangalangin-pipeline-zeta.vercel.app/#knocking-on-door.

Live verification: 30 tiles and 30 direct breakdown links; no long case/evidence on tiles; intro removed; first row heights all 428px at desktop width1348, document has no horizontal overflow. Legend expands to all three definitions. Selecting Development first shows the matching explanation and 11 players. De Vries direct chapter shows health-dependent path, sourced surgery update and expanded analysis. Browser found entry-history injection into the new aside note; fixed note to div role=note. Reloaded production verifies zero entry cards inside chapter and one in the actual sidebar. At320px review, expanded legend and individual Made chapter both have clientWidth305/scrollWidth305. Needs a lane selected helper and direct chapter link work. Temporary review tab closed; hub left open with legend expanded.

Proof screenshot: /workspace/scratch/pipeline-door-path-explanations-20261027.jpg. No research measurements are claimed beyond the saved sources; no production trade-value changes in this work.
