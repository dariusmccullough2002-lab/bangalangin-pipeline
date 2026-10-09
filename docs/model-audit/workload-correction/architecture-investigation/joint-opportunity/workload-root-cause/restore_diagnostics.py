"""Restore diagnostic CSVs from hash-verified repository archive parts."""
from pathlib import Path
import json,hashlib,io,zipfile
D=Path(__file__).resolve().parent
m=json.loads((D/'Recovery_Manifest.json').read_text())
parts=[]
for p in m['parts']:
 b=(D/p['path']).read_bytes();assert hashlib.sha256(b).hexdigest()==p['sha256'];parts.append(b)
b=b''.join(parts);assert hashlib.sha256(b).hexdigest()==m['archive_sha256']
with zipfile.ZipFile(io.BytesIO(b)) as z:
 assert z.testzip() is None
 for n in z.namelist():
  assert not Path(n).is_absolute() and '..' not in Path(n).parts
  data=z.read(n);assert hashlib.sha256(data).hexdigest()==m['files'][n]
  (D/n).parent.mkdir(parents=True,exist_ok=True);(D/n).write_bytes(data)
print('Restored',len(m['files']),'diagnostic files')
