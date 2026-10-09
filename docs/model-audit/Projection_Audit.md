# V2.3C pitching and hitter projection audit

October 9, 2026. Production engine unchanged. UI baseline commit: `2a5141ee889f4663120fce6cf142ea8e59464979`.

## Decision

Do not release a blanket projection or valuation increase. The saved arithmetic reproduces the live estimates. Misiorowski's workload and Smith's deployment opportunity warrant separate corrections; Anthony's partial-season availability and missing individual development evidence warrant a distinct hitter correction. The latest-season-only ablation below is diagnostic, not an accepted candidate. No numerical coefficients, catalog records, ownership, picks, prior registry, or saved trades were changed.

## What the engine actually does

The default is a recent four-calendar-year estimator, restricted to positive exposure in the selected observed role. The 2023/24/25/26 weights are .1/.2/.3/.4, renormalized over available matching-role seasons. The 1.5-year half-life belongs to a separate career diagnostic and does not control the default. Older career seasons remain evidence but do not directly enter the default recent-rate mean. Some audit fields inherited from that diagnostic are misleading: SP `rate_prior_strength` can say100 while the actual default uses30 IP; actual default hitter strength is100 PA.

Default workload is `(1-pw) * (.7*weighted_recent + .3*median_of_top_two_observed_workloads) + pw*role_median`, with `pw=1/(number_of_seasons+3)` and a historical98th-percentile cap. With only two seasons, the supposedly healthy statistic averages the partial and full seasons. It does not establish a full-season healthy ceiling.

Rates use `(weighted_counts + strength*early_role_average)/(weighted_exposure+strength)`. Priors are pooled regular-workload2010–2012 role rates, not replacement rates. Replacement is a separate contribution floor. Role is SP when starts/appearances is at least.5, otherwise RP, with eligibility fallback for absent appearances. This is primary-role classification, not a future start/relief probability model.

After workload and talent estimation, the engine applies a direct age/contribution-quartile cohort path from fixed2011–2017 anchors. Missing future MLB years enter workload attrition once. There is no extra injury haircut, diagnosis, player-specific rehabilitation forecast, MiLB-to-MLB skill translation, pitch-quality input, or individualized development curve. Per-category cohort ratios can change future K/9, ERA and hitter power independently. The three production states are bounded scaling states, not calibrated full player outcome distributions; a displayed0% elite-event probability does not prove a player has no elite upside.

Saves/holds are treated as historical rates per IP. The selected no-growth policy prevents positive cohort growth but does not estimate closer/setup opportunity, team opportunities, managerial decisions or job retention. Thus confirmed recent role changes are diluted by older seasons and the broad RP prior.

Exact QA3 is `(outs>=15 and ER<=2) OR (outs>=18 and ER<=3)`. Conventional QS is not substituted. The model forecasts historical QA3/IP after shrinkage and cohort adjustment, capped atIP/5; it does not predict starts or start depth. Small relief QA3 estimates are possible because qualifying long relief appearances exist. Current QA3 counts come from the saved Fantrax export; the compact historic Retrosheet cache distinguishes QA3 from QS. Missing original raw game files prevent certification of a new full raw-event replay.

## Misiorowski

Stable ID061yu / MLBAM694819, age24, correctly SP. Saved2025 MLB:66IP/87K/32ER/5QA3; saved2026:174⅔IP/252K/35ER/26QA3. MLB's current page agrees with2026 IP/K/ER. His2025 AAA63⅓IP/80K are omitted from the engine, so it interprets only66MLB innings as that year's workload, rather than129⅓ total professional innings. Prior minor-league workloads were71⅓IP in2023 and97⅓IP in2024. Those establish development/workload context, not directly interchangeable MLB rates.

The recent estimator gives128.10IP, the top-two median120.33IP, and role-prior-adjusted134.81IP. First-year cohort workload factor.9574 gives129.07IP. Forecast11.59K/9 and2.77ERA are not league-average ability: most of the counting-stat suppression is innings. The neutral contribution value is already93.41, so conservative workload does not establish an undervalued trade-market price.

Independent reference: December9,2025 ZiPS for the2026 season projected116.7 decimalIP/142K/3.86ERA and23starts, with A.J.Burnett, ChanHoPark and RedRuffing similarity comps. These are distribution comparables, not promised careers. This preseason2026 forecast is an earlier-horizon reference, not an independently sourced2027 forecast or validation target after observing2026.

## Cade Smith

Stable ID04eor / MLBAM671922, age27, correctly RP. The saved2026 line74IP/107K/16ER/41SV agrees with MLB; the saved export has1HLD. Earlier setup usage was1SV/28HLD in2024 and16SV/19HLD in2025.

Pre-aging workload71.39IP is reasonable relative to74recentIP, but the RP cohort reduces it14.5% to61.03IP. Default regression gives11.45K/9 before aging and11.33 after, compared with his observed13.01K/9.20.04ER means2.96ERA, rather than20ER being independently excessive. The15.81SV/9.17HLD forecast represents historical-role averaging rather than his demonstrated closer deployment. That is an opportunity-model limitation, separate from underlying skill and innings.

Independent December17,2025 ZiPS2026 reference:69.7 decimalIP/93K/21ER/2.71ERA; published similarity comps MarianoRivera, BobJames and DannyFrisella. No guarantee or acquisition premium follows. Relief deployment remains optional in this league, SVH7 is3SV+2HLD, and roster-specific marginal value can be low or negative. A higher saves forecast must not automatically become a high acquisition price. Saved39.23neutral is fundamental contribution utility, not a claim managers pay that price.

## Hitters: Tatis and Roman Anthony

The screenshot with647.6PA/22.7HR is FernandoTatisJr. His recent HR totals are25,21,25,25; the famous2021 42-HR season is outside the default window. His live24.1SB and.269AVG are coherent with projected counts. PA/AB/H/HR/TB reconciliation remains intact. The January2026 ZiPS article's2026 reference was644PA/26HR/25SB, so the live647.6PA/22.7HR/24.1SB is modestly lower in power, not an obviously broken playing-time forecast. Its2027 horizon and later information differ from preseason2026.

Anthony, stable ID05u9z / MLBAM701350, age22: saved545careerPA from303in2025 and242in2026. MLB matches these totals. He is correctly a hitter, but no saved individual prospect prior is present; the2026 preseason eligible-prospect list did not contain him. This is not failure of the identity-prior guard to retain an existing registered prior. The engine uses MLB rates plus a broad young-hitter cohort, not his specific scouting/development record.

Default268.14recentPA,272.5healthy statistic and317.36pre-agingPA become381.07first-yearPA after a1.20075young-cohort multiplier. It projects9.79HR,4.64SB and25.47neutral. The MLB transaction history establishes a June2025 debut and a May–August2026 injured-list interval; the estimator treats those partial years as workload evidence without explaining their causes. It consequently conflates delayed debut/absence with a recurring part-time role. There is no extra explicit injury penalty.

Independent December23,2025 ZiPS2026 reference:588PA/18HR/8SB/.267AVG/.369OBP/.443SLG. Its comparables include ChristianYelich, KenHenderson and DougClemens. A conditional588PA illustration with every saved talent rate and cohort path otherwise fixed gives15.10HR/7.17SB/39.30neutral. That is a workload sensitivity, not evidence that588PA or39.30 is the right2027 forecast/value. Anthony's rate and upside representation also need development evidence; increasing PA alone does not repair those omissions. Do not add a rank bonus or arbitrary prospect premium.

## Before/after diagnostic, not a release candidate

The ablation uses only the latest observed season for rates and workload, with the same priors, caps, aging cohorts, reconciliation and valuation architecture. No parameter search or market-value adjustment was performed.

| Player | Live baseline | Latest-season-only diagnostic |
|---|---|---|
| Misiorowski |129.1IP /166.2K /39.8ER /16.0QA3|166.3IP /222.7K /40.7ER /23.1QA3|
| Smith |61.0IP /76.8K /20.0ER /15.8SV /9.2HLD|59.6IP /76.2K /17.9ER /25.3SV /3.0HLD|
| Anthony |381.1PA /9.8HR /4.6SB|341.0PA /8.6HR /4.1SB|
| Tatis |647.6PA /22.7HR /24.1SB|667.2PA /22.1HR /28.7SB|

The attached CSV contains all22representatives: young/established starters, closers/setup/swingmen, elite/young/injury-affected hitters. Each representative's live projection and neutral value reproduces the frozen runtime to<1e-8. No actual numerical after-release exists.

Existing inspected identity-holdout2017 anchors →2018 outcomes:65H/21SP/42RP. Compact recovered GP/GS are used and disclosed; this is not original official-input certification, a new untouched holdout, or a full eight-year calibration. The reserved2021prospect cohort remains untouched. Latest-only worsened H PA MAE133.0→139.8, HR6.39→6.67, hits33.17→34.80 and TB56.67→58.46. SP K MAE60.57→61.41 and ER27.36→28.78 worsened despite modest IP/QA3 improvements. RP save MAE3.71→3.24 improved, but K21.53→21.64 and holds5.81→5.87 worsened. These mixed results fail a blanket adoption gate.

## Narrow proposed corrections and release gates

1. Separate conditional playing time from availability/deployment. Distinguish debut-only MLB exposure and verified absence from observed part-time role; use MiLB exposure for workload evidence only after an explicit, validated cross-level policy. Do not annualize every short season or erase injury uncertainty. Test young/full-season/absence/swingman groups using the existing inspected caches, with unaltered labels and grouped identities.
2. Separate RP talent from leverage opportunity. Retain multi-year K/BB/run-prevention estimates while using independently dated closer/setup evidence for future deployment scenarios. Validate SV and HLD jointly, including job losses and optional league deployment; retain no-growth safeguards until role transitions are modeled. Do not hardcode Smith's41saves or an arbitrary RP discount.
3. For Anthony and similar graduates, recover only verified pre-debut individual evidence by stable ID, with correct time alignment and a validated MLB/prior update. Do not reuse rankings that already incorporate MLB performance as independent priors. The previous mean-shifting debut blend failed saved low-PA tests; it must not be quietly reinstated.
4. Forecast QA3 through expected starts and start-depth/run distributions only if the saved appearance inputs support independent validation. Preserve the exact definition, count coherence and relief eligibility; a standalone IP/5 bound is insufficient opportunity modeling.
5. Audit diagnostic labels separately: distinguish default versus career strengths and conditional versus expected production; no statistical adjustment is required to make labels honest.

No new valuation candidate is proposed for approval yet. A later candidate must beat the frozen baseline on relevant groups without degrading established cases, preserve stable IDs/ownership/picks, avoid unsupported premiums, pass exact-category coherence and first-activity continuity checks, and undergo explicit approval before production. The header can be reviewed independently.

## Sources and reproducibility

All external observations retrievedOctober9,2026. MLB stat/transaction evidence: [Misiorowski](https://baseballsavant.mlb.com/savant-player/jacob-misiorowski-694819), [Smith](https://baseballsavant.mlb.com/savant-player/cade-smith-671922), [Anthony](https://baseballsavant.mlb.com/savant-player/roman-anthony-701350).

Independently published preseason projection references: [Brewers, December9,2025](https://blogs.fangraphs.com/2026-zips-projections-milwaukee-brewers/), [Guardians, December17,2025](https://blogs.fangraphs.com/2026-zips-projections-cleveland-guardians/), [RedSox, December23,2025](https://blogs.fangraphs.com/2026-zips-projections-boston-red-sox/), [Padres](https://blogs.fangraphs.com/2026-zips-projections-san-diego-padres/). ZiPS decimals such as69.7 represent decimal innings, not baseball69⅔ notation.

Run `python3 projection_audit.py RECOVERY_ROOT DECOMPRESSED_VERIFIED_CATALOG OUTPUT_DIRECTORY`. `RECOVERY_ROOT` is the preserved `BangaLangin_V23C` directory. The output JSON records the catalogSHA256, parity checks, individual diagnostic lines and every historical case. The CSV is presentation data only. The script does not write into the recovery root or production model. Requires the preserved recovery inputs and Python/numpy; it is not a reconstruction from these22players.


## League-wide young-pitcher workload experiment

The same workload-only substitution now applies by stable player ID and season, independently of MLB talent rates. The saved roster contains 821 owned players. The inventory identified 335 MLB-exposed pitcher-seasons from 170 pitchers who were age26 or younger in the2023–26 forecast window. Age26 is a transparent inventory screen, not a calibrated development cutoff. Prospects without MLB histories remain listed separately in the821-player coverage file.

Only one qualifying season currently has independently verified, nonoverlapping MiLB workload input in this experiment: Misiorowski2025, 66 MLB IP plus63⅓ AAA IP. Its combined129⅓ IP changes his first-year projection from129.1 to150.9 IP,166.2 to194.3 K, and16.0 to18.7 QA3. MLB talent rates are identical. ER also increases from39.8 to46.5 because projected innings increase; ERA does not change. The resulting neutral sensitivity is109.77 versus93.41, not an adopted value or acquisition price.

The remaining334 inventoried seasons have unverified MiLB totals. They retain the baseline rather than treating missing data as zero or adding invented innings. Comprehensive league-wide numerical adoption cannot be certified from the frozen MLB-only inputs. Young_Pitcher_Season_Coverage.csv identifies each missing season; Professional_Workload_Experiment.json records coverage and the only verified change. professional_workload_audit.py reproduces the experiment.

The integration rule requires same-season affiliated regular-season totals, conversion of baseball innings notation to outs/decimal innings, and deduplication of aggregate rows against team/level splits. It must preserve MLB-only K, ER, SV, HLD and QA3 rates. It does not restore injury-shortened workloads or turn relief innings into starter experience. MiLB-only earlier seasons require a separately specified and validated weighting policy before insertion; they are not silently added to an MLB career window. Production remains unchanged pending regression validation and explicit model-release approval.
