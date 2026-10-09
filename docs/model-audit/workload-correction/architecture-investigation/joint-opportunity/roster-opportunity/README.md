# Pipeline first-year hybrid research adapter

Implemented on the research branch only. No production entry point, deployment,
Trade Analyzer implementation, prospect model, or later dynasty reward changed.
The deliverable is an executable first-year adapter and complete league replay.
It is not release-ready: read Hybrid_Release_Gates.json and Repair_Report.md.

## Small practical integration surface

- talent.py: TalentRateForecast exposes preserved independent Pipeline per-unit
  production rates and reconciles them with opportunity. Existing skill data,
  translations and rate aging remain intact; absent Statcast is not invented.
- hybrid.py: HybridForecastEngine produces first-year expected workload and
  role components. One development-selected method per family, saved RP expert.
- engine.py: own appearance/count models, smoothed PA/game and IP/start,
  explicit missing-count flags, dated evidence, capped team-budget allocator.
- integrate.py: multiplies rate and opportunity contracts and changes only the
  first-year utility reward in existing eight-year valuation paths.

Chosen P blend is75% principal joint role/appearance forecast +25% saved repair;
H blend is50% new conditional-mean appearance-equivalent forecast +50% saved
repair. Weights are fixed and selected using ID4 development, not external
forecast values. The separated count learners and other tested candidates
are executable and preserved, including failures; no proprietary code copied.

## Run with the preserved recovery inputs

Use Python with numpy/scipy/scikit-learn/joblib and the existing recovered
model root containing trade-preview-v22/model and the preserved catalog JSON.
From this directory (substitute absolute input locations):

```bash
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 python integrate.py /path/to/recovered/model /path/to/beta-unpacked.json
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 python validate_hybrid.py /path/to/recovered/model /path/to/beta-unpacked.json
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 python independent.py /path/to/recovered/model /path/to/beta-unpacked.json
```

Historical integrated replay intentionally passes preserved incumbent
components. The old parent past-hitter-2019.joblib is empty; do not load it.
Parent artifact remains unchanged. Replay of arbitrary2019 inputs requires
rebuilding that same chronological prior specification separately; the saved
historical comparisons do not require rebuilding it.

Research reproduction order: run.py (final separated-count iteration),
neighbors.py, mean_select.py, hybrid_select.py (preserved router experiment),
simple_select.py (final family blend freeze), integrate.py, validate_hybrid.py,
independent.py. run.py can take several minutes; keep output logs. The final
release gates also include finalize.py's protected-cohort and annual checks.
Each selection stage uses ID4 only. Original ID0 cohorts have been previously
exposed, so these are chronological retrospective checks, not fresh holdouts.
Input SHA manifests and fitted artifacts are included. All99 own fitted model
files were deserialized and verified. Earlier research checkpoints are retained.

## Evidence and scope

Current evidence contains a dated MLB Judge injury report and an observed
Pirates rotation snapshot. Neither is a2027 medical timetable or guaranteed
2027 roster. Injury facts alone do not trigger fabricated missed-game amounts.
Numerical roster allocations require separately labeled expectations and a
team budget ID. Future publications and mismatched target years are rejected.
Team allocations honor player caps and preserve uncovered reserve slots.
Complete historical organizational depth and medical return feeds are missing.
The numerical league replay therefore uses demonstrated usage plus statistical
opportunity, with sparse factual annotations, not a fully covered roster feed.

The19 public ZiPS article comparisons have the same target full season but
January external publication dates versus December own input cutoffs. They are
conditional ZiPS totals, NOT historical RosterResource allocations. They do not
establish a same-day roster-aware accuracy advantage. Public forecasts are
never used as features, targets, or direct substitutes for Pipeline projections.

Large data/model files are packed in Research_Recovery.zip and split under
Stored_Parts for the git checkpoint. restore_checkpoint.py reconstructs and
verifies the archive from all parts without requiring any external forecast
service. Small source and review documents are also directly available in git.
