# First-year workload repair implementation

This research implementation continues9b411d231e895fb43dd99906158c564ec8879766. It is not deployed or release-ready. `Repair_Report.md` gives results and blockers; `Release_Gates.json` records the decision.

`engine.py` implements a callable `FirstYearForecastEngine`. The pitcher active-conditional opportunity expert and hitter robust directPA expert replace first-year workload, retaining calibrated role/absence probabilities and coherent conditional opportunity components. Shared/hierarchical/appearance/specialist alternatives are fitted and saved. No player IDs/names enter regression features or routing. Capacity, age, recent/durable exposure, role and interruptions remain distinct predictors. Verified debutMLB/MiLB evidence is inherited unchanged. Counting stats retain inherited talent rates/rate-aging, except exactQA3 appearance logic. Expected workload receives no second absence/age/attrition multiplier. Picks/prospects/unsupported/two-way forecasts stay frozen.

## Recovery and replay
The executable sources and small result files are stored directly here. All fitted models and complete forecast/case tables are also stored in the verified split `Research_Recovery.zip` archive under `Stored_Parts`. Run `python restore_checkpoint.py` in this folder to restore it without overwriting differing files. Parent archives have their own restore scripts; restore required parent artifacts first. Supply the recovered verified model package and frozen catalog from the earlier checkpoint as ROOT and CAT; no new collection is performed.

Run from repository root (substitute actual ROOT and CAT paths):

```sh
python docs/model-audit/workload-correction/architecture-investigation/joint-opportunity/first-year-repair/develop.py ROOT CAT
python docs/model-audit/workload-correction/architecture-investigation/joint-opportunity/first-year-repair/validate.py ROOT CAT
python docs/model-audit/workload-correction/architecture-investigation/joint-opportunity/first-year-repair/rbi_rate.py ROOT CAT
python docs/model-audit/workload-correction/architecture-investigation/joint-opportunity/first-year-repair/current.py ROOT CAT
python docs/model-audit/workload-correction/architecture-investigation/joint-opportunity/first-year-repair/independent.py ROOT CAT
python docs/model-audit/workload-correction/architecture-investigation/joint-opportunity/first-year-repair/finalize.py ROOT CAT
```

Dependencies: Python3.12, numpy, scipy, scikit-learn1.8.0, joblib, threadpoolctl and the preserved source/model inputs. `Runtime_Manifest.json` records actual versions. Development scripts recompute all predeclared candidates on IDs4; regression fitting uses IDs1/2/3. ID0 is never fit. Freeze occurs before new test predictions. Previously exposed benchmark outcomes remain retrospective checks, not pristine confirmation. Replaying is reproduction, not permission to retune against ID0.

The saved output includes `First_Year_Supported_MLB.csv` (1900rows), `First_Year_All_Assets.csv` (2546rows), `Current_League.json.gz`, `Representative_Forecasts.csv`, `Cohort_Metrics.csv`, `Original_Starter_Diagnostics.csv`, `Validation.json`, development and selection freezes, chronological manifests, RBI development/test cases and a limited independent sample. All competitive modes and neutral ranks are included. Primary valuation is first-year-only bounded workload sensitivity; conditional opportunity utility/future-role-floor outputs are separate sensitivity columns. Years2–8 are frozen; new joint dynasty uncertainty is not claimed.

Next engineering work should be a new, predeclared development-only experiment specified in `Engineering_Blockers.json`, followed by genuinely reserved confirmation. Do not change this freeze or relabel its failed original-starter gate as a pass.
