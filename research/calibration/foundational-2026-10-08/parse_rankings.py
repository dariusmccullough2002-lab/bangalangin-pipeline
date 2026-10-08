"""Parse factual ranking/grade excerpts retrieved from primary dated FanGraphs reports."""
import json,re
from pathlib import Path
P=Path(__file__).resolve().parent;R=P/'raw'
def plain(s):return re.sub(r'【\d+†([^†】]+)(?:†[^】]+)?】',r'\1',s)
result=[];audit=[]
for year in [2010,2011,2014,2015,2019,2020]:
 lines={}
 for f in R.glob(f'fg-web-{year}-*.json'):
  for line in json.load(open(f))['lines']:
   m=re.match(r'L(\d+): (.*)',line)
   if m:lines[int(m[1])]=plain(m[2])
 current=None;rows={};keys=[]
 for no,s in sorted(lines.items()):
  m=re.match(r'(?:> )?(\d+)\. ([^,]+), ([^,]+), ([^:]+)',s)
  if not m and year==2011:m=re.match(r'(\d+)\. ([^|]+)\s*\|\s*([^|]+)\s*\|\s*(.+)',s)
  if m:
   rank=int(m[1]);current=rank
   if rank<=200:rows.setdefault(rank,{'year':year,'rank':rank,'name':m[2].strip(),'position':m[3].strip(),'organization':m[4].strip(),'provider':'FanGraphs','source_line':no,'FV':None,'tools':{}})
  if year in [2019,2020]:
   parts=[x.strip() for x in s.split('|')]
   if len(parts)==8 and parts[0].isdigit():
    rank=int(parts[0]);rows[rank]={'year':year,'rank':rank,'name':parts[1],'organization':parts[2],'published_age':float(parts[3]),'level':parts[4],'position':parts[5],'ETA':parts[6],'FV':float(parts[7]),'tools':{},'provider':'FanGraphs','source_line':no}
  if year==2020 and current in rows:
   parts=[v.strip() for v in s.split('|')]
   if parts[0] in ['Hit','Fastball']:keys=parts
   elif keys and len(parts)==len(keys) and all('/' in v or v=='-' for v in parts):
    for k,z in zip(keys,parts):
     m=re.match(r'\d+/(\d+)(\+?)',z)
     if m:rows[current]['tools'][k]=float(m[1])+(2.5 if m[2] else 0)
  if year==2015 and current in rows and 'FV:' in s:
   m=re.search(r'FV: (\d+)',s)
   if m:rows[current]['FV']=int(m[1])
   for k,present,future,plus in re.findall(r'([A-Za-z ]+): (\d+)/(\d+)(\+?)',s):rows[current]['tools'][k.strip()]=float(future)+(2.5 if plus else 0)
 missing=[r for r in range(1,101) if r not in rows];audit.append({'year':year,'rows':len(rows),'missing_top100':missing,'fv_top100':sum(rows[x]['FV'] is not None for x in rows if x<=100)})
 result.extend(rows.values())
(R/'fg-rankings.json').write_text(json.dumps(result,indent=2));(P/'results/ranking-extraction-audit.json').write_text(json.dumps(audit,indent=2));print(json.dumps(audit))
