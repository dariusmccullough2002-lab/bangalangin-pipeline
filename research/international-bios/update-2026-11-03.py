"""Reproduce the sourced bio-only update; run from the repository root."""
import copy
import json
from pathlib import Path

path = Path('data/international/2027.json')
data = json.loads(path.read_text())
before = copy.deepcopy(data)
players = {p['id']: p for p in data['players']}
retrieved = '2026-11-03'
changes = []

def evidence(pid, fields, source, url, date, note):
    p = players[pid]
    entry = dict(fields=fields, source=source, sourceUrl=url, sourceDate=date,
                 retrievedDate=retrieved, note=note)
    p.setdefault('bioEvidence', [])
    if entry not in p['bioEvidence']:
        p['bioEvidence'].append(entry)

ba = 'https://www.baseballamerica.com/stories/10-top-names-to-watch-in-the-2027-mlb-international-signing-class/'
countries = {'alfredo-sena':'Dominican Republic','mairon-de-la-rosa':'Dominican Republic',
 'miguel-grullon':'Dominican Republic','junior-fortunato':'Dominican Republic',
 'nicolas-quintero':'Venezuela','jesus-arteaga':'Venezuela','dylan-rodriguez':'Venezuela',
 'axel-carrasco':'Dominican Republic','eddy-hernandez':'Dominican Republic',
 'euniel-de-la-cruz':'Dominican Republic'}
for pid, country in countries.items():
    players[pid]['country'] = country
    evidence(pid, ['country'], 'Baseball America', ba, '2026-10-05',
             'Country stated in indexed player heading; direct article access returned 403. Existing identity and scouting match.')

def physical(pid, height, source, url, date, note, weightLb=None, weightKg=None):
    p=players[pid]
    m=p.get('measurements') or {}
    m.update(height=height, source=source, sourceUrl=url, sourceDate=date,
             retrievedDate=retrieved, notes=note)
    if weightLb is not None: m['weightLb']=weightLb
    if weightKg is not None: m['weightKg']=weightKg
    p['measurements']=m
    evidence(pid, ['height','weight'], source, url, date, note)

physical('kendry-morales', "6' 2\"", 'La Prensa',
 'https://www.laprensani.com/2026/10/15/deportes/3799844-prospecto-nicaraguense-firma-medias-rojas',
 '2026-10-15', 'Reported measurements for the 16-year-old Nicaraguan outfielder linked to Boston; not the former Cuban MLB player.', weightLb=170)
physical('erick-gonzalez-nicaragua-2027', "6' 0\"", 'La Prensa',
 'https://www.laprensani.com/2026/08/18/deportes/3765250-erick-gonzalez-prospecto-nicaraguense-yanquis',
 '2026-08-18', 'Reported measurements for the Belén, Rivas right-hander linked to the Yankees for January 2027.', weightLb=162)
physical('marko-morua', "6' 0\"", 'XEU Deportes',
 'https://www.xeudeportes.mx/beisbol/1386491/marko-morua-primer-jugador-hungaro-en-firmar-en-grandes-ligas',
 '2025-09-04', 'Historical reported measurements, not a current official measurement. The article’s Padres signing narrative is superseded; it does not change the current organization or signing status.', weightLb=175)
wbsc='https://static.wbsc.org/uploads/federations/0/documents/23ec3b36-73e0-2c0f-03f7-c9f467f77586.pdf'
for pid, weight, identity in [('luis-garcia-nicaragua-2027',75,'Luis Leonidas García Otero'),('enyel-gonzalez',79,'Enyel Joel González Ramírez')]:
    physical(pid, '178 cm', 'WBSC 2024 U-15 Baseball World Cup roster', wbsc,
     '2024', f'Historical Nicaragua tournament listing for {identity}; current reporting identifies the same 2024 U-15 participants. Not a new measurement; adolescent size may have changed.', weightKg=weight)
cai='https://blackpanthercup.tw/2025桃園市立平鎮高級中等學校/'
physical('cai-chen-long', '178 cm', 'Black Panther Cup official Pingzhen roster', cai,
 '2025', 'Historical school roster for 蔡辰瀧 (Tsai Cheng-lung / Cheng-Lung Tsai). Official roster lists 80 kg; an unofficial 2026 compilation lists 85 kg, not independently confirmed. Historical roster weight retained.', weightKg=80)
players['cai-chen-long']['bats']='R'
players['cai-chen-long']['aliases']=list(dict.fromkeys(players['cai-chen-long'].get('aliases',[])+['Tsai Cheng-lung','Cheng-Lung Tsai','蔡辰瀧']))
evidence('cai-chen-long',['bats','throws'], 'Black Panther Cup official Pingzhen roster',cai,'2025','Roster lists R/R. Identity linked through the Blue Jays Nation alias and CNA Taiwan U-18 reporting.')
raider='https://es.scribd.com/document/996973804/Reglamento-64-SNB'
physical('raider-sanchez-trutie','183 cm','64th Cuban National Series roster (reproduced document)',raider,
 '2025–26', 'Historical Santiago de Cuba listing under Raider Abel Sánchez Trutie; 81 kg, 1.83 m. Reproduced federation document, not a current MLB measurement. Former catcher identity matches reporting; current OF designation retained.',weightKg=81)
players['raider-sanchez-trutie']['bats']='R'
players['raider-sanchez-trutie']['throws']='R'
evidence('raider-sanchez-trutie',['bats','throws'],'Radio COCO federation preselection roster',
 'https://radiococooficial.blogspot.com/2025/08/convocados-siete-habaneros-preseleccion.html','2025-08-02','Santiago de Cuba catcher Raider Abel Sánchez Trutié is listed D/D (right/right); independently corroborates handedness in the reproduced roster.')
cp=players['carlos-adrian-hernandez-cuba']
old=cp['measurements']['height']
if old != '185 cm':
    cp['measurements']['reportedHeightText']=old
cp['measurements']['height']='185 cm'
cp['measurements']['notes']='Reported 1.85 m converted to centimeters for display. Weight remains unverified.'
evidence(cp['id'],['height'],'CiberCuba citing Francys Romero',cp['measurements']['sourceUrl'],'2026-10-08','Normalized the existing 1.85 m report; no new measurement or weight claim.')

def gaps(p):
    m=p.get('measurements') or {}
    return [k for k, missing in [('country',not p.get('country')),('height',not m.get('height')),('weight',not(m.get('weightLb') or m.get('weightKg'))),('bats',not p.get('bats')),('throws',not p.get('throws'))] if missing]

for p in data['players']:
    prior=next(x for x in before['players'] if x['id']==p['id'])
    changes.append(dict(id=p['id'],name=p['name'],rank=p['pipelineRank'],
     missingBefore=gaps(prior),missingAfter=gaps(p),bioEvidence=p.get('bioEvidence',[])))
path.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')
report=dict(asOf=retrieved,scope='All 47 international board players; bio-only research. Rankings, scouting, organizations and signing statuses unchanged.',
 method='Existing source review, English/Spanish/Chinese exact-name searches and official tournament rosters. Historical measurements are dated reports, not present-day verification. No photo estimates or handedness inference from pitching arm.',
 identityRejections=['Martin Morua is not Márkó Morua.','Natanael Yuten is not Eudi Yuten.','Older MLB/MiLB Luis García and Eliander Moisés Alcalde records are not these amateurs.','US school athletes named Anthony Calderon are not the Cuban catcher.'],
 unresolvedPolicy='Remaining fields lack reliable identity-matched public evidence in this pass. Leave unverified; absence of a retrieved source does not establish that none exists.', players=changes)
Path('research/international-bios/2026-11-03.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print('Remaining field gaps:',sum(len(x['missingAfter']) for x in changes))
