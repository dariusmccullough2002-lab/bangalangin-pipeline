"""Condition playing-time paths on a verified first MLB season; no debut penalty."""
from pathlib import Path
import json,sys,re,gzip,base64,datetime,collections
import numpy as np
sys.path.insert(0,str(Path(__file__).parent));import model as m
OUT=Path(__file__).parent;ROOT=OUT.parents[1]
def post(a,observed,pool,k=30,exclude_id=None):
 f=m.fam(a);threshold=300 if a.get('position')=='C' else 400;known=observed>=(threshold if f=='H' else 80 if a.get('role')=='SP' else 40)
 sample=[]
 for d in pool:
  if m.fam(d['a'])!=f or d['duration']<2 or d['a']['mlbamId']==exclude_id:continue
  dknown=m.regular(d['a'],d['debut'])
  if dknown!=known:continue
  if f=='P':
   drole='SP' if m.AN.get((d['a']['mlbamId'],d['debut'],'P'),{}).get('GS',0)>=5 else 'RP'
   if drole!=a.get('role'):continue
  sample.append(d)
 if len({d['a']['mlbamId'] for d in sample})<10:return None
 X=np.array([[m.age(d['a'])+d['debut']-d['a']['year'],d['workload'][0]] for d in sample]);target=np.array([m.age(a),observed]);scale=np.maximum(np.std(X,axis=0),.5);dist=np.sqrt(np.sum(((X-target)/scale)**2,axis=1));order=np.argsort(dist)[:min(k,len(sample))];ws=np.array([sample[j]['weight'] for j in order])*np.exp(-dist[order]);ws/=sum(ws);sample=[sample[j] for j in order];annual=[];survival=1.;support=[]
 for t in range(1,8):
  ix=[j for j,d in enumerate(sample) if t<d['duration'] and d['workload'][t] is not None];mass=sum(ws[ix]);values=np.array([sample[j]['workload'][t] for j in ix]);expected=float(ws[ix]@values/mass) if mass else None;active=float(ws[ix]@(values>0)/mass) if mass else None
  risk=[j for j,d in enumerate(sample) if t<d['duration'] and d['workload'][t] is not None and (d['event'] is None or d['event']>=t)];den=sum(ws[risk]);haz=sum(ws[j] for j in risk if sample[j]['event']==t)/den if den else 0;survival*=1-haz;count=len({sample[j]['a']['mlbamId'] for j in ix});support.append(count)
  annual.append({'year':a['year']+t,'first_mlb_probability':0.,'mlb_arrived_by_year':1.,'mlb_active_probability':active,'expected_workload':expected,'regular_role_reached_by_year':1. if known else float(1-survival),'minimum_workload_support_players':count})
 return {'annual':annual,'arrival_status':'Observed MLB debut; arrival probability is 100%','regular_already_observed':known,'conditional_support':support,'observed_debut_workload':observed,'workload_unit':'PA' if f=='H' else 'IP','no_mlb_by_horizon_probability':0.,'regular_not_reached_by_horizon_probability':0. if known else float(survival)}

def build():
 cases=[]
 for a in m.CO:
  if a['year'] not in [2019,2020] or not m.eligible(a):continue
  debut=m.first(a)
  if debut is None or debut==2020 or debut+1>2025 or debut+1==2020:continue
  obs=m.exposure(a['mlbamId'],debut,m.fam(a));b=dict(a);b['year']=debut;b['age']=m.age(a)+debut-a['year'];b['role']='H' if m.fam(a)=='H' else 'SP' if m.AN.get((a['mlbamId'],debut,'P'),{}).get('GS',0)>=5 else 'RP';p=post(b,obs,m.donors(debut),exclude_id=a['mlbamId'])
  if p and p['annual'][0]['expected_workload'] is not None:cases.append({'id':a['mlbamId'],'name':a['name'],'origin':debut+1,'role':b['role'],'observed_first_year':obs,'next_year_actual':m.exposure(a['mlbamId'],debut+1,m.fam(a)),'next_year_prediction':p['annual'][0]['expected_workload']})
 m.write_csv(OUT/'Post_Debut_Cases.csv',cases);metrics={}
 for role in ['H','SP','RP']:
  r=[a for a in cases if a['role']==role]
  if r:metrics[role]={'cases':len(r),'players':len({a['id'] for a in r}),'model_MAE':float(np.mean([abs(a['next_year_prediction']-a['next_year_actual']) for a in r])),'repeat_first_year_MAE':float(np.mean([abs(a['observed_first_year']-a['next_year_actual']) for a in r])),'bias':float(np.mean([a['next_year_prediction']-a['next_year_actual'] for a in r]))}
 (OUT/'Post_Debut_Validation.json').write_text(json.dumps(metrics,indent=2)+'\n');print(json.dumps(metrics,indent=2))
 html=(ROOT/'trade-analyzer-beta/index.html').read_text();catalog=json.loads(gzip.decompress(base64.b64decode(re.search(r"const packed='([^']+)'",html)[1])));data=json.loads((ROOT/'data/arrival-workload-model.json').read_text());players={};pool=m.donors(2025)
 for asset in catalog['assets']:
  seasons=asset.get('career_profile',{}).get('seasons',[]);identity=asset.get('career_profile',{}).get('identifiers',{});debut=identity.get('first_mlb_year') or (asset['audit'].get('MLB') or asset['audit']).get('projection_audit',{}).get('identity_match',{}).get('first_mlb_year')
  if debut!=2026:continue
  role=asset['audit'].get('role');f='H' if role=='H' else 'P' if role in ['SP','RP'] else None
  if f is None:continue
  history=[a for a in seasons if a['year']==2026 and (a['role']=='H')==(f=='H')];observed=sum(a['stat'].get('PA' if f=='H' else 'IP',0) for a in history)
  if observed<=0:continue
  birth=identity.get('birthDate') or (asset['audit'].get('MLB') or asset['audit']).get('projection_audit',{}).get('identity_match',{}).get('birthDate');age=(datetime.date(2026,4,1)-datetime.date.fromisoformat(birth)).days/365.25 if birth else 23
  a={'name':asset['name'],'year':2026,'age':age,'position':asset['position'],'pitcher':int(f=='P'),'role':role};p=post(a,observed,pool)
  if not p:continue
  players[asset['id']]={'name':asset['name'],'role':role,'workload_unit':'PA' if f=='H' else 'IP','inputs':a,'rank_input_source':'Observed debut workload; no new source-rank conversion','flags':['Research post-debut model conditioned on observed first-season workload. Arrival is already known.','Mean forecasts and trade values in the live calculator are unchanged.','Future role retention and injuries are not individually predicted.'],**p}
 data['debuted_players']=players;data['post_debut_validation']=metrics;(ROOT/'data/arrival-workload-model.json').write_text(json.dumps(data,separators=(',',':'))+'\n');print('Observed debut diagnostics',len(players));print('Culpepper',next((p['annual'][0] for p in players.values() if p['name']=='Kaelen Culpepper'),None));print('Bolte',next((p['annual'][0] for p in players.values() if p['name']=='Henry Bolte'),None))
if __name__=='__main__':build()
