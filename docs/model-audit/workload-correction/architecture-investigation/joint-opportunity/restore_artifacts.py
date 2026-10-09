"""Restore piece-stored artifacts, verifying every byte; do not replace differing files."""
from pathlib import Path
import hashlib,json
P=Path(__file__).resolve().parent
manifest=json.loads((P/'Recovery_Manifest.json').read_text());done=0
for record in manifest['files']:
 target=P/record['path'];parts=record['storage_paths']
 if parts==[record['path']]:
  data=target.read_bytes()
 else:
  data=b''.join((P/a).read_bytes() for a in parts)
 assert len(data)==record['bytes'] and hashlib.sha256(data).hexdigest()==record['sha256'],record['path']
 if parts!=[record['path']]:
  if target.exists():assert target.read_bytes()==data,'Refusing to replace differing '+str(target)
  else:target.write_bytes(data)
 done+=1
print('Verified/restored',done,'research artifacts; fitted models require the recorded Python/sklearn versions.')
