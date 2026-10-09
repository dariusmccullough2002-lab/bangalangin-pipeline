"""Rate-aging-isolated RBI and one-year conditional-GS path-value sensitivities."""
import sys
from pathlib import Path
HERE=Path(__file__).resolve().parent;sys.path.insert(0,str(HERE.parent))
from continuation import *
from opportunity_followup import adjust,score

def utility_case_validation():
 out=[]
 for rr,xs in [('P',pcases),('H',hcases+[z for z in hextra if z['anchor']+1!=2020])]:
  for z in xs:
   role=z['role'];key='PA' if role=='H' else 'IP';c=z['components']['past_only'];p,work,conds,_=conditional_states(c,role);forecast=z['past_only'];meanutil=r.utility(r.surplus(forecast,role));pathutil=0
   for s in range(3):
    st={k:(v*work[s]/forecast[key] if forecast[key] else 0) for k,v in forecast.items()}
    if role=='H':st=v.reconcile(st)
    else:st['QA3']=conds[s].get('QA3',0)
    pathutil+=p[s]*r.utility(r.surplus(st,role))
   actual=r.utility(r.surplus(z['actual'],role));out.append({'family':rr,'mlbam_id':z['mlbam_id'],'anchor':z['anchor'],'role':role,'groups':z['groups'],'actual_utility':actual,'mean_utility':meanutil,'path_utility':pathutil})
 scores={}
 for fam in ['P','H']:
  ys=[z for z in out if z['family']==fam];scores[fam]={}
  for g in sorted({g for z in ys for g in z['groups']}):
   xs=[z for z in ys if g in z['groups']];scores[fam][g]={k:metric([(z[k],z['actual_utility']) for z in xs]) for k in ['mean_utility','path_utility']}
 put('Annual_Utility_Validation.json',{'scores':scores,'scope':'One-year realized fantasy utility; frozen category rates, floors and normalizers retain original provenance. No historical eight-year realized-price or independently calibrated talent distributions.'});put('Annual_Utility_Cases.json.gz',out)

def correct_frozen():
 xs=read(HERE/'Opportunity_Cases.json.gz');bys={(z['mlbam_id'],z['anchor']):z for z in xs};frozen=[]
 for z in read(PARENT.parent/'Historical_Cases.json'):
  q=copy.deepcopy(bys[z['mlbam_id'],z['anchor']]);q['baseline']=z['baseline']
  for name in ['linear_SP','past_only','linear_GS','blend_GS','pooled_RP_QA3']:
   if name=='linear_SP':ratio=q[name]['IP']/q['baseline']['IP'];qa=q[name]['QA3']
   else:ratio=q['components'][name]['IP']/q['baseline']['IP'];qa=q['components'][name]['QA3']
   q[name]={k:v*ratio for k,v in q['baseline'].items()};q[name]['QA3']=qa
  frozen.append(q)
 data=read(HERE/'Opportunity_Validation.json');data['frozen94']=score(frozen);put('Opportunity_Validation.json',data)

def run():
 rb={z['id']:z for z in read(HERE/'RBI_Aging_Current.json.gz')};cur={z['id']:z for z in csv.DictReader((HERE/'Opportunity_Current.csv').open())};mn=read(HERE/'Opportunity_Current_Manifest.json');qgs=mn['RP_QA3_per_GS'];rpq=mn['RP_pure_relief_QA3_rate'];oldrows={z['id']:z for z in read(HERE/'Path_League_Impact.json.gz')};rows=[];annualrows=[]
 for z in league:
  row={'id':z['id'],'name':z['name'],'role':z['role'],'status':z['status'],'baseline':z['baseline_values'],'prior_mean':z['variants']['joint_principal']['values'],'variants':{}}
  if z['status']!='supported_MLB':
   for name in ['paths_RBI_frozen_aging','paths_linear_GS','paths_blend_GS','paths_pooled_RP_QA3']:row['variants'][name]={'values':z['baseline_values']}
   rows.append(row);continue
  role=z['role'];key='PA' if role=='H' else 'IP';family='H' if role=='H' else 'P';pplayer=old.players[z['id']];ps,_=m.paths(pplayer);ma=v.mlb_role_paths(pplayer,role)[1];bp=np.array([a[0] for a in ps[:3]]);baseannual=z['variants']['joint_principal']['annual'];basec=z['variants']['joint_principal']['components'];P=np.array([marg(c,role) for c in basec]);K=[np.array(a) for a in oldrows[z['id']]['transition_kernels']]
  for name in ['paths_RBI_frozen_aging','paths_linear_GS','paths_blend_GS','paths_pooled_RP_QA3']:
   E=[]
   for t in range(8):
    c=basec[t]
    if role!='H' and t==0 and name!='paths_RBI_frozen_aging':
     g=float(cur[z['id']]['linear_GS_conditional_GS']);c=adjust(c,g,qgs,rpq,name=='paths_blend_GS',name=='paths_pooled_RP_QA3')
    p,work,conds,_=conditional_states(c,role);per=[];base_stats=[]
    for j in range(3):
     factor=ma['outcome_state_projections'][j][t][key]/ma['annual_projection'][t][key] if ma['annual_projection'][t][key] else 0;us=[]
     for s in range(3):
      st={k:(v*work[s]/baseannual[t][key]*factor if baseannual[t][key] else 0) for k,v in baseannual[t].items()}
      if role=='H':
       st=v.reconcile(st)
       if name=='paths_RBI_frozen_aging':st['RBI']=min(4*st['PA'],max(st['HR'],st['RBI']*rb[z['id']]['rate_ratio_for_frozen_aging_horizons']));assert st['RBI']>=st['HR']-1e-7
      else:st['QA3']=conds[s].get('QA3',0)*factor
      future=role if role=='H' or s==0 else 'RP' if s==1 else 'SP';us.append(r.utility(r.surplus(st,future)))
      if j==1:base_stats.append(st)
     per.append(us)
    E.append(per)
    if name=='paths_RBI_frozen_aging' or (role!='H' and t==0):
     a={'id':z['id'],'name':z['name'],'role':role,'variant':name,'horizon':t+1};a.update({k:float(sum(p[s]*base_stats[s].get(k,0) for s in range(3))) for k in baseannual[t]});annualrows.append(a)
   E=np.array(E);values={};sd={}
   for mode in r.MODES:
    discount={'neutral':.88,'balanced':.88,'contender':.75,'rebuild':.94}[mode];w=np.array([discount**t for t in range(8)]);w*=sum(old.weights('neutral'))/sum(w);mu=second=0
    for j in range(3):a,b=moments(P,K,E[:,j,:],w);mu+=bp[j]*a;second+=bp[j]*b
    for pr,path in ps[3:]:val=float(np.array(path)@w);mu+=pr*val;second+=pr*val*val
    values[mode]=r.DISPLAY*mu;sd[mode]=r.DISPLAY*math.sqrt(max(0,second-mu*mu))
   row['variants'][name]={'values':values,'dispersion':sd}
  rows.append(row)
 for name in ['baseline','prior_mean','paths_RBI_frozen_aging','paths_linear_GS','paths_blend_GS','paths_pooled_RP_QA3']:
  def key(z):return z[name] if name in ['baseline','prior_mean'] else z['variants'][name]['values']
  for rank,z in enumerate(sorted([a for a in rows if key(a).get('neutral') is not None],key=lambda a:-key(a)['neutral']),1):z.setdefault('ranks',{})[name]=rank
 flat=[]
 for z in rows:
  q={k:z[k] for k in ['id','name','role','status']}
  for name in ['baseline','prior_mean']:
   for mode,vv in z[name].items():q[name+'_'+mode]=vv
  for name,va in z['variants'].items():
   for mode,vv in va['values'].items():q[name+'_'+mode]=vv;q[name+'_delta_'+mode]=vv-z['baseline'][mode] if vv is not None and z['baseline'][mode] is not None else None;q[name+'_sd_'+mode]=va.get('dispersion',{}).get(mode)
  for name,rank in z.get('ranks',{}).items():q[name+'_rank']=rank
  flat.append(q)
 writecsv('Candidate_League_Impact.csv',flat);put('Candidate_League_Impact.json.gz',rows);writecsv('Candidate_Annual_Production.csv',annualrows)
 utility_case_validation();correct_frozen();print('Completed additional candidate values',len(rows),flush=True)
if __name__=='__main__':run()
