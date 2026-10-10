"""Build the report from frozen comparison outputs. No model changes."""
from pathlib import Path
import csv,json
D=Path(__file__).resolve().parent
def read(name):return list(csv.DictReader((D/name).open()))
def table(rows,fields):
 return '| '+' | '.join(fields)+' |\n|'+ '|'.join(['---']*len(fields))+'|\n'+'\n'.join('| '+' | '.join(str(a.get(k,'')) for k in fields)+' |' for a in rows)
metrics=read('Matched_Validation.csv');primary=[{'Family':a['family'],'Model':a['model'],'n':a['n'],'MAE':f"{float(a['MAE']):.3f}",'RMSE':f"{float(a['RMSE']):.3f}",'Bias':f"{float(a['bias']):+.3f}"} for a in metrics if a['subset']=='all' and a['cohort']=='all']
affected=[{'Sample':a['subset'],'Model':a['model'],'n':a['n'],'MAE':f"{float(a['MAE']):.3f}",'RMSE':f"{float(a['RMSE']):.3f}",'Bias':f"{float(a['bias']):+.3f}"} for a in metrics if a['family']=='H' and a['cohort']=='all' and a['subset'] in ['target_GP_repaired','input_GP_repaired','neither_repaired']]
cohorts=[]
for cohort in ['established','young','interrupted','aging33plus','uncertain_role']:
 ys=[a for a in metrics if a['family']=='H' and a['subset']=='all' and a['cohort']==cohort];cohorts.append({'Cohort':cohort,'n':ys[0]['n'],**{a['model']:f"{float(a['MAE']):.3f}" for a in ys}})
coverage=read('Coverage_Before_After.csv')
report='''# Historical GP coverage repair and unchanged-model retraining

## Recommendation

Retain the preserved strong benchmark. The repair is complete and useful: both hitter candidates improve after consistent retraining, and role/outcome-state calibration improves substantially. Neither candidate meets the frozen full-population accuracy and protected release criteria. Keep the corrected research records and fitted models; the repaired five-state hitter candidate merits narrowly scoped independent confirmation. No numerical replacement, deployment, or new candidate was selected.

This is the specific retraining test that the earlier fixed-model patch did not perform. It uses all 4,004 identical historical cases: 1,487 hitters and 2,517 pitchers. All samples, including previously scored 2026 waves, are exposed. No genuinely untouched confirmation sample was identified. Results are exploratory.

## Frozen scope and source repair

The pre-score inventory and correction rules were committed locally in ba13da3, with a pre-score validity-rule amendment in 1e0b03d. The amendment permits GP greater than PA (pinch runners) and 163 historical regular-season/tiebreak games; it changes no model settings. Protocol_Freeze.json and Pre_Repair_Inventory.json preserve the scope.

The eligible population is the existing chronological training/evaluation population. Only missing GP and the resulting demonstrated-usage proxies were repaired. Fifteen complete official MLB regular-season hitting censuses cover 2010–2024; 2018/2024 responses were reused. Previously verified 2025/2026 sources remain unchanged. No player was selected based on error size or diagnostic status. No new medical/transaction collection was needed for this GP test.

Verification requires a complete nonempty census, unique MLBAM identities, correct season, valid GP and exact PA agreement within 1e-8. All 5,219 missing positive player-season GP observations match; none remain unresolved, and there are no PA mismatches or existing-GP disagreements. Counts below are unique player-season references and overlap across uses; do not add them.

'''+table(coverage,['population','unique_player_seasons','positive_seasons','missing_GP_before','missing_GP_after'])+'''

At the case level, 2,079 training targets and 439 evaluation targets lacked GP. Missing GP in the four-season input window affected 3,462 training cases and 766 evaluation cases. The record-level input counts above are larger because one case can use several missing seasons. Correction_Log.csv preserves original/corrected GP, unchanged workload/status, source path, statistical cutoff and medical-label flag. Pre_Repair_Records.csv preserves the original full observation fields. Source_Coverage.json and verified/*.provenance.json retain URLs, retrieval/HTTP dates and response hashes.

Annual censuses are retrospective verified statistics, not recovered historical medical snapshots. Publication timestamps are unknown. Season cutoffs bound model inputs; no future-season record enters a prediction. PA, zero-season status, missing-exposure status, debut evidence and workload targets are untouched. Two pitcher targets differ from source observations only in floating-point representations of 5/3 IP (2.2e-16); no substantive discrepancy or target repair occurred.

## Rebuilt labels and fitting

Exactly 2,086 hitter training state labels and 2,780 forecast-role inputs change. The training residual label count drops from 2,085 to zero. All 441 evaluation unknown-role labels become identifiable usage outcomes after repairing both ends of the comparison. Forecast-date role evidence remains unidentifiable for 14 evaluation hitters, down from 586; all 14 have verified zero target workload. Their lack of recent positive usage is retained explicitly in Remaining_AsOf_Role_Unidentifiable.csv and is not called medical absence. Known demonstrated usage does not make future role retention certain.

The preserved PA/GP thresholds, high-usage thresholds, structural fallbacks and PA-only incumbent fallback remain unchanged. State index 4 is exported as `retention_unidentifiable`; the legacy internal `unknown_role` key remains for binary/code compatibility. It is a missing-evidence residual, not a role-change or injury claim. No synthetic injury/health/demotion labels were added.

Twenty-four affected hitter artifacts were refitted: twelve five-state and twelve direct models. The same features, sample weights, partitions, tree/Ridge settings, clipping limits (754 PA/251 IP), temporal rules and shortened-2020 handling remain in place. Five-state fitting uses corrected input history and corrected target labels. Direct fitting uses corrected role inputs and the same unconditional workload targets, including shortened and verified zero seasons. It receives no subsequent participation discount.

Pitching observation logic is unaffected; its 24 original artifacts were reused byte-for-byte, with identical predictions and GP/GS coverage verified. This is not a fresh pitching experiment. Artifact_Lineage.csv records original/repaired hashes, fitting support and reuse.

The preserved five-class calibration support rule requires all five labels. Removing the coverage-driven residual leaves no examples in that class, so the rule disables hitter calibration. Nine of twelve original hitter classifiers had calibrators; none of the twelve repaired classifiers do. This consequence is disclosed rather than silently changing the fitting rule or adding a post-score calibration candidate.

## Matched unconditional workload accuracy

`frozen_hybrid` is the preserved strong benchmark; `expected_fitted` and `direct_mean` are the original candidates. H units are PA, P units IP. Bias is forecast minus actual. Every primary forecast excludes team allocation and medical envelopes.

'''+table(primary,['Family','Model','n','MAE','RMSE','Bias'])+'''

The five-state hitter model gains 3.272 PA MAE and 4.120 PA RMSE versus its original version, but remains 1.105 PA worse than the benchmark on MAE and 0.364 worse on RMSE. Direct gains 2.354 PA MAE and 1.465 PA RMSE; its RMSE is 0.229 PA better than the benchmark, while MAE remains 2.354 worse. This small RMSE difference is not independent evidence of superiority. Five-state overall bias worsens from −2.263 to +5.047; direct improves from +6.550 to −0.075.

'''+table(affected,['Sample','Model','n','MAE','RMSE','Bias'])+'''

On the 439 repaired targets, five-state beats the benchmark on both MAE and RMSE. Across the 766 input-repaired cases it improves versus the original outcome model but still loses to the benchmark. Direct regresses on the input-repaired group; its gains concentrate in cases without a local GP repair because retraining changes the shared fitted function. The 439 target-repaired cases are a subset of the 766 input-repaired cases; these groups are not additive.

## Forecast-date cohort tradeoffs

Cohort membership is frozen from the prior report, not retrospectively changed to favor the repairs. Repaired role classifications are separately recorded. Hitter MAE:

'''+table(cohorts,['Cohort','n','frozen_hybrid','expected_fitted','five_retrained','direct_mean','direct_retrained'])+'''

Repaired five-state improves established-hitter MAE/RMSE versus the benchmark (130.599/167.012 versus 133.562/169.649). Young-hitter MAE still loses, although RMSE improves. Interrupted hitters retain excessive positive bias (+25.433), and aging-hitter bias rises to +18.496. Direct improves young-hitter MAE/RMSE, but not the other cohort MAEs against the benchmark. Matched_Validation.csv supplies all cohorts and affected subsets; Year_Validation.csv and Window_Validation.csv preserve chronological windows, including explicitly exposed 2026 results.

## Outcome probabilities and severity

Against the same repaired labels, hitter joint-state Brier improves from 1.0288 to 0.6132, participation Brier from 0.11226 to 0.10769, and known-active retention Brier from 0.44782 to 0.21670. The original 41.14% predicted unknown frequency becomes 0%, matching zero unresolved outcome labels in this population. This does not eliminate genuine future uncertainty: the probabilities across absence, retained usage and changed usage remain nondegenerate.

Predicted absence becomes 28.87% versus observed 28.85%; high retained usage becomes 20.00% versus 19.03%; reduced retained usage 28.48% versus 27.98%; changed usage 22.66% versus 24.14%. These are annual usage proxies, not clinical or organizational outcomes.

Within high-retained seasons, workload bias improves +16.710 to +2.157 PA and conditional MAE 67.059 to 41.958. Reduced-state bias improves +46.096 to +17.385 and conditional MAE 114.357 to 89.934. Changed-state bias moves −12.767 to +2.486, but conditional MAE remains large at 150.441 (previously 160.698).

The exact algebraic decomposition is `W−Y = Σ_s(p_s−1[S=s])m_s + (m_S−Y)`. Both models use the same repaired observed labels for this comparison. Frequency-component MAE falls 101.684 to 82.502 PA, severity-component MAE 83.551 to 69.465. Signed components move −15.256/+12.994 to −0.827/+5.874. Components cancel, so absolute terms must not be added or interpreted as causal injury effects. Improved labels and state calibration have not eliminated unconditional forecast error.

## Protected gates and remaining limits

Both candidates retain every inherited release gate and fail numerical promotion. The repaired five-state candidate still fails unchanged pitching gates and the comparable high-RBI bias gate (+3.535 against ±3); it passes the durable-hitter gate. The repaired direct candidate fails durable-hitter MAE (97.148 against 89.132), along with unchanged pitching gates. Full-population accuracy criteria also fail. Gate JSONs disclose every value and threshold; none were relaxed.

All requested GP fields were recovered, so no missing GP prevents the matched experiment. What annual totals still cannot recover is true healthy availability, dated injury intervals, organizational opportunity and actual lineup/role retention. Those fields were neither needed nor fabricated for this test. Allocator accuracy, medical-envelope independence and independent untouched confirmation remain unvalidated. No further models were fitted after seeing scores.

The 1,900-player CSV includes production, preserved benchmark, original/repaired expected forecasts, participation/state probabilities, conditional workload, separate full-role scenarios, explicit fallback and prior allocator/medical sensitivities. The twelve diagnostic players are illustrations only. Pitcher figures are unchanged by the hitter repair; this test does not fix the separate starter workload mechanism.

## Reproduction and preservation

Restore archived files with `python restore.py`; restore parent archived research directories with their existing restore scripts. Run the scripts with the same recovered model source and beta export used by the preserved engines:

```
python inventory.py /path/to/recovered/model /path/to/beta-unpacked.json
python collect.py
python run.py /path/to/recovered/model /path/to/beta-unpacked.json
python summarize.py
python report.py
python test_contracts.py /path/to/recovered/model /path/to/beta-unpacked.json
```

Use the preserved Python runtime with numpy, scikit-learn and joblib; set OPENBLAS_NUM_THREADS=1, OMP_NUM_THREADS=1 and PYTHONDONTWRITEBYTECODE=1. Existing cached source responses make replay independent of new data retrieval. Contract tests verify matched targets/population, exact PA matching, missing-versus-zero semantics, future-input exclusion, unchanged fitting parameters, byte-identical unaffected pitcher models, absence applied once and protected thresholds. Eight tests pass. Reporting_Corrections.json documents a corrected affected-group flag for pitchers with batting records; it changed no forecasts.

Executable research code, correction logs, verified sources, all model artifacts and validation outputs are preserved in the hash-verified checkpoint. Production branch/code, talent rates, years 2–8, prospect translations, dynasty valuation and Trade Analyzer are unchanged. No deployment occurred.
'''
(D/'Report.md').write_text(report);print('Report generated')
