# Independent international scouting update — November 25, 2026

This update implements the supplied Independent 2027 J15 Talent Re-Rank and handoff. The existing table, profile, filter, navigation, styling and simulator controls are retained. All 86 Pipeline identities are preserved; the simulator now contains the same 86 international profiles (Harris Miller Jackson, Luis Fiallo and Enmanuel Beltre were missing from its research snapshot). These three additions are retained as pending, not automatically draft-eligible.

## Ranking policy and deviations

- Dynasty is the primary displayed Pipeline order. Pure talent, supplied research talent/dynasty, and BA bonus ranks are separate fields. No new visible column or selector was added.
- Oda: supplied dynasty 7 → effective dynasty 5, pure talent 3. The explicit route discount was removed. Sena, Grullon, De La Rosa and Tarifa retain priority for offensive/category value; normal teenage-pitcher health, command and workload attrition remains. No route-dependent score or market penalty is applied.
- Yoel King: omitted from the supplied 58, reviewed from indexed BA scouting. Premium velocity and a starter repertoire justify inclusion; delivery repetition and secondary command keep him below the more complete offensive bets.
- Ashton Hernandez: omitted from the supplied 58, reviewed from indexed BA scouting. Contact, swing decisions and a plausible shortstop route merit placement ahead of less selective lower-board power bets; strength remains the offensive constraint.
- Other omitted profiles were compared on their retained detailed scouting rather than automatically placed last. Recent signees including Raider Sánchez Trutie, Anthony Calderón, Hiroike, Nogami and Harris are integrated as mixed-period comparisons. Their inclusion does not establish 2027 signing class or draft eligibility.
- These insertions shift displayed numbers after the top group. The supplied order remains preserved in researchTalentRank/researchDynastyRank; apart from Oda, its relative dynasty order is unchanged.
- BA’s 50 rank assignments and bonus tiers remain intact. Expected destinations remain projections. More precise existing bonus estimates, domestic/professional values and domestic relative order are preserved.

## Scouting and valuation work

Sixty profiles received the new qualitative research review. Existing detailed scouting is retained, including the richer simulator-only material for Oda, Raider Sánchez, Edenis Cruz and Proenza. No new numerical pitch/tool grades or success percentages were invented. Scouting tiers and confidence are evidence judgments, not probabilities of professional success.

Mixed-FYPD values were reviewed individually on the existing score scale using contact/impact, category fit, positional development, starter repertoire, time and evidence uncertainty. They are not J15 ordinals. Superseded internal BA FYPD forecasts are archived rather than blended back into the new international talent scores. Verified BA bonus rank retains only its existing bounded, manager-dependent publicity effect.

## Eligibility and research gaps

- Yeremy De León: the reported November 25, 2026 San Diego transaction remains recorded. The earlier user-designated 2027 class remains in provenance, but the latest handoff explicitly requires a separate watchlist. Default FYPD inclusion is pending league confirmation; the transaction does not itself establish eligibility.
- Markus Rodriguez: projected CHW destination retained; acquisition-route clearance remains pending. Eudy Alcantara’s expected destination is TEX. Neither is converted into an official signing.
- Morua: January 2027 arrival language conflicts with class terminology; default inclusion pending. Enmanuel Beltre: Perfect Game class does not by itself prove signing/FYPD class; pending. Carlos Adrián Hernández, Proenza and Blanco retain unresolved routes/eligibility.
- Other current-period acquisitions retain their existing reported/official distinctions and eligibility settings unless the new handoff explicitly required a change. Class audit notes distinguish 2027 candidates, recent signees and unresolved routes. Oda remains league-confirmed independently of route.
- Sparse competitive information remains material for Kendry Morales, Morua, Beltre, Carlos Hernández, Proenza, Blanco, Luis García and Enyel González. No missing measurements, birth dates or grades were filled speculatively.

## Validation

- Targeted Pipeline ranking/source/class tests: 11/11 passing. Targeted simulator bonus, Oda, Hiroike and independent synchronization tests: 19/19 passing.
- Pipeline production build passed and retained the evidence registry’s 2,186 player identities.
- Broad suites: Pipeline 317/346 passing (29 failures reproduced on the baseline); simulator 38/50 passing (12 failures reproduced on the baseline). No new failing test names relative to the prior versions. Historical snapshot/count assertions and unrelated existing failures remain disclosed rather than represented as a clean suite.
- Simulator HTML outside the bounded embedded research block is byte-identical to the prior version, verified by SHA-256. No CSS, layout, controls, manager mechanics, team ownership or CPS/OQI files changed. Pipeline presentation code changes only the outdated BA-backbone explanatory sentence.

## International rank comparison

| Prospect | Previous Pipeline | Updated dynasty | Updated talent | Supplied dynasty | BA bonus |
|---|---:|---:|---:|---:|---:|
| Alfredo Sena | 1 | 1 | 1 | 1 | 1 |
| Miguel Grullon | 2 | 2 | 2 | 2 | 2 |
| Mairon De La Rosa | 4 | 3 | 4 | 3 | 4 |
| Jose Tarifa | 21 | 4 | 7 | 4 | 19 |
| Shoki Oda | 6 | 5 | 3 | 7 | — |
| Junior Fortunato | 8 | 6 | 6 | 5 | 7 |
| Camilo Gutierrez | 19 | 7 | 9 | 6 | 17 |
| Jesus Arteaga | 3 | 8 | 5 | 8 | 3 |
| Dylan Rodriguez | 9 | 9 | 8 | 9 | 8 |
| Nicolas Quintero | 11 | 10 | 10 | 10 | 10 |
| Eddy Hernandez | 7 | 11 | 11 | 11 | 6 |
| Joh Sung-chul | 16 | 12 | 12 | 12 | — |
| Antonio Figueroa | 12 | 13 | 13 | 13 | 11 |
| Cesar Montero | 31 | 14 | 14 | 14 | 27 |
| Manuel Hernandez | 32 | 15 | 17 | 15 | 28 |
| Jeiler Blanco | 28 | 16 | 18 | 16 | 25 |
| Michael Prado | 14 | 17 | 19 | 17 | 13 |
| Raider Sánchez Trutie | 23 | 18 | 15 | — | — |
| Snaiker Garcia | 29 | 19 | 16 | 18 | 26 |
| Yasleyker Parra | 27 | 20 | 21 | 19 | 24 |
| Axel Carrasco | 13 | 21 | 20 | 20 | 12 |
| Snafe Alvarez | 24 | 22 | 23 | 21 | 21 |
| Anthony Calderón | 30 | 23 | 24 | — | — |
| Eudi Yuten | 5 | 24 | 25 | 22 | 5 |
| Cristian Oscar Lías Bienemé | 15 | 25 | 26 | 23 | 14 |
| Fernando Marmolejos | 34 | 26 | 27 | 24 | 29 |
| Sebastián Pérez Acuña | 18 | 27 | 22 | 25 | 16 |
| Euniel De La Cruz | 10 | 28 | 29 | 26 | 9 |
| Wilson Reyes | 20 | 29 | 28 | 27 | 18 |
| Kosei Hiroike | 33 | 30 | 30 | — | — |
| Amaurys Martinez | 39 | 31 | 31 | 28 | 32 |
| Markus Rodriguez | 25 | 32 | 32 | 29 | 22 |
| Salamon Millan | 60 | 33 | 33 | 30 | 44 |
| Tatsuya Nogami | 35 | 34 | 34 | — | — |
| Harris Miller Jackson | 38 | 35 | 35 | — | — |
| Jhonn Rodriguez | 47 | 36 | 36 | 31 | 37 |
| Marlon Polanco | 67 | 37 | 37 | 32 | 47 |
| Loryi Pineda | 17 | 38 | 38 | 33 | 15 |
| Moisés Alcalde | 43 | 39 | 40 | — | — |
| William Alejandro Álvarez Landa | 26 | 40 | 41 | 34 | 23 |
| Albert Hernandez | 50 | 41 | 43 | 35 | 39 |
| Boni Guzman | 22 | 42 | 42 | 36 | 20 |
| Angel Rojas | 42 | 43 | 48 | 37 | 34 |
| Breidy Campusano | 64 | 44 | 44 | 38 | 46 |
| Ashton Hernandez | 58 | 45 | 45 | — | 43 |
| Denyer Ramirez | 62 | 46 | 51 | 39 | 45 |
| Cai-Chen Long | 48 | 47 | 46 | — | — |
| Wilver Hernandez | 41 | 48 | 47 | 40 | 33 |
| Erick González | 61 | 49 | 49 | — | — |
| Eyder Orasma | 37 | 50 | 50 | 41 | 31 |
| Yoel King | 49 | 51 | 39 | — | 38 |
| Omar Guerra | 53 | 52 | 52 | — | — |
| Leandri Benitez | 70 | 53 | 53 | 42 | 48 |
| Edenis Cruz | 55 | 54 | 56 | — | — |
| Eudy Alcantara | 54 | 55 | 57 | 43 | 41 |
| Alexis Liriano | 44 | 56 | 58 | 44 | 35 |
| Raymer Moreno | 57 | 57 | 54 | — | — |
| Yirvel Figuereo | 52 | 58 | 55 | 45 | 40 |
| Jose Muñiz | 36 | 59 | 59 | 46 | 30 |
| Rodelvis Santiesteban | 59 | 60 | 60 | — | — |
| Jendry Gonell | 73 | 61 | 61 | 47 | 49 |
| Amaurys Dilon | 56 | 62 | 62 | 48 | 42 |
| Luis Advincola | 76 | 63 | 64 | 49 | 50 |
| Luis Fiallo | 63 | 64 | 65 | — | — |
| Kendry Morales | 45 | 65 | 66 | 50 | — |
| Yonewris Garcia | 68 | 66 | 67 | — | — |
| Enmanuel Beltre | 51 | 67 | 68 | 51 | — |
| Yeferson Sanchez | 46 | 68 | 63 | 52 | 36 |
| Cayro Hazel | 69 | 69 | 69 | — | — |
| Márkó Morua | 40 | 70 | 70 | 53 | — |
| Jhonny Damon Proenza | 71 | 71 | 72 | 54 | — |
| Carlos Adrián Hernández | 65 | 72 | 71 | 55 | — |
| Luis García | 74 | 73 | 74 | 56 | — |
| Alayn Daniel Blanco | 72 | 74 | 73 | 57 | — |
| Enyel González | 75 | 75 | 75 | 58 | — |
| Yeremy De León | 66 | 76 | 76 | — | — |
| Orangel Guanaguaney | 77 | 77 | 77 | — | — |
| Luis Zapata | 78 | 78 | 78 | — | — |
| Lenyert Rios | 79 | 79 | 79 | — | — |
| Alexis Medina | 80 | 80 | 80 | — | — |
| Keddy Roa | 81 | 81 | 81 | — | — |
| Sebastian Zorrilla | 82 | 82 | 82 | — | — |
| Maykoll Jaspe | 83 | 83 | 83 | — | — |
| Elvin Cepeda | 84 | 84 | 84 | — | — |
| Manuel Cordero | 85 | 85 | 85 | — | — |
| Windel Encarnacion | 86 | 86 | 86 | — | — |

## Mixed FYPD board changes

The ranks below are the actual displayed model board ranks under default settings, including its existing treatment of excluded records. They are model values, not observed ADP. Absolute domestic ranks can move when international players move around them; their relative order and individual scores are unchanged.

| Prospect | Before FYPD | After FYPD | Before score | After score | Default eligible |
|---|---:|---:|---:|---:|---|
| Alfredo Sena | 12 | 12 | 13.31 | 13.30 | Conditional/yes |
| Miguel Grullon | 29 | 21 | 24.48 | 18.90 | Conditional/yes |
| Mairon De La Rosa | 30 | 22 | 24.98 | 19.50 | Conditional/yes |
| Jose Tarifa | 34 | 24 | 27.48 | 20.20 | Conditional/yes |
| Shoki Oda | 25 | 27 | 21.60 | 20.80 | Conditional/yes |
| Junior Fortunato | 38 | 36 | 30.00 | 28.40 | Conditional/yes |
| Camilo Gutierrez | 107 | 38 | 74.93 | 29.60 | Conditional/yes |
| Jesus Arteaga | 89 | 45 | 64.80 | 32.80 | Conditional/yes |
| Dylan Rodriguez | 114 | 46 | 77.50 | 34.90 | Conditional/yes |
| Nicolas Quintero | 61 | 49 | 45.70 | 36.70 | Conditional/yes |
| Eddy Hernandez | 149 | 55 | 90.70 | 39.20 | Conditional/yes |
| Joh Sung-chul | 94 | 60 | 70.20 | 41.70 | Conditional/yes |
| Antonio Figueroa | 45 | 63 | 33.47 | 44.30 | Conditional/yes |
| Cesar Montero | 170 | 64 | 101.00 | 46.60 | Conditional/yes |
| Manuel Hernandez | 172 | 70 | 103.00 | 49.10 | Conditional/yes |
| Jeiler Blanco | 60 | 74 | 44.67 | 51.80 | Conditional/yes |
| Michael Prado | 128 | 77 | 82.00 | 53.30 | Conditional/yes |
| Raider Sánchez Trutie | 90 | 99 | 65.90 | 65.90 | Pending/excluded |
| Snaiker Garcia | 206 | 79 | 120.00 | 54.70 | Conditional/yes |
| Yasleyker Parra | 59 | 83 | 43.73 | 56.10 | Conditional/yes |
| Axel Carrasco | 144 | 86 | 88.20 | 57.90 | Conditional/yes |
| Snafe Alvarez | 87 | 89 | 62.89 | 59.60 | Conditional/yes |
| Anthony Calderón | 74 | 81 | 55.50 | 55.50 | Pending/excluded |
| Eudi Yuten | 117 | 92 | 78.52 | 61.20 | Conditional/yes |
| Cristian Oscar Lías Bienemé | 80 | 96 | 59.10 | 63.80 | Conditional/yes |
| Fernando Marmolejos | 43 | 98 | 32.22 | 65.70 | Conditional/yes |
| Sebastián Pérez Acuña | 217 | 101 | 138.20 | 67.90 | Conditional/yes |
| Euniel De La Cruz | 169 | 104 | 100.50 | 70.30 | Conditional/yes |
| Wilson Reyes | 81 | 111 | 59.73 | 72.20 | Conditional/yes |
| Kosei Hiroike | 98 | 108 | 71.00 | 71.00 | Conditional/yes |
| Amaurys Martinez | 115 | 116 | 77.66 | 74.10 | Conditional/yes |
| Markus Rodriguez | 180 | 124 | 108.00 | 76.50 | Pending/excluded |
| Salamon Millan | 190 | 126 | 112.00 | 78.40 | Conditional/yes |
| Tatsuya Nogami | 101 | 112 | 72.40 | 72.40 | Conditional/yes |
| Harris Miller Jackson | New record | 138 | — | 81.50 | Pending/excluded |
| Jhonn Rodriguez | 181 | 135 | 109.00 | 80.80 | Conditional/yes |
| Marlon Polanco | 203 | 141 | 119.00 | 82.10 | Conditional/yes |
| Loryi Pineda | 184 | 148 | 110.00 | 84.60 | Conditional/yes |
| Moisés Alcalde | 147 | 160 | 89.60 | 89.60 | Pending/excluded |
| William Alejandro Álvarez Landa | 157 | 154 | 96.40 | 86.90 | Conditional/yes |
| Albert Hernandez | 197 | 158 | 116.00 | 88.80 | Conditional/yes |
| Boni Guzman | 195 | 162 | 114.00 | 90.60 | Conditional/yes |
| Angel Rojas | 176 | 165 | 107.00 | 92.70 | Conditional/yes |
| Breidy Campusano | 214 | 166 | 128.00 | 94.30 | Conditional/yes |
| Ashton Hernandez | 204 | 167 | 120.00 | 95.40 | Conditional/yes |
| Denyer Ramirez | 199 | 170 | 117.00 | 96.80 | Conditional/yes |
| Cai-Chen Long | 142 | 155 | 87.40 | 87.40 | Pending/excluded |
| Wilver Hernandez | 210 | 177 | 123.00 | 98.90 | Conditional/yes |
| Erick González | 119 | 129 | 80.00 | 80.00 | Conditional/yes |
| Eyder Orasma | 183 | 182 | 110.00 | 101.20 | Conditional/yes |
| Yoel King | 212 | 184 | 124.00 | 102.10 | Conditional/yes |
| Omar Guerra | 104 | 115 | 74.00 | 74.00 | Pending/excluded |
| Leandri Benitez | 215 | 185 | 128.00 | 103.50 | Conditional/yes |
| Edenis Cruz | 95 | 105 | 70.50 | 70.50 | Pending/excluded |
| Eudy Alcantara | 211 | 189 | 124.00 | 105.80 | Conditional/yes |
| Alexis Liriano | 202 | 191 | 119.00 | 107.60 | Conditional/yes |
| Raymer Moreno | 110 | 121 | 76.00 | 76.00 | Pending/excluded |
| Yirvel Figuereo | 207 | 194 | 120.00 | 109.80 | Conditional/yes |
| Jose Muñiz | 205 | 200 | 120.00 | 112.10 | Conditional/yes |
| Rodelvis Santiesteban | 152 | 164 | 92.20 | 92.20 | Pending/excluded |
| Jendry Gonell | 209 | 204 | 123.00 | 114.50 | Conditional/yes |
| Amaurys Dilon | 216 | 207 | 133.00 | 116.80 | Conditional/yes |
| Luis Advincola | 213 | 210 | 127.00 | 119.10 | Conditional/yes |
| Luis Fiallo | New record | 213 | — | 125.70 | Pending/excluded |
| Kendry Morales | 208 | 211 | 120.40 | 121.80 | Conditional/yes |
| Yonewris Garcia | 139 | 152 | 86.00 | 86.00 | Conditional/yes |
| Enmanuel Beltre | New record | 212 | — | 124.60 | Pending/excluded |
| Yeferson Sanchez | 182 | 214 | 109.00 | 127.30 | Pending/excluded |
| Cayro Hazel | 161 | 174 | 98.20 | 98.20 | Pending/excluded |
| Márkó Morua | 192 | 215 | 112.60 | 130.70 | Pending/excluded |
| Jhonny Damon Proenza | 141 | 216 | 87.00 | 133.40 | Pending/excluded |
| Carlos Adrián Hernández | 153 | 217 | 94.60 | 136.20 | Pending/excluded |
| Luis García | 154 | 218 | 95.00 | 139.10 | Conditional/yes |
| Alayn Daniel Blanco | 150 | 219 | 91.00 | 142.60 | Pending/excluded |
| Enyel González | 164 | 220 | 99.00 | 145.30 | Conditional/yes |
| Yeremy De León | 129 | 140 | 82.00 | 82.00 | Pending/excluded |
| Orangel Guanaguaney | 173 | 186 | 104.20 | 104.20 | Pending/excluded |
| Luis Zapata | 175 | 188 | 105.40 | 105.40 | Pending/excluded |
| Lenyert Rios | 177 | 190 | 107.00 | 107.00 | Conditional/yes |
| Alexis Medina | 179 | 193 | 108.00 | 108.00 | Conditional/yes |
| Keddy Roa | 188 | 198 | 111.00 | 111.00 | Conditional/yes |
| Sebastian Zorrilla | 186 | 196 | 110.20 | 110.20 | Pending/excluded |
| Maykoll Jaspe | 189 | 199 | 111.40 | 111.40 | Pending/excluded |
| Elvin Cepeda | 191 | 201 | 112.60 | 112.60 | Pending/excluded |
| Manuel Cordero | 194 | 203 | 113.80 | 113.80 | Pending/excluded |
| Windel Encarnacion | 196 | 205 | 115.00 | 115.00 | Pending/excluded |

## Production-engine draft audit

Ran 10,000 before and 10,000 after complete 60-pick drafts with seed 20261125, the same production engine, League Realism settings and the same Shea selection policy. Distinct drafts: 10,000 before / 10,000 after. International selections per draft: 9.16 → 11.48. Every selected player was eligible and each draft contained 60 unique selections. These are conditional model scenarios, not measured league ADP. Comparisons include changed eligibility as well as scouting, so they are not an isolated causal BA-publication experiment.

ADP is conditional on being selected within the first 60 picks; undrafted outcomes are censored. Availability means not selected before that pick, averaged over all runs. Confidence in source evidence does not imply certainty in these estimates.

| Prospect | Before ADP | After ADP | Before available at 32 | After available at 32 | Before selected | After selected |
|---|---:|---:|---:|---:|---:|---:|
| Alfredo Sena | 13.6 | 13.6 | 0.0% | 0.0% | 100.0% | 100.0% |
| Miguel Grullon | 30.0 | 23.9 | 25.0% | 0.3% | 100.0% | 100.0% |
| Mairon De La Rosa | 31.9 | 26.1 | 54.2% | 1.6% | 100.0% | 100.0% |
| Jose Tarifa | 36.0 | 28.1 | 95.2% | 7.5% | 100.0% | 100.0% |
| Shoki Oda | 23.8 | 23.9 | 1.2% | 2.6% | 100.0% | 100.0% |
| Junior Fortunato | 39.7 | 37.2 | 99.9% | 98.9% | 100.0% | 100.0% |
| Camilo Gutierrez | — | 40.8 | 100.0% | 100.0% | 0.0% | 100.0% |
| Jesus Arteaga | — | 44.8 | 100.0% | 100.0% | 0.0% | 100.0% |
| Dylan Rodriguez | — | 48.0 | 100.0% | 100.0% | 0.0% | 100.0% |
| Cesar Montero | — | 59.6 | 100.0% | 100.0% | 0.0% | 0.3% |

Full per-player availability at picks 8, 14, 18, 32, 35, 38, 43, 56 and 58, selection rates and 10th–90th-percentile selection ranges are stored in the simulator’s data/independent-j15-before.json and data/independent-j15-after.json audit files. The existing Decision Lab calculates recommendations with the updated pool and shared engine.

Oda’s score improves from 21.6 to 20.8 even though his overall ordinal moves from 25 to 27: other amateurs also improved. This movement is not a route penalty.

## Source provenance

Primary bonus/scouting reference for the two omitted BA prospects: [Ben Badler, Baseball America, November 25, 2026](https://www.baseballamerica.com/stories/2027-mlb-international-prospects-top-50-bonus-board/), indexed text because direct access is blocked. The supplied independent research and implementation handoff are the authoritative evaluation inputs; original profile source links remain attached. [FanGraphs’ November 6 Asia update](https://blogs.fangraphs.com/scouting-players-from-asia-2026-2027-offseason-update/) supplies a separate first-round-caliber comparison for Oda.
