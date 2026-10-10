"""Collect only the frozen official GP censuses; preserve bytes and provenance."""
from pathlib import Path
import json,gzip,hashlib,datetime,urllib.request,concurrent.futures,shutil
D=Path(__file__).resolve().parent;V=D/'verified';V.mkdir(exist_ok=True)
protocol=json.loads((D/'Protocol_Freeze.json').read_text())
def collect(year):
 p=V/f'hitting-{year}.json.gz';prov=p.with_suffix('').with_suffix('.provenance.json')
 if not p.exists():
  cached=D.parent/'direct-workload-correction/verified'/f'GP{year}.json.gz'
  if cached.exists():
   p.write_bytes(cached.read_bytes());old=cached.parent/f'GP{year}.provenance.json';meta=json.loads(old.read_text()) if old.exists() else {};meta.update(reused_from=str(cached.relative_to(D.parent)),reuse_timestamp=datetime.datetime.now(datetime.timezone.utc).isoformat());prov.write_text(json.dumps(meta,indent=2))
  else:
   url=protocol['endpoint'].format(year=year)
   try:
    with urllib.request.urlopen(url,timeout=30) as response:raw=response.read();httpdate=response.headers.get('Date')
    p.write_bytes(gzip.compress(raw,mtime=0));prov.write_text(json.dumps({'url':url,'retrieved_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'http_date':httpdate,'sha256':hashlib.sha256(raw).hexdigest(),'statistical_cutoff':f'{year} regular season end','historical_publication_timestamp':'unknown; retrospective complete census','medical_availability_evidence':False},indent=2))
   except Exception as ex:return {'year':year,'status':'unavailable','error':str(ex),'url':url}
 a=json.loads(gzip.decompress(p.read_bytes()));stats=a.get('stats',[])
 if not stats:return {'year':year,'status':'no_stats','source':str(p)}
 splits=stats[0]['splits'];ids=[s['player']['id'] for s in splits]
 valid=len(splits)==stats[0]['totalSplits'] and 0<len(splits)<5000 and len(ids)==len(set(ids)) and all(int(s['season'])==year for s in splits)
 return {'year':year,'status':'verified_complete' if valid else 'failed_completeness','rows':len(splits),'totalSplits':stats[0]['totalSplits'],'unique_ids':len(set(ids)),'source':str(p.relative_to(D)),'sha256':hashlib.sha256(gzip.decompress(p.read_bytes())).hexdigest()}
if __name__=='__main__':
 with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:rows=list(pool.map(collect,protocol['seasons']))
 (D/'Source_Coverage.json').write_text(json.dumps(rows,indent=2));print(json.dumps(rows,indent=2))
