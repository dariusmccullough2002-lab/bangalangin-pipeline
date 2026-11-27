# Site-wide scouting-grade audit — November 27, 2026

Audited 1335 profile records across eight sections. Records overlap where the same player appears in multiple sections; counts are not unique-player totals. 437 records gained published-grade coverage. No rankings, league eligibility, existing scouting estimates, or performance statistics were recalculated. Archive grade-only identity associations were added without changing stored archive player records.

| Section | Records | Previous published coverage | Published coverage now | Existing Pipeline estimates | No numerical grade available |
|---|---:|---:|---:|---:|---:|
| archive | 355 | 0 | 277 | 0 | 78 |
| rankings | 260 | 242 | 254 | 6 | 0 |
| draft | 114 | 1 | 106 | 8 | 0 |
| j15 | 86 | 0 | 0 | 64 | 22 |
| dsl | 46 | 19 | 26 | 19 | 1 |
| winter | 193 | 18 | 39 | 0 | 154 |
| afl | 265 | 117 | 132 | 126 | 7 |
| professionals | 16 | 0 | 0 | 16 | 0 |

## Changes

- Archive profiles now use the same compact grade cards as other profiles. Historical rankings stay unchanged. Grades are available matched source records, not asserted to have been part of the August snapshot. Archive identities use explicit current-profile IDs or unique exact normalized names. The two ambiguous Luis names additionally require matching organization and pitcher/hitter identity; unresolved collisions are not guessed.
- Public MLB Pipeline report data was checked across all 30 organizational boards plus the Draft board. The collector found 1,061 report records; unique MLBAM identities, selected report year, grade labels and exact profile source URLs are retained. Organizational reports take priority over draft reports within the newly collected source. Existing cached FanGraphs/AFL/individual published grades retain priority.
- New published records are shared by draft, AFL, winter, DSL, ranked and archive profiles through MLBAM identity; no copied per-section grading dataset is maintained.
- Published grades now carry a source/date disclosure. Present/future pairs continue displaying the future value. Unpublished pitches are no longer filled with heuristic numerical grades inside a published-source card. Source-only FV remains visible even if no tool grades were supplied. MLB Pipeline's generic Power grade is labeled Power; it is not relabeled as two independently measured raw/game-power grades.
- Existing Pipeline projections/estimates remain available, clearly labeled as estimates. Their numerical inputs are unchanged. Kona's individually reviewed card retains its own rationale. J15 internal estimates remain internal; no external grades are fabricated.
- Profiles without reviewed numerical evidence remain ungraded. Published-source absence is not a poor-talent grade. This audit does not claim to have obtained every paywalled or unpublished evaluation.

## Verification

The audit renders every covered record and fails on suppressed published grades, invalid values or broken output. Regression tests cover identity matching, cross-section consistency, source-only FV, source labels and keeping unavailable grades blank. Production build passed; 20 targeted tests passed. The full suite completed with 324/354 passing and 30 failures, compared with 31 failures reproduced on the baseline. No new failing test names were introduced. A live mobile browser was unavailable, so responsive CSS was preserved and no mobile visual verification is claimed.

## Historical professional references

Four undated FanGraphs indexed-board FV references (Taira, Takahashi, Moinelo and Carter Stewart) are retained in separate disclosures. Direct page access returned 403, so these are labeled historical indexed references and do not replace reviewed Pipeline estimates or claim current tool grades. Takahashi’s Pipeline FV 45 and the older indexed FanGraphs FV 35+ remain explicitly distinct.

## Remaining gaps

The accompanying JSON lists every record's coverage state and source link. These records have no numerical grades in the sources reviewed for this audit:

| Section | Player | ID |
|---|---|---|
| archive | Cooper Pratt | cooper-pratt |
| archive | Jeferson Quero | jeferson-quero |
| archive | Blade Tidwell | blade-tidwell |
| archive | Dylan Beavers | dylan-beavers |
| archive | Jake Bennett | jake-bennett |
| archive | Shane Drohan | shane-drohan |
| archive | T.J. Rumfield | t-j-rumfield |
| archive | Walbert Urena | walbert-urena |
| archive | Angel Genao | angel-genao |
| archive | Connor Prielipp | connor-prielipp |
| archive | Hyeseong Kim | hyeseong-kim |
| archive | Joe Mack | joe-mack |
| archive | Jordan Lawlar | jordan-lawlar |
| archive | Luisangel Acuna | luisangel-acuna |
| archive | Marcelo Mayer | marcelo-mayer |
| archive | Tommy Troy | tommy-troy |
| archive | Troy Melton | troy-melton |
| archive | Coleman Crow | coleman-crow |
| archive | Bryce Eldridge | bryce-eldridge |
| archive | Christian Moore | christian-moore |
| archive | Darell Hernaiz | darell-hernaiz |
| archive | Gavin Collyer | gavin-collyer |
| archive | Hurston Waldrep | hurston-waldrep |
| archive | Ian Seymour | ian-seymour |
| archive | Logan Henderson | logan-henderson |
| archive | Luis Morales | luis-morales |
| archive | Nick Yorke | nick-yorke |
| archive | Ryan Waldschmidt | ryan-waldschmidt |
| archive | Troy Johnston | troy-johnston |
| archive | Wade Meckler | wade-meckler |
| archive | Sean Keys | sean-keys |
| archive | Abimelec Ortiz | abimelec-ortiz |
| archive | Chase Burns | chase-burns |
| archive | Chase Dollander | chase-dollander |
| archive | DJ Herz | dj-herz |
| archive | Eduardo Valencia | eduardo-valencia |
| archive | Erik Sabrowski | erik-sabrowski |
| archive | Gabriel Hughes | gabriel-hughes |
| archive | Hao-Yu Lee | hao-yu-lee |
| archive | Jack Perkins | jack-perkins |
| archive | Joe Boyle | joe-boyle |
| archive | Mitch Jebb | mitch-jebb |
| archive | Shane Smith | shane-smith |
| archive | Zac Veen | zac-veen |
| archive | CJ Hughes | cj-hughes |
| archive | Clayton Beeter | clayton-beeter |
| archive | Deyvison De Los Santos | deyvison-de-los-santos |
| archive | Lucas Ramirez | lucas-ramirez |
| archive | Tristan Peters | tristan-peters |
| archive | Tyler Black | tyler-black |
| archive | J.R. Ritchie | j-r-ritchie |
| archive | Tyson Hardin | tyson-hardin |
| archive | Yohandy Morales | yohandy-morales |
| archive | Leanders Matos | leanders-matos |
| archive | Edwin Arroyo | edwin-arroyo |
| archive | George Lombard Jr. | george-lombard-jr |
| archive | Tommy White | tommy-white |
| archive | Adrian Del Castillo | adrian-del-castillo |
| archive | Billy Amick | billy-amick |
| archive | Jonatan Clase | jonatan-clase |
| archive | Kyren Paris | kyren-paris |
| archive | Otto Kemp | otto-kemp |
| archive | Ryan Bliss | ryan-bliss |
| archive | Tim Elko | tim-elko |
| archive | Carson Williams | carson-williams |
| archive | Kevin Alcantara | kevin-alcantara |
| archive | Kyle Karros | kyle-karros |
| archive | Ronny Mauricio | ronny-mauricio |
| archive | Thomas Saggese | thomas-saggese |
| archive | Jonah Tong | jonah-tong |
| archive | Kendry Rojas | kendry-rojas |
| archive | Ben Joyce | ben-joyce |
| archive | Edgardo Henriquez | edgardo-henriquez |
| archive | Fran-Jean Haseth | fran-jean-haseth |
| archive | Gage Jump | gage-jump |
| archive | Mason Montgomery | mason-montgomery |
| archive | Hagen Smith | hagen-smith |
| archive | Easton Shelton | easton-shelton |
| j15 | Raider Sánchez Trutie | raider-sanchez-trutie |
| j15 | Anthony Calderón | anthony-calderon |
| j15 | Ashton Hernandez | ashton-hernandez |
| j15 | Omar Guerra | omar-guerra |
| j15 | Rodelvis Santiesteban | rodelvis-santiesteban |
| j15 | Kendry Morales | kendry-morales |
| j15 | Enmanuel Beltre | enmanuel-beltre |
| j15 | Cayro Hazel | cayro-hazel |
| j15 | Márkó Morua | marko-morua |
| j15 | Jhonny Damon Proenza | jhonny-damon-proenza |
| j15 | Luis García | luis-garcia-nicaragua-2027 |
| j15 | Enyel González | enyel-gonzalez |
| j15 | Orangel Guanaguaney | orangel-guanaguaney |
| j15 | Luis Zapata | luis-zapata |
| j15 | Lenyert Rios | lenyert-rios |
| j15 | Alexis Medina | alexis-medina |
| j15 | Keddy Roa | keddy-roa |
| j15 | Sebastian Zorrilla | sebastian-zorrilla |
| j15 | Maykoll Jaspe | maykoll-jaspe |
| j15 | Elvin Cepeda | elvin-cepeda |
| j15 | Manuel Cordero | manuel-cordero |
| j15 | Windel Encarnacion | windel-encarnacion |
| dsl | Leanders Matos | 837864 |
| winter | Adolfo Oviedo | 801743 |
| winter | Adrian Rodriguez | 703641 |
| winter | Agustin Acosta | 802528 |
| winter | Ahbram Liendo | 699157 |
| winter | Alan Espinal | 694541 |
| winter | Alberto Mota | 699215 |
| winter | Aldo Gaxiola | 815220 |
| winter | Alejandro Hidalgo | 691576 |
| winter | Alejandro Urias | 703060 |
| winter | Alexis Hernandez | 692562 |
| winter | Alfred Morillo | 801219 |
| winter | Allan Castro | 691369 |
| winter | Amilcar Chirinos | 702847 |
| winter | Andrés Nolaya | 800438 |
| winter | Angel Hernandez | 805097 |
| winter | Angel Ortiz | 691292 |
| winter | Angel Perez | 823862 |
| winter | Angel Ramirez | 807587 |
| winter | Antonio Jimenez | 806128 |
| winter | Antonis Macias | 805950 |
| winter | Augusto Mendieta | 800078 |
| winter | Bryan Gonzalez Garcia | 811314 |
| winter | Carlos Colmenarez | 694181 |
| winter | Carlos Espinosa | 800514 |
| winter | Carter Trice | 807714 |
| winter | Chris Arroyo | 701360 |
| winter | Christian Cerda | 692416 |
| winter | Christian Lopez | 809326 |
| winter | Christian Olivo | 700840 |
| winter | Colton Becker | 813851 |
| winter | Cooper Kinney | 695692 |
| winter | Cristian Alvarado | 800079 |
| winter | Cristofer Gomez | 805684 |
| winter | Daniel Corniel | 802192 |
| winter | Daniel Nunez | 805982 |
| winter | Dayan Frias | 682679 |
| winter | Diego Rosa | 828227 |
| winter | Diego Velasquez | 694196 |
| winter | Douglas Orellana | 702878 |
| winter | Dylan Jasso | 815734 |
| winter | Eddinson Paulino | 682796 |
| winter | Edgar Lugo | 814812 |
| winter | Elwis Mijares | 808274 |
| winter | Emanuel Hernandez | 842386 |
| winter | Emmanuel Reyes | 800539 |
| winter | Esmerlin Vinicio | 691263 |
| winter | Fabian Bonilla | 834843 |
| winter | Felipe De La Cruz | 700370 |
| winter | Fernando Peguero | 800387 |
| winter | Francisco Pazos | 802387 |
| winter | Frank Rodriguez | 684491 |
| winter | Gabriel Rosado | 815531 |
| winter | Gerardo Lopez | 825751 |
| winter | Gerardo Salas | 692401 |
| winter | Gerelmi Maldonado | 698965 |
| winter | Giovanni Vargas | 808133 |
| winter | Gregori Louis | 805774 |
| winter | Gustavo Melendez | 828116 |
| winter | Hedbert Perez | 691616 |
| winter | Heriberto Caraballo | 812430 |
| winter | Ichiro Cano | 802560 |
| winter | Inmer Lobo | 800308 |
| winter | Irving Cota | 806522 |
| winter | Ismael Agreda | 697795 |
| winter | J.D. Gonzalez | 806083 |
| winter | Jaime Ferrer | 695634 |
| winter | Javier Rivas | 691922 |
| winter | Jayson Bass | 814188 |
| winter | Jean Cabrera | 691893 |
| winter | Jesus Castillo | 691913 |
| winter | Jesus Gamez | 804966 |
| winter | Jesus Hernandez | 698929 |
| winter | Jesus Mendez | 805079 |
| winter | Jesús Broca | 695871 |
| winter | Jheremy Vargas | 691621 |
| winter | Jhon Gil | 830459 |
| winter | Joel Ibarra | 684169 |
| winter | Johan Moreno | 808052 |
| winter | Johan Simon | 696059 |
| winter | John Bay | 700083 |
| winter | Jorge Hernandez | 808702 |
| winter | Jorge Ruiz | 702409 |
| winter | Jorhan Castro | 835729 |
| winter | Jose Astudillo | 698973 |
| winter | Jose G. Gonzalez | 696035 |
| winter | Jose Gonzalez | 683681 |
| winter | Jose Guedez | 803247 |
| winter | Jose Ledesma | 702874 |
| winter | Jose Olivares | 699276 |
| winter | Jose Ortiz | 806176 |
| winter | Josh Trentadue | 815048 |
| winter | Juan Carela | 683636 |
| winter | Juan Cruz | 809397 |
| winter | Keiner Delgado | 700731 |
| winter | Kelly Austin | 675502 |
| winter | Leonard Garcia | 692623 |
| winter | Lizandro Espinoza | 692371 |
| winter | Luis Cohen | 800324 |
| winter | Luis Hernandez | 801346 |
| winter | Luis Suisbel | 692044 |
| winter | Luis Velasquez | 686433 |
| winter | Luke Stofel | 814477 |
| winter | Magnus Ellerts | 701884 |
| winter | Manuel Olivares | 683416 |
| winter | Marco Vargas | 804614 |
| winter | Marvin Alcantara | 800421 |
| winter | Mauricio Estrella | 800442 |
| winter | Maxwell Romero Jr. | 686912 |
| winter | Melkis Hernández | 800292 |
| winter | Michael Arias | 683522 |
| winter | Milan Tolentino | 675455 |
| winter | Moises Palma | 800457 |
| winter | Nelson Quiroz | 685716 |
| winter | Nestor Lorant | 686544 |
| winter | Nestor Rios | 701980 |
| winter | Orlando Gonzalez | 701432 |
| winter | Oswaldo Osorio | 800424 |
| winter | Pascanel Ferreras | 814299 |
| winter | Poncho Ruiz | 695000 |
| winter | Raimon Gomez | 703148 |
| winter | Ramiro Dominguez | 823719 |
| winter | Randal Diaz | 695538 |
| winter | Randel Clemente | 695003 |
| winter | Ricardo Cova | 699698 |
| winter | Ricardo Estrada | 698962 |
| winter | Ricardo Gonzalez | 800357 |
| winter | Richard Gallardo | 682620 |
| winter | Robert Moore | 691001 |
| winter | Roberto Campos | 691449 |
| winter | Ronald Hernandez | 698933 |
| winter | Roque Gutierrez | 692262 |
| winter | Rosman Verdugo | 698916 |
| winter | Roynier Hernandez | 800281 |
| winter | Ryan Cermak | 688714 |
| winter | Sabin Ceballos | 694754 |
| winter | Samir Chires | 698968 |
| winter | Sandy Gaston | 682624 |
| winter | Saul Garcia | 702903 |
| winter | Saul Teran | 699703 |
| winter | Sean Barnett | 826141 |
| winter | Steven Pérez | 682897 |
| winter | Stiven Cruz | 691602 |
| winter | Trent Youngblood | 827636 |
| winter | Victor Garcia | 806625 |
| winter | Wilian Bormie | 693781 |
| winter | Won-Bin Cho | 800231 |
| winter | Wuilfredo Antunez | 686404 |
| winter | Yael Romero | 806873 |
| winter | Yahil Melendez | 806161 |
| winter | Yamal Encarnacion | 699043 |
| winter | Yasmil Bucce | 698935 |
| winter | Yeison Morrobel | 694218 |
| winter | Yonatan Henriquez | 800257 |
| winter | Yorman Gómez | 691414 |
| afl | Sam Horn | 802413 |
| afl | Aaron Davenport | 702126 |
| afl | Kyle Scott | 815066 |
| afl | Juan Bello | 805694 |
| afl | Randy Rodríguez | 678495 |
| afl | Harrison Feinberg | 695664 |
| afl | Williams Salazar | 816266 |
