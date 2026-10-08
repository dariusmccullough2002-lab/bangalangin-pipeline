"""Aggregate exact custom QA3 and harmonize weekly official pitching totals."""
import gzip,json,datetime,collections,csv,io,zipfile
from pathlib import Path
P=Path(__file__).resolve().parent;R=P/'raw';O=P/'results'
reg=[r for block in json.load(gzip.open(R/'identity-register.json.gz','rt')) for r in block['rows']];cross={r['key_retro']:int(r['key_mlbam']) for r in reg if r['key_retro'] and r['key_mlbam']};bios={int(r['key_mlbam']):{'birthDate':f"{int(r['birth_year']):04}-{int(r['birth_month']):02}-{int(r['birth_day']):02}",'name':r['name_first']+' '+r['name_last'],'retroId':r['key_retro']} for r in reg if r['key_mlbam'] and all(r[k] for k in ['birth_year','birth_month','birth_day'])}
from category_engine import qa3
n=lambda r,k:int(float(r.get(k,0) or 0))
week=lambda s:(datetime.datetime.strptime(str(s),'%Y%m%d').date()-datetime.timedelta(days=datetime.datetime.strptime(str(s),'%Y%m%d').weekday())).isoformat()
annual={};weeks={};coverage=[];qaweekly=collections.defaultdict(lambda:collections.defaultdict(int));pos={};unmatched=set()
for y in range(2010,2026):
 d=json.load(gzip.open(R/f'daily-{y}.json.gz','rt'));games={};gs=collections.defaultdict(int);a=collections.defaultdict(lambda:collections.defaultdict(int));w=collections.defaultdict(lambda:collections.defaultdict(lambda:collections.defaultdict(int)))
 for r in d['pitching']:
  if r['id'] not in cross:unmatched.add(r['id']);continue
  id=cross[r['id']];key=(r['gid'],id);g=games.setdefault(key,{'outs':0,'ER':0,'GS':0,'date':r['date']})
  for target,src in [('outs','p_ipouts'),('ER','p_er'),('GS','p_gs')]:g[target]+=n(r,src)
 for (gid,id),g in games.items():
  q=qa3(g['outs'],g['ER']);qstd=int(g['GS'] and g['outs']>=18 and g['ER']<=3);a[id]['QA3']+=q;a[id]['QS']+=qstd;a[id]['GS']+=g['GS'];a[id]['appearances']+=1;qaweekly[week(g['date'])][id]+=q
 for r in d['pitching']:
  if r['id'] not in cross:continue
  id=cross[r['id']]
  for key,src in [('outs','p_ipouts'),('ER','p_er'),('K','p_k'),('BB','p_w'),('H','p_h'),('SV','save')]:a[id][key]+=n(r,src)
 for r in d['batting']:
  if r['id'] not in cross:unmatched.add(r['id']);continue
  id=cross[r['id']];wk=week(r['date'])
  for k,src in [('AB','b_ab'),('H','b_h'),('BB','b_w'),('HBP','b_hbp'),('SF','b_sf'),('HR','b_hr'),('R','b_r'),('RBI','b_rbi'),('SB','b_sb')]:w[wk][id][k]+=n(r,src)
  w[wk][id]['TB']+=n(r,'b_h')+n(r,'b_d')+2*n(r,'b_t')+3*n(r,'b_hr')
 for wk,z in w.items():weeks.setdefault(wk,{})['H']=dict(z)
 z=zipfile.ZipFile(R/f'retrosheet-{y}.zip');f=csv.DictReader(io.TextIOWrapper(z.open(f'{y}fielding.csv'),encoding='utf-8-sig'));positions=collections.defaultdict(lambda:collections.defaultdict(set))
 for r in f:
  if r['gametype']=='regular' and r['stattype']=='value' and r['id'] in cross:positions[cross[r['id']]][r['d_pos']].add(r['gid'])
 pos[y]={id:{k:len(v) for k,v in z.items()} for id,z in positions.items()};annual[y]=dict(a);coverage.append({'year':y,'pitcher_appearances':len(games),'QA3':sum(x['QA3'] for x in a.values()),'conventional_QS':sum(x['QS'] for x in a.values()),'additional_QA3':sum(x['QA3']-x['QS'] for x in a.values()),'QA3_nonstarters':sum(qa3(g['outs'],g['ER']) for g in games.values() if not g['GS']),'pitcher_ids':len(a)})
# API by-date-range totals include holds; filter totals unique players and check outs vs Retrosheet.
errors=[];duplicated=[]
for f in R.glob('week-*.json.gz'):
 wk=f.name[5:15];raw=json.load(gzip.open(f,'rt'));p={}
 for ss in raw['data'].get('stats',[]):
  for x in ss['splits']:
   id=x['player']['id'];s=x['stat']
   if id in p:duplicated.append([wk,id]);continue
   p[id]={key:int(s.get(src,0) or 0) for key,src in [('outs','outs'),('ER','earnedRuns'),('K','strikeOuts'),('BB','baseOnBalls'),('H','hits'),('SV','saves'),('HLD','holds')]};p[id]['QA3']=qaweekly[wk].get(id,0)
 weeks.setdefault(wk,{})['P']=p
# Compact replay inputs, not a second collection.
cache={'annual_QA3':annual,'weekly':weeks,'positions':pos,'bios':bios,'coverage':coverage,'unmatched_retrosheet_ids':sorted(unmatched),'API_duplicate_week_player_rows':duplicated}
with gzip.open(R/'game-inputs.json.gz','wt') as f:json.dump(cache,f,separators=(',',':'))
(O/'qa3-coverage.json').write_text(json.dumps({'coverage':coverage,'unmatched_retrosheet_ids':sorted(unmatched),'duplicate_week_player_rows':duplicated},indent=2));print(json.dumps(coverage[-3:]));
