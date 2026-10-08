"""Offline design experiment. Not deployment code; probabilities are hypotheses, not fitted estimates."""
import json,gzip,math,statistics,re,copy,hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parent
DB=json.load(gzip.open(ROOT/'inputs/baseline.json.gz'))
HISTORY=json.load(open(ROOT/'inputs/transactions.json'))
DRAFT=json.load(open(ROOT/'inputs/draft.json'))['players']
OLD=json.load(open(ROOT/'production-values.json'))
P={p['id']:p for p in DB['players']}; PICK={p['id']:p for p in DB['picks']}
# Verified MLB regular seasons only; 2026 comes from the persisted league export.
HIST={
'03wha':[
 dict(year=2023,GP=159,AB=643,PA=735,H=217,HR=41,R=149,RBI=106,BB=80,SO=84,HBP=9,SF=3,SB=73,TB=383),
 dict(year=2024,GP=49,AB=192,PA=222,H=48,HR=4,R=38,RBI=15,BB=27,SO=53,HBP=3,SF=0,SB=16,TB=70),
 dict(year=2025,GP=95,AB=338,PA=412,H=98,HR=21,R=74,RBI=42,BB=71,SO=102,HBP=3,SF=0,SB=9,TB=175)],
'03ojr':[
 dict(year=2023,GP=156,AB=602,PA=682,H=159,HR=26,R=78,RBI=94,BB=67,SO=100,HBP=9,SF=4,SB=5,TB=267),
 dict(year=2024,GP=159,AB=616,PA=697,H=199,HR=30,R=98,RBI=103,BB=72,SO=96,HBP=5,SF=4,SB=2,TB=335),
 dict(year=2025,GP=156,AB=589,PA=680,H=172,HR=23,R=96,RBI=84,BB=81,SO=94,HBP=6,SF=4,SB=6,TB=275)]}
MODES=['neutral','contender','balanced','rebuild']
def ip(x):
 x=float(x or 0);return int(x)+round((x-int(x))*10)/3

def quant(a,q):
 a=sorted(a);i=(len(a)-1)*q;return a[int(i)]*(1-i%1)+a[min(int(i)+1,len(a)-1)]*(i%1)

def role(p):
 return ('SP' if float(p.get('pit',{}).get('GS',0))>=5 or 'SP' in p.get('position','') else 'RP') if ip(p.get('pit',{}).get('IP'))>0 or p.get('position') in ['SP','RP','P'] else 'H'
def volume(p):
 return ip(p.get('pit',{}).get('IP')) if role(p)!='H' else p.get('bat',{}).get('PA',0)
QUAL=[p for p in P.values() if (p.get('bat',{}).get('AB',0)>=150 if role(p)=='H' else ip(p.get('pit',{}).get('IP'))>=30)]
OWN=[p for p in QUAL if p['owner']!='Free agent']; FA=[p for p in QUAL if p['owner']=='Free agent']
FULL={'H':600,'SP':170,'RP':65}
FIELDS={'H':['AB','PA','H','HR','R','RBI','SB','BB','HBP','SF','TB'],'SP':['IP','K','ER','SVH7','QA3','H','BB'],'RP':['IP','K','ER','SVH7','QA3','H','BB']}
# Cohort mean rates are solely shrinkage targets, not individually invented histories.
PRIOR={r:{k:sum((ip(p['pit'].get(k,0)) if k=='IP' else p.get('bat' if r=='H' else 'pit',{}).get(k,0)) for p in QUAL if role(p)==r)/sum(volume(p) for p in QUAL if role(p)==r) for k in FIELDS[r]} for r in FULL}

def rates(p,multi=True):
 r=role(p); rows=HIST.get(p['id'],[]) if multi and r=='H' else [];rows=rows+[p.get('bat' if r=='H' else 'pit',{})]
 weights=[.1,.2,.3,.4] if len(rows)==4 else [1.]
 exposure=sum(w*(a.get('PA',0) if r=='H' else ip(a.get('IP'))) for w,a in zip(weights,rows)); strength=100 if r=='H' else 30
 out={k:(sum(w*(ip(a.get(k)) if k=='IP' else a.get(k,0)) for w,a in zip(weights,rows))+strength*PRIOR[r][k])/(exposure+strength) for k in FIELDS[r]}
 return out,exposure

def vector(p,multi=True):
 r=role(p);a,e=rates(p,multi);f=FULL[r];a={k:v*f for k,v in a.items()}
 if r=='H':
  obp=(a['H']+a['BB']+a['HBP'])/max(1,a['AB']+a['BB']+a['HBP']+a['SF']);ops=obp+a['TB']/max(1,a['AB'])
  return [a['HR'],a['R'],a['RBI'],a['SB'],a['H']-.250*a['AB'],(ops-.720)*a['AB']]
 return [a['K'],-a['ER'],a['SVH7'],a['QA3'],a['K']-3*a['BB'],1.25*a['IP']-a['H']-a['BB']]
# Per-category dispersion proxy, not actual weekly win probability.
DEN={r:[max(1,statistics.pstdev([vector(p)[i] for p in OWN if role(p)==r])) for i in range(6)] for r in FULL}
def score(p,multi=True):return sum(x/s for x,s in zip(vector(p,multi),DEN[role(p)]))
def matches(p,pos):return pos in re.split(r'[,/ ]+',p.get('position',''))
def replacement(p,depth=5):
 r=role(p);pos=p.get('position','').split(',')[0].split('/')[0];pool=[q for q in FA if role(q)==r and (r!='H' or matches(q,pos))]
 if not pool:pool=[q for q in FA if role(q)==r]
 # Replacement is an available player at observed workload, not a fictitious 600-PA free agent.
 available=lambda q:score(q)*min(1,rates(q)[1]/FULL[role(q)])
 ordered=sorted(pool,key=available,reverse=True)[:depth]
 return statistics.median(available(q) for q in ordered)
def surplus(p,depth=5,multi=True):return max(0,score(p,multi)-replacement(p,depth))
ANCHOR={r:[quant([surplus(p) for p in OWN if role(p)==r],q) for q in [.30,.60,.85,.98]] for r in FULL}
SCALE=max(1,quant([surplus(p) for p in OWN],.90))

def weights(mode,horizon=8,discount=.88):
 a=[discount**t for t in range(horizon)]
 if mode=='contender': a=[x*(3 if t==0 else 1.5 if t==1 else .7 if t==2 else .25) for t,x in enumerate(a)]
 if mode=='rebuild':a=[x*(.2 if t==0 else .5 if t==1 else 1.2) for t,x in enumerate(a)]
 if mode=='balanced':a=[x*(1.2 if t<3 else .85) for t,x in enumerate(a)]
 # Same total value for an identical, constant annual stream under each strategy.
 z=sum(discount**t for t in range(horizon))/sum(a)
 return [x*z for x in a]

def probabilities(p,rank=None,scouting=True,tail=1,success=1):
 r=float(rank or p.get('prospect',{}).get('rank',350));reach=max(.12,min(.88,(.22+.58*math.exp(-(r-1)/160))*success))
 # Conditional on reaching meaningful MLB output: regular, above-average, star, superstar.
 elite=(.015+.20*math.exp(-(r-1)/35))*tail;star=.07+.25*math.exp(-(r-1)/100);above=.25
 if scouting:
  tools=p.get('prospect',{}).get('grades',{}).get('tools',{});fv=p.get('prospect',{}).get('grades',{}).get('fv')
  # Narrow residual tail shift; keeps contribution probability and rank prior fixed.
  future=[]
  for key in ['Hit','Game Power','Run']:
   m=re.findall(r'\d+',str(tools.get(key,'')))
   if m:future.append(float(m[-1]))
  if len(future)>=2:
   modifier=max(-.04,min(.04,(max(future)-55)*.003+(sum(future)/len(future)-50)*.001))
   elite=max(.005,elite+modifier)
  # FV deliberately not added again; rank already uses scouting evidence.
 elite=min(.4,elite);regular=1-elite-star-above
 return [1-reach,reach*regular,reach*above,reach*star,reach*elite]

def utility(x,gamma):return 10*(max(0,x)/SCALE)**gamma

def player_value(p,mode,candidate='B',**o):
 gamma=o.get('gamma',1 if candidate=='A' else 1.35);w=weights(mode,o.get('horizon',8),o.get('discount',.88));r=role(p);age=float(p.get('age') or 26);vals=[]
 if p.get('prospect') and volume(p)<(250 if r=='H' else 100):
  probs=probabilities(p,scouting=o.get('scouting',True),tail=o.get('tail',1),success=o.get('success',1));eta=int(re.search(r'20\d\d',p['prospect'].get('eta','2030')).group())
  outcomes=[0]+ANCHOR[r]
  # Proxy available unranked prospect: rank 400, ETA 2030. Not an observed replacement.
  baseline=probabilities({},rank=o.get('prospect_floor',400),scouting=False)
  for t in range(len(w)):
   ramp=max(0,min(1,(2027+t-eta+1)/2));base_ramp=max(0,min(1,(2027+t-2030+1)/2))
   aging=math.exp(-.04*max(0,age+t-29))
   u=sum(pr*utility(x*aging,gamma) for pr,x in zip(probs,outcomes))*ramp
   u-=sum(pr*utility(x*aging,gamma) for pr,x in zip(baseline,outcomes))*base_ramp
   vals.append(max(0,u))
  # C uses an illustrative certainty-equivalent discount ONCE, not a separate bust discount.
  uncertainty=(sum(pr*(utility(x,gamma))**2 for pr,x in zip(probs,outcomes))-sum(pr*utility(x,gamma) for pr,x in zip(probs,outcomes))**2)**.5
 else:
  s=surplus(p,o.get('depth',5),o.get('multi',True));_,e=rates(p,o.get('multi',True))
  health=o.get('health',1);availability=min(1,e/FULL[r])*health
  for t in range(len(w)):
   # Transparent design prior, not empirically fitted age curve.
   aging=math.exp(-(.07 if r!='H' else .045)*max(0,age+t-29))*(1+.01*min(3,max(0,26-age)))
   vals.append(availability*utility(s*aging,gamma))
  uncertainty=(.18 if r=='H' else .30)*max(vals,default=0)
 result=sum(x*y for x,y in zip(vals,w))
 if candidate=='C':result=max(0,result-{'neutral':0,'contender':.30,'balanced':.15,'rebuild':.06}[mode]*uncertainty*sum(w))
 return result

def draft_proxy(d,year):
 rank=d.get('sourceRanks',{}).get('ddOverall') or 400+(d.get('pipelineRank') or 100)
 return {'id':d['id'],'name':d['name'],'age':float(d.get('age') or 20)-(year-2027),'position':'SP' if d.get('type')=='P' else d.get('position','SS'),'bat':{},'pit':{},'prospect':{'rank':rank,'eta':str(year+3)}}
DRAFT=sorted([d for d in DRAFT if d.get('pipelineRank')],key=lambda d:d['pipelineRank'])

def asset_value(p,mode,candidate='B',**o):
 if p.get('kind')!='pick':return player_value(p,mode,candidate,**o)
 yr=p['year'];round=p['round'];slots=range((round-1)*12,round*12)
 if o.get('slot')=='early':slots=list(slots)[:4]
 if o.get('slot')=='late':slots=list(slots)[-4:]
 # Pick produces a prospect, not an independent point curve. Rank-order draft proxy.
 v=[player_value(draft_proxy(DRAFT[min(i,len(DRAFT)-1)],yr),mode,candidate,**o) for i in slots]
 # Exclusive draft rights relative to hypothetical access after 60; not a roster charge.
 after=o.get('postdraft',60);f=[player_value(draft_proxy(d,yr),mode,candidate,**o) for d in DRAFT[after:after+12]]
 floor=statistics.mean(f) if f else 0
 return max(0,(statistics.mean(v)-floor)*(o.get('class_quality',1) if yr>2027 else 1))

def cost(give,receive,free=2,lam=3,tau=2):
 def burden(a):return sum(1 if p.get('kind')!='pick' else .88**(p['year']-2026) for p in a)
 delta=burden(receive)-burden(give)
 soft=lambda x:lam*tau*math.log1p(math.exp(x/tau))
 return soft(delta-free)-soft(-free)

def old_value(p,m):return OLD[p['id']]['balanced' if m=='neutral' else m]
def compare(a,b,**o):
 result={}
 for mode in MODES:
  result[mode]={}
  for c in ['Live','A','B','C']:
   av=sum(old_value(p,mode) if c=='Live' else asset_value(p,mode,c,**o) for p in a);bv=sum(old_value(p,mode) if c=='Live' else asset_value(p,mode,c,**o) for p in b)
   ca=8*max(0,sum(p.get('kind')!='pick' for p in b)-sum(p.get('kind')!='pick' for p in a)) if c=='Live' else cost(a,b,free=o.get('free',2),lam=o.get('lam',3))
   cb=8*max(0,sum(p.get('kind')!='pick' for p in a)-sum(p.get('kind')!='pick' for p in b)) if c=='Live' else cost(b,a,free=o.get('free',2),lam=o.get('lam',3))
   result[mode][c]={'surrendered':[av,bv],'received':[bv,av],'roster_adjustment':[-ca,-cb],'net':[bv-av-ca,av-bv-cb]}
 return result

def cases():
 pick=lambda y,r,owner:next(p for p in PICK.values() if p['year']==y and p['round']==r and p['originalOwner']==owner)
 proposal=[P['05mx9'],P['06f1c'],pick(2027,5,'Shea Stadiums'),pick(2027,5,'Young Guns'),pick(2028,2,'Shea Stadiums')]
 out=[{'id':'Josuar negotiation','teams':['Shea Stadiums','The Sandlot Sluggers'],'a':proposal,'b':[P['06ps2']],'date':'2026-10-07','status':'Negotiation; not completed'}]
 for t in HISTORY['trades']:
  if t['id'] not in ['trade-export-005','trade-export-029','trade-export-039','trade-export-003','trade-export-004','trade-export-013','trade-export-018','trade-export-019','trade-export-025']:continue
  teams=list(dict.fromkeys(a['from'] for a in t['assets']));s=[[],[]]
  for a in t['assets']:
   if a['kind']=='player':p=P[a['fantraxId']]
   else:
    m=re.search(r'(202[789]) Draft Pick, Round ([1-5]) \((.+)\)',a['name']);p=pick(int(m[1]),int(m[2]),m[3])
   s[teams.index(a['from'])].append(p)
  out.append({'id':t['id'],'teams':teams,'a':s[0],'b':s[1],'date':t['date'],'status':'NOW stress test; THEN and REALIZED unestimated'})
 priority={'Josuar negotiation':0,'trade-export-005':1,'trade-export-029':2,'trade-export-039':3}
 return sorted(out,key=lambda c:priority.get(c['id'],4))

def main():
 cs=cases(); results=[]
 for c in cs:
  results.append({k:v for k,v in c.items() if k not in ['a','b']}|{'sends':[[p['name'] for p in c[x]] for x in ['a','b']],'identities':[[p['id'] for p in c[x]] for x in ['a','b']],'comparisons':compare(c['a'],c['b'])})
 sensitive={}
 tests={'Default':{},'Linear tail gamma 1':{'gamma':1},'Gamma 1.6':{'gamma':1.6},'3-year horizon':{'horizon':3},'5-year horizon':{'horizon':5},'Discount .80':{'discount':.80},'Discount .95':{'discount':.95},'Prospect success -25%':{'success':.75},'Prospect success +20%':{'success':1.2},'Superstar tail x.5':{'tail':.5},'Superstar tail x1.5':{'tail':1.5},'Rank only; no tool residual':{'scouting':False},'Replacement best FA':{'depth':1},'Replacement top10 median':{'depth':10},'No open roster spots':{'free':0},'Six open roster spots':{'free':6},'No capacity cost':{'lam':0},'Capacity cost 1':{'lam':1},'Capacity cost 6':{'lam':6},'Capacity cost 12':{'lam':12},'Prospect replacement rank250':{'prospect_floor':250},'Prospect replacement rank600':{'prospect_floor':600},'Future class -20%':{'class_quality':.8},'Future class +20%':{'class_quality':1.2},'Expected early slot':{'slot':'early'},'Expected late slot':{'slot':'late'},'Postdraft proxy after84':{'postdraft':84},'No supplemental star history':{'multi':False}}
 for label,o in tests.items():sensitive[label]={c['id']:{m:compare(c['a'],c['b'],**o)[m]['B']['net'] for m in MODES} for c in cs[:4]}
 audit={'players':len(P),'free_agents':sum(p['owner']=='Free agent' for p in P.values()),'qualified_free_agents':{r:sum(role(p)==r for p in FA) for r in FULL},'evaluated_free_agent_prospects':sum(p['owner']=='Free agent' and bool(p.get('prospect')) for p in P.values()),'draft_profiles':len(DRAFT),'draft_actual_pick_records':sum(bool(d.get('actualFypdPick')) for d in DRAFT),'annual_surplus_anchors':ANCHOR,'scale':SCALE,'category_denominators':DEN,'multiyear_ids':list(HIST),'replacement_examples':{r:[{'id':p['id'],'name':p['name'],'full_season_category_score':score(p)} for p in sorted([p for p in FA if role(p)==r],key=score,reverse=True)[:10]] for r in FULL}}
 assets={p['id']:p for c in cs for side in ['a','b'] for p in c[side]}
 asset_results=[{'id':p['id'],'name':p['name'],'type':'pick' if p.get('kind')=='pick' else 'prospect' if p.get('prospect') and volume(p)<(250 if role(p)=='H' else 100) else 'MLB','probabilities':probabilities(p) if p.get('prospect') else None,'values':{m:{c:old_value(p,m) if c=='Live' else asset_value(p,m,c) for c in ['Live','A','B','C']} for m in MODES}} for p in assets.values()]
 invariants={'unique_player_ids':len(P)==len(DB['players']),'unique_pick_ids':len(PICK)==len(DB['picks']),'constant_stream_same_value_across_modes':max(sum(weights(m)) for m in MODES)-min(sum(weights(m)) for m in MODES)<1e-9,'upper_tail_reward_at_equal_mean':(.5*utility(0,1.35)+.5*utility(8,1.35))>(.5*utility(3,1.35)+.5*utility(5,1.35)),'smooth_cost_at_three':abs(cost([], [P['03wha']]*3,lam=3)-cost([], [P['03wha']]*2,lam=3))<3,'roster_order_invariant':abs(cost(cs[0]['a'],cs[0]['b'])-cost(list(reversed(cs[0]['a'])),cs[0]['b']))<1e-9,'roster_cost_separate_from_asset_value':'cost' not in asset_value.__code__.co_names,'package_values_order_invariant':abs(sum(asset_value(p,'neutral') for p in cs[0]['a'])-sum(asset_value(p,'neutral') for p in reversed(cs[0]['a'])))<1e-9,'production_model_sha256':hashlib.sha256((ROOT/'inputs/production-trade-model.js').read_bytes()).hexdigest()}
 assert all(v for v in invariants.values())
 output={'as_of':'2026-10-07','status':'OFFLINE DESIGN EXPERIMENT; NOT A CALIBRATED FORECAST','audit':audit,'cases':results,'assets':asset_results,'sensitivity':sensitive,'invariants':invariants,'smooth_curve':[{'net_incoming_players':n,'cost':cost([], [P['03wha']]*n)} for n in range(-0,10)],'star_health_sensitivity':{P[i]['name']:{str(h):{m:asset_value(P[i],m,'B',health=h) for m in MODES} for h in [.6,.8,1]} for i in HIST}}
 (ROOT/'results.json').write_text(json.dumps(output,indent=2));(ROOT/'verified-star-history.json').write_text(json.dumps(HIST,indent=2))
 print(json.dumps({'audit':audit,'key_cases':[{ 'id':c['id'],'sends':c['sends'],'neutral':c['comparisons']['neutral']} for c in results[:4]]},indent=2))
if __name__=='__main__':main()
