"""Allow exactly one additional DOM display hook; reject valuation/data edits."""
import re,json,base64,gzip,hashlib,subprocess
from pathlib import Path
root=Path(__file__).resolve().parents[1];base='f0388d84af4eda0d2a1319cac57daacbefcb0863'
read=lambda p:subprocess.check_output(['git','show',base+':'+p],cwd=root)
old=read('trade-analyzer-beta/index.html').decode();new=(root/'trade-analyzer-beta/index.html').read_text()
packed=lambda h:re.search("const packed='([^']+)'",h)[1]
code=lambda h:json.loads(re.search(r'script.textContent=("(?:[^"\\]|\\.)*");document.body.append',h)[1])
assert packed(old)==packed(new)
assert code(new)==code(old).replace('if(!window.PipelineStarterDisplay?.mount(body,a)&&evidence.projection)','if(!window.PipelineStarterDisplay?.mount(body,a)&&!window.PipelineRoleDisplay?.mount(body,a)&&evidence.projection)')
unchanged=['trade-model.js','trade-ui.js','trade-analyzer-beta/trade-narrative.js','data/trade/2026-baseline.json.gz','data/editions/october-2026.json','data/starter-display-scenarios.json','trade-analyzer-beta/starter-display.js','trade-analyzer-beta/history-display.js']
for path in unchanged:assert (root/path).read_bytes()==read(path),path
catalog=json.loads(gzip.decompress(base64.b64decode(packed(new))))
result={'baseCommit':base,'assetsUnchanged':len(catalog['assets']),'catalogExactByteMatch':True,'catalogSHA256':hashlib.sha256(gzip.decompress(base64.b64decode(packed(new)))).hexdigest(),'embeddedValuationCodeUnchanged':True,'allowedAppChange':'One additional display-only mount call','unchangedFiles':unchanged,'displayWrites':'DOM only','scenarioInputsToValuation':False}
(root/'docs/website/role-display-isolation.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
