# Prospect arrival timing audit — October 13, 2026

## Finding and release decision

Morales's 2027 calculator ETA is an inherited Pipeline snapshot input, not the published ETA in the linked scouting evidence. The existing website evidence sidecar already records FanGraphs 2030. Its independently sourced display was never connected to the calculator's frozen trajectory. Current MLB Pipeline lists 2029. Both contradict the calculator's 2027 assumption.

Morales turned 20 on September 22, 2026; he spent most of this season at 19. Highest verified level remains A+. Age alone does not determine ETA.

Sources checked October 13:
- https://www.mlb.com/milb/prospects/dodgers — Morales, MLBAM 815896, A+, ETA 2029.
- https://www.fangraphs.com/players/emil-morales/sa3023887/stats/batting — ETA 2030.
- https://blogs.fangraphs.com/los-angeles-dodgers-top-52-prospects/ — dated December 5, 2025; Morales ETA 2030. The article explains that ETA generally follows 40-man/Rule 5 roster timing. That is a further reason not to equate it with regular MLB production.

The exact upstream assignment procedure for the inherited Pipeline 2027 field is not preserved in the inspected inputs. No claim that FanGraphs supplied 2027, or that a particular default generated this field, is justified.

## Population audit

All 267 prospect-only catalog forecasts were joined by stable Fantrax ID to existing dated ETA evidence. 218 have traceable published ETAs; 49 do not. 28 disagree with the model ETA. See Audit.json for every player, including mismatches in both directions. These are saved-source comparisons, not a claim that all 218 sources were independently refreshed today. An initial low-level screening found 23 A/A+ prospects assigned 2027, but level alone is not proof their ETA is wrong.

The wider defect is in revised.py prospect_paths: the model builds historical paths aligned to first regular exposure (250 PA for hitters, 40 IP for pitchers), then sets their first year equal to the player's ETA. It removes the historical arrival lag and does not model the individual interval between debut and regular playing time. Bust outcomes and zero seasons remain in the historical paths; they do not fix the erroneous calendar alignment. It also borrows censored later trajectory means. Current MiLB level is not a numerical arrival input.

model_asset_fit.py competitive applies normalized eight-year timing weights (.75 contender, .88 neutral/balanced, .94 rebuild). These weights are not the defect. They emphasize Morales's erroneously early production. His archived production baseline is 28.2835, contender 28.3782; the actual contender increase is only 0.335%. His ranking-led dynasty value is 20.2116. Culpepper's mean-preserving debut forecast is a different calculation: production baseline 15.8011, contender 16.5724 (+4.881%), ranking-led dynasty value 21.5959. The comparison of trade value with fit was misleading even before this timing defect.

## Corrective behavior

Prospect-only competitive point estimates are withheld from live trade calculations until debut and regular-role timing are calibrated separately. This applies consistently to all 267 prospect-only assets, not just Morales or the low-level screening list. Neutral dynasty values, rankings, MLB forecasts and fits, pitcher diagnostics, ownership and all historical archives remain intact. Recently debuted hybrid forecasts are not given a new arrival delay: they already have positive MLB evidence and their restored scouting distribution preserves the MLB expected mean.

A prospect's selected card says fit unavailable; its breakdown explains why and shows traceable published ETAs. The old annual production chart, first-year arrival-dependent probabilities and assumption envelope are no longer presented as current prospect forecasts. Mixed packages display a known subtotal with an explicit incomplete status; net fit, fit envelope and near-term production conclusions are withheld. Missing fit is not zero value. The guard works even if the timing evidence module fails to load.

Conditional sensitivity tables shift the existing annual trajectory to a published ETA plus illustrative zero-, one- and two-year delays to regular playing time. No delay probabilities, preferred scenario or new injury/arrival model are invented. For source ETAs earlier than the frozen trajectory, scenarios are omitted because missing earlier production cannot be reconstructed. The fixed 2027–2034 horizon is retained, so postponement removes production beyond 2034 rather than extending the horizon.

For Morales, published anchors 2029 and 2030 yield contender scores 14.8 and 10.3 if regular-role production begins in that anchor year. Adding illustrative delays yields 10.3/6.8 and 6.8/4.3 respectively. These are conditional model sensitivities, not a new fair-value range or validated expected fit, and are excluded from totals. No central replacement for 28.4 is published.

## Validation and remaining work

Regression checks cover every prospect, unchanged packed catalog, actual calculator missing-value aggregation, source joins, zero pre-arrival years, normalized timing reconstruction, fixed horizon and rendered disclosures. Run npm test and npm run build. Browser verification is recorded separately after deployment.

A calibrated replacement requires historical snapshots with separately defined debut, first regular season, delayed arrival and non-arrival outcomes; chronological evaluation and censoring-aware treatment; and level/age/opportunity inputs validated before adoption. This release fixes the unsupported live conclusions by withdrawing them. It does not claim that a new individual arrival probability model has been trained. Existing archived model code remains preserved as evidence and is not re-run to generate active prospect fits.
