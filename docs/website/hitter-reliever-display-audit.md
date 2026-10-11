# Hitter and reliever display preview

Scope: display adapters only. Production remains AFL-link commit `f0388d84af4eda0d2a1319cac57daacbefcb0863`. No forecasting candidate is adopted. Existing starter scenarios, talent rates, aging, years 2–8, valuations, ranking/replacement inputs, and trade logic remain unchanged.

## Workload audit

The saved GP-repaired five-state **parent** components in research checkpoint `5e00a76d83f1d0427add2132ec75beef3da6adf4` are reused. The failed starter-severity candidate in that same artifact is explicitly ignored. Corrected hitter full-role values replace the older pre-GP-repair scenario exports as display sources.

Three quantities are distinct:

1. `F = full-role GP × PA/game` for hitters; `F = GS × IP/start + RA × IP/relief appearance` for pitchers.
2. Research unconditional workload `W = Σ p(state) × F × within-state ratio(state)`, with zero workload in the absent state.
3. Research workload conditional on MLB participation `W / (1 − p(absent))`.

References: preserved `full-workload-scenario/run.py`, `depths` (86), `slot_work` (97), `fitted_slots` (106), `predict` (154–174); GP repair and fitting overrides in `historical-coverage-retrain/run.py`. The residual's legacy `unknown_role` export name is not an additional risk state.

The display reads `F`, not `W / participation`, and applies **no** state/participation/medical/team multiplier. The secondary expected view copies the website catalog's production line, which is a separate V2.3C recent-performance/aging forecast. It does not substitute the research parent's W. No additional discount is applied to either production counts or the research mixture. Overlapping state-severity risks remain a research limitation; this display extension neither resolves nor introduces them.

Preserved appearance depth: hitter PA/game = `(Σ weights × PA + 82)/(Σ weights × GP + 20)`, clipped 2–5.2, latest three seasons weighted 3/2/1, with inherited shortened-season normalization. Reference: `targeted-repair/engine.py:evidence_features`, lines 63–69. Pure-relief depth = `(Σ weights × IP + 10)/(Σ weights × GP + 10)`, clipped .25–3, using positive pure-relief observations. Reference: `full-workload-scenario/run.py:depths`, lines 86–95. These smooth observed workloads; they are not health estimates.

Roles use forecast-date PA/GP and GS/GP. Full-role appearance fits use historical high-usage proxies (everyday 145+ GP, platoon 100+, bench 70+, reliever 60+ RA), not medically verified season-long availability. The saved observation status/completeness fields are retained, including verified zero. Missing evidence never becomes a zero workload in this exporter. Verified zero is never called medical absence.

### Catchers

The preserved fitter does not distinguish catcher/DH assignment. A pooled everyday fit alone cannot justify a 154-game catcher assumption. The preview therefore uses a disclosed **display sensitivity**: `min(preserved fitted GP, maximum complete positive GP in the latest three observation seasons) × preserved PA/game`. This is a demonstrated total-MLB-usage proxy, not a newly validated catcher model or proof of full availability. Example: Langeliers' pooled 653.43 PA becomes a labeled 137-GP / 582.01-PA scenario. Missing adequate GP means unavailable, not invented 650 PA. The catcher sensitivity and original fitted F both appear in the comparison artifact.

### Relievers

Only preserved `reliever` roles get a supported bullpen scenario. Swingmen keep their original routes. The display retains fitted RA and preserved relief IP/appearance, excluding the fit's unsupported fractional starter component. Assumed starts are zero and disclosed. A latest positive record with missing GS or nonzero GS fails the pure-bullpen support check.

Saves/holds are separate opportunity assumptions: `RA × (Σ weight × event count)/(Σ weight × observed RA)`, same latest-three-observation calendar weights 3/2/1. Source rows must uniquely match player identity, year, innings and GP; GS must be zero; SV and HLD must both be present, with SV+HLD≤RA. Sources and rows are saved. No matching evidence means unavailable, never zero inferred from missingness. Closer/setup labels describe which historical event rate dominates, not a confirmed future bullpen assignment. The events sum cannot exceed projected appearances. No team budget is applied.

QA3 uses the preserved conditional performance yield per appearance from `Repair_League.component.conditional['1']`, multiplied by scenario RA and bounded by IP/5 and RA. It is not scaled from production QA3 by innings. Actual league definition: at least 5 IP and no more than 2 ER, OR at least 6 IP and no more than 3 ER. Without a supported yield it remains unavailable.

## Production-rate and RBI checks

Hitter counts are scaled together by scenario PA / production PA: PA, AB, H, HR, R, RBI, SB, BB, HBP, SF and TB. AVG=H/AB; OBP=(H+BB+HBP)/(AB+BB+HBP+SF); SLG=TB/AB are calculated before rounding and remain equal across views. Other non-AB PA remain the existing positive residual, not fabricated sacrifices/interference. Production does not export separate doubles/triples; these display unavailable rather than inventing a split. Tests verify H≤AB, HR≤H, H+3HR≤TB≤4H and PA accounting.

Pitcher K, ER, H and BB scale with scenario IP. ERA=9ER/IP and WHIP=(H+BB)/IP are unchanged. SV/HLD and QA3 follow the separate mechanisms above.

Preserved `calibration-starter/run.py` lines 77–84 establishes RBI attribution: `error = rate × (predicted PA − actual PA) + (rate × actual PA − actual RBI)`. Actual PA is an evaluation diagnostic only. The 62-player high-RBI cohort was selected using **prior anchor** PA≥500 and RBI≥90, not future RBI. It is an extreme-prior-season cohort, so its results do not establish universal league RBI bias.

| Historical population/model | N | RBI bias | Workload contribution | Rate error at actual PA |
|---|---:|---:|---:|---:|
| High-RBI benchmark | 62 | +3.436 | −0.546 | +3.982 |
| High-RBI GP-repaired five-state | 62 | +3.535 | −0.447 | +3.982 |
| All retrospective hitters, GP-repaired | 1,215 | +0.542 | +0.519 | +0.022 |

No verified arithmetic correction is needed in this adapter. Increasing scenario PA increases RBI by unchanged rate×ΔPA; it can amplify high-RBI rate error. Judge's display rises from 73.15 to104.08 RBI solely because PA rises from469.41 to667.91. This is not evidence that his expected projection or RBI rate is fixed. No new historical scoring, fitting or holdout claim is made.

## Examples (unrounded computations; rounded presentation)

| Player / role | Expected PA or IP | Full-role PA or IP | Assumed GP/RA | Expected / scenario opportunity |
|---|---:|---:|---:|---|
| Judge / everyday | 469.41 PA | 667.91 PA | 151.44 GP | RBI73.15 /104.08 |
| Olson / everyday | 600.55 PA | 684.88 PA | 157.67 GP | RBI78.17 /89.15 |
| Langeliers / catcher sensitivity | 482.92 PA | 582.01 PA | 137 GP | RBI62.52 /75.35 |
| Lux / platoon | 458.45 PA | 445.73 PA | 124.24 GP | RBI50.38 /48.99 |
| Iglesias / closer usage proxy | 52.20 IP | 65.22 IP | 65.06 RA | Scenario32.95 SV /0.68 HLD |
| Brash / setup usage proxy | 39.56 IP | 57.07 IP | 64.94 RA | Scenario3.13 SV /23.47 HLD |

Full role can be below the production expectation for a specified platoon role; it is not a mandatory upward adjustment. The research model can assign probability to a different, larger role.

## Coverage and isolation

Sidecar contains1,756 hitter/RP entries: supported202 everyday,337 platoon,302 bench,621 reliever;294 have no supported scenario. Catcher sensitivity applies to133 supported entries. Existing two-way and swingman routes are excluded. Prospects require preserved positive MLB appearance evidence and an existing positive MLB rate line; otherwise unavailable, preserving arrival information. Hypothetical labels do not imply a full MLB season is expected.

`scripts/verify-role-isolation.py` proves all2,546 catalog assets are byte-identical to production, including outcome probabilities, values, annual inputs and replacement data. Packed catalog SHA256: `9dd046ed57f4fa8e60a1e43cf06885e955c96961de5cc4d9f54df0a06e7bd120`. Embedded executable code differs only by one extra DOM mount call. Trade model/UI/narrative, baseline, October rankings, starter data/adapter and history adapter are byte-identical. `tests/role-display.test.js` deep-freezes the entire catalog, exercises every adapter line, checks ratios, PA accounting, feasible bullpen events, separate QA3, unsupported data and unchanged routes. All78 tests and the publication build pass.

Artifacts: `role-display-comparison.csv` (every routed asset), `role-display-coverage.json`, `role-display-isolation.json`, source-hashed `data/role-display-scenarios.json`, executable exporter and DOM adapter. Browser evidence and preview deployment commit are recorded separately after review.

Recommendation: review the preview as conditional scenario presentation only. Catcher capacity, future leverage assignments, separate doubles/triples and RBI rate calibration remain limitations. Keep the production expected-season and valuation systems unchanged.
