# Full-season starter display preview

Preview application commit: `5d7bdb86021ad90fd132836af2cb70ca66bfa895`.
Deployment: `dpl_5v6nt3Mgw8rtDfsnaaWJeHXG9Ued` (preview, READY).
URL: https://bangalangin-pipeline-gwwjppfxx-shea-stadiums.vercel.app/trade-analyzer-beta/
Vercel authentication applies. The authorized temporary access link is supplied in the delivery message; no access credential is committed.

Open Trade Analyzer, select Island on Side A, add Paul Skenes, then click his name in the selected package to open the detail. Full-season scenario is the default statistical view. Expected-season projection is a separate button. Switches only update this panel's DOM.

## Sources and scope

The 211 demonstrated starters reuse the preserved fitted full-role starts/relief appearances and innings from `full-workload-scenario`, verified against the unchanged pitcher scenarios in research checkpoint `de28a48022fd204944b9fe3697fbfd2ac5cbfc3b`. These are historical high-usage proxies interpreted as conditional role scenarios, not models trained on clinically verified uninterrupted availability. That limitation is visible on every supported scenario. No outcome probabilities or rejected expected-workload predictions are adopted.

Other 62 players with legacy SP labels have demonstrated swingman (61) or reliever (1) usage and keep their existing displays. Hitter, RP and two-way display routes remain unchanged. Prospects with no established MLB rotation evidence retain arrival/outcome information. Unsupported numerical scenarios explicitly report unknown starts and innings rather than invented totals.

The secondary expected-season view uses the existing website V2.3C identity-prior guard catalog's first-year projection, supplied by the V2.3 recent-performance estimator and inherited aging path. It does not substitute the preserved research benchmark or five-state/direct candidates. Starts are labeled not exported by that model; they are not reverse-engineered from innings.

## Counting-stat calculation

Let I be the saved scenario innings and B the existing first-year projection. K, ER, H and BB equal `B[stat] * I/B.IP`. Thus `ERA = 9*ER/IP` and `WHIP = (H+BB)/IP` are exactly unchanged between the views. No talent, aging or probability adjustment is added.

QA3 uses the exact preserved starts/performance mechanism from `full-workload-scenario/run.py:307–331`, replayed from the pre-allocation conditional components. It is `min(I/5, GS*qSP + reliefAppearances*qRP)`, where the q terms are the saved conditional QA3 appearance yields, not conventional-QS rates or a blanket IP multiplier. QA3 qualification is at least 5 IP and at most 2 ER, OR at least 6 IP and at most 3 ER. Each exported QA3 exactly reproduces the saved full-role statistic before display.

Incidental relief appearances from the preserved fitted scenario remain explicit. Saves/holds cannot exceed that opportunity; a scenario with no relief appearances has zero saves and holds. This display-only feasibility bound changes no valuation quantity.

## Data-flow isolation

Research tables → reproducible exporter → `data/starter-display-scenarios.json` → `starter-display.js` → detail-panel DOM.

The display adapter copies the existing expected line; it never writes the embedded catalog, application state, storage, trade aggregates or value functions. The embedded catalog remains byte-identical across all 2,546 assets. The entire embedded app differs only at the projection-rendering hook. Rankings, replacement inputs, talent formulas, years 2–8, production expected workloads and trade calculations remain identical. `starter-display-isolation.json` contains the hash proof and unchanged-file inventory.

## Verification

65 tests pass; static build passes. Added checks execute every supported adapter against a recursively frozen catalog, assert ERA/WHIP identity, workload feasibility, exact QA3 boundaries and preserved fallback routes. Skenes QA3 is 21.2722, different from a blind IP-scaled 21.4384.

Chromium desktop and the existing responsive review at 390px and 320px were checked. Effective content widths are 375px and 305px after scrollbars. Tables scroll inside the panel, without page overflow. Browser checks cover Skenes, Wheeler, Bradish, Misiorowski and unsupported prospect Jamie Arnold. Visible valuation grids remain identical while switching; static isolation proves all catalog valuations unchanged. Cal Quantrill's demonstrated swingman display, Raisel Iglesias' RP display and Matt Olson's hitter display remain unchanged. Safari/Firefox and physical mobile devices were not tested.

Skenes: 32.4 assumed starts, 182.6 IP, 202.1 K, 21.3 QA3; expected secondary 165.3 IP. Wheeler: 31.4 starts, 188.3 IP, 214.4 K, 20.1 QA3. Bradish: 31.9 starts/169.6 IP; Misiorowski: 31.4 starts/174.3 IP. These are illustrations, not calibration targets or valuation inputs.

Before/after screenshots are preserved in `starter-display-screenshots/`. The mobile screenshots show the actual responsive application in the existing width-controlled review iframe, not a device mockup.

Production remains at `81cda32efc4ddc42bdae003e83f950a6d66bf129`. Only the preview branch is updated. No production deployment or research-model alteration occurred.
