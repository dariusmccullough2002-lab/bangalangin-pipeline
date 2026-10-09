# Workload correction review — October9,2026

Header UI release is live at https://bangalangin-pipeline-zeta.vercel.app/. Commit d757773ec0a2ed685be2320d69218eaa501cee5d; deployment dpl_BSbfNLhB782wAPz2ZR4dUfX35xEL READY. GitHub main and preview CI passed. All58 existing tests and production build passed before release. Desktop1728/1366/1200, tablet768 and mobile390/320 checked; no horizontal overflow. Production desktop header77px; live Resources lists Beta only. Embedded model scripts remain identical to pre-header production. Island public naming/internal identity unchanged. Rollback: dpl_EDdjX3FTitctk3jeQmDbiwCKBddE at2a5141ee889f4663120fce6cf142ea8e59464979; V2.3B checkpoint remains preserved.

## Evidence coverage

All335 young pitcher-seasons are now resolved against exhaustive six-level affiliated MLB Stats API season responses:252 contain MiLB innings;83 contain no recorded affiliated MiLB innings.72 cached responses from2015–26 support current and historical comparisons. Last-team labels in season leader listings do not mean team splits: exactly one player aggregate per sport/season was retained. Different sports sum once; innings notation is converted to integer outs. Source URLs, timestamps, original-response hashes and raw responses are preserved. No MiLB talent rates enter the experiment.

## Historical paired comparison

94 held-out pitcher cases:2018->2019 (51) and2022->2023 (43), identities divisible by5 excluded from the aging training cohort, age<=26. No fitting or threshold selection. Absent next-year MLB appearances score zero. Original frozen priors, caps and aging curves remain inherited; this is not a newly fitted fully chronological engine.

| Group | N | IP MAE baseline→combined | K MAE baseline→combined | QA3 MAE baseline→combined | IP bias baseline→combined |
|---|---:|---:|---:|---:|---:|
| MLB_only_anchor | 10 | 26.29 → 24.99 | 24.89 → 23.34 | 0.57 → 0.52 | -4.79 → -1.51 |
| RP | 67 | 19.28 → 36.56 | 18.60 → 33.29 | 0.70 → 1.00 | 2.16 → 30.58 |
| SP | 27 | 39.10 → 61.33 | 34.92 → 57.53 | 4.07 → 5.86 | 9.62 → 52.08 |
| all | 94 | 24.97 → 43.68 | 23.29 → 40.25 | 1.67 → 2.39 | 4.31 → 36.75 |
| promoted | 84 | 24.81 → 45.90 | 23.10 → 42.27 | 1.80 → 2.61 | 5.39 → 41.31 |
| swingmen | 25 | 31.08 → 54.06 | 31.27 → 47.67 | 3.21 → 5.26 | 7.70 → 40.91 |
| workload_shortfall_proxy_not_diagnosed_injury | 10 | 18.58 → 35.69 | 16.25 → 31.99 | 1.35 → 1.64 | 11.16 → 33.63 |

**Recommendation: do not release the blanket substitution.** It improves physical workload measurement but does not establish next-year MLB opportunity. Promoted pitchers and swingmen are systematically overprojected; short MLB samples route all professional innings to an observed MLB role. This is especially risky for relievers who logged starter innings in the minors. Workload-shortfall results are only a proxy; no injury-safety certification is claimed. Rehab innings are physical workload, not proof of health.

The first-positive-MLB boundary remains unresolved: a first small MLB season creates a forecast window and role assignment. Within a fixed existing season, moving innings between MLB and MiLB at fixed total and fixed MLB talent leaves the workload component invariant. Numerical boundary tests are recorded separately.

## Narrow provisional release diff — pending approval

The evidence gate matches stable IDs and season, verifies original MLB outs and deduplicated source MiLB outs, requires an explicit reviewed manifest record and later same-role MLB workload at least as large as the combined season. It contains no player-name checks or hardcoded projected IP/value. The candidate manifest currently enables only Misiorowski2025. All other collected records remain research-only until separately reviewed; source verification alone does not activate the policy. This is a deliberately limited evidence configuration, not a league-wide deployment.

Misiorowski:66 MLB IP+63⅓ AAA IP=129⅓ physical workload. Existing weights/cap/aging produce150.8933 projected IP vs129.0654,194.3206 K vs166.2106,18.7185 QA3 vs16.0107. ERA/K-per-IP unchanged; ER scales with innings. Neutral fundamental sensitivity109.7701 vs93.4071; acquisition price remains unestimated. The2026 same-role174⅔ MLB IP corroborates capacity but does not prove forecast superiority.

Regression:2,546 assets retained;2,545 assets deeply identical; MLB talent rates identical; teams, ownership, identities, picks and current data untouched. One saved trade example containing Misiorowski is recalculated; its IDs remain unchanged. Strategy neutral invariance preserved. Bad/duplicated evidence rejected. Disabling the offline gate yields exact original forecast tuples. Catalog distribution summaries and scenario ranges are recomputed for the changed asset. Beta notice and player warnings explicitly label the adjustment provisional.

Candidate files: evidence_gate.py, Provisional_Workload_Manifest.json, build_provisional.py, Provisional_Regression.json, Provisional_Release_Diff.json, Provisional_Catalog.json.gz and provisional-preview.html. The HTML is a prepared artifact only; it has not replaced production. Approval would authorize the catalog payload/notice update plus reproducibility files; unrelated website files remain unchanged. Rollback restores the frozen payload by disabling the gate and rebuilding, or promotes the current UI-only deployment.

Raw collection is resumable; collect_workload.py skips hash-preserved cache files. validate_workload.py and build_provisional.py take recovery-root and frozen-catalog paths. Keep prior audit outputs as historical evidence; new outputs are in workload-correction.

## Independent source/dedup cross-checks

The individual player-history endpoint agrees with the season-level aggregate: Misiorowski2025 AAA190 outs; two traded-pitcher checks independently reconcile team components21+43=64 outs and122+117=239 outs. Aggregate and team splits are never added together. Independent_Dedup_Checks.json preserves URLs, response hashes and component totals.

Documented injury examples in the held-out2022 cohort: Dustin May returned after Tommy John surgery (Dodgers activation release,2022-08-20: https://www.mlb.com/press-release/press-release-dodgers-activate-dustin-may). His baseline52.2 versus combined59.4 projected IP compares with48.0 actual next-year IP. Luis Patiño had a left oblique strain (MLB report,2022-04-12: https://www.mlb.com/amp/news/luis-patino-exits-season-debut-early.html); baseline56.7 versus combined78.2 compares with21.7 actual next-year IP. Both examples illustrate why rehab workload cannot certify future availability. They are case checks, not a statistically representative diagnosed-injury cohort.

Website regression checks against the generated provisional HTML: all58 existing tests and publication build passed. The numerical candidate remains undeployed. The prepared HTML and full catalog are reproducible via extract_catalog.py and build_provisional.py; exact JSON-pointer before/after changes are preserved in Provisional_Release_Diff.json. Raw source responses and hashes are retained with this review.

The narrow evidence gate also verifies complete six-level queries for the reviewed season; incomplete coverage fails closed. Running build_provisional.py with --disabled reproduces the exact original header-release HTML bytes. The2022 historical window includes the shortened2020 MLB season under the same raw workload weighting in both paired forecasts; no pandemic-specific refit is claimed.
