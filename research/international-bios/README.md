# International bio research — November 3, 2026

Reviewed all 47 current board players. Filled 27 previously empty data fields (10 nations, 14 measurements, 3 handedness fields). Four nation entries previously displayed through renderer fallbacks. Normalized Carlos Adrián Hernández’s existing 1.85 m report so it displays correctly. Rankings, order, scouting, signing periods, agreements and organizations are unchanged.

Measurements are reported listings, not measurements taken by Pipeline. Historical roster sizes may have changed. Metric conversions display approximately in feet/inches and pounds. The profile now links its measurement source and displays dated limitations.

## Recovered measurements

| Player | Listed measurement | Evidence date / qualification |
|---|---|---|
| Raider Sánchez Trutie | 183 cm, 81 kg | [2025–26](https://es.scribd.com/document/996973804/Reglamento-64-SNB); Historical Santiago de Cuba listing under Raider Abel Sánchez Trutie; 81 kg, 1.83 m. Reproduced federation document, not a current MLB measurement. Former catcher identity matches reporting; current OF designation retained. |
| Márkó Morua | 6' 0", 175 lb | [2025-09-04](https://www.xeudeportes.mx/beisbol/1386491/marko-morua-primer-jugador-hungaro-en-firmar-en-grandes-ligas); Historical reported measurements, not a current official measurement. The article’s Padres signing narrative is superseded; it does not change the current organization or signing status. |
| Kendry Morales | 6' 2", 170 lb | [2026-10-15](https://www.laprensani.com/2026/10/15/deportes/3799844-prospecto-nicaraguense-firma-medias-rojas); Reported measurements for the 16-year-old Nicaraguan outfielder linked to Boston; not the former Cuban MLB player. |
| Cai-Chen Long | 178 cm, 80 kg | [2025](https://blackpanthercup.tw/2025桃園市立平鎮高級中等學校/); Historical school roster for 蔡辰瀧 (Tsai Cheng-lung / Cheng-Lung Tsai). Official roster lists 80 kg; an unofficial 2026 compilation lists 85 kg, not independently confirmed. Historical roster weight retained. |
| Erick González | 6' 0", 162 lb | [2026-08-18](https://www.laprensani.com/2026/08/18/deportes/3765250-erick-gonzalez-prospecto-nicaraguense-yanquis); Reported measurements for the Belén, Rivas right-hander linked to the Yankees for January 2027. |
| Luis García | 178 cm, 75 kg | [2024](https://static.wbsc.org/uploads/federations/0/documents/23ec3b36-73e0-2c0f-03f7-c9f467f77586.pdf); Historical Nicaragua tournament listing for Luis Leonidas García Otero; current reporting identifies the same 2024 U-15 participants. Not a new measurement; adolescent size may have changed. |
| Enyel González | 178 cm, 79 kg | [2024](https://static.wbsc.org/uploads/federations/0/documents/23ec3b36-73e0-2c0f-03f7-c9f467f77586.pdf); Historical Nicaragua tournament listing for Enyel Joel González Ramírez; current reporting identifies the same 2024 U-15 participants. Not a new measurement; adolescent size may have changed. |

## Remaining gaps

No sufficiently reliable identity-matched evidence was recovered for these fields. This is a search limitation, not proof that no public listing exists. No values were inferred from photographs, position, nationality or throwing arm.

| Player | Unverified fields |
|---|---|
| Eudi Yuten | height, weight |
| Cristian Oscar Lías Bienemé | height, weight |
| Anthony Calderón | weight |
| Moisés Alcalde | height, weight, bats |
| Wilson Reyes | height, weight |
| Sebastián Pérez Acuña | height, weight |
| Omar Guerra | height, weight, bats, throws |
| Edenis Cruz | weight |
| Raymer Moreno | height, weight, bats |
| Carlos Adrián Hernández | weight, bats |
| Yeremy De León | height, weight, bats |
| Jhonny Damon Proenza | height, weight, bats, throws |
| Alayn Daniel Blanco | weight, bats |

## Reproducibility

`python research/international-bios/update-2026-11-03.py` applies the sourced bio update. `2026-11-03.json` records every board player, gaps before/after and field-level evidence. Existing measurements are retained except the documented display normalization. Country evidence comes from the indexed Baseball America October 5 player headings; direct access returned 403.

Identity checks rejected similarly named older professionals, unrelated school athletes, Natanael Yuten and Márkó’s brother Martin. Reproduced Cuban roster evidence was limited to public baseball attributes; personal identification numbers were not retained.

Validation: measurement tests pass and production build succeeds. Seven existing assertions in the older international-additions/November-review tests fail identically on the unchanged starting commit (obsolete ranks, player counts, date and country list). They were not rewritten to conceal those baseline failures.

## Subsequent author confirmation — November 3, 2026

The Pipeline author personally confirmed Eudi Yuten at 5 ft 11 in / 185 lb, Cristian Oscar Lías Bienemé at 6 ft 0 in (weight still unverified), and Moisés Alcalde at 6 ft 2 in / 180 lb. These five filled fields are recorded as author-confirmed, not independently roster-verified. The earlier JSON report above remains the original research snapshot; its unresolved-field list predates this follow-up.
