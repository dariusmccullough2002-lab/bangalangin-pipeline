Run from repository recovery root:

```bash
PYTHONDONTWRITEBYTECODE=1 OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 "$CODEX_PRIMARY_RUNTIME_PYTHON" pipeline/docs/model-audit/workload-correction/architecture-investigation/joint-opportunity/workload-root-cause/audit.py recovered/model recovered/beta-unpacked.json
"$CODEX_PRIMARY_RUNTIME_PYTHON" pipeline/docs/model-audit/workload-correction/architecture-investigation/joint-opportunity/workload-root-cause/summarize.py
```

Requires preserved checkpoint data/models and compatible Python/scikit-learn. No fit method is invoked. Reports reproduce the frozen export; they do not modify forecast artifacts. Full numbered source trace and SHA256 manifest are included. CSV units are PA or decimal innings. Empty branch values are genuinely not applicable, never filled as fabricated zeros.
