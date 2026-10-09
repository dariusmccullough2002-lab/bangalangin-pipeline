from engine import *
VAR=['usage','ridge_100','ridge_1000','ridge_10000','tree','blend','tree_quarter','tree_half','ridge_quarter','usage_quarter']
def saveout(name,obj):
 b=json.dumps(obj,default=lambda a:a.item() if isinstance(a,np.generic) else a,allow_nan=False).encode();(HERE/name).write_bytes(gzip.compress(b,mtime=0) if name.endswith('.gz') else b)
def csvout(name,rows):
 with (HERE/name).open('w',newline='') as f:
  w=csv.DictWriter(f,list(dict.fromkeys(k for a in rows for k in a)));w.writeheader();w.writerows(rows)
def summaries(rows,methods):
 return {g:{m:metric([(a[m],a['actual']) for a in rows if g in a['groups']]) for m in methods} for g in sorted({g for a in rows for g in a['groups']})}
