"""Restore the exact research checkpoint from its git-stored binary parts."""
from pathlib import Path
import json,hashlib,zipfile,io
HERE=Path(__file__).resolve().parent
m=json.loads((HERE/'Recovery_Manifest.json').read_text());chunks=[]
for a in m['parts']:
 b=(HERE/a['path']).read_bytes();assert len(b)==a['bytes'] and hashlib.sha256(b).hexdigest()==a['sha256'];chunks.append(b)
b=b''.join(chunks);assert len(b)==m['bytes'] and hashlib.sha256(b).hexdigest()==m['sha256'];(HERE/m['archive']).write_bytes(b)
with zipfile.ZipFile(io.BytesIO(b)) as z:
 for a in m['files']:
  target=(HERE/a['path']).resolve();assert target.is_relative_to(HERE.resolve());data=z.read(a['path']);assert hashlib.sha256(data).hexdigest()==a['sha256'];target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(data)
print('Restored and verified',len(m['files']),'research files')
