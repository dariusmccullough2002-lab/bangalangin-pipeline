"""General stable-ID/season evidence gate. No name matching or hardcoded projections."""
import copy,math

def guarded_forecast(original,manifest,player,role,scenario='base',enabled=False,context=None):
 out=original(player,role,scenario)
 if not enabled or not out or role not in ['SP','RP']:return out
 v,r,old=context;rows=[z for z in v.seasons(player,role) if 2023<=z['year']<=2026 and z['role']==role and z['stat']['IP']>0]
 ident=v.cf.IDS.get(player['id'],player.get('mlbamId'));records=[z for z in manifest['records'] if z['fantrax_id']==player['id'] and z['mlbam_id']==ident and z['review_status']=='verified_for_provisional_candidate']
 if not records:return out
 additions={}
 for e in records:
  row=next((z for z in rows if z['year']==e['season']),None)
  if not row:raise ValueError('Evidence season absent from original MLB role window')
  if abs(row['stat']['IP']*3-e['MLB_outs'])>1e-7:raise ValueError('MLB workload mismatch')
  coverage=e.get('complete_level_queries',[]);covered=[c['sport_id'] for c in coverage]
  if sorted(covered)!=list(range(11,17)) or any(c['season']!=e['season'] or c['status']!=200 or not c.get('sha256_uncompressed') or c['split_count']!=c['totalSplits'] for c in coverage):raise ValueError('Incomplete affiliated level coverage')
  comps=e['components'];keys=[(c['mlbam_id'],c['season'],c['sport_id']) for c in comps]
  if len(keys)!=len(set(keys)) or any(c['mlbam_id']!=ident or c['season']!=e['season'] or c['sport_id'] not in range(11,17) for c in comps):raise ValueError('Duplicate or mismatched minor evidence')
  if sum(c['outs'] for c in comps)!=e['MiLB_outs'] or any(c['outs']<0 or not c.get('source_sha256') or not c.get('source_url','').startswith('https://statsapi.mlb.com/') for c in comps):raise ValueError('Invalid source workload')
  age=player.get('age',99)-(2026-e['season'])
  if age>26:raise ValueError('Outside transparent young-season screen')
  total=(e['MLB_outs']+e['MiLB_outs'])/3
  if not any(z['year']>e['season'] and z['stat']['IP']>=total for z in rows):raise ValueError('No later same-role MLB workload corroboration')
  if e['season'] in additions:raise ValueError('Repeated season evidence')
  additions[e['season']]=e['MiLB_outs']/3
 weights={2023:.1,2024:.2,2025:.3,2026:.4};mass=sum(weights[z['year']] for z in rows);ips=[z['stat']['IP']+additions.get(z['year'],0) for z in rows]
 recent=sum(x*weights[z['year']]/mass for z,x in zip(rows,ips));top=sorted(ips,reverse=True)[:2];healthy=sum(top)/len(top);pw=1/(len(rows)+3)
 prior=out[2]['role_workload_prior'];work=min(v.cf.cap(role),(1-pw)*(.7*recent+.3*healthy)+pw*prior)
 audit=copy.deepcopy(out[2]);audit.update(projected_workload=work,professional_workload_policy={'version':manifest['policy_version'],'status':'PROVISIONAL_BETA','MLB_talent_rates_unchanged':True,'original_projected_workload':out[1],'source_seasons':sorted(additions),'limitations':'Physical workload correction; not out-of-sample predictive superiority. Future MLB opportunity and promotion boundary remain uncertain.'})
 return out[0],work,audit
