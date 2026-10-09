# Documented principles and their implementation

FanGraphs, January28 2026, All the 2026 Projections Are In:
https://blogs.fangraphs.com/all-the-2026-projections-are-in/
Depth Charts averages Steamer and ZiPS talent rates and prorates them to
RosterResource playing time. ZiPS DC also applies RosterResource allocations.
Steamer600 normalizes talent; its200IP/600PA are not player workload promises.
Pipeline implements independent appearance opportunity and per-appearance
work; it does not import FanGraphs numbers as model features or forecasts.

FanGraphs Depth Charts tutorial:
https://library.fangraphs.com/how-to-use-fangraphs-depth-charts/
Documented manual allocations account for depth, lineup and injuries. Pipeline
now accepts explicitly dated facts and team appearance budgets separately
from statistical talent. Missing organization/medical evidence stays unknown.
A player cannot receive both an unconditional count and another absence
penalty. Team budgets normalize opportunity and never impose player floors.

ZiPS author's2026 introduction:
https://blogs.fangraphs.com/the-2026-zips-projections-are-almost-here/
Basic ZiPS totals do not predict actual MLB roster playing time. Public team
article totals therefore remain conditional-talent benchmarks, not evidence
that a roster allocator is accurate. The exact proprietary model is unknown.

ATC author's methodology:
https://fantasy.fangraphs.com/the-atc-projection-system/
ATC combines projections with weights informed by past accuracy; exact weights
are not available. Pipeline tests its own fixed blend using development-only
selection. No ATC weights or code copied, and no independent forecast enters
training. A crowd can outperform a single playing-time source; architecture
alone does not establish accuracy:
https://fantasy.fangraphs.com/2022-projection-accuracy-hitter-playing-time/

Steamer author's update and public schema:
https://blogs.fangraphs.com/instagraphs/steamer-projections-updated/
https://steamerprojections.com/index.php/about/glossary
Documented distinctions include role, lineup positions and context-neutral
rates versus contextual totals. Exact regressions are not reproduced. No
membership tables or restricted archive accessed.

Marcel author's public overview:
https://www.tangotiger.net/marcel/
Recent-season weighting, regression and age adjustments are documented. Our
usage baseline is independently estimated from preserved chronological core
records; it is not labeled an implementation of Marcel's unpublished details.

## Concrete causes being corrected
The previous robust active-workload learner used absolute-error loss, which
estimates a conditional median. Multiplying it by participation probability
does not produce a statistical mean. A season's small exposure conflated
healthy role with missed opportunity. Hitter games played were absent from
the shared feature vector despite being present in preserved career skills.
The new layer recovers those counts, smooths PA/game or IP/start, and learns
future appearances separately. Participation is a nonzero-MLB event, NOT a
medical-health label. Conditional appearances still include partial seasons;
a separate medical cap is only applied to explicit dated evidence.

Remaining evidence limits: historical team depth and injury return timetables
are not comprehensive. Cached injury placements do not establish future
missed games. We do not invent clinical return dates or use today's roster
for historical backtests. Full roster-aware production certification requires
those feeds; current outputs state missing evidence explicitly.
