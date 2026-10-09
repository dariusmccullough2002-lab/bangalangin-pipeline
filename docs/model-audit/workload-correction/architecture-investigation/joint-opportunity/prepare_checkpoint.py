"""Package additive research files in content-download-safe pieces."""
from pathlib import Path
import json,hashlib,sys,platform,sklearn,numpy
P=Path(__file__).resolve().parent;files=[];entries=[];cut=700000
for f in sorted(P.iterdir()):
 if not f.is_file() or f.name in ['Recovery_Manifest.json']:continue
 data=f.read_bytes();paths=[]
 if len(data)>cut:
  for i,start in enumerate(range(0,len(data),cut)):
   target=P/'Stored_Parts'/f'{f.name}.part{i:03d}';target.parent.mkdir(exist_ok=True);target.write_bytes(data[start:start+cut]);paths.append(str(target.relative_to(P)))
 else:paths=[f.name]
 files.append({'path':f.name,'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest(),'storage_paths':paths})
 for path in paths:
  raw=(P/path).read_bytes();entries.append({'local_path':str((P/path).resolve()),'relative_path':path,'bytes':len(raw),'git_blob_sha':hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()})
manifest={'schema':1,'parent_commit':'8c7df81d6b3fb45905c826aade9919a73aac7ae2','branch':'review/capacity-opportunity-attrition-20261009','additive_research_only':True,'python':platform.python_version(),'sklearn':sklearn.__version__,'numpy':numpy.__version__,'catalog_sha256':'aadad4dc7763510da7eba928aae5018af1bc48cfacd8b5f510ca5f5cd0995235','model_source_package':'BangaLangin_V23C_Verified_Recovery_Package.zip; preserved original recovery package, no model source changes','recovery':'Download all direct files and Stored_Parts; run python restore_artifacts.py before loading models/cases. Existing differing files are never overwritten.','files':files,'stored_blobs':[{k:v for k,v in e.items() if k!='local_path'} for e in entries]}
(P/'Recovery_Manifest.json').write_text(json.dumps(manifest,indent=2));raw=(P/'Recovery_Manifest.json').read_bytes();entries.append({'local_path':str((P/'Recovery_Manifest.json').resolve()),'relative_path':'Recovery_Manifest.json','bytes':len(raw),'git_blob_sha':hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()});Path('/tmp/joint-upload-files.json').write_text(json.dumps(entries));print('Packaged',len(files),'artifacts into',len(entries),'blobs, bytes',sum(e['bytes'] for e in entries))
