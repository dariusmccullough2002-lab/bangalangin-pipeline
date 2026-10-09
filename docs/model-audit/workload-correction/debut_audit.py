"""Universal debut-season evidence ledger; frozen catalog is read-only."""
import json,gzip,hashlib,re,collections,csv
from pathlib import Path
OUT=Path(__file__).resolve().parent
CAT=OUT.parents[3]/'unused'
def load_index():
 index={};complete={};errors=[]
 for f in (OUT/'source-cache').glob('*.meta.json'):
  match=re.fullmatch(r'(\d+)-(\d+)\.meta\.json',f.name)
  if not match:continue
  year,sport=map(int,match.groups());meta=json.loads(f.read_text());raw=gzip.decompress(f.with_name(f.name.replace('.meta.json','.json.gz')).read_bytes())
  assert hashlib.sha256(raw).hexdigest()==meta['sha256_uncompressed']
  groups=json.loads(raw).get('stats',[])
  if len(groups)!=1 or len(groups[0]['splits'])!=groups[0]['totalSplits']:continue
  complete.setdefault(year,set()).add(sport);seen={}
  for z in groups[0]['splits']:
   ident=z['player']['id'];s=z['stat'];a,b=(str(s['inningsPitched']).split('.')+['0'])[:2];assert b in ['0','1','2'];outs=int(a)*3+int(b);assert outs==s.get('outs',outs)
   if ident in seen:
    assert seen[ident]==outs;continue
   seen[ident]=outs
   index.setdefault((ident,year),[]).append({'sport_id':sport,'outs':outs,'games':s.get('gamesPlayed'),'starts':s.get('gamesStarted'),'source_url':meta['url'],'source_sha256':meta['sha256_uncompressed']})
 return index,complete
def inventory(catalog,profilemap=None):
 rows=[];index,complete=load_index()
 for a in catalog['assets']:
  if a.get('group')=='Pick' or a['id'].startswith('pick:'):continue
  roles=re.split(r'[,/ ]+',a.get('position',''));au=a.get('audit',{});p=a.get('career_profile') or (profilemap or {}).get(a['id'],{});seasons=[z for z in p.get('seasons',[]) if z.get('role')!='H' and z.get('stat',{}).get('IP',0)>0]
  if not (set(roles)&{'P','SP','RP'} or au.get('role') in ['SP','RP','H+SP'] or seasons):continue
  ids=p.get('identifiers',{});ident=ids.get('mlbamId');identity=a.get('playerIdentity','')
  if not ident and identity.startswith('mlbam:'):ident=int(identity.split(':')[1])
  first=ids.get('first_mlb_year');debut=min((z['year'] for z in seasons),default=None)
  # first_mlb_year can refer to a hitter's debut; actual positive pitching season is authoritative.
  if debut is not None and first is not None and first<debut and not p.get('missing_pre2010_seasons'):first=debut
  first=first or debut
  components=index.get((ident,first),[]) if ident and first else []
  resolved=bool(first and ident and complete.get(first,set())==set(range(11,17)))
  mlb=next((z['stat']['IP'] for z in seasons if z['year']==first),None)
  mi=sum(z['outs'] for z in components)/3 if resolved else None
  status='verified_affiliated_debut' if resolved else 'identity_or_debut_unresolved' if not ident else 'no_recorded_MLB_pitching_debut' if not first else 'missing_complete_debut_source'
  rows.append({'id':a['id'],'name':a['name'],'owner':a.get('owner'),'position':a.get('position'),'role':au.get('role'),'age':p.get('age'),'mlbam_id':ident,'debut_year':first,'earliest_cached_pitching_year':debut,'MLB_IP':mlb,'MiLB_IP':mi,'professional_IP':mlb+mi if mlb is not None and mi is not None else None,'status':status,'components':components,'other_professional_assignments':'Not verified; affiliated total is a lower-bound where foreign/independent assignments exist','workload_corrected':bool(mi and mlb is not None),'recent_window_affected':bool(mi and first and 2023<=first<=2026),'predebut_cached_seasons':[{'season':y,'IP':sum(t['outs'] for t in cs)/3} for (i,y),cs in index.items() if ident==i and (first is None or y<first)]})
 return rows
if __name__=='__main__':
 import sys
 cat=json.loads(Path(sys.argv[1]).read_text());profiles={}
 if len(sys.argv)>2:
  cache=json.loads((Path(sys.argv[2])/'trade-preview-v22/model/career_history_cache.json').read_text());profiles={p['fantraxId']:p for p in cache['profiles']}
 rows=inventory(cat,profiles)
 (OUT/'Debut_Evidence_Ledger.json').write_text(json.dumps(rows,indent=2))
 counts={'catalog_assets':len(cat['assets']),'pitchers_audited':len(rows),'status_counts':dict(collections.Counter(z['status'] for z in rows)),'verified_positive_MiLB':sum(bool(z['MiLB_IP']) for z in rows),'verified_zero_recorded_affiliated':sum(z['MiLB_IP']==0 for z in rows),'workload_evidence_corrected':sum(z['workload_corrected'] for z in rows),'recent_window_affected':sum(z['recent_window_affected'] for z in rows),'missing_source_years':sorted({z['debut_year'] for z in rows if z['status']=='missing_complete_debut_source'}),'baseline_sha256':hashlib.sha256(Path(sys.argv[1]).read_bytes()).hexdigest()}
 (OUT/'Debut_Coverage.json').write_text(json.dumps(counts,indent=2));print(json.dumps(counts,indent=2))
