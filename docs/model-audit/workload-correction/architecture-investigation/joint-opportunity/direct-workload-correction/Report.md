# Targeted playing-time correction: retain the preserved benchmark

Neither replacement earned numerical adoption. The frozen comparison used 4,004 matched chronological cases (1,487 hitters, 2,517 pitchers), including 1,562 zero outcomes. All scored 2026 waves are exposed; no untouched confirmation sample was identified. These results are exploratory, not an independent release certification. Production, talent rates, years 2–8, prospect translations, dynasty valuation and Trade Analyzer remain unchanged.

## Matched primary comparison

| Forecast | H MAE / RMSE / bias (PA) | P MAE / RMSE / bias (IP) |
|---|---|---|
| Preserved frozen benchmark |111.412 /154.320 /+0.309|20.337 /32.593 /−1.696|
| Five-state expected season |115.789 /158.804 /−2.263|20.876 /33.403 /−0.402|
| Direct unconditional mean |116.120 /155.557 /+6.550|21.409 /33.931 /−0.031|

The direct estimator improves hitter RMSE versus the outcome model, but loses MAE and does not beat the benchmark on either overall error measure. Pitcher signed bias approaches zero while absolute and squared error worsen. A mean target does not guarantee improved absolute-error performance. The older strong-prior comparator and prior repair remain in the validation tables; all prior artifacts are retained.

The direct candidate fails protected original94, originalSP, expanded pitchers, young starters and durable-hitter gates. Original SP MAE is 43.939 against 36.880; young SP is 46.188 against 43.410; durable hitters are 100.136 against 89.132. Stable-rotation and standard-hitter gates pass, which does not override the failures. Release_Gates.json preserves every inherited threshold and separately rejects independent confirmation, allocator accuracy and clinical-label identification.

## Frozen implementation and target

Protocol_Freeze.json and Inventory.md were committed before scoring (local freeze commit 68c2305). Only one new numerical candidate was fitted: inherited squared-error histogram boosting settings (100 iterations, 15 leaves, minimum leaf 30, learning rate .07, L2 10, seed 2309). Inputs are forecast-date workload history, age/tenure, demonstrated role, pitcher GS/GP shares and explicit observation missingness. Training uses inherited chronological population and core-ID partitions, target years through min(anchor,2025), excluding the shortened 2020 target; the inherited pitcher helper also excludes 2020 anchors. Targets include shortened and verified zero seasons. The coverage check found no positive pitcher targets excluded by a missing target appearance count.

The estimator predicts E[PA or IP | forecast-date inputs] across participation outcomes. There is no subsequent participation, availability, allocator or medical multiplier. Existing 754 PA/251 IP limits are retained. The full-role scenario is a separate column, never substituted for unconditional production. Existing talent forecasts are untouched. No candidates or hyperparameters were added after scoring.

## Probability versus severity

For state probabilities p_s, conditional workloads m_s, observed state S and realized workload Y:

`forecast − Y = sum_s (p_s − 1[S=s]) m_s + (m_S − Y)`.

The first term is outcome-frequency attribution; the second is within-state severity. This identity reconciles to numerical precision. Absolute magnitudes cannot be added because terms cancel. It is an algebraic diagnostic, not a causal attribution or an attainable oracle forecast. Single-player outcome differences contain irreducible uncertainty; group frequencies expose calibration problems.

Across hitters, signed bias −2.263 PA decomposes into −6.051 frequency and +3.788 severity. Pitcher bias −0.402 IP decomposes into −1.084 and +0.682. Frequency MAE is 72.465 PA/16.110 IP; severity MAE is 82.639 PA/12.814 IP. Oracle-state results are diagnostic only.

| Forecast-date cohort | H reduced-state predicted / observed | H within-state bias PA | P reduced-state predicted / observed | P within-state bias IP |
|---|---|---:|---|---:|
| Established |10.19% /21.29%|+32.45|46.89% /45.77%|+4.25|
| Young |21.21% /21.18%|+14.02|43.82% /45.30%|−1.07|
| Interrupted |10.43% /14.86%|+84.02|32.27% /25.75%|+5.52|
| Aging |3.34% /6.29%|+3.55|19.45% /21.74%|+1.64|
| Uncertain role |8.74% /8.51%|+40.51|21.58% /23.64%|+2.42|

Overall, reduced hitter seasons are underpredicted (12.42% versus 15.67%), while their severity forecasts are too high by 37.91 PA. Interrupted pitchers overpredict this outcome by 6.52 percentage points. Thus a universal increase in participation or workload is unsupported. Pitcher nonparticipation is overpredicted overall (47.67% versus 45.01%). State_Frequency_Severity.csv supplies every state/cohort; Year_Validation.csv supplies chronological results.

## Confirmed coverage defect and narrow correction

439 of 441 observed hitter `unknown_role` cases involve missing future games played, despite known workload. Predicted unknown frequency is 41.14%, observed 29.66%. Its signed frequency contribution is +49.58 PA, offsetting −55.63 PA across known positive states. This category partly models record coverage rather than baseball role changes. Annual totals cannot identify clinical injury, demotion or genuine role retention.

The bounded sample uses complete official MLB hitting censuses for 2018 and 2024 and 23 deterministically selected players' 2025 transaction histories. Official API URLs, retrieval dates, response hashes and cached responses are preserved under verified/. Matching existing PA exactly recovered 71 target-season GP gaps. Thirty-one become identifiable usage proxies (7 high retained, 12 reduced, 12 changed); forty still lack forecast-date role evidence. Research label auditing now calls these forty `retention_unidentifiable_asof`, preserving missingness instead of declaring future-role uncertainty. No medical absence labels or numerical forecasts were changed by this correction.

The fixed-model forecast-date coverage sensitivity separately repairs 73 anchor GP gaps among 240 eligible cases, using only 2018/2024 information for 2019/2025 forecasts. Fifty-three predictions change; mean prediction rises 34.51 PA. Affected-sample MAE worsens from 130.930 to 144.155, RMSE from 163.656 to 170.563, and bias from +23.253 to +57.765. This is an exposed source-coverage stress test, not another fitted candidate and not adopted. Filling a feature without fitting against consistently covered historical inputs introduces a domain mismatch; it is not a validated numerical correction.

The 169 transaction events contain 22 IL-status events, 22 options and 22 recall/promotion events; other events are preserved. Effective transaction dates are available, publication timestamps are unknown. Empty responses do not establish health. No complete absence intervals were identified. Additional data specifically needed: paired forecast-date GP, dated IL placement/activation, option/recall intervals, daily roster eligibility and starter-role assignments. These would distinguish medical absence, demotion and role loss; annual PA/IP cannot do so.

Evidence selection was frozen before fetching. Its original broader protected-cohort aliases differ from the narrower reporting masks; overlap yields 23 unique IDs. Evidence_Selection_Disclosure.json documents the limitation. It is a coverage/feasibility sample, not representative injury calibration. Reporting masks were corrected to the frozen forecast-date cohort contract without changing predictions, fitting or parameters; earlier broad-mask tables are retained transparently.

## Recommendation and reproduction

Retain the preserved benchmark. Keep the semantic missing-role correction in research auditing; do not promote the failed direct or five-state forecasts. Roster allocation and medical envelopes remain separately labeled sensitivities and were not applied in this primary comparison. A consistently covered historical role/transaction panel and genuinely untouched future outcomes are required before numerical replacement. Named diagnostics illustrate the complete league table and do not determine parameters or floors.

Restore this directory's checkpoint with `python restore.py` if archived files are absent. Restore parent research checkpoints with their existing restore scripts. Run `python run.py /path/to/recovered/model /path/to/beta-unpacked.json`; pass these same two source arguments to `audit_evidence.py`, `coverage_sensitivity.py` and `test_contracts.py`. `run.py` reuses the preceding scenario engine; `audit_evidence.py` performs semantic evidence corrections; `coverage_sensitivity.py` performs the frozen source-coverage stress test; `test_contracts.py` verifies six contracts. Paths and source prerequisites are documented in the inherited checkpoint. Model artifacts, cached official evidence, full player tables, year/cohort validation and failed alternatives are preserved in the hash-verified archive. No deployment was performed.
