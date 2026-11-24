#!/usr/bin/env python3
"""Supplement winter prospect entry cards with official original-entry evidence."""
import concurrent.futures as cf,datetime as dt,importlib.util,json,os
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('winter',ROOT/'scripts/winter-ball.py');w=importlib.util.module_from_spec(spec);spec.loader.exec_module(w)
def main():
 path=ROOT/'data/winter/profiles-2026.json';catalog=json.loads(path.read_text());stamp=dt.datetime.now(dt.timezone.utc).isoformat();existing=w.read('data/player-entry-history.json')['entries'];known={r['mlbamId']:r for r in existing.values()if r.get('mlbamId')};orgs={t['id']for t in w.get('/teams',sportId=1)['teams']}
 def enrich(p):
  pid=p['mlbamId']
  if p.get('proEntry')and p['proEntry'].get('kind')!='unverified':return p
  if pid in known:p['proEntry']=known[pid];return p
  person=w.get('/people/'+str(pid),hydrate='draft')['people'][0]
  url=w.API+f'/transactions?playerId={pid}&startDate=2000-01-01&endDate={stamp[:10]}'
  events=sorted(w.get('/transactions',playerId=pid,startDate='2000-01-01',endDate=stamp[:10]).get('transactions',[]),key=lambda x:(x.get('date',''),x['id']))
  drafts=[r for r in person.get('drafts',[])if r.get('isDrafted')and r.get('team',{}).get('id')in orgs]
  entry=dict(name=p['name'],mlbamId=pid,checked=stamp[:10],kind='unverified',method='Entry details not yet verified',summary='Original acquisition details remain unverified.',country=person.get('birthCountry'),sources=[dict(label='Official MLB biography and amateur draft record',url=w.API+f'/people/{pid}?hydrate=draft'),dict(label='Official MLB transaction history',url=url)])
  if drafts:
   d=min(drafts,key=lambda r:int(r['year']));entry.update(kind='draft',method='MLB draft pick',year=d['year'],team=d['team']['name'],round=d.get('pickRound'),overallPick=d.get('pickNumber'),school=d.get('school',{}).get('name'),summary=f"Selected by {d['team']['name']} in the {d['year']} MLB draft.")
   if d.get('signingBonus')is not None:entry.update(signingBonusUsd=float(d['signingBonus']),bonusStatus='Official draft record',bonusSource=entry['sources'][0])
   signs=[t for t in events if t.get('toTeam',{}).get('id')==d['team']['id']and t.get('date','').startswith(str(d['year']))and 'signed' in t.get('description','').lower()]
   if signs:entry['signingDate']=signs[0]['date']
  else:
   signs=[t for t in events if t.get('toTeam',{}).get('id')in orgs and t.get('typeCode')=='SFA'and 'signed' in t.get('description','').lower()]
   if signs:
    t=signs[0];entry.update(kind='signing',method='Free-agent signing',team=t['toTeam']['name'],signingDate=t['date'],summary=t['description'],detail='Earliest MLB-organization signing in the retrieved official transaction history. A signing bonus is not supplied by this feed.')
  p['proEntry']=entry;return p
 with cf.ThreadPoolExecutor(max_workers=6)as ex:catalog['players']=list(ex.map(enrich,catalog['players']))
 temp=path.with_suffix('.tmp');temp.write_text(json.dumps(catalog,ensure_ascii=False,separators=(',',':'))+'\n');os.replace(temp,path)
 print(json.dumps({'players':len(catalog['players']),'entryKinds':{k:sum(p['proEntry']['kind']==k for p in catalog['players'])for k in ['draft','signing','unverified']}}))
if __name__=='__main__':main()
