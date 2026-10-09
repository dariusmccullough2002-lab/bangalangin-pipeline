# League-wide debut-season workload review — October 9, 2026

**Recommendation: retain the corrected workload evidence; do not release either numerical prototype.** This investigation tests debut-season-only processing, separately from the earlier failed blanket all-seasons substitution. No production file, valuation, owner, pick, saved trade, or website component was changed.

## Recovered checkpoint and completed work

The previous research branch remains at `485d0f27dbbe090f1d45cc1d36c89ccb12cdfd8b`. It preserves 72 official affiliated MiLB responses, the completed 335-season young-pitcher collection, the 94-case benchmark, previous failed blanket results, and the undeployed narrow provisional artifact. The narrow player manifest is superseded for release purposes, not deleted. New research is isolated on `review/debut-workload-role-20261009`.

GitHub main was inspected at `ca15ab54d31e6b8f19c782d1b5185d8aed57bda0`: the only changes after the deployed header commit were AFL data and its test. The header and analyzer were not touched. No deployment was initiated by this investigation. The frozen 2,546-asset catalog SHA256 is `aadad4dc7763510da7eba928aae5018af1bc48cfacd8b5f510ca5f5cd0995235`. V2.3B and the existing production rollback remain preserved.

Only outstanding collection was performed: 48 additional successful six-level responses for missing debut years 2005, 2008–2014. Existing 2015–2026 queries were reused. Eighteen independent individual-history checks for Misiorowski, McLean, and Smith agree with the bulk level aggregates. Source URLs, raw compressed responses, hashes, retained outs, and aggregate/team reconciliation are preserved.

## Universal evidence processing

The ledger audits 1,287 assets: **1,155 pitching/two-way assets and 132 secondary pitching-history or pitching-eligibility assets**. Counts include free agents, not just rostered players. A separate positive pitching stream prevents hitter PA from becoming pitching workload. Two-way projections are inspected through their pitching component.

| Coverage | Count |
|---|---:|
| Verified affiliated debut-year coverage | 1,190 |
| Positive debut-year affiliated MiLB innings | 959 |
| Zero recorded affiliated MiLB innings after complete queries | 231 |
| Combined workload evidence corrected, with recorded MLB IP | 958 |
| No recorded MLB pitching debut | 86 |
| Unresolved identities, explicitly excluded from joins | 11 |
| Modeled MLB pitching streams evaluated | 1,071 |

The 86 nondebut records retain verified identities and available predebut level-season histories. The same processing applies automatically once a positive MLB pitching season is recorded; it has no name checks or manual player activation list. Eleven unresolved records are free agents: Jose Fermin (06qwb), Matt Wilkinson, Jack Anderson, Yunior Marte, Jose Rodriguez, Trevor Martin, Jose Cabrera, Sean Sullivan, Logan Allen (05jp3), Luis Garcia, and Cameron Foster. Names alone are not used to select an ambiguous ID. Carlos Cortes and Eric Yang have affiliated evidence but no matching recorded MLB pitching innings; no combined MLB total is invented.

All workloads use integer outs. One aggregate per player/sport/season is retained; aggregate and team components are never added together. Distinct levels sum once. Missing sources or identities remain unknown. Zero means no record in successful exhaustive affiliated queries, not zero worldwide workload. Foreign, independent, winter, college, and unrecorded assignments remain an explicit coverage limitation. Rehab innings count as workload evidence, not proof of health or starter readiness.

## Methods and validation

Both numerical prototypes alter only verified debut-season workload within the original four-year forecast window. MLB-only K, ER, BB, H, QA3, save and hold rates remain unchanged. Role routing, caps, utility, and dynasty scale remain frozen for current impact comparisons.

* **Direct debut substitution:** replace debut MLB workload evidence with MLB plus verified affiliated MiLB innings.
* **Opportunity attenuation:** add MiLB capacity multiplied by `min(1, largest observed same-role MLB workload through forecast date / combined debut workload)`. This is a general observational sensitivity, not an established opportunity model. It does not use future seasons at historical prediction dates.

The original 94-case frozen comparison exactly reproduces baseline projections. It retains the original caps/aging curves and their inherited future-information limitation; it is not described as a newly leak-free engine.

| Frozen 94 cases | Baseline | Debut substitution | Opportunity attenuation |
|---|---:|---:|---:|
| IP MAE | 24.97 | 36.33 | 25.85 |
| IP signed bias | +4.31 | +27.40 | +10.09 |
| K MAE | 23.29 | 33.88 | 24.18 |
| QA3 MAE | 1.67 | 2.16 | 1.75 |

An additional **1,084 chronological cases across 411 held-out identities** use anchors 2016, 2017, 2018, 2021, 2022, 2023, and 2024. Caps use only seasons through each forecast date. Aging uses only completed one-year training pairs, excludes holdout identities, and never uses later outcomes. Early 2010–2012 talent priors are available before every anchor. Pandemic pairs are omitted from this companion aging training rather than blindly annualized. This companion is not byte-identical V2.3C; it tests the correction under a past-only reconstruction. No parameters were selected on these outcomes. Missing next-year MLB participation scores zero. ER, BB, H, saves and holds are also reported in the JSON results. Eighty-two cases have unknown or incomplete debut evidence and retain baseline workload instead of assumed zero.

| Chronological subgroup | N | IP MAE baseline | Direct | Attenuated |
|---|---:|---:|---:|---:|
| All | 1,084 | 29.42 | 33.66 | 29.99 |
| SP | 288 | 51.75 | 57.14 | 53.03 |
| RP | 796 | 21.34 | 25.16 | 21.65 |
| Young, age ≤26 | 306 | 29.16 | 39.56 | 30.43 |
| Established, age >26 | 778 | 29.53 | 31.34 | 29.81 |
| First MLB season | 253 | 24.24 | 39.44 | 26.14 |
| Second MLB season | 159 | 26.53 | 28.76 | 26.95 |
| Swingmen | 238 | 39.75 | 46.32 | 41.06 |

Aggregate chronological K MAE is 28.06 →31.71/28.51; QA3 MAE is 1.92 →2.06/1.94. IP bias rises +1.82 →+10.97/+4.67. Both candidates fail aggregate and important subgroup gates. These are descriptive paired errors, not a statistical superiority claim; overlapping cases are not independent. Confirmed injury cases and workload-shortfall proxies from the previous audit remain preserved, but this expansion does not infer medical diagnoses or certify injury-specific performance.

## Diagnostic examples and league impact

| Player | Debut workload MLB + MiLB | IP baseline → candidate | K baseline → candidate | QA3 baseline → candidate | Neutral baseline → candidate |
|---|---|---:|---:|---:|---:|
| Jacob Misiorowski | 66 +63⅓ =129⅓ (2025) | 129.1 →150.9 | 166.2 →194.3 | 16.0 →18.7 | 93.4 →109.8 |
| Nolan McLean | 48 +113⅔ =161⅔ (2025) | 120.1 →157.8 | 124.7 →163.8 | 15.1 →19.8 | 42.9 →56.3 |
| Cade Smith | 75⅓ +0 recorded (2024) | 61.0 →61.0 | 76.8 →76.8 | 0.03 →0.03 | 39.2 →39.2 |

Both prototypes yield the same results for these three cases because later same-role MLB workload exceeds debut professional workload for Misiorowski and McLean; Smith has no affiliated debut innings to add. These are experimental sensitivities, not recommended or deployed projections.

McLean's 2025 evidence is 26⅓ AA plus 87⅓ AAA plus 48 MLB innings. His preserved 2026 export records 179⅔ MLB innings and 31 starts. The existing four-year estimator blends a 123.24 recent MLB average, a 113.83 two-season healthy median, and a 171-IP role prior to 130.53 IP, then applies a 0.92027 cohort workload factor to reach 120.13. Adding debut capacity raises the healthy/recent inputs; it does not change his strikeout talent or independently establish 2027 opportunity. Age is 25 in the preserved snapshot; no unverified injury explanation is used. Misiorowski similarly combines his 2025 partial MLB season with 63⅓ AAA innings; his 2026 export has 174⅔ MLB innings. Capacity is corroborated, but the league-wide validation does not justify automatic forecast increases.

Smith's limitation is role/opportunity forecasting, not lost debut workload. His recent saved MLB seasons have 1/16/41 saves and 28/19/1 holds. A pooled save/hold-per-IP estimate plus regression and cohort attrition produces 15.8 saves and 9.2 holds. Workload correction cannot resolve closer assignment. His 61.0 IP comes from 71.39 preaging IP times 0.85488 attrition. Production, replacement surplus, neutral dynasty contribution, and unestimated acquisition-market pricing remain distinct; this audit introduces no reliever trade-value premium.

Wheeler's 2013 debut ledger is corrected to 100 MLB +68⅔ MiLB innings, but his current 2023–2026 projection remains unchanged. Tyler Holton and Reid Detmers also remain unchanged because debut years precede the window. Skenes changes modestly, 165.3 →168.7 IP, from 27⅓ verified 2024 MiLB innings. These contrasts arise from the same processing rule.

428 modeled pitchers change under each prototype; 423 direct and 404 attenuated changes meet the documented material threshold of at least 1 projected IP. `Debut_Material_Impact.csv` supplies every material row, including organization, age, role, source workload, IP/K/QA3/value comparisons, reasons, failed validation support, and uncertainty. Full JSON includes unchanged modeled pitchers. Island is displayed publicly while stable asset/owner identities remain preserved.

Maximum projected IP remains 175.8 and maximum K 194.5, but bounded individual totals do not prevent systematic inflation. Across the catalog, direct substitution adds 546.7 projected saves and 932.4 holds; attenuation still adds 126.8 saves and 237.5 holds. Per-IP rates are unchanged, but routing capacity into MLB innings inflates opportunity totals. Neither is acceptable for release. QA3 uses the preserved exact definition (at least 5 IP and ≤2 ER, OR at least 6 IP and ≤3 ER); no conventional QS substitution or MiLB QA3 rate is introduced.

## 2020 diagnostic

Raw 2020 totals can suppress historical recent-workload windows, but **current default forecasts use 2023–2026**, so 2020 is not directly lowering Olson's current recent-workload estimate. His preaging forecast is 681.61 PA and final projection 600.55 PA. Original aging paths and career diagnostic workload already annualize 2020 by 162/60; that normalization is itself a limitation, not an unaddressed raw-total effect everywhere.

541 historical player-cases compare raw totals, omitting 2020, and bounded capacity (annualized 2020 capped by previously observed same-role workload). Hitter PA MAE is 145.22/145.33/144.38, but bias rises +17.41/+43.43/+38.53. SP IP MAE is 53.15/51.18/52.75; RP IP MAE is 21.84/22.04/22.13. No uniform pandemic policy passes a league-wide accuracy/bias gate. Omitting a season also changes talent evidence, so it is an ablation, not a pure capacity correction. No blind normalization was added to production.

## Remaining work and reproducibility

The universal affiliated capacity ledger is usable research evidence. A numerical release still needs a separately validated probability of MLB participation, starter/reliever opportunity and expected starts/appearance depth, conditional workload, and closer/setup assignment. Capacity should constrain those estimates rather than replace them. Eleven identities need verified ID resolution; foreign/independent debut assignments and historical censored debuts require additional provenance. The first-positive-MLB role/existence discontinuity remains unresolved. None of these are reasons to discard the completed evidence or modify production prematurely.

Run `debut_audit.py <frozen-catalog> <recovery-root>`, then `validate_debut.py <recovery-root> <frozen-catalog>`, then `summarize_debut.py`. Large result JSON files are stored compressed in Git and can be regenerated. The original baseline, research and test datasets remain read-only. Both numerical prototypes are rejected for release; no approval for numerical deployment is requested.
