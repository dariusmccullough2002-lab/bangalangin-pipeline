"""Resolve to stable official MLBAM/Retrosheet keys before opening final labels."""
import json,gzip,re,unicodedata,datetime,collections
from pathlib import Path
P=Path(__file__).resolve().parent
norm=lambda s:re.sub('[^a-z]','',unicodedata.normalize('NFKD',re.sub(r'\b(Jr\.?|III|II)\b','',s,flags=re.I)).encode('ascii','ignore').decode().lower())
reg=[r for b in json.load(gzip.open(P/'raw/identity-register.json.gz','rt')) for r in b['rows'] if r['key_mlbam']]
byid={int(r['key_mlbam']):r for r in reg};names=collections.defaultdict(dict)
for r in reg:
 for first in [r['name_first'],r['name_given'],r.get('name_nick','')]:
  if first:names[norm(first+' '+r['name_last']+((' '+r['name_suffix']) if r['name_suffix'] else ''))][int(r['key_mlbam'])]=r
aliases={'mikestanton':'giancarlostanton','devarisgordon':'deegordon','jonathangray':'jongray','alexgonzalez':'chichigonzalez','francelismontas':'frankiemontas','luisrobert':'luisrobert','franklinsbarreto':'franklinbarreto','danielnorris':'danielnorris','michaelmontgomery':'mikemontgomery','devarisgordon':'deestrangegordon','deegordon':'deestrangegordon','zachwheeler':'zackwheeler','zachbritton':'zackbritton','jiomier':'jiovannimier','carlosmatias':'carlosmartinez','chriscolon':'christiancolon','jonathansingleton':'jonsingleton','mattwiser':'mattwisler','vincentvelasquez':'vincevelasquez','cjedwards':'carledwards','phillipervin':'philervin','ozhainoalbies':'ozziealbies','bradzimmer':'bradleyzimmer','peteralonso':'petealonso'}
overrides=json.load(open(P/'raw/identity-overrides.json')) if (P/'raw/identity-overrides.json').exists() else {}
rows=json.load(open(P/'raw/fg-rankings.json'));resolved=[];unknown=[]
for x in rows:
 key=norm(x['name']);cand=list(names.get(aliases.get(key,key),{}).values());cand=[r for r in cand if r['birth_year'] and 14<=x['year']-int(r['birth_year'])<=35]
 if 'published_age' in x:cand=[r for r in cand if abs(x['published_age']-(x['year']-int(r['birth_year'])))<1.5]
 if x['year']==2010 and key=='joshbell':cand=[byid[458679]]
 if str(x['year'])+'-'+key in overrides:cand=[byid[overrides[str(x['year'])+'-'+key]]]
 if len(cand)!=1:unknown.append(x|{'candidates':[{'id':r['key_mlbam'],'name':r['name_first']+' '+r['name_last'],'birth':r['birth_year']} for r in cand]});continue
 r=cand[0];dob= None
 if all(r[k] for k in ['birth_year','birth_month','birth_day']):dob=f"{int(r['birth_year']):04}-{int(r['birth_month']):02}-{int(r['birth_day']):02}"
 resolved.append(x|{'mlbamId':int(r['key_mlbam']),'retroId':r['key_retro'],'birthDate':dob,'pitcher':int(x['position'] in ['RHP','LHP','P']),'resolution':'Chadwick MLBAM key + stable birth-date plausibility; aliases explicit'})
(P/'results/resolved-rankings.json').write_text(json.dumps(resolved,indent=2));(P/'results/unresolved-rankings.json').write_text(json.dumps(unknown,indent=2));print('resolved',len(resolved),'unresolved',[(r['year'],r['rank'],r['name'],r['candidates']) for r in unknown]);
