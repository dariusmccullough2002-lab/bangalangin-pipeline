from pathlib import Path
import hashlib,json,zipfile,io
D=Path(__file__).resolve().parent
m=json.loads((D/'Recovery_Manifest.json').read_text());chunks=[]
for p in m['parts']:
 b=(D/p['path']).read_bytes();assert hashlib.sha256(b).hexdigest()==p['sha256'];chunks.append(b)
b=b''.join(chunks);assert hashlib.sha256(b).hexdigest()==m['archive_sha256']
with zipfile.ZipFile(io.BytesIO(b)) as z:z.extractall(D)
for p in m['files']:assert hashlib.sha256((D/p['path']).read_bytes()).hexdigest()==p['sha256']
print('Restored',len(m['files']),'verified files')
