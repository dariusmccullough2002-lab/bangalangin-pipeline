"""Bounded investigation of existing unresolved evidence, without changing identity links."""
from shared import *
import datetime,collections,hashlib
ledger=read(PARENT.parent/'Debut_Evidence_Ledger.json.gz');cross=read(Path(sys.argv[1])/'trade-preview-v22/model/player_id_crosswalk.json');cx={z['fantraxId']:z for z in cross['rows']};cat={z['id']:z for z in catalog['assets']};out=[]
for z in ledger:
 if z['status']!='identity_or_debut_unresolved':continue
 a=cat[z['id']];c=cx[z['id']];candidates=[]
 for ident in c['candidate_mlbam_ids']:
  bio=games['bios'].get(str(ident),{});birth=bio.get('birthDate');ag=(datetime.date(2026,10,8)-datetime.date.fromisoformat(birth)).days/365.2425 if birth else None
  candidates.append({'mlbam_id':ident,'cached_bio':bio,'age_oct8':ag,'snapshot_age_difference':abs(ag-z['age']) if ag is not None else None,'recorded_MLB_P_years':sorted(q['year'] for q in hist.get((ident,'P'),[])),'recorded_MLB_H_years':sorted(q['year'] for q in hist.get((ident,'H'),[])),'cached_affiliated_years':sorted({year for key,year in index if key==ident})})
 near=[c['mlbam_id'] for c in candidates if c['snapshot_age_difference'] is not None and c['snapshot_age_difference']<1]
 out.append({'fantrax_id':z['id'],'name':z['name'],'snapshot_age':z['age'],'snapshot_team':old.players[z['id']].get('team'),'snapshot_role':z['role'],'snapshot_position':z['position'],'candidates':candidates,'age_consistent_candidates':near,'resolution':'Withheld: age/name compatibility is insufficient to establish stable provider identity. Snapshot team is retained; independent exact DOB/provider link and verified current team crosscheck are absent.','flags':c['flags']})
missing=[z for z in ledger if z['status']=='no_recorded_MLB_pitching_debut'];rows=[]
for z in missing:
 ident=z['mlbam_id'];aff=[q for (i,y),qs in index.items() if i==ident for q in qs];years=sorted({y for i,y in index if i==ident});rows.append({'fantrax_id':z['id'],'name':z['name'],'mlbam_id':ident,'role':z['role'],'owner':z['owner'],'affiliated_years':years,'cached_affiliated_IP':sum(q['outs'] for q in aff)/3,'status':'No recorded MLB pitching debut; no debut-season correction manufactured. Predebut affiliated evidence retained separately.'})
foreign=[z for z in ledger if z['status']=='verified_affiliated_debut' and not z['MiLB_IP'] and (z['MLB_IP'] or 0)>0]
save('Coverage_Followup.json',{'unresolved11':out,'no_debut86':rows,'counts':{'unresolved':len(out),'no_debut':len(rows),'no_debut_with_affiliated_records':sum(bool(z['affiliated_years']) for z in rows),'no_debut_by_role':dict(collections.Counter(z['role'] for z in rows))},'non_affiliated_scope':'Foreign_Workload_Evidence.json preserves twelve official-source native-league 2026 pitching snapshots from the existing GitHub international research. No older foreign debut-season history is verified. Zero affiliated records is not zero professional workload. Foreign workload is not made into MLB opportunity or added without calendar/overlap checks.','zero_affiliated_debut_cases':len(foreign),'preserved_ledger_sha256':hashlib.sha256((PARENT.parent/'Debut_Evidence_Ledger.json.gz').read_bytes()).hexdigest(),'identity_changes':0});print('Coverage follow-up saved',len(out),len(rows),flush=True)
