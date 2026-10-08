"""Independent source reconciliation and category boundary checks."""
import gzip,json,datetime,collections,hashlib
from pathlib import Path
import numpy as np
from category_engine import qa3,innings,combine,points,hitting,pitching
P=Path(__file__).resolve().parent;R=P/'raw';O=P/'results'
assert [qa3(15,2),qa3(15,3),qa3(17,3),qa3(18,3),qa3(18,4)]==[1,0,0,1,0]
assert innings('5.2')==17 and innings('6.0')==18
try:innings('5.3');raise RuntimeError('invalid notation accepted')
except AssertionError:pass
assert np.all(points({'outs':104},{'outs':105})==0)
assert np.all(points({'outs':105},{'outs':104})==1)
assert np.all(points({'outs':60},{'outs':59},days=4)==1)
x=combine({'AB':10,'H':4,'TB':6},{'AB':30,'H':6,'TB':8});assert abs(hitting(x)[4]-.25)<1e-12
assert abs(pitching(combine({'outs':30,'H':6,'BB':2},{'outs':60,'H':15,'BB':3}))[-1]-26/30)<1e-12
assert points({'outs':120,'ER':1},{'outs':120,'ER':5})[0]==1
assert pitching({'outs':120,'K':10,'BB':0})[4]==10.1
register=[r for b in json.load(gzip.open(R/'identity-register.json.gz','rt')) for r in b['rows']];cross={r['key_retro']:int(r['key_mlbam']) for r in register if r['key_retro'] and r['key_mlbam']}
n=lambda r,k:int(float(r.get(k,0) or 0));acc=collections.defaultdict(lambda:collections.defaultdict(lambda:collections.defaultdict(int)))
for y in [2010,2011,2012,2018,2023,2024]:
 for r in json.load(gzip.open(R/f'daily-{y}.json.gz','rt'))['pitching']:
  dt=datetime.datetime.strptime(r['date'],'%Y%m%d').date();wk=(dt-datetime.timedelta(days=dt.weekday())).isoformat();id=cross[r['id']]
  for k,s in [('outs','p_ipouts'),('ER','p_er'),('K','p_k'),('BB','p_w'),('H','p_h'),('SV','save')]:acc[wk][id][k]+=n(r,s)
cache=json.load(gzip.open(R/'game-inputs.json.gz','rt'));diff=[];tested=0
for wk,vals in cache['weekly'].items():
 if 'P' not in vals:continue
 for id in set(acc[wk])|{int(j) for j in vals['P']}:
  a=acc[wk].get(id,{});b=vals['P'].get(str(id),{});tested+=1
  for k in ['outs','ER','K','BB','H','SV']:
   if a.get(k,0)!=b.get(k,0):diff.append({'week':wk,'id':id,'field':k,'Retrosheet':a.get(k,0),'MLB':b.get(k,0)})
checks={'category_boundary_checks':'PASS','compressed_JSON_snapshots':sum(1 for f in R.glob('*.json.gz') if json.loads(gzip.decompress(f.read_bytes())) is not None),'reconciled_week_player_pairs':tested,'source_difference_fields':len(diff),'source_differences':diff,'duplicate_week_players':cache['API_duplicate_week_player_rows'],'unmatched_retrosheet_ids':cache['unmatched_retrosheet_ids']}
(O/'verification.json').write_text(json.dumps(checks,indent=2));print({k:v for k,v in checks.items() if k!='source_differences'})
