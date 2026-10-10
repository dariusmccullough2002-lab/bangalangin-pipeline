"""Recover the bounded experiment, rejecting altered parts or conflicting files."""
from pathlib import Path
import hashlib,json,zipfile,io
D=Path(__file__).resolve().parent
m=json.loads((D/'Recovery_Manifest.json').read_text());chunks=[]
for part in m['parts']:
    b=(D/part['path']).read_bytes()
    assert hashlib.sha256(b).hexdigest()==part['sha256'];chunks.append(b)
b=b''.join(chunks);assert len(b)==m['archive_bytes'];assert hashlib.sha256(b).hexdigest()==m['archive_sha256']
with zipfile.ZipFile(io.BytesIO(b)) as z:
    for f in m['files']:
        path=D/f['path'];assert path.resolve().is_relative_to(D.resolve())
        payload=z.read(f['path']);assert hashlib.sha256(payload).hexdigest()==f['sha256']
        if path.exists():assert path.read_bytes()==payload,f'Conflicting existing file: {path}'
        else:path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(payload)
print('Restored/verified',len(m['files']),'research files; no deployment')
