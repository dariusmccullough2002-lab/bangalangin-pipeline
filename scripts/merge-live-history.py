"""Merge verified, read-only Fantrax player-tab captures into publication history.
Usage: python3 scripts/merge-live-history.py /path/to/live-prospect-histories.json
Only transaction rows are published; browser/session data and errors are excluded.
"""
import sys,json,re
from pathlib import Path
root=Path(__file__).resolve().parents[1]
p=root/'data/transactions.json';data=json.loads(p.read_text());captures=json.loads(Path(sys.argv[1]).read_text())
clean=lambda s:re.sub(r'\s*\(\*?deleted\*?\)','',s,flags=re.I).strip()
ranked=json.loads((root/'data/editions/october-2026.json').read_text())['rankings']
identities={r['fantraxId']:r['name'] for r in ranked}
live={}
for pid,c in captures['players'].items():
 if pid not in identities or c['name']!=identities[pid]:raise ValueError('Unmatched identity '+pid)
 rows=[]
 for r in c['rows']:
  if len(r)!=3:raise ValueError('Invalid transaction row')
  if not re.fullmatch(r'[A-Z][a-z]{2} \d{1,2} \d{4}',r[0]):raise ValueError('Invalid source date')
  if not re.match(r'^(Kept|Drafted|Claimed|Dropped|Traded)',r[1]):raise ValueError('Unrecognized action '+r[1])
  rows.append([clean(v) for v in r])
 live[pid]={'name':c['name'],'capturedDate':c['capturedDate'],'rows':rows}
data['livePlayers']=live;data['identities']=identities
data['coverage']=f"{len(live)} of {len(ranked)} October prospect profiles have a live Fantrax Trans (Fntsy) capture. Remaining profiles use partial supplied records where available; failed or rate-limited lookups are not represented as empty histories."
data['sources']=[s for s in data['sources'] if s['id']!='fantrax-live-player-tabs']+[{'id':'fantrax-live-player-tabs','label':'Fantrax Trans (Fntsy) player tabs','capturedDate':'2026-10-06','playerCount':len(live),'scope':'All rows returned by each captured tab; date precision is day.'}]
p.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n');print(data['coverage'])
