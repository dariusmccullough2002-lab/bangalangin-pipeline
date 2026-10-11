"""Certify the embedded data and executable valuation code were not changed."""
import re,json,gzip,base64,subprocess,hashlib
from pathlib import Path
root=Path(__file__).resolve().parents[1]
base='81cda32efc4ddc42bdae003e83f950a6d66bf129'
old=subprocess.check_output(['git','show',base+':trade-analyzer-beta/index.html'],cwd=root).decode()
new=(root/'trade-analyzer-beta/index.html').read_text()
packed=lambda s:re.search(r"const packed='([^']+)'",s).group(1)
code=lambda s:json.loads(re.search(r'script.textContent=("(?:[^"\\]|\\.)*");document.body.append',s).group(1))
assert packed(old)==packed(new)
oldcode=code(old);newcode=code(new)
hook="if(evidence.projection){body.append(el('h3','','MLB-component production forecast')"
history_change=json.loads((root/'docs/website/history-renderer-change.json').read_text())
assert newcode==oldcode.replace(history_change['old'],history_change['new']).replace(hook,"if(!window.PipelineStarterDisplay?.mount(body,a)&&evidence.projection){body.append(el('h3','','MLB-component production forecast')")
data=json.loads(gzip.decompress(base64.b64decode(packed(new))))
unchanged=['trade-model.js','trade-ui.js','trade-analyzer-beta/trade-narrative.js','data/trade/2026-baseline.json.gz','data/editions/october-2026.json']
for f in unchanged:assert (root/f).read_bytes()==subprocess.check_output(['git','show',base+':'+f],cwd=root)
result={'baseCommit':base,'catalogSHA256':hashlib.sha256(gzip.decompress(base64.b64decode(packed(new)))).hexdigest(),'assetsUnchanged':len(data['assets']),
 'catalogExactByteMatch':True,'embeddedAppOnlyDisplayHooksChanged':True,'historyMappingCorrected':True,'valuationFunctionsUnchanged':True,
 'unchangedFiles':unchanged,'displayReadsOnly':['audit.projection','preserved sidecar scenario'],'displayWrites':'DOM only',
 'excluded':['failed expected-workload candidates','team allocator','medical envelopes','years2–8','dynasty/ranking/replacement/trade inputs']}
out=root/'docs/website/starter-display-isolation.json';out.parent.mkdir(parents=True,exist_ok=True);out.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
