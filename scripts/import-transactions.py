"""Import a Fantrax trade CSV without changing ownership or rankings.
Usage: python3 scripts/import-transactions.py /absolute/path/export.csv
Only neutral league transaction fields are retained. No strategy inputs.
"""
import csv,json,re,sys,hashlib,unicodedata
from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo
root=Path(__file__).resolve().parents[1]
read=lambda p:json.loads((root/p).read_text())
clean=lambda s:re.sub(r'\s*\(\*?deleted\*?\)','',s,flags=re.I).strip()
normalize=lambda s:re.sub(r'[^a-z0-9]','',unicodedata.normalize('NFKD',s).encode('ascii','ignore').decode().lower())
snapshot=read('data/ownership-snapshots/2026-10-06.json')
catalog={}
for t in snapshot['teams']:
 for p in t['players']:catalog.setdefault(normalize(p['name']),{})[p['fantraxId']]=p
edition=read('data/editions/october-2026.json')
for p in edition['rankings']:catalog.setdefault(normalize(p['name']),{})[p['fantraxId']]=p
rows=list(csv.DictReader(open(sys.argv[1],newline='',encoding='utf-8-sig')))
groups={}
for r in rows:
 # CSV has no transaction IDs. Pair both sides and exact source timestamp.
 key=(r['Date (EDT)'],tuple(sorted([r['From'],r['To']])))
 groups.setdefault(key,[]).append(r)
trades=[];histories={};unmatched=[]
for i,((date,teams),rs) in enumerate(groups.items(),1):
 dt=datetime.strptime(date,'%a %b %d, %Y, %I:%M%p').replace(tzinfo=ZoneInfo('America/New_York'))
 assets=[]
 for r in rs:
  name=clean(r['Player']); candidates=catalog.get(normalize(name),{})
  fid=next(iter(candidates)) if len(candidates)==1 else None
  is_pick='Draft Pick' in name
  assets.append({'name':name,'kind':'draft-pick' if is_pick else 'player','fantraxId':fid,'from':r['From'],'to':r['To']})
  if not fid and not is_pick:unmatched.append(name)
 trade={'id':f'trade-export-{i:03d}','date':dt.date().isoformat(),'occurredAt':dt.isoformat(),'sourceDateText':date,'sourceId':'fantrax-trade-export-2026','grouping':'Same source timestamp and pair of teams; export provides no transaction ID.','assets':assets}
 trades.append(trade)
 for a in assets:
  if a['fantraxId']:histories.setdefault(a['fantraxId'],[]).append({'id':trade['id']+'-'+a['fantraxId'],'date':trade['date'],'type':'trade','from':a['from'],'to':a['to'],'tradeId':trade['id'],'sourceId':trade['sourceId']})
# Independently supplied player-tab screenshot: date-only events; not a league-wide feed.
cel=next(p for p in edition['rankings'] if p['name']=='Felnin Celesten')['fantraxId']
extra=[('2026-09-28','kept','Shea Stadiums',''),('2025-09-29','kept','The Sandlot Sluggers',''),('2024-10-01','kept','Mostly Misfits',''),('2024-08-10','claim-fa','Mostly Misfits',''),('2024-08-06','drop','Mostly Misfits',''),('2024-08-06','claim-waivers','Mostly Misfits','Dropped Craig Kimbrel'),('2024-08-04','drop','jackson','Claimed Brandon Sproat'),('2024-07-25','claim-waivers','jackson','Dropped Chase Dollander'),('2024-07-23','drop','jackson','Claimed Hayden Birdsong'),('2024-05-18','claim-fa','jackson','Dropped Jonathan India')]
for i,(date,kind,team,detail) in enumerate(extra):histories.setdefault(cel,[]).append({'id':f'celesten-screenshot-{i}','date':date,'type':kind,'team':team,'detail':detail,'sourceId':'celesten-player-tab'})
trades.append({'id':'celesten-screenshot-trade-2025','date':'2025-02-18','sourceId':'celesten-player-tab','grouping':'Full trade package transcribed from player-tab screenshot.','assets':[{'name':n,'kind':'player','fantraxId':cel if n=='Felnin Celesten' else None,'from':a,'to':b} for a,b,ns in [('Young Guns','The Sandlot Sluggers',['Brock Wilken','Spencer Jones','Colt Emerson','Felnin Celesten','Ronny Mauricio']),('The Sandlot Sluggers','Young Guns',['Matt McLain','Seiya Suzuki','Will Smith'])] for n in ns]})
histories[cel].append({'id':'celesten-screenshot-trade-2025-'+cel,'date':'2025-02-18','type':'trade','from':'Young Guns','to':'The Sandlot Sluggers','tradeId':'celesten-screenshot-trade-2025','sourceId':'celesten-player-tab'})
for events in histories.values():events.sort(key=lambda e:e['date'],reverse=True)
output={'asOf':'2026-10-06','coverage':'Partial history: February 17–August 20, 2026 trade export; additional 2024–2026 player-tab history for Felnin Celesten. Draft, claim, drop and keeper records for other players were not supplied.','ownershipRule':'Current ownership remains the October 6 roster snapshot. Historical trades never overwrite it.','sources':[{'id':'fantrax-trade-export-2026','label':'User-supplied Fantrax trade export','firstDate':'2026-02-17','lastDate':'2026-08-20','assetRows':len(rows),'sha256':hashlib.sha256(Path(sys.argv[1]).read_bytes()).hexdigest()},{'id':'celesten-player-tab','label':'User-supplied Felnin Celesten Trans (Fntsy) screenshot','capturedDate':'2026-10-06','datePrecision':'day; same-day order not established'}],'trades':trades,'players':histories,'importAudit':{'unmatchedPlayerNames':sorted(set(unmatched)),'matching':'Unique normalized name against latest roster IDs; no fuzzy matches.','exportAssetCount':sum(len(t['assets']) for t in trades if t['sourceId']=='fantrax-trade-export-2026')}}
(root/'data/transactions.json').write_text(json.dumps(output,ensure_ascii=False,indent=2)+'\n')
print(f'{len(rows)} assets, {len(groups)} trade groups, {len(histories)} players with imported history.')
