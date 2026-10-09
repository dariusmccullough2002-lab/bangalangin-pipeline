"""Verify bundled research and restore missing artifacts without overwriting differences."""
from pathlib import Path
import hashlib,json,io,zipfile
P=Path(__file__).resolve().parent
m=json.loads((P/'Recovery_Manifest.json').read_text());pieces=[]
for record in m['parts']:
 data=(P/record['path']).read_bytes()
 assert len(data)==record['bytes'] and hashlib.sha256(data).hexdigest()==record['sha256'],record['path']
 pieces.append(data)
data=b''.join(pieces)
assert len(data)==m['archive_bytes'] and hashlib.sha256(data).hexdigest()==m['archive_sha256']
with zipfile.ZipFile(io.BytesIO(data)) as z:
 assert set(z.namelist())=={r['path'] for r in m['artifacts']}
 for record in m['artifacts']:
  name=record['path'];target=P/name
  assert target.resolve().parent==P.resolve(),name
  payload=z.read(name)
  assert len(payload)==record['bytes'] and hashlib.sha256(payload).hexdigest()==record['sha256'],name
  if target.exists():assert target.read_bytes()==payload,'Refusing to overwrite differing '+name
  else:target.write_bytes(payload)
print('Verified/restored',len(m['artifacts']),'research artifacts; run scripts from original workspace with the preserved model package and catalog.')
