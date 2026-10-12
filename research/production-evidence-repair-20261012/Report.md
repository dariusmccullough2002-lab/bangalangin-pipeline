# Actual-model evidence repairs — bounded result

**Not all requested valuation problems are fixed.** A first-year reliever opportunity correction passes the frozen historical gates and has a reproducible actual-model catalog candidate. Recent-debut prospect and young-pitcher capacity corrections remain unresolved: tested candidates fail accuracy gates or lack sufficient support. Production has not been changed.

## Reliever correction that passed

Use verified pure-relief appearances to estimate saves and holds separately. Observed probabilities shrink to fixed 2010–2012 relief priors. Development selection chooses five appearance pseudocounts from the predeclared grid 5,10,20,40; no player-specific coefficients. Infer expected appearances from production expected innings divided by separately smoothed observed IP per appearance. Preserve innings, K, ER, H, BB, QA3, the original aging cohort and category/replacement calculations.

Historical selection uses 243 cases at 2016–2018 anchors. Evaluation uses 426 cases at 2021–2024 anchors. These are previously inspected chronological cases, not a new independent holdout. Target-year observations never enter the opportunity predictors. Historical baseline is the preserved past-only chronological companion, not a claim that the current 2026 engine existed at every historical forecast date.

|Later evaluation MAE|Existing expected method|Corrected opportunities|Change|
|---|---:|---:|---:|
|Saves|2.829|2.265|−19.9%|
|Holds|4.075|3.705|−9.1%|
|League SVH7: 3 SV + 2 HLD|14.668|12.576|−14.3%|
|First-year contribution utility|0.7573|0.7088|−6.4%|

The actual-model candidate changes **only year-one** saves/holds and contribution. All years2–8 utility rewards remain exactly unchanged. First-year evidence does not validate extending the new opportunity estimates across eight years. This correction estimates expected opportunities; it does not establish a future closer or setup assignment.

|Player|Deployed eight-year calculator value|Candidate calculator value|Expected IP, unchanged|Candidate year-one SV|Candidate year-one HLD|
|---|---:|---:|---:|---:|---:|
|Raisel Iglesias|18.29|19.43|52.20|25.48|0.63|
|Matt Brash|12.75|13.22|39.56|2.24|15.02|
|Eiberson Castellano|3.04|3.55|16.95|5.08|1.12|

All 2,546 catalog assets are checked: 441 supported MLB relief assets receive the correction; 2,105 remain exactly unchanged. Strategies share the same neutral transferable value; competitive timing scores remain separate. State means, uncertainty ranges, and cached trade packages reconcile. Unsupported, mixed-role, prospect/hybrid and two-way routes are preserved.

The older full-role display's one-save-in-one-appearance extrapolation is a separate defect and remains unchanged in this deliverable. The corrected expected-model candidate does **not** fix or validate that display. Randy Wynne lacks matched current-model appearance evidence and remains unsupported rather than receiving an invented opportunity estimate.

## Recent-debut prospects: confirmed transition issue, no validated price correction

Josue De Paula's deployed value is 20.04 after 42 PA; Culpepper's is 15.80 after 128 PA. Dated scouting evidence is retained, but its mean weight is zero on the newly restored-prior route. By contrast, other archived-prior routes use the inherited reliability mixture. This is inconsistent transition behavior. Standalone scouting-prior values of 35.45 and 21.38 are diagnostics, not established corrected prices or guaranteed floors.

The earlier exp100 mean phase-in failed expanded sub250-PA scrutiny. A new frozen candidate instead aligns empirical contribution paths to first positive MLB exposure, conditions class probabilities on a debut already observed, and retains subsequent zero-workload seasons. Past-completed training excludes every evaluation identity; no future path observation is used and no unsupported class path is invented.

This new candidate **also fails**: later first-year utility MAE is 1.954 versus 2.085 across 349 matched cases. Only three later cases below250PA are supported, representing two players; their MAE changes from 0.277 to 1.818. These sparse subset numbers are not generalizable, but they cannot justify deployment. Of627 preserved scrutiny cases,171 lack required recovered rank/class/path support. Current De Paula and Culpepper eight-year paths are unsupported because the necessary completed, debut-aligned class4 path is unavailable under the frozen rule. No borrowing rule was added after seeing these results.

**Remaining requirement:** a coherent debut-aware talent/contribution transition supported by more independently dated, mature debut cohorts, with regular-workload capacity distinguished from initial arrival. A supported long-horizon evaluation is needed before treating a new first-year estimate as a corrected dynasty price. Do not simply restore rejected blending, use max(prior,MLB), or impose a price floor.

## Young pitchers: capacity is not expected MLB opportunity

The preserved professional-workload ledger already distinguishes verified minor-league innings from missing data. Talent rates must continue to use actual MLB counts over actual MLB innings. Minor-league workload can establish capacity but cannot establish rotation access or expected MLB appearances.

On253 first-MLB-season chronological cases, IP MAE is24.24 for baseline,39.44 for direct professional-IP substitution, and26.14 for the bounded opportunity comparator. On306 young-pitcher cases, the corresponding errors are29.16,39.56 and30.43. Neither correction passes. QA3 and leverage errors also worsen. Those archived candidates were replayed and rejected, not silently adopted.

The full-role experiment's higher workloads therefore do not establish a correction to the actual expected model. A supported repair must predict MLB starts/relief appearances separately from demonstrated professional capacity and count availability/attrition only once. No blanket full-season workload was added.

## Reproduce and verify

From repository root, using the preserved recovered model and research roots:

```sh
python research/production-evidence-repair-20261012/repair.py ../model-recovered ../preserved-research/docs/model-audit/workload-correction
python research/production-evidence-repair-20261012/debut.py ../model-recovered
python research/production-evidence-repair-20261012/verify.py
```

`Protocol.json` was committed before reliever scoring (`9ac1c86`). Its horizon restriction was amended after scoring (`cdb9b27`) to preserve years2–8; it is not falsely represented as a wholly prescore decision. `Debut_Protocol.json` was committed before its candidate evaluation (`f59b252`).

Outputs include separate current and chronological comparisons, unsupported cases, validation decisions, `Candidate_Catalog.json.gz`, and a generated calculator HTML candidate. The HTML is an integration asset that needs the existing website assets at their normal paths; it is not a self-contained hosted test site. No production projection, value, ranking, trade calculation, display or deployment file has been modified.

Recommendation: the first-year reliever repair is reviewable and improves the evaluated errors. Do not declare all three problems fixed or adopt the rejected prospect/pitcher corrections. Do not adopt the full-role eight-year experiment as a substitute for these missing repairs.
