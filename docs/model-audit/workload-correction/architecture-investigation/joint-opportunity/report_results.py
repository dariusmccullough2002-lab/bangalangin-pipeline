"""Render the saved audit evidence without rerunning fits."""
import json,gzip,pathlib,numpy as np
P=pathlib.Path(__file__).resolve().parent
read=lambda p:json.loads(gzip.decompress(p.read_bytes()) if p.suffix=='.gz' else p.read_text())
p=read(P/'Past_Only_Pitch_Validation.json');h=read(P/'Past_Only_Hitter_Validation.json');di=read(P/'Diagnostics.json');hv=read(P/'Past_Only_Horizon_Validation.json');cu=read(P/'Past_Only_League_Impact.json.gz');cs=read(P/'Past_Only_League_Impact_Summary.json');ab=read(P/'Minor_Role_Ablation.json');cov=read(P/'Coverage_Followup.json');hc=read(P/'Past_Only_Hitter_Cases.json.gz');he=read(P/'Past_Only_Hitter_Additional.json.gz');il=read(P.parent/'Verified_Availability_Checks.json')['sources'];ilby={z['mlbam_id']:z for z in il};clinical=[z for z in hc+[z for z in he if z['anchor']+1!=2020] if any(f"{z['anchor']-2}-01-01"<=t['date']<=f"{z['anchor']}-12-31" for t in ilby.get(z['mlbam_id'],{}).get('placements',[]))]
def met(xs,method,key):
 d=np.array([z[method][key]-z['actual'].get(key,0) for z in xs]);return {'n':len(d),'MAE':float(np.mean(abs(d))),'bias':float(np.mean(d)),'RMSE':float(np.sqrt(np.mean(d*d)))}
clinical_scores={m:met(clinical,m,'PA') for m in ['baseline','selected','hitter_selected','past_only']};(P/'Prior_IL_Followup.json').write_text(json.dumps({'cases':len(clinical),'players':len({z['mlbam_id'] for z in clinical}),'metrics':clinical_scores,'scope':'Documented prior IL placements diagnostic only, not a comprehensive injury model.'},indent=2))
lines=[]
def add(s=''):lines.append(s)
def table(head,rows):
 add('| '+' | '.join(head)+' |');add('| '+' | '.join(['---']*len(head))+' |')
 for row in rows:add('| '+' | '.join(str(x) for x in row)+' |')
 add()
add('# BangaLangin V2.3C: recovered joint-opportunity audit')
add()
add('The interrupted research was recovered and continued from `8c7df81d6b3fb45905c826aade9919a73aac7ae2` on `review/capacity-opportunity-attrition-20261009`. The original 1,084 pitching and 682 hitter cases, their exact baseline predictions, source caches, failed experiments, and earlier results are retained. All changes in this checkpoint are additive research files. No production projection, valuation, UI, header or website file is changed.')
add()
add('The new joint approach improves the original starter benchmark, durability diagnostics and the 2020 schedule test. It does **not** dominate the strongest prior experiments across all cohorts/categories. Full dynasty valuation remains an offline sensitivity, with material ranking effects and incomplete uncertainty propagation. **No numerical release is recommended yet.**')
add()
add('## Recovery and reproducibility')
add()
add('The recovered parent preserved 441 prior blobs and added twelve continuation artifacts. Recovery verified 365 of 369 original audit artifacts locally; four files larger than the content-download limit remained intact on GitHub rather than being replaced. Source training/game/model helpers came from the verified recovery package. The catalog SHA256 remains `aadad4dc7763510da7eba928aae5018af1bc48cfacd8b5f510ca5f5cd0995235`. The final tree comparison verifies every parent blob is retained unchanged, including the deployed header correction (`d757773e`) and unrelated website files. Main was `ca15ab54d31e6b8f19c782d1b5185d8aed57bda0` at recovery.')
add()
add('Saved fitted models avoid repeating completed fits. Large model/case/impact artifacts are stored in recoverable pieces listed in `Recovery_Manifest.json`; run `python restore_artifacts.py` after downloading this directory. Pieces have byte counts and SHA256/Git blob checks. Research uses the existing preserved model root and extracted catalog as the two positional arguments; no site build or deployment is needed.')
add()
add('## Model and chronology')
add()
add('Pitching now models absent/RP/SP probabilities, starts and relief appearances conditional on principal role, pure-role IP per appearance, and exact QA3 expectations separately. Verified debut/current MiLB starting shares and raw combined MLB+MiLB workload are evidence features. Physical capacity is not converted into guaranteed MLB opportunity. Expected innings are the probability-weighted sum of starts × starting depth and relief appearances × relief depth. Future role, GP/GS and workload are labels only. Historical age and known forecast horizon are inputs; no names, arbitrary bonuses or player targets enter fitting.')
add()
add('The development-only selector chose joint linear starting depth. A fixed principal-role QA3 amendment addresses the initial model applying pure-starter QA3 rates to sporadic starts/openers in relief-dominant seasons. A fixed 50/50 blend with direct conditional workload was tested separately. These follow-ups were specified after exposed retrospective diagnostics and are exploratory; they were not selected as deployment winners using test labels. Mixed-role innings and QA3 splits are not directly verified: the principal-role QA3 relief offset is an aggregate modeling assumption. Rare relief QA3 is learned, not hardcoded to zero.')
add()
add('A final chronology audit found inherited full-history MLB ability priors in the initial joint features and an H calendar flag sourced from pitching-debut mapping. Both initial results are preserved. The `Past_Only_*` follow-up replaces ability priors with non-holdout records completed by each feature anchor and uses the observed hitter stream for its debut flag. All new workload/role fits exclude MLBAM-ID remainder0 and targets after the anchor; current multi-horizon training explicitly stops at completed 2025 outcomes rather than treating unavailable 2026 targets as absence. Frozen baseline category priors, rate aging and utility normalizers retain their original provenance for comparison. They are not newly validated chronological talent/category baselines.')
add()
add('Identity remainder4 supplies development outcomes and past-only calibration. It is longitudinal development, not independent identity confirmation. Historical test identities were never fitted, but their outcomes and earlier preprocessing choices have been examined. Results are retrospective chronological tests; no pristine confirmation claim is made. `PROSPECTIVE_CONFIRMATION.md` specifies the future completed-2027 gate.')
add()
add('## Pitching: preserved benchmarks')
add()
rows=[]
for label,scope,g in [('Expanded all','expanded','all'),('Expanded current SP','expanded','SP'),('Expanded current RP','expanded','RP'),('Expanded first MLB','expanded','first_MLB_season'),('Expanded second MLB','expanded','second_MLB_season'),('Frozen94 all','frozen94','all'),('Frozen94 SP','frozen94','SP'),('Frozen94 RP','frozen94','RP'),('Frozen94 second MLB','frozen94','second_MLB_season')]:
 d=p[scope][g]['metrics']['IP'];rows.append([label,p[scope][g]['n'],f"{d['baseline']['MAE']:.2f}",f"{d['linear_SP']['MAE']:.2f}" if 'linear_SP' in d else {'all':'23.77','SP':'37.55','RP':'18.22','second_MLB_season':'19.39'}.get(g,'—'),f"{d['past_only']['MAE']:.2f}",f"{d['past_only_blend']['MAE']:.2f}"])
table(['IP MAE cohort','n','Baseline','Prior linear-SP','Past-only joint','Fixed blend'],rows)
add('The original first candidate improved expanded MAE from29.42 to27.03 but still regressed starters in the original benchmark. The expanded set is dominated by796 RP cases versus288 SP; aggregate improvement can conceal a starter problem. The later direct linear-SP sensitivity reached25.92 expanded MAE. The new past-only count×depth architecture reaches26.05 expanded,22.997 frozen94 and35.880 frozen-SP. It improves the frozen starter gate while slightly losing to the prior linear-SP direction across the expanded set (46.54 vs46.38 SP). Second-season forecasting still favors the prior linear-SP sensitivity in the expanded set (24.13 vs24.87).'.replace('from29','from 29').replace('to27','to 27').replace('by796','by 796').replace('versus288','versus 288').replace('reached25','reached 25').replace('reaches26','reaches 26'))
add()
add(f"Expanded past-only IP bias is {p['expanded']['all']['metrics']['IP']['past_only']['bias']:.2f} and RMSE {p['expanded']['all']['metrics']['IP']['past_only']['RMSE']:.2f}, versus baseline bias1.82 and RMSE38.80. It beats baseline IP MAE in each of the seven preserved anchor seasons, but not the prior direction in every season. The paired player-cluster bootstrap MAE delta versus prior linear-SP is+0.13,95% interval[-0.46,+0.73]. This is not evidence of a decisive improvement over that prior direction.")
add()
add('Role transitions explain remaining underprediction. The prior/new forecasts overpredict SP→absent and SP→RP, and underpredict continuing starters and RP→SP. A larger physical-workload total alone does not determine starts. For current Skenes, the past-only model gives93.8% SP probability but only23.7 conditional starts, producing132.86 expected IP despite187.67 demonstrated raw capacity. For Misiorowski,97.5% SP probability and21.2 conditional starts produce124.50IP from174.67 raw capacity. These are general-model outputs, not individual adjustments: conditional start counts remain too regressive for some established/high-opportunity examples. The fixed blend lifts these estimates but weakens the original starter benchmark. A blanket starter uplift would not fix transition/absence bias.')
add()
add('Calibration improved the high-confidence SP bin: initial raw mean90.85%, observed85.47% over117 cases; the final past-only calibrated bin mean89.42%, observed90.80% over87 cases. Final multiclass Brier=.3871 and logloss=.6395. Bin membership changes with the model, so these are calibration diagnostics rather than paired proof. Full bins and transition MAE/bias are in `Diagnostics.json`.')
add()
rows=[]
for k in ['K','QA3','ER','BB','H','SV','HLD']:
 d=p['expanded']['all']['metrics'][k];rows.append([k,f"{d['baseline']['MAE']:.3f}",f"{d['linear_SP']['MAE']:.3f}",f"{d['past_only']['MAE']:.3f}",f"{d['past_only']['bias']:.3f}"])
table(['Expanded category','Baseline MAE','Prior linear-SP MAE','Past-only MAE','Past-only bias'],rows)
add('Exact QA3 uses game outs/ER: at least5IP with≤2ER OR at least6IP with≤3ER. It is not quality starts, starts alone, ERA/IP-derived QA3 or rate-scaled synthetic target labels. The principal-role amendment improves frozen-SP QA3 MAE4.073→3.362 and expanded-SP5.868→5.113. Expanded RP QA3 remains worse: baseline.487, prior.485, new.578. That category gate fails. Save/hold counts never increase from extra workload. K/ER/BB/H/SV/HLD and hitter talent rates remain frozen per-opportunity rates for this workload audit; role-specific talent and leverage deployment are unfinished.')
add()
add('## Verified MiLB usage and universal capacity')
add()
add('The league/catalog ledger retains1,287 pitching streams:1,190 verified affiliated-debut queries,959 positive MiLB results,231 no recorded affiliated workload,958 combined-workload corrections,86 no recorded MLB pitching debut and11 unresolved identities. All266 owned MLB pitching assets were already covered by verified debut evidence. The correction is universal and evidence-based, with no Misiorowski exception. Verified missing coverage is distinct from observed zero.')
add()
d=ab['scores'];rows=[]
for g in ['all','SP','RP','first_MLB_season','young_SP']:
 z=d[g];m=z['metrics']['IP'];rows.append([g,z['n'],f"{m['joint_selected']['MAE']:.3f}",f"{m['without_MiLB_role']['MAE']:.3f}"])
table(['Fixed2018/2021/2024 ablation','n','With MiLB role MAE','Without MiLB role MAE'],rows)
add('Only the two verified MiLB starting-share features were removed; physical capacity, MLB roles and ability features were retained. Aggregate and SP MAE favor MiLB usage; RP does not. Young-SP predictions remain worse than baseline in this diagnostic. This is limited retrospective evidence that minor usage helps opportunity, not proof that every young pitcher should receive more innings. The ablation retains initial frozen-prior feature provenance and is not a new pristine confirmation test.')
add()
add('All86 no-debut cases have cached affiliated workload;81 are SP,3 RP and2 H/two-way eligibility. Their predebut capacity is retained separately, without inventing an MLB debut season. The11 ambiguous provider links remain withheld. Nine have a single age-compatible candidate, Trevor Martin has two, and Yunior Marte has a material age conflict. Snapshot teams, exact cached candidate DOBs, MLB/MiLB years and the unresolved rationale are saved in `Coverage_Followup.json`. Age/team/name resemblance is insufficient to establish a stable provider identity.')
add()
add('The existing GitHub international-professionals research also contained12 official-source native-league pitching snapshots for2026. Their innings, appearance counts, sources and correct baseball-decimal conversion are preserved in `Foreign_Workload_Evidence.json`. None has a verified identity match to the current2,546-asset catalog (six match the broader old crosswalk outside that catalog). They therefore do not alter league projections. Their2026 records cannot supply older NPB/KBO debut-season workload for Olson/Ohtani or other historical cases. Foreign professional history and college/independent overlap remain incomplete; zero affiliated records is not zero total professional capacity.')
add()
add('## Hitters and schedule normalization')
add()
rows=[]
for label,scope,g in [('Preserved all','preserved','all'),('Preserved durable4years','preserved','durable_four_years'),('Preserved age33+','preserved','aging_33plus'),('Extended ordinary-season all','combined_standard','all'),('Extended durable4years','combined_standard','durable_four_years'),('Extended age33+','combined_standard','aging_33plus'),('Extended returning missed season','combined_standard','returning_after_missed_season'),('Extended young first full opportunity','combined_standard','young_first_full_opportunity')]:
 z=h[scope][g];d=z['metrics']['PA'];rows.append([label,z['n'],z['players'],f"{d['baseline']['MAE']:.2f}",f"{d['selected']['MAE']:.2f}",f"{d['past_only']['MAE']:.2f}",f"{d['past_only']['bias']:.2f}"])
table(['PA cohort','cases','players','Baseline MAE','Prior candidate MAE','Past-only calendar MAE','New bias'],rows)
add('The new hitter selector chose calendar hurdle on development data. It improves baseline, durability and aggregate extended bias, but is worse than the prior candidate on the original682-case aggregate, aging, returning and young first-full-opportunity cohorts. The extension adds533 ordinary-season cases to make1,215;117 unexpected2019→2020 shortened targets are reported separately, never silently pooled to claim ordinary-season gains. Returning after a missed recorded season is not automatically returning from medical IL.')
add()
add(f"The documented prior-IL diagnostic has{len(clinical)} cases and{len({z['mlbam_id'] for z in clinical})} players. PA MAE: baseline{clinical_scores['baseline']['MAE']:.2f}, prior{clinical_scores['selected']['MAE']:.2f}, past-only{clinical_scores['past_only']['MAE']:.2f}. The injury/availability gate fails. The cached nine-player IL sources are not comprehensive enough for an individualized medical forecast. No extra injury multiplier was added.")
add()
add('On the extended ordinary-season set, PA MAE165.29→116.08 and bias46.54→0.04; RMSE190.67→157.21. Category MAE also improves baseline, but not every prior-category score: HR4.650 prior vs4.653 new, SB2.721 prior vs2.830 new. Better workload bias does not establish uniformly better fantasy-category forecasting.')
add()
add('Matt Olson\'s original681.6PA starting workload and0.88107 first-year cohort multiplier yield600.55PA. No second injury penalty or multi-year attrition multiplier explains that first-year reduction. That cohort uses2012–2018 outcomes, so COVID did not cause his specific reduction. The prior workload candidate gives628.66PA; the past-only calendar model gives639.42PA, conditional active645.24PA and absent probability0.90%. It replaces the old workload attrition with modeled participation and conditional workload; it does not apply another cohort workload penalty. This does not prove every durable hitter is fixed: Freeman and Ramírez remain lower than baseline, and Judge falls469.41→402.96PA. Those outputs and the failed IL/aging gates are retained.')
add()
rows=[]
for cohort,key in [('H_anchor_2020','PA'),('H_anchor_2019','PA'),('P_anchor_2020','IP')]:
 d=di['COVID'][cohort][key]
 for method in ['baseline','selected','joint_selected','joint_calendar','past_only']:
  if method in d:rows.append([cohort,method,d[method]['n'],f"{d[method]['MAE']:.2f}",f"{d[method]['bias']:.2f}",f"{d[method]['RMSE']:.2f}"])
table(['Schedule cohort','Method','n','MAE','Bias','RMSE'],rows)
add('For the same86 positive2020-anchor hitters, PA MAE is168.21 baseline,183.05 prior raw candidate,152.02 earlier bounded candidate and143.77 new calendar/past-only. New bias+19.84 remains material. Calendar capacity/workload features normalize2020 by162/60, while actual talent rates and raw demonstrated professional capacity are not annualized. Completed2020 targets can be used with confidence weight60/162; future2020 shortened outcomes are not retrospectively assumed known at2019 prediction time. Positive2020-anchor pitching favors the calendar sensitivity26.60 vsbaseline30.50 and initial raw joint29.08; however the calendar pitching variant did not win the development objective. There is no test-selected pandemic-only production switch.')
add()
add('## Horizons, values and remaining gates')
add()
rows=[]
for rr in ['H','SP','RP']:
 for horizon in range(2,7):
  z=hv['role_horizon'][f'{rr}_{horizon}'];d=z['PA' if rr=='H' else 'IP'];rows.append([rr,horizon,z['n'],f"{d['baseline']['MAE']:.2f}",f"{d['candidate']['MAE']:.2f}",f"{d['candidate']['bias']:.2f}"])
table(['Role','Horizon','n','As-of cohort reference MAE','Past-only pooled model MAE','New bias'],rows)
add('These fixed pooled-horizon fits use chronological anchors2019/2021/2023 and completed targets through2025. They are new comparisons to an as-of cohort reference, not a byte-identical saved multi-year baseline. At2019 there are803 pitching horizon6 training rows and zero horizon7/8 rows. Current fits can train on completed2013–2025 pairs at horizons7/8, but no corresponding past-anchor forecast can both train and be scored through2025 at those horizons. Years7/8 therefore lack chronological validation. Role/workload attrition is learned directly by horizon; the old cohort workload multiplier is replaced once, while frozen rate aging remains.')
add()
add(f"The full sensitivity accounts for all{cs['assets']} assets:841 H,273 SP and786 RP supported MLB projections;645 picks/prospects/unresolved or unsupported assets andone two-way combined valuation remain unchanged. Baseline value recomputation matches exactly. Both frozen full-prior and corrected past-only sensitivity outputs are saved. In the past-only principal case, median neutral change={cs['joint_principal']['median_neutral_change']:.2f}, mean={cs['joint_principal']['mean_neutral_change']:.2f}, maximum absolute change={cs['joint_principal']['max_absolute_neutral_change']:.2f};{cs['joint_principal']['count_abs_delta_over1']} supported assets move by more thanone value point.")
add()
rows=[]
for name in ['Matt Olson','Freddie Freeman','Jose Ramirez','Aaron Judge','Jacob Misiorowski','Nolan McLean','Paul Skenes','Zack Wheeler','Cade Smith']:
 z=next(a for a in cu if a['name']==name);k='PA' if z['role']=='H' else 'IP';a=z['variants']['joint_principal'];b=z['variants']['conditional_blend'];rows.append([name,k,f"{z['baseline_annual'][0][k]:.2f}",f"{z['prior_first_year_workload']:.2f}",f"{a['annual'][0][k]:.2f}",f"{b['annual'][0][k]:.2f}",f"{z['baseline_values']['neutral']:.2f} → {a['values']['neutral']:.2f}",f"{z['neutral_ranks']['baseline']} → {z['neutral_ranks']['joint_principal']}"])
table(['Diagnostic player','Work','Baseline year1','Prior year1 direction','Joint year1','Blend year1','Neutral eight-year value','Neutral rank'],rows)
add('The prior pitching comparison here is the linear-SP sensitivity, not the earlier development-selected future_role_caps. H uses its earlier development-selected candidate. New first-year means use the separate one-year model; years2–8 use the pooled-horizon model. Values pass the resulting eight-year stats through the preserved surplus, nonlinear utility, discounting and competitive-fit evaluator. Strategy-specific competitive fit is saved separately for all existing modes. Rates, leverage growth guard, prospects, mixture weights and existing MLB low/base/high state amplitudes remain frozen. Category/count coherence passed40,368 H state checks and101,664 leverage checks. No injury or attrition factor is applied twice.')
add()
add('**The valuation uncertainty gate fails.** The new absent/RP/SP mixture is collapsed into a yearly mean, then evaluated inside inherited contribution-state paths. It is not a calibrated, correlated joint role/availability path distribution across eight years. Missing mixtures, two-way overlap and horizon7/8 extrapolation can drive large future-value/rank changes; for example the blend puts Misiorowski first by the existing neutral evaluator. This is a disclosed model sensitivity, not a ranking recommendation or a player-specific target. Paired historical bootstrap diagnostics quantify MAE differences, not dynasty-value intervals.')
add()
add('Remaining work: obtain independently verified provider links for11 unresolved identities; add calendar-verified historical foreign/independent capacity where available; improve continuing-SP and RP→SP starts without increasing absence/transition bias; resolve RP QA3 without treating mixed innings as verified component data; develop comprehensive prior-IL and durable-player opportunity forecasts; implement and validate correlated role/availability/category paths and two-way overlap; score untouched prospective outcomes and longer horizons. No proposed numerical projection or value change is deployed or approved by this checkpoint.')
add()
add('## Saved evidence')
add()
add('`PROTOCOL.md`, `PROTOCOL_AMENDMENT.md`, `Development_Selection.json`, `Hitter_Development.json`; initial joint/principal/past-only case and validation files; `Minor_Role_Ablation*`; `Diagnostics.json`; `Prior_IL_Followup.json`; `Coverage_Followup.json`; `Foreign_Workload_Evidence.json`; both original and past-only horizon files; `League_Impact*` and `Past_Only_League_Impact*` (all asset/year/category/component/value/rank details); all fitted model files; source scripts; `Integrity.json`; `PROSPECTIVE_CONFIRMATION.md`; and the piece/hash recovery manifest. Earlier experiments remain at their original paths and commits.')
add()
text='\n'.join(lines)+'\n'
# Make number-bearing prose readable while retaining machine-generated exact tables.
import re
parts=re.split(r'(`[^`]*`)',text)
for i in range(0,len(parts),2):
 parts[i]=re.sub(r'(?<=[a-z])(?=\d)', ' ', parts[i]);parts[i]=re.sub(r'(?<=\d)(?=[a-z])',' ',parts[i]);parts[i]=re.sub(r'(?<=\d)(?=(?:IP|PA|SP|RP|ER|IL)\b)',' ',parts[i])
text=''.join(parts)
text=re.sub(r'(MAE|RMSE|SP)(?=\d)',r'\1 ',text)
text=text.replace('is+0.13,95% interval[','is +0.13, 95% interval [').replace('expanded,22.997','expanded, 23.00').replace('35.880 frozen-SP','35.88 frozen-SP').replace('Misiorowski,97.5%','Misiorowski, 97.5%').replace('baseline.487, prior.485, new.578','baseline 0.487, prior 0.485, new 0.578')
(P/'Joint_Opportunity_Audit_Report.md').write_text(text)
print('Report saved',len(text),'IL',clinical_scores)
