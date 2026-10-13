import json,csv,html
from pathlib import Path
D=Path(__file__).parent;ROOT=D.parents[1]
def j(n):return json.loads((D/n).read_text())
S=j('Summary.json');P=list(csv.DictReader((D/'Population_Comparison.csv').open()));E=j('inputs/model-evidence.json');T=j('Representative_Trades.json');by={x['name']:x for x in P}
names=['Kyle Bradish','Jose Soriano','Colt Keith','Ramon Marquez','Taitn Gray','Franklin Primera','Emmanuel Rodriguez','Ethan Holliday']
def values(ns):
 return '\n'.join('| '+n+' | '+ ' | '.join(f'{float(by[n][k]):.6f}' for k in ['before','after_spacing','after_extension'])+' |' for n in ns)
def annual(n):
 p=next(x for x in E['players'].values() if x['name']==n)
 return '\n'.join('| '+str(a['year'])+' | '+' | '.join(f'{a[k]:.6f}' for k in ['workload','gross_category_score','replacement_deduction','state_expected_utility','discount','discounted_display_contribution'])+' |' for a in p['annual'])
def season(n):
 p=next(x for x in E['players'].values() if x['name']==n);out=[]
 for a in p['history']:
  sk=a.get('skills',{});ap=p['verified_appearances'][str(a['year'])];gp=ap.get('GP',sk.get('gamesPlayed','missing'));gs=ap.get('GS',sk.get('gamesStarted','missing'));out.append(f"| {a['year']} | {a['role']} | {a['stat']['IP']:.6f} | {gp} | {gs} | {a['stat']['QA3']} |")
 return '\n'.join(out)
def largest(key,delta):return '\n'.join(f"| {x['name']} | {x['before']:.4f} | {x[key]:.4f} | {x[delta]:+.4f} |" for x in S['largest_spacing_changes' if key=='after_spacing' else 'largest_extension_changes'][:10])
def sensitivity(n):
 p=next(x for x in E['players'].values() if x['name']==n)
 return '\n'.join(f"| {n} | {x['label']} | {x['initial_workload']:.4f} | {x['value']:.4f} |" for x in p['workload_sensitivity'])
report=f'''# BangaLangin Pipeline — valuation audit and review candidates

Base: `4607c1619458be18aa884a106eb1be2ac7bd13ee`. Audit date: October 12, 2026.

## Recommendation

Adopt the **10% spacing policy** after review. It removes broad isotonic plateaus without individual price overrides, keeps supplied prospect ranks dominant, and retains existing supported deviations and debut continuity. Keep contribution forecasts unchanged.

Treat the **overall-ranking extension as a review candidate**, not a proven model correction. It supplies the requested dominant overall anchor, but should not be adopted automatically: it materially moves elite starters, boosts some relievers despite weak league scarcity, has incomplete source coverage, and has no transaction-price calibration. Review these cohort effects and source vintage before choosing it.

No valuation changes have been deployed. The recovered actual model reproduces Bradish, Soriano and Keith exactly. No confirmed arithmetic or SP/RP routing defect explains those three values. A metadata correction now identifies the active estimator parameters separately from inherited career diagnostics; it changes neither forecasts nor fundamental values.

## Recovery and production status

Remote `main` was fetched and points to `4607c16`. The live Trade Analyzer HTML is byte-identical to that commit's local HTML (`Live_Verification.json`). Earlier release commits `975ab6e`, `ce326ae`, `f0388d8` and `2f2b392` are ancestors. The prior workspaces and untracked research were left intact; this work uses an isolated branch.

This verifies Git and live release state. It does **not** establish whether the other conversation is still actively executing; no cross-conversation running-task monitor is available.

## Before and after

| Player | Deployed | Spacing only | Overall extension |
|---|---:|---:|---:|
{values(names)}

All figures are internal trade-value points. Six decimals here support reproducibility; the interface can retain ordinary rounded displays. These are valuation policy outputs, not empirically established market prices.

## 1. Prospect spacing correction

The original fixed decreasing isotonic curve pools conflicting source-rank/fundamental pairs into identical values. The fix uses **90% of that fixed pooled curve plus 10% of a positive decreasing power curve fitted across its rank domain**. The power component is normalized to preserve the mean across the original 500-point curve. This imposes a modest ordinal-distance prior rather than player-specific prices or tiny uniqueness epsilons. Both components decrease, so the resulting curve declines strictly. Linear interpolation is continuous; source tiers do not trigger extra value jumps.

The 10% choice is the smallest predeclared sensitivity examined (10%, 20%, 30%). It is a conservative policy judgment, not a parameter selected from transaction outcomes. The biggest change is Sebastian Walcott, **54.2757 → 57.4834 (+3.2077)**. This upper-tail effect must be reviewed even though aggregate value barely changes.

The existing effective ranks, evidence strengths, source weights and adjacent-tier deviation bounds stay fixed for all 265 players. Rodriguez's effective rank remains **80.4082116**; unlike the old plateau, the new curve responds to that supported deviation. Debut metadata never refits the curve or removes source membership.

- Exact tie groups: **16 → 0** among the 265 affected prospects.
- One-decimal tie groups: **16 → 28**. Previously distinct plateau groups fan out into several rounded groups; this increase does not mean more exact plateaus. `Tie_Diagnostics.json` separately reports exact values and distinct values within each rounded group.
- Sum of affected prospect values: **{S['prospect_total_before']:.9f} → {S['prospect_total_after_spacing']:.9f}**, a **{S['prospect_total_after_spacing']-S['prospect_total_before']:+.9f}** change.
- Every rank-curve interval declines; there are no remaining flat curve sections. No attempt is made to make every rounded display unique.
- All tier boundaries and adjacent-rank changes appear in `Tier_Boundaries.csv`. Tier bounds can still saturate supported deviations; that is a disclosed rank-deviation policy, not a price discontinuity.

| Largest spacing changes | Before | After | Change |
|---|---:|---:|---:|
{largest('after_spacing','delta')}

The five reported tied players now separate modestly: Marquez 20.1313, Gray 20.1117, Primera 20.1021, Rodriguez 20.0283, Holliday 20.0399. Rodriguez's supported negative adjustment places him below Holliday. Their displayed values may still round together.

## 2. Actual production pitcher audit

### Identity, coverage and roles

José Soriano is Fantrax **04c0o**, MLBAM **667755**, linked through the preserved crosswalk and career profile. Kyle Bradish is **04pq4 / 680694**; Colt Keith is **05jrh / 690993**. Source-table team labels are snapshots and are not used to override stable identity. No ambiguous name-only match is used.

The values here are the current verified *website snapshot* values. The 2026 inputs are the preserved Fantrax regular-season export; 2022–2025 inputs are the cached official MLB records. They are not newly fetched 2026 statistics. Historical QA3 counts use the preserved game-level calculation, not conventional quality starts.

| Bradish season | Routed role | IP | Appearances | Starts | QA3 |
|---|---|---:|---:|---:|---:|
{season('Kyle Bradish')}

| Soriano season | Routed role | IP | Appearances | Starts | QA3 |
|---|---|---:|---:|---:|---:|
{season('Jose Soriano')}

All listed seasons have positive observed innings. Bradish has no missing post-debut calendar year within this series. Soriano's 2023 relief season is preserved but excluded from the current SP rate/workload fit. His 2024–2026 start shares support the SP route. A short relief debut never independently establishes a permanent bullpen role.

**Zero/missing limitation:** SV/HLD zeros are zeros in the preserved normalized records; absent years and absent component keys are recorded separately. The inherited normalization uses `.get(field, 0)` in places, so raw-field presence cannot be independently proven for every historical zero from these normalized artifacts. This audit does not relabel an absent record as a verified zero or silently repair forecasts without original evidence. Both pitchers' positive-season IP, GP and GS are supported; their tiny smoothed SV/HLD contributions are not material to the discrepancy.

### Talent versus workload

The active recent estimator uses weights 0.1/0.2/0.3/0.4 for 2023–2026, renormalized across positive matching-role seasons. The rate pseudocount is **30 IP** for pitchers, **100 PA** for hitters. Rate shrinkage is not an extra subtraction from final value.

Bradish: recent weighted workload **96.333333 IP**, healthy top-two median **161.833333**, historical SP prior **171**, prior weight **1/7**. Base workload = `(6/7) × (0.7 × 96.333333 + 0.3 × 161.833333) + (1/7) × 171` = **123.842857 IP**. His 2024–2025 interrupted seasons therefore lower future baseline workload despite 155 observed 2026 IP. Projected rates are K/IP **0.961869**, ER/IP **0.412560**, BB/IP **0.378459**, H/IP **0.929719**, QA3/IP **0.106514**.

Soriano: matching SP seasons 2024–2026; recent workload **160.259259**, healthy median **173.166667**, prior **171**, prior weight **1/6**. Base workload **165.276235 IP**. Rates: K/IP **0.896406**, ER/IP **0.440265**, BB/IP **0.409212**, H/IP **0.900520**, QA3/IP **0.093210**. His low value is not mainly a very short projected baseline workload.

The first future cohort multiplier produces **101.751448 IP** for Bradish and **135.392894 IP** for Soriano. Their subsequent aging/attrition paths are substantially shorter than Keith's age-25 hitter path. Historical cohort support: Bradish 77 anchors/52 players; Soriano and all representative cohorts are recorded in `inputs/model-evidence.json`.

Yes, short/interrupted seasons enter long-term baseline capacity. That is a confirmed mechanism, but not by itself evidence that replacing them with a healthy ceiling improves forecasting. Starting workload already reflects recent availability; applying a generic future cohort can compound conservative availability assumptions. There is **no duplicated explicit injury haircut**, but calibration of that interaction remains unresolved. The model does not separately forecast cause-specific injury recovery or future role retention.

### Numerical value decomposition

Signed category score includes HR/R/RBI/SB/AVG impact/OPS impact for hitters; negative raw ER/K/SVH7/QA3/K-to-walk impact/WHIP impact for pitchers. The preserved SVH7 vector is `3×SV + 2×HLD`; the model uses raw earned runs, not ERA as an independent category. QA3 is at least 5 IP and at most 2 ER, **or** at least 6 IP and at most 3 ER. Ratios are exposure-weighted impacts relative to frozen references, not predicted head-to-head wins.

Replacement = role floor × exposure / role reference workload. Floors: H **4.614672**, SP **−0.348355**, RP **0.113167**; workloads: H **509 PA**, SP **171 IP**, RP **56.666667 IP**. A negative SP floor means the SP replacement deduction below is negative: it slightly **adds** surplus. It is not a large SP penalty. Floors are inherited historical structural proxies, not a newly validated estimate of this league's free-agent acquisition scarcity.

Value = **2.6501808806 × Σ (0.88^t × expected state utility)**, for 2027–2034. Utility truncates negative surplus at zero and retains the frozen convex upper tail. Three states carry 0.25/0.50/0.25 probabilities; utility is computed within states before averaging. Neutral risk-preference deduction, additional injury penalty and explicit role-retention penalty are **all zero**. Future cohort workload/rate multipliers already include historical loss and aging; no second external discount is applied.

| Bradish | IP | Gross score | Replacement deduction | Expected utility | Time discount | Value contribution |
|---|---:|---:|---:|---:|---:|---:|
{annual('Kyle Bradish')}

Total **10.5291542146**.

| Soriano | IP | Gross score | Replacement deduction | Expected utility | Time discount | Value contribution |
|---|---:|---:|---:|---:|---:|---:|
{annual('Jose Soriano')}

Total **11.3478234055**.

| Keith | PA | Gross score | Replacement deduction | Expected utility | Time discount | Value contribution |
|---|---:|---:|---:|---:|---:|---:|
{annual('Colt Keith')}

Total **24.1369769967**. Keith's long tail, rather than an overall ranking advantage, drives the deployed result. Annual category components and exact state paths for 14 representative players are included in `Annual_Decomposition.csv` and `inputs/model-evidence.json`: established starters, young/partial-season starters, relievers, mixed-role histories and hitters.

### Diagnostic workload sensitivities — not proposed forecast fixes

These counterfactuals hold rates, aging curves, state probabilities, utility, replacement and discounting fixed and change only initial workload. They show sensitivity; they are not evidence to promote a workload forecast.

| Player | Initial-workload assumption | Workload | Value |
|---|---|---:|---:|
{sensitivity('Kyle Bradish')}
{sensitivity('Jose Soriano')}

### Confirmed metadata correction

The audit object inherited career-estimator fields such as 100-IP rate strength and exponential recency weights even when the active V2.3 recent estimator uses 30 IP and fixed season weights. Those fields are misleading when read as active inputs. The candidates add `active_forecast_inputs` for **{S['confirmed_metadata_defects']}** records with this estimator, while retaining the inherited career diagnostic separately. This is an explanatory metadata correction, with **zero forecast or price effects**. It does not claim all inherited fields were numerically applied twice.

## 3. Ranking coverage and proposed extension

The deployed registry covers listed prospects only. Bradish, Soriano and Keith are absent, so all three retain contribution-fundamental values. The same coverage boundary explains why the overall table has no direct effect on Soriano.

Overall source: recovered `Dynasty_Dugout_Overall.tsv`, 500 unique stable Fantrax IDs, received **2026-10-08**; publication date **not independently established**. Prospect source: the separately supplied 500-player prospect snapshot received **2026-10-12**; publication date unknown. These are distinct source scopes, not interchangeable ranks. The source filenames/tabs, dates, tiers, Fantrax and available MLBAM IDs appear in `Source_Registry.json`.

The extension fits an overall rank curve from **486 supported listed players' contribution fundamentals** on the existing display scale; existing ranking-led values are **excluded** from this fit. It blends the overall pooled curve with the same 10% fitted power spacing prior. Direct overall ranks take precedence when available. Prospect-only identities absent from the overall list use a disclosed monotone scope bridge fitted from **117 shared stable IDs** and evaluated on the **single overall value curve**. This is not overall rank = prospect rank, and not two summed value anchors.

MLB deviations use at most 25% evidence weight, scaled by career exposure, and are bounded to ±10% of source rank. Unsupported roles/samples retain the source-only anchor. Existing prospect talent deviations are retained with explicit scope translation; they do not use damaged short-season workload to erase prospect standing. Source weights remain greater than 50% for all supported identities. These are bounded policy choices, not historically fitted market-price coefficients.

- Direct overall coverage: **486**; absent catalog source rows: **14**, explicitly unsupported.
- Prospect-only bridged coverage: **162**; total candidate coverage: **648** assets.
- Other catalog assets retained unchanged: **1,898**; omission never means zero value.
- Final curves have no flat rank sections. Five exact asset-level ties remain because different supported deviations arrive at the same effective rank; no artificial separation is added. Full identities and rounded ties are in `Tie_Diagnostics.json`.
- Contribution forecasts and competitive-fit values remain untouched across all **2,546** assets. Pick values and Rounds 1–5 eligibility remain unchanged; Rounds 6–20 are never introduced as assets.

| Largest extension effects (relative to spacing candidate) | Deployed | Extension | Extension minus spacing |
|---|---:|---:|---:|
{largest('after_extension','delta_extension')}

**League-context limit:** the inherited contribution engine uses common pitching-category dispersion, role-specific replacement proxies, no arbitrary RP penalty, and no scarcity premium. It preserves 35-IP weekly eligibility context and optional RP deployment, but does not independently quantify this league's replacement acquisition cost. Source-led reliever increases (for example Mason Montgomery) therefore remain material adoption concerns. Dominant overall rankings cannot be represented as validated league-specific market prices. Do not force hitter/pitcher equality or tune Bradish/Soriano/Keith individually.

## 4. Trade arithmetic and validation

`Prospects_All_265.csv` compares every affected prospect. `Population_Comparison.csv` supplies every candidate-covered identity. `Saved_Trade_Comparisons.json` recalculates every saved package. Representative packages:

| Package comparison | Deployed sides | Spacing sides | Extension sides |
|---|---|---|---|
'''
for t in T:
 report+='| '+' + '.join(t['sides'][0])+' vs '+' + '.join(t['sides'][1])+' | '+ ' | '.join(' / '.join(f'{v:.4f}' for v in t[k]) for k in ['before','spacing','extension'])+' |\n'
report+='''
All packages sum player/pick policy values directly. Neutral trade values are strategy-invariant. Competitive fit remains a separate forecast timing quantity, so changing a ranking anchor does not rewrite expected contribution or imply a trade is a guaranteed competitive improvement. Policy ranges are ±15% sensitivity envelopes, not confidence intervals.

No forecasting changes are promoted here, so no new forecast-accuracy claim is made. Previously inspected chronological evidence is preserved and labeled **development evidence**: recent-debut mean shifts had worse low-PA error; prior full-workload candidates failed forecast gates; the separate reliever opportunity candidate improved cached first-year checks but is not merged into this policy audit or described as independent new validation. No fresh historical data collection or recycled holdout certification occurs.

Regression checks cover production byte isolation, all 265 matches, curve monotonicity/continuity, 44 debuted identities, distinct source scopes/no stacking, bounded deviations, omitted identity retention, forecast/scenario separation, exact 14-player model reconstruction and routing, one cohort application/discount per annual path, active estimator metadata, and saved trade-package arithmetic. These tests establish implementation consistency, not calibration of ordinal ranks to actual transactions or future injury recovery. They do not resolve potential implicit availability conservatism.

## Preview and reproduction

Two review calculators reuse the deployed shell, AFL links, scenario displays, historical pitching-stat renderer and removal of doubles/triples columns:

- `/value-audit-preview/spacing/`: spacing-only prospect policy plus corrected explanatory metadata.
- `/value-audit-preview/overall/`: the proposed overall dynasty extension.

`/value-audit-preview/` provides a comparison table and quick additive trade comparison. Open the downloadable complete preview package by extracting it, running `python3 -m http.server 8080` in its folder, then opening `http://localhost:8080/value-audit-preview/`. Local calculators require serving rather than opening individual HTML files because they reuse root-relative deployed assets. The review table itself is self-contained.

Regenerate from committed frozen inputs: `python docs/value-audit-20261012/build_candidate.py`, then `python docs/value-audit-20261012/render_review.py`; run `npm test` and `npm run build`. Exact source model files and hashes are retained for inspection. `export_model_evidence.py <recovered-model-root>` reconstructs diagnostic evidence if the preserved model checkpoint is available; normal candidate regeneration requires only committed frozen evidence and source tables.

Browser interaction has not been verified in this session; the available managed environment lacks the required browser-control skill. Numerical/catalog regressions and the build verify the candidates, with that browser QA limit explicit. No production approval or deployment is implied by a successful preview build.
'''
(D/'Report.md').write_text(report)
# Self-contained review surface, separate from the two unchanged calculator shells.
review='''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>BangaLangin valuation review</title><style>body{font:16px system-ui;background:#07151e;color:#e8f0f3;max-width:1200px;margin:auto;padding:24px}h1{font-size:28px}a{color:#72e0ce}input,select,button{font:inherit;padding:10px;border-radius:6px;background:#122d3b;color:#fff;border:1px solid #416273}table{border-collapse:collapse;width:100%;font-size:14px}td,th{padding:9px;border-bottom:1px solid #36505c;text-align:right}td:first-child,th:first-child{text-align:left}section{background:#0c2430;padding:20px;margin:20px 0;border-radius:12px}.table{overflow:auto}label{display:block;margin:10px 0}.muted{color:#b4c8d0}#trade{font-size:20px}ul{line-height:1.7}</style><h1>BangaLangin Pipeline — valuation review</h1><p>Production stays at <b>4607c16</b>. These candidates change trade-value policy; contribution forecasts stay unchanged.</p><section><b>Recommendation: review the 10% prospect-spacing correction first.</b><p>Exact prospect tie groups: 16 → 0. Total of 265 values: 4712.2394 → 4712.0138. The overall extension has broader effects and remains a policy proposal.</p><p><a href="spacing/">Open spacing calculator</a> · <a href="overall/">Open overall-ranking calculator</a> · <a href="../docs/value-audit-20261012/Report.md">Read full audit</a></p></section><section><h2>Compare values</h2><label>Find a player <input id="search" placeholder="Bradish, Soriano, Keith…"></label><p class="muted">Showing all 648 covered identities. Values are internal points, not observed transaction prices. Source overall ranks and prospect ranks stay distinct.</p><div class="table"><table><thead><tr><th>Player</th><th>Role</th><th>Source scope / rank</th><th>Deployed</th><th>Spacing</th><th>Overall extension</th></tr></thead><tbody id="rows"></tbody></table></div></section><section><h2>Quick trade totals</h2><p>Enter player names separated by commas. This sums the policy values; competitive fit is separate.</p><label>Side A <input id="left" value="Kyle Bradish, Jose Soriano" style="width:min(90%,600px)"></label><label>Side B <input id="right" value="Eury Perez" style="width:min(90%,600px)"></label><label>Policy <select id="policy"><option value="before">Deployed</option><option value="after_spacing">Spacing only</option><option value="after_extension">Overall extension</option></select></label><p id="trade" aria-live="polite"></p></section><section><h2>What the audit found</h2><ul><li>Bradish and Soriano correctly route as starters; stable MLBAM IDs are 680694 and 667755.</li><li>Bradish's interrupted seasons depress initial workload to 123.84 IP. His first-year cohort projection is 101.75 IP.</li><li>Soriano starts at 165.28 IP; his first-year cohort projection is 135.39 IP.</li><li>No extra explicit injury penalty was found. Implicit availability conservatism remains unresolved.</li><li>Inherited career diagnostic fields are separate from the active 30-IP rate pseudocount.</li><li>Source publication dates and league-specific reliever acquisition scarcity are not established.</li></ul></section><script>const DATA=__DATA__;const $=id=>document.getElementById(id);const esc=s=>String(s).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));const num=v=>Number(v).toFixed(2);function render(){const q=$('search').value.toLowerCase();$('rows').innerHTML=DATA.filter(x=>x.name.toLowerCase().includes(q)).map(x=>`<tr><td>${esc(x.name)}</td><td>${esc(x.role)}</td><td>${esc(x.source_scope)} ${x.source_rank}</td><td>${num(x.before)}</td><td>${num(x.after_spacing)}</td><td>${num(x.after_extension)}</td></tr>`).join('')}function sum(s,k){let total=0;for(const name of s.split(',').map(x=>x.trim()).filter(Boolean)){const p=DATA.find(x=>x.name.toLowerCase()===name.toLowerCase());if(!p)return {error:'Player not in this comparison: '+name};total+=Number(p[k])}return {total}}function trade(){const k=$('policy').value,a=sum($('left').value,k),b=sum($('right').value,k);$('trade').textContent=a.error||b.error||`Side A ${num(a.total)} · Side B ${num(b.total)} · B − A ${num(b.total-a.total)}`}$('search').oninput=render;for(const id of ['left','right','policy'])$(id).oninput=trade;render();trade();</script></html>'''.replace('__DATA__',json.dumps(P,separators=(',',':')).replace('</','<\\/'))
(ROOT/'value-audit-preview/index.html').write_text(review);print('Report and self-contained review created')
