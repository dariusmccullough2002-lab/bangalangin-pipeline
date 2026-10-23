# Vargas–Naylor underlying-trend research checkpoint

Status: research and offline tests complete; production unchanged. Read Report.md and Backtest.json first.

Question: Do recent skill changes support the production model's heavy Vargas regression and Naylor rebound? Compare year-to-year expected quality, power, discipline and stolen-base contribution. Separate observed 2026 evidence, counterfactual sensitivity and actual prediction validation. Do not tune a correction to obtain a preferred player order.

Baseline live code release: shared-quality-forecast-20261023, source commit 547074ccb04203fc637d0314a37d6d678bc617e8; recovery documentation commit 90300945a5a72b249f64902de6fd9410ea7ca500. Vargas neutral44.5051 / contender34.0302; Naylor neutral33.4593 / contender35.4988. Existing correction is a bounded sensitivity bridge, not a validated new talent forecast.

Sources: Baseball Savant MLBAM678246 and647304 profiles; Kodo public player endpoints with those IDs. Freeze downloaded responses under `inputs/`, retain hashes, source dates and discrepancies. Kodo describes MLB Stats API and Baseball Savant as upstream data sources, so agreement is cross-checking, not independent evidence.

Completed: 31 frozen public source files; Savant/Kodo quality reconciliation; annual trends and monthly swing data; equal-opportunity category decomposition; a predeclared 934-training/775-test retrospective rate backtest (381 test players), excluding both named players. Training-selected 25% quality weight improved held-out AVG MAE 3.36%, SLG MAE 1.07%, but worsened breakout-group SLG MAE about9%. Decline-group SLG MAE improved about4.9%. Do not hide the failed breakout generalization.

Important new context: MLB documented Naylor's wrist surgery and expected spring-training recovery. Kodo's null injury fields / false on_il did not capture that information. Poor injured-season power does not establish permanently poor healthy talent.

Resume: no need to repeat downloads or player scans. `python analyze.py` uses the supplied frozen inputs and reproduces all results. Full annual/category-win prediction and injury-conditioned recovery probabilities remain blocked. The existing production bridge remains unchanged. A future implementation should evaluate a shared component-rate forecast and explicit health scenarios; do not tune to flip Vargas/Naylor.
