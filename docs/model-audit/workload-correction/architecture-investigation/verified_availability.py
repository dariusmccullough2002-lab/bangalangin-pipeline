"""Bounded independently documented availability checks; labels never enter fitting."""
import sys,json,urllib.request,time,gzip,hashlib,datetime
from pathlib import Path
import numpy as np
OUT=Path(__file__).resolve().parent;RAW=OUT/'availability-sources';RAW.mkdir(exist_ok=True)
ids=[592885,596115,571745,543685,624585,502110,621035,669160,672715]
ledger=[]
for ident in ids:
 f=RAW/f'{ident}.json.gz';meta=f.with_name(f'{ident}.meta.json');url=f'https://statsapi.mlb.com/api/v1/transactions?playerId={ident}&startDate=01/01/2013&endDate=12/31/2025'
 if f.exists():b=gzip.decompress(f.read_bytes());metadata=json.loads(meta.read_text())
 else:
  with urllib.request.urlopen(url,timeout=40) as r:b=r.read()
  f.write_bytes(gzip.compress(b,mtime=0));metadata={'url':url,'retrieved_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'sha256_uncompressed':hashlib.sha256(b).hexdigest()};meta.write_text(json.dumps(metadata,indent=2));time.sleep(.75)
 assert hashlib.sha256(b).hexdigest()==metadata['sha256_uncompressed']
 rows=json.loads(b)['transactions'];assert all(z.get('person',{}).get('id')==ident for z in rows)
 placements=[z for z in rows if 'placed ' in z.get('description','').lower() and ('injured list' in z['description'].lower() or 'disabled list' in z['description'].lower()) and z.get('toTeam',{}).get('id',999)<200]
 ledger.append({'mlbam_id':ident,'name':rows[0]['person']['fullName'] if rows else str(ident),'placements':placements,'provenance':metadata})
test=json.loads(gzip.decompress((OUT/'Opportunity_Test_Cases.json.gz').read_bytes()));records=[]
for z in test:
 evidence=next((x for x in ledger if x['mlbam_id']==z['mlbam_id']),None)
 if not evidence:continue
 prior=[t for t in evidence['placements'] if f"{z['anchor']-2}-01-01"<=t['date']<=f"{z['anchor']}-12-31"]
 if not prior:continue
 records.append(z|{'documented_prior_IL_placements':prior})
scores={}
for rr in ['H','SP','RP']:
 xs=[z for z in records if z['role']==rr];key='PA' if rr=='H' else 'IP'
 if xs:scores[rr]={'n':len(xs),'metrics':{method:{'MAE':float(np.mean([abs(z[method][key]-z['actual'].get(key,0)) for z in xs])),'bias':float(np.mean([z[method][key]-z['actual'].get(key,0) for z in xs]))} for method in ['baseline','selected','ridge']}}
(OUT/'Verified_Availability_Checks.json').write_text(json.dumps({'sources':ledger,'scores':scores,'cases':[{'name':z['name'],'anchor':z['anchor'],'role':z['role'],'prior_placements':z['documented_prior_IL_placements']} for z in records],'scope':'Nine bounded historically documented diagnostics, not representative medical cohort. Prior IL placements are facts, not assumed ongoing injuries. Labels use dates<=forecast anchor and are never forecast features. Broader repeated-shortfall cohort remains an availability proxy, not diagnosed injury.'},indent=2));print('Verified availability checks',len(records),scores,flush=True)
