"""Read public MLB Pipeline team/draft report data; retain grades, identity and provenance only."""
import json,re,html,urllib.request,concurrent.futures
from pathlib import Path
from html.parser import HTMLParser
root=Path(__file__).resolve().parents[1];out=root/'research/scouting-grade-audit';out.mkdir(parents=True,exist_ok=True)
clubs='dbacks braves orioles redsox cubs whitesox reds guardians rockies tigers astros royals angels dodgers marlins brewers twins mets yankees athletics phillies pirates padres giants mariners cardinals rays rangers bluejays nationals'.split()
class State(HTMLParser):
 def __init__(self):super().__init__();self.data=None
 def handle_starttag(self,tag,attrs):
  for k,v in attrs:
   if k=='data-init-state' and v and 'prospectBio' in v:self.data=json.loads(v)
def collect(club):
 url='https://www.mlb.com/milb/prospects/'+('draft' if club=='draft' else '2026/'+club)
 try:
  raw=urllib.request.urlopen(url,timeout=35).read().decode();parser=State();parser.feed(raw)
  if parser.data is None:return {'club':club,'url':url,'error':'No prospect report state'}
  data=parser.data['payload'];rows=[];seen=set()
  for key,group in data['ROOT_QUERY'].items():
   if not key.startswith('getPlayerRankingsFromSelection') or not isinstance(group,list):continue
   for entry in group:
    entity=entry.get('playerEntity',{});ref=entity.get('player',{}).get('__ref');person=data.get(ref,{})
    if not person.get('id') or person['id'] in seen:continue
    seen.add(person['id']);bios=entity.get('prospectBio',[]);bio=next((b for b in bios if b.get('contentTitle')==('draft' if club=='draft' else '2026')),None)
    if not bio:continue
    content=bio.get('contentText','');m=re.search(r'Scouting grades:.*?</p>',content,re.I|re.S)
    if not m:continue
    gradeText=html.unescape(re.sub('<[^>]+>',' ',m.group()));pairs=dict(re.findall(r'([A-Za-z][A-Za-z /-]*):\s*(\d{2}(?:\+)?(?:/\d{2})?)',gradeText));pairs={k.strip():v for k,v in pairs.items() if k.strip()!='Scouting grades'};fv=pairs.pop('Overall',None)
    if not fv or len(pairs)<2:continue
    name=' '.join(filter(None,[person.get('useName'),person.get('useLastName')]));rows.append({'mlbamId':person['id'],'name':name,'position':entity.get('position'),'source':'MLB Pipeline','sourceDate':None,'retrievedDate':'2026-11-27','reportContext':'2026 organizational report' if club!='draft' else '2026 Draft report','sourceUrl':url+'/'+person['nameSlug'],'fv':fv,'tools':pairs,'scale':'Published 20–80 scouting grades; source publication date not supplied by report state.'})
  return {'club':club,'url':url,'grades':rows,'total':len(rows)}
 except Exception as exc:return {'club':club,'url':url,'error':str(exc)[:200]}
results=[]
with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
 for r in pool.map(collect,clubs+['draft']):results.append(r);print(r['club'],r.get('total',r.get('error')),flush=True)
(out/'mlb-pipeline-source-grades.json').write_text(json.dumps(results,ensure_ascii=False,indent=2)+'\n')
print('Total',sum(r.get('total',0) for r in results),'published grade records')
