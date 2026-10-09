from run_helpers import *
from hybrid import HybridForecastEngine
adapter=HybridForecastEngine()
samples=[]
for name,pa in [('Aaron Judge',522),('Starlin Castro',624),('Jacoby Ellsbury',561),('Brett Gardner',587),('Chase Headley',531),('Didi Gregorius',586),('Gary Sanchez',499)]:samples.append((name,2017,'2017-01-03','H',pa,'https://blogs.fangraphs.com/2017-zips-projections-new-york-yankees/'))
for name,pa in [('Aaron Judge',621),('Giancarlo Stanton',593),('Todd Frazier',583),('Gary Sanchez',532),('Brett Gardner',608),('Didi Gregorius',593),('Aaron Hicks',423),('Jacoby Ellsbury',473)]:samples.append((name,2018,'2018-01-05','H',pa,'https://blogs.fangraphs.com/2018-zips-projections-new-york-yankees/'))
for name,ip in [('Paul Skenes',155.3),('Mitch Keller',168),('Jared Jones',129.7),('Bailey Falter',125.7),('Johan Oviedo',109.7),('Braxton Ashcraft',81)]:samples.append((name,2025,'2025-01-22','P',ip,'https://blogs.fangraphs.com/2025-zips-projections-pittsburgh-pirates/'))
import unicodedata
def norm(s):return ''.join(c for c in unicodedata.normalize('NFKD',s).lower() if c.isalnum())
sel=read(HERE/'Selection_Freeze.json')['selected'];rows=[];missing=[];models={}
for name,ty,date,fam,value,url in samples:
 zs=[z for rr in (['H'] if fam=='H' else ['SP','RP']) for z in records[rr] if z['year']==ty-1 and norm(z['name'])==norm(name)]
 if not zs:missing.append({'name':name,'target_year':ty,'reason':'no preserved anchor row'});continue
 z=zs[0];key='PA' if fam=='H' else 'IP';asof=ty-1
 if (asof,fam) not in models:models[asof,fam]=fit_layer(asof,fam)
 c=incumbent(asof,fam,[z])[0];p=adapter.predict([z],asof=str(asof)+'-12-31')[0];b=historical_baseline(z)
 rows.append({'name':name,'mlbam_id':z['id'],'target_year':ty,'publication_date':date,'own_input_cutoff':str(asof)+'-12-31','forecast_type':'ZiPS conditional talent total; not roster allocation','horizon':'next full MLB regular season','information_dates_identical':False,'source_url':url,'public_forecast':value,'actual':(target(z) or {}).get('stat',{}).get(key,0),'production':(b or {}).get(key,0),'prior_joint':c[key],'new_selected':p[key],'fit_partition':z['id']%5,'not_population_sample':True})
csvout('Independent_Dated_Comparisons.csv',rows);saveout('Independent_Provenance.json',{'matched':len(rows),'missing':missing,'used_as_features':False,'same_target_full_season':True,'same_information_cutoff':False,'roster_allocated_forecast_sample':False,'limitation':'Purposive public conditional ZiPS sample. Not a same-day or roster-informed population validation; January news not encoded in December own inputs.'})
