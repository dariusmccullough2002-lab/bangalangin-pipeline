# Offline foundational calibration checkpoint

Read `Foundational_Calibration_Review.md` first. **Not ready for production or Phase 2.** No live code, player data, rankings, rosters, archives or transactions are altered by these research scripts.

This successor builds on research/historical-calibration-phase1-2026-10-08 (f80d9b5355ce370f76987d65e6aee29d4a1787dc), and the preserved U2 research. The new directory is research/calibration/foundational-2026-10-08. The successor branch is research/foundational-calibration-2026-10-08. Its sole change outside research is a branch-specific deployment-disabled rule in vercel.json; main is unchanged. Never merge this research branch as a production implementation.

## Saved outputs

- protocol.json: frozen outcome/validation specification and pre-final addendum.
- results/trained-model-freeze.json: training identities, coefficients, scalers and freeze receipt before final labels.
- results/prospect-calibration.json: model comparisons, paired confidence intervals, probability bands and exact final predictions.
- results/delayed-arrival-diagnostic.json and empirical-tail-ranges.json: separate five/seven-year outcomes and conservative empirical tail ranges.
- results/source-publication-audit.json: primary article dates, inherited date limitations, feature cutoff audit.
- results/qa3-coverage.json and verification.json: exact game-level QA3, QS difference, source reconciliation and boundary checks.
- results/fixed-roster-contexts.json, weekly-category-diagnostics.json and eligibility-context-sensitivity.json: hypothetical fixed roster category contributions and separate replacement deltas.
- results/ledger-and-narrative-checks.json and trade-explanation-examples.json: offline four-ledger contract and requested owner explanations; the Josuar example uses saved U2, not a new verdict.
- results/production-check.json: unchanged production formula hash and observed main/deployment identifiers.
- input-source-manifest.json: hashes and scope of replay and full collected source snapshots.

## Replaying without data recollection

Use Python 3.12 and the versions in requirements.txt. Extract the existing sibling `phase1-2026-10-08/raw-data.zip` into that directory. Extract this package's `replay-inputs.zip` in this directory; it creates raw/. Run scripts only if deliberately reproducing this checkpoint, not when doing a recovery inspection.

```bash
python calibrate_prospects.py
python uncertainty_diagnostics.py
python weekly_diagnostics.py
python context_sensitivity.py
python explanations.py
python ledger_contract.py
python make_review.py
```

These analysis commands require the sibling Phase1 results. `historical_features.py` supports the original local phase1-calibration name and the repository phase1-2026-10-08 name. `make_review.py` reads saved verification/QA3 results. The 2020 cohort is now exposed: replay is reproducibility verification, not a new untouched validation, and must not be used to select/tune a model. The 2021 reserve remains unevaluated.

The replay archive preserves exact selected MLB/MiLB rows, game inputs, stable identities plus ambiguous name candidates, ordinal rankings and grade tables. MiLB source audits quote the full collection, whose SHA256 is preserved; unrelated rows are omitted from replay. Generated game inputs retain the 2018/2024 weekly contexts, prior eligibility positions, all 2010–2025 annual QA3 summaries and cohort biographies. The full original game/source caches remain in the original workspace; the large public Retrosheet ZIPs are not duplicated in Git.

`parse_rankings.py` and `identities.py` can rebuild the factual extraction/identity stage from the replay archive. Expressive scouting prose is excluded. `collect_games.py`, `collect_weeks.py`, `collect_register.py`, `collect_minor.py`, `build_games.py` and `check_inputs.py` support full-source collection/reconciliation, which is not necessary for the analysis replay. Full-source collection requires the corresponding public responses and Retrosheet ZIPs; compact replay alone is deliberately insufficient to rerun the complete 63,027-pair source audit. Preserve the saved audit and source hashes rather than calling a filtered archive a full-source recollection.

## Attribution

The information used here was obtained free of charge from and is copyrighted by Retrosheet. Interested parties may contact Retrosheet at 20 Sunset Rd., Newark, DE 19711.

Ranking/scouting facts originate from the dated FanGraphs articles linked in the methodology/source audit; MLB outcomes and holds from MLB StatsAPI; stable MLBAM/Retrosheet identity keys from the Chadwick Bureau register. Source-date and completeness limitations are documented; no archive evidence or career completion status is invented.
