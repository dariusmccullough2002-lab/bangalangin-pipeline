# Readable trade summary — October 24, 2026

Follow-up request: keep both strategy scores, but make the explanation readable without numbers or technical language. Put detailed calculations behind a “For more details” control.

The shared result now shows short team summaries: which return the calculator prefers for the selected plan, supported hitter strengths, overall dynasty tradeoff and a plain uncertainty statement. It uses the same selected assets, active values and forecasts as the detailed calculation; no scoring changes. The shared details disclosure contains the full neutral ledger, numeric reasoning, tables, forecast evidence, technical caveats and original model output. Closed by default; keyboard accessible; expansion persists when selections update. Structured downloads include both plain summaries and original detailed explanations.

Verification: static build and JS syntax pass. 26 targeted checks pass (13 explanation checks, 8 shared-forecast checks, 5 conditional-prospect checks). Live browser checks follow publication.

Live verification complete: code commit `63055c8474177fe5030de45c6c1e7b3eb31351aa`, production deployment `dpl_J7kNhsUE5MZd1LTYRk3NCRyxK3B1` READY with public alias assigned. Browser confirmed both scores remain unchanged, only plain prose appears initially, details opens the complete neutral ledger and calculations, switching contender/rebuild changes the plain recommendation, and the open details control stays expanded through updates. Restored contender example with details collapsed for handoff. No valuation changes.
