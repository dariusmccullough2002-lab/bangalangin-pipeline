# Valuation-priorities audit

Offline research; no numerical valuation changes are deployed by this commit. Production warning UI was released separately in cbba516.

Run from repository root with Node and Python (numpy, scipy, scikit-learn):

```sh
node scripts/audit-valuation-priorities.mjs
python scripts/audit-neutral-scale.py
python scripts/audit-bench-sensitivity.py
node scripts/audit-pick-timing.mjs
node --test tests/valuation-review.test.js
```

Use the committed Frozen_Inputs.json.gz for reproduction. The optional --freeze switch requires a freshly built dist and deliberately replaces the frozen catalog; do not use it to reproduce this run.

The copied common.py and rostermodel.py under reference are the supplied audit optimizer. The bench wrapper documents its explicit eligibility and calendar-path changes. No bench coefficient was calibrated.

Scale agreement tests failed; no automatic common-scale repricing was approved. The catalog review module labels missing ranking coverage and close uneven packages without changing asset prices. See CHECKPOINT.md for exact findings, limitations and pending browser/roster checks.
