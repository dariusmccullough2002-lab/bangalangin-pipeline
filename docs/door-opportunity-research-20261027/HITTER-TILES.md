# Hitter tile sample checkpoint — October 27, 2026

Requested: display a useful sample instead of tiny promotion stints; Walcott AFL specifically; replace hitter K%/HR emphasis with more useful hitting stats.

Implemented: AVG / OBP / SLG as primary metrics; PA / HR / SB underneath. Pitcher metrics and profile chapter metrics stay separate. Regular-season selection uses highest level with >=40 PA, then prior-season highest substantial level if no 2026 sample qualifies. Small higher-level sample is disclosed with PA and, when verified, AB. No rates are averaged.

Official raw per-player/per-level season responses saved in Hitter_Sample_Responses.json. Run python scripts/build-door-hitter-samples.py offline to reproduce data/door-hitter-samples.json; --refresh explicitly requests official data. All 2026 queried PA/K/HR/SB totals checked against existing frozen level counts. 22 hitters covered. OBP uses (H+BB+HBP)/(AB+BB+HBP+SF); AVG H/AB and SLG TB/AB. Teamless totals preferred; otherwise unique team splits summed.

Four brief-promotion cases: Walcott regular fallback AA171PA but tile uses separately dated AFL snapshot when available; Sirota AA333PA; Willits A+289PA; Miller 2025AA489PA with 2026AA11PA/10AB note. Walcott highest AAA9PA/8AB; Sirota AAA9PA/6AB; Willits AA17PA/14AB. Fall and regular-season counts never combine.

AFL counts come from the shared dated data/afl/full-2026.json snapshot and continue to follow that data’s existing refresh process. No new claim of live tile refresh. If optional sample/AFL inputs fail, cards remain usable; missing OBP is displayed as unavailable rather than invented.

Checks: 7 focused tests passed for exact sample source/season, threshold40 inclusive, no fabricated AB/OBP, Walcott AFL fallback, all22 hitters and compact-card/filter/member gating. Build passed. Live deploy/desktop/mobile verification pending.
