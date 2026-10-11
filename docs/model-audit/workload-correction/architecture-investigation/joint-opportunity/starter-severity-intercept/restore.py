from pathlib import Path
import json,hashlib,io,zipfile
D=Path(__file__).resolve().parent;m=json.loads((D/'Recovery_Manifest.json').read_text());chunks=[]
for p in m['parts']:
 b=(D/p['name']).read_bytes();assert hashlib.sha256(b).hexdigest()==p['sha256'];chunks.append(b)
b=b''.join(chunks);assert len(b)==m['archive_bytes'] and hashlib.sha256(b).hexdigest()==m['archive_sha256']
with zipfile.ZipFile(io.BytesIO(b)) as z:
 for f in m['files']:
  p=D/f['path'];assert D in p.resolve().parents
  v=z.read(f['path']);assert len(v)==f['bytes'] and hashlib.sha256(v).hexdigest()==f['sha256']
  if p.exists():assert p.read_bytes()==v,'differing existing artifact: '+str(p)
  else:p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(v)
print('Restored',len(m['files']),'verified source/data/model artifacts')
