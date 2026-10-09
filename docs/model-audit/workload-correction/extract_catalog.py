import sys,re,json,gzip,base64
from pathlib import Path
s=Path(sys.argv[1]).read_text();match=re.search(r"const packed='([^']+)'",s);assert match
x=json.loads(gzip.decompress(base64.b64decode(match[1])));Path(sys.argv[2]).write_text(json.dumps(x))
