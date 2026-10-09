# First-year hybrid implementation,2026-10-09

The talent/opportunity boundary is implemented and executable. The strongest
saved experiments and all production files are preserved. A complete replay
contains2546 catalog assets,1900 supported MLB players, all league categories,
all valuation modes, ranks, and unchanged prospect branches and years2–8.
No deployment or numerical production modification was performed.

FanGraphs' documented structure is the useful principle: combine independent
Steamer/ZiPS talent rates, then apply RosterResource playing-time allocations.
Basic ZiPS tables are a different product and are not MLB roster opportunity
forecasts. Steamer600 is talent normalization, not a200IP/600PA floor. ATC's
accuracy-informed aggregation supports testing an ensemble; its proprietary
weights are unknown. Detailed primary-source links and distinctions are in
Methodology.md. No FanGraphs projection is imported into the runtime.

## What changed and why

1. Recover actual historical hitter games played from the preserved career
   cache. The previous shared hitter feature vector had GP=0 even when games
   were available. Missing observations are explicit, not zero-game seasons.
2. Estimate PA/game and IP/start from completed usage. This separates work per
   appearance from the number of opportunities a team/player can receive.
3. Fit conditional-mean appearance/count models and own empirical usage
   baselines on completed, disjoint-core records. Participation means any MLB
   appearance, not medical health. Apply its probability only once.
4. After the first GP-only candidate failed, remove nonrandom target-coverage
   selection: H targets use future PA divided by as-of smoothed PA/game. These
   are appearance equivalents, explicitly not invented observed games.
5. Keep role maturity independent of a three-year tenure prerequisite. A young
   pitcher with24+ current starts and80% start share already demonstrates a
   rotation role. Preserve age and tenure as statistical evidence.
6. Test mean forecasts with a proper squared-error score. The earlier
   absolute-loss hurdle estimates a conditional median; median times
   participation probability is not an expected workload. MAE-only selection
   can favor suppression in an asymmetric mixture of absence and full usage.
7. Simplify the final runtime to one frozen blend per family, instead of
   routing to separate models for each cohort. Development guards keep every
   protected development cohort within5% of the strongest prior MAE.
8. Add dated roster/injury evidence and capped team allocations. Missing
   timetables do not imply recovery or a medical penalty. An incomplete roster
   leaves explicit unallocated slots rather than overfilling known players.
9. TalentRateForecast retains existing independent category rates and rate
   aging. The old exposure total is replaced, not discounted again. QA3 remains
   the league definition:5+IP/<=2ER or6+IP/<=3ER, including qualifying relievers.
   Conditional QA3 yields and SV/HLD caps remain tied to actual forecast work.
10. Integrate only first-year rewards into existing dynasty paths. All later
    utility rewards, probabilities, replacement rules, prospect branches and
    valuation modes remain fixed.56 inherited first-year state workloads were
    bounded; all1900 expected-stat projections passed coherence checks.

The final P blend uses75% saved principal joint role/appearance forecast and
25% saved first-year repair. H uses50% new conditional-mean count forecast and
50% saved first-year repair. Weights were chosen using ID4 chronological
2016/17/18/21/22 development outcomes. The extra neighbor and role-router
experiments are preserved but are absent from the final runtime.

## Chronological results

MAE, using the preserved production reference and exact existing cohorts:

| Cohort | n | Production reference | Strongest prior repair | Hybrid |
|---|---:|---:|---:|---:|
| Expanded pitchers,IP |1084|29.422|26.000|25.983|
| Expanded starters,IP |288|51.748|46.348|46.285|
| Original pitchers,IP |94|24.972|23.672|23.072|
| Original starters,IP |27|39.096|38.230|36.142|
| Young starters,IP |111|44.876|43.124|41.970|
| Stable rotation,IP |87|50.626|48.312|50.698|
| Standard hitters,PA |1215|165.293|111.727|111.809|
| Interrupted hitters,PA |188|208.951|126.340|125.770|
| Durable hitters,PA |24|146.189|84.132|94.090|

This is not a universal improvement over the strongest repair. It repairs the
original27-starter gate that the previous repair failed, while preserving the
expanded and young-starter limits. The durable-hitter protected gate still
fails:94.090 exceeds89.132. Its player-cluster interval versus the strong repair
is [-4.589,29.851]PA; only12 distinct players support the24 cases. That uncertainty
is not a reason to waive the numerical gate. Keep the successful durable
experiment saved and available; do not release this candidate wholesale.

The62 comparable high-RBI cases have signed RBI bias+3.436, exceeding the3.0
gate. Category rates were deliberately held fixed for workload attribution.
This cannot be honestly solved by subtracting0.436 from scored test cases.
The prior general RBI-rate experiment remains preserved and rejected under
its development requirement; no heldout-derived rate correction was applied.

All3526 historical expected-stat replays are coherent. Training target dates
end no later than each anchor; new fits exclude ID0 and ID4 core fitting.
Earlier incumbent calibration may use completed ID4 outcomes, as documented
in the parent research. Protected cases have been exposed before, including
in this engineering sequence. These are retrospective chronological results;
there is no claim of a new untouched out-of-sample validation.

## Named workload mechanisms and limits

| Player | Preserved production reference | Prior repair | Final hybrid |
|---|---:|---:|---:|
| Paul Skenes,IP |165.32|113.11|127.92|
| Aaron Judge,PA |469.41|253.08|353.60|
| Zack Wheeler,IP |142.43|133.69|116.27|
| Matt Olson,PA |600.55|661.14|646.95|

Skenes's frozen season already contains32 starts and174⅓IP, with187⅔IP in
2025. His old repair assigns93.8% probability to SP, so absence or loss of role
is not the main suppression: the conditional start-count/workload learner
falls to about20 starts. A young-entry cohort takes precedence over demonstrated
rotation use, and median workload fitting contributes to the reduction.
The new interface makes that decomposition inspectable and raises the mean;
127.92 remains too low to call this case fully repaired.

Judge's recent285PA/66GP should inform availability, not erase the prior158-game
lineup role. The mean count component forecasts about454PA versus the median
repair's253; the fixed blend gives353.60. MLB verifies a recent injury, but no
2027 lost-game timetable was supplied. Healthy opportunity is represented
separately; the system does not simply force600PA. The result remains provisional.
Wheeler's current blend is worse than the prior repair. This is specifically
flagged, not concealed by aggregate improvements. Representative and full
player-level CSVs expose all changes and selection explanations.

## Independent historical evidence

The19 matched public forecasts cover2017/18 Yankees hitters and2025 Pirates
pitchers. Each has publication date, URL, full-season target, actual outcome,
Pipeline production reference, prior joint, and final hybrid. Two requested
sample rows lack a preserved anchor. These are purposive ZiPS conditional
article totals; they are not a representative historical playing-time population.
External January dates differ from own December data cutoffs, and no historical
RosterResource allocation archive was retrieved. The matched-season comparison
is useful evidence, but the same-date roster-aware benchmark gate remains open.
No restricted table or proprietary algorithm was accessed.

## What is and is not ready

Ready: runnable rate/opportunity contracts, appearance models and saved
artifacts, explicit evidence/roster-budget interface, complete first-year league
projection/value replay, chronological comparisons, physical coherence and
preserved production/dynasty behavior.99 fitted artifacts verified readable.

Not ready: full dated organizational/medical evidence coverage, same-date
independent roster-allocated validation, durable-hitter protection, high-RBI
signed-bias gate, and complete resolution of established-player suppression.
The saved release file explicitly blocks numerical deployment. Architecture
implementation is concrete; numerical acceptance remains unfinished.
