"""Cache primary Retrosheet annual CSVs and compact regular-season daily inputs."""
import urllib.request,concurrent.futures,zipfile,csv,io,json,gzip,hashlib,time
from pathlib import Path
R=Path(__file__).resolve().parent;RAW=R/'raw';OUT=R/'results'
NOTICE='The information used here was obtained free of charge from and is copyrighted by Retrosheet. Interested parties may contact Retrosheet at 20 Sunset Rd., Newark, DE 19711.'
def get(y):
 out=RAW/f'daily-{y}.json.gz'
 if out.exists():
  try:
   json.load(gzip.open(out,'rt'));return {'year':y,'cached':True}
  except (EOFError,OSError,json.JSONDecodeError):pass
 f=RAW/f'retrosheet-{y}.zip';url=f'https://www.retrosheet.org/downloads/{y}/{y}csvs.zip'
 if not f.exists():
  for i in range(3):
   try:f.write_bytes(urllib.request.urlopen(url,timeout=60).read());break
   except Exception:
    if i==2:raise
 z=zipfile.ZipFile(f);data={'year':y,'url':url,'copyright_notice':NOTICE,'input_sha256':hashlib.sha256(f.read_bytes()).hexdigest()}
 for group in ['pitching','batting','allplayers']:
  rows=list(csv.DictReader(io.TextIOWrapper(z.open(f'{y}{group}.csv'),encoding='utf-8-sig')))
  if group!='allplayers':rows=[r for r in rows if r['gametype']=='regular' and r['stattype']=='value']
  data[group]=rows
 temp=out.with_suffix('.tmp');temp.write_bytes(gzip.compress(json.dumps(data,separators=(',',':')).encode()));temp.replace(out)
 json.load(gzip.open(out,'rt'))
 print(y,len(data['pitching']),len(data['batting']),flush=True);return {'year':y,'pitching':len(data['pitching']),'batting':len(data['batting']),'compressed_bytes':out.stat().st_size}
if __name__=='__main__':
 with concurrent.futures.ThreadPoolExecutor(max_workers=5) as pool:
  res=list(pool.map(get,range(2010,2026)))
 (OUT/'collection-checkpoint.json').write_text(json.dumps(res,indent=2))
