# Shared research forecast checkpoint — October 23, 2026

Status: implementation and publication build verified; deployment pending.

## Request

Use the same supported underlying talent evidence in contender and rebuilding forecasts. Keep dynasty rankings as the primary neutral valuation, with bounded research deviations. Do not tune to make Vargas/Naylor or any other named trade produce a preferred result.

## Confirmed cause

`docs/research-layer-20261013/build.py` builds verified, coherent rate lines from the Pipeline forecast, a single FanGraphs ensemble family, and Kodo expected quality. Its historical release intentionally leaves `competitive_values`, annual projections, and contribution paths unchanged. Consequently the current strategy fit ignores that research while neutral dynasty price includes a bounded adjustment.

Frozen evidence: `docs/research-layer-20261013/{Comparison.json,Evidence.json,inputs/}`. Model category references, dispersions and replacement floors: `docs/value-audit-20261012/inputs/model-evidence.json`. Annual statistics and uncertainty states are already in the packed analyzer catalog.

Baseline: Vargas neutral 44.505072206, contender 31.718857734; Naylor neutral 33.459323332, contender 35.622228184. Naylor + Peña for Vargas gives about -2.1 neutral and -12.0 contender fit. Those are diagnostics, not target outcomes.

## Implementation plan

1. Validate saved evidence identity, dates, role, exposure and rate coverage.
2. Apply a bounded, disclosed rate correction to the same annual MLB stat paths for every strategy. Preserve playing time, eligibility, pick paths and existing age/attrition assumptions.
3. Recompute coherent statistics, category contribution and uncertainty from those paths, then apply each strategy's existing time weights.
4. Keep neutral dynasty prices unchanged; expose provenance and forecast adjustments in player details and exports.
5. Test identity failures, missing evidence, no-op evidence, physical statistics, common paths, package symmetry, and the broad catalog; record before/after results.
6. Build and deploy the reviewed change to the existing Vercel project, retaining earlier safeguards and draft corrections.

## Resume

Repository: `/workspace/scratch/8fdddaaf5501/model-release` (dirty changes from earlier authorized releases must be preserved). Existing build uses `scripts/integrate-model-safeguards.mjs`; integrate the new shared forecast before rendering. Latest known production commit `828d61ace2d549f2008930d8df64fae3e9b050d4`. Vercel project `prj_PD98X8Xzj0hOX9oHJXuh9jpTJjun`, team `team_xSQbS7lnhn0g6zVi1ebsZ9lT`.

## Completed implementation and findings

The compact production catalog does **not** retain full annual statistic/state paths. Therefore this release uses a transparent bounded trajectory bridge rather than claiming to refit those unavailable paths. `shared-forecast.js` adjusts the first projection's H/TB using validated xBA/xSLG, or ER using validated expected ERA. Quality has the existing research family's 10% maximum weight, shrunk by reconciled exposure using the active forecast's 100-PA/30-IP pseudocount. A 10% contribution departure cap is a disclosed policy limit; rate weight is reduced when necessary so adjusted statistics and the bounded contribution factor agree.

The new versus old projected category surplus defines one contribution factor, applied to all saved annual utility years and all strategy values/ranges. Existing aging, availability, PA/IP and strategy time discounts remain fixed. This is an approximate sensitivity overlay, **not** a validated forecast-accuracy gain or a reconstructed annual component/state model. Unsupported elite exceedance probabilities are withheld and displayed as unavailable. No barrel, whiff, xwOBA or health bonus is stacked on the same expected-quality family.

The saved ZiPS/Steamer rows lack an explicit forward season/publication date; they remain contextual benchmarks and do not enter this forward correction. Neutral dynasty prices retain their existing ranking-dominated research policy. Prospect, hybrid and two-way paths remain unchanged because an isolated supported adjustment is unavailable.

- Usable adjustments: 341 / 2,546 assets; 2,205 retained.
- Neutral dynasty prices changed: 0.
- Vargas contribution factor: 1.0728693223; contender 31.7189 → 34.0302; rebuild 27.5756 → 29.5850.
- Naylor contribution factor: 0.9965353295; contender 35.6222 → 35.4988; rebuild 27.8103 → 27.7139.
- The remaining contender difference is inherited projection/category weighting. No desired named-trade outcome was imposed.

## Verification and reproducibility

`node --test tests/shared-forecast.test.js tests/space-sensitivity.test.js tests/conditional-prospect-fit.test.js tests/prospect-timing.test.js tests/model-safeguards.test.js tests/draft-rules-correction.test.js tests/trade-narrative.test.js tests/research-layer.test.js` — **52/52 pass**.

`node scripts/build.js /tmp/bangalangin-shared-forecast-20261023` — passed; retains the earlier safeguards, shared slot-cost sensitivity, conditional prospect timing and 17-round correction.

`node scripts/audit-shared-forecast.mjs` writes the complete before/after catalog, saved trades, input hashes and blocked checks to `shared-research-forecast-20261023-results.json`. The compressed copy is committed for durable recovery. The original frozen inputs and baseline HTML remain in the repository and are hash-identified in the report.

Outstanding validation: chronological testing needs historical expected-quality snapshots, which the saved evidence does not contain. Browser verification and deployment ID are to be recorded after publication. Full-repository historical failures were not reclassified as fixed by this targeted release.
