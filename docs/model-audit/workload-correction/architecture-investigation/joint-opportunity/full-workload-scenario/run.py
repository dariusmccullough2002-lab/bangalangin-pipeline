"""Research-only fixed scenario experiment; cached inputs, no collection/deployment.

Run with the preserved recovery model directory and beta-unpacked.json arguments.
Annual high usage is not a clinical availability certificate. Future labels are
used only inside training/evaluation, never in inputs to prediction functions.
"""
import os
os.environ.setdefault('OMP_NUM_THREADS','1')
os.environ.setdefault('OPENBLAS_NUM_THREADS','1')
import sys, importlib.util, json, gzip, csv, hashlib, copy
from pathlib import Path
from collections import Counter
import numpy as np
import joblib
from sklearn.ensemble import HistGradientBoostingClassifier, HistGradientBoostingRegressor
from sklearn.pipeline import make_pipeline
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import Ridge, LogisticRegression

HERE=Path(__file__).resolve().parent
PRIOR=HERE.parent/'targeted-repair'
# Older helper entrypoints expect an expanded JSON alongside the tracked gzip.
# Materialize only absent read caches, with exact bytes; never overwrite inputs.
for gz in (HERE.parent.parent.parent).rglob('*.json.gz'):
    if HERE in gz.parents:continue
    expanded=gz.with_suffix('')
    if not expanded.exists():expanded.write_bytes(gzip.decompress(gz.read_bytes()))
spec=importlib.util.spec_from_file_location('preserved_targeted_engine',PRIOR/'engine.py')
e=importlib.util.module_from_spec(spec);spec.loader.exec_module(e)
PROTOCOL=json.loads((HERE/'Protocol_Freeze.json').read_text())
ROLES=['everyday','platoon','bench','starter','reliever','swingman','uncertain']
STATES=['absent','retained_high_usage','retained_reduced','changed','unknown_role']
SLOTS=PROTOCOL['structural_scenario_slots']

def put(name,a):
    b=json.dumps(a,allow_nan=False,default=lambda x:x.item() if isinstance(x,np.generic) else x,indent=None).encode()
    (HERE/name).write_bytes(gzip.compress(b,mtime=0) if name.endswith('.gz') else b)

def csvout(name,rows):
    with (HERE/name).open('w',newline='') as f:
        w=csv.DictWriter(f,list(dict.fromkeys(k for a in rows for k in a)));w.writeheader();w.writerows(rows)

def role_from(o,family):
    if not o['exposure']:return 'absent' if o['exposure']==0 else 'uncertain'
    gp=o['GP'];gs=o['GS']
    if family=='H':
        if not gp:return 'uncertain'
        depth=o['exposure']/gp
        return 'everyday' if depth>=3.8 else 'platoon' if depth>=2.8 else 'bench'
    if not gp or gs is None:return 'uncertain'
    share=gs/gp
    return 'starter' if share>=.8 else 'reliever' if share<=.1 else 'swingman'

def forecast_role(z):
    # No future observation may be queried in this function.
    for year in range(z['year'],z['year']-3,-1):
        o=e.observation(z,year)
        if o['exposure'] and o['exposure']>0:
            rr=role_from(o,'H' if z['role']=='H' else 'P')
            if rr=='uncertain' and z['role']=='H' and o['exposure']>=400:
                return 'everyday','PA-only incumbent proxy; GP unknown'
            return rr,'latest positive verified MLB usage; prior role scenario if latest zero'
    return 'uncertain','insufficient demonstrated role; hypothetical MLB role scenario only'

def full_proxy(o,rr,year):
    if year==2020 or rr in {'uncertain','absent'} or not o['GP']:return False
    if rr=='reliever':return o['GP']-(o['GS'] or 0)>=60
    return o['GP']>=({'everyday':145,'platoon':100,'bench':70,'reliever':60,'swingman':40}.get(rr,0)) if rr!='starter' else bool(o['GS'] and o['GS']>=30)

def target_label(z):
    # Explicit future-only outcome labels. Not called by predict().
    o=e.observation(z|{'year':z['year']+1},z['year']+1);rr=role_from(o,'H' if z['role']=='H' else 'P');fr,_=forecast_role(z)
    if o['exposure'] is None:return None
    if o['exposure']==0:s=0
    elif rr=='uncertain' or fr=='uncertain':s=4
    elif rr!=fr:s=3
    elif full_proxy(o,rr,z['year']+1):s=1
    else:s=2
    return {'observation':o,'target_role':rr,'state':s,'proxy_eligible':s==1}

def inputs(z):
    x,d=e.fz(z);rr,_=forecast_role(z)
    return np.r_[x,[rr==v for v in ROLES]],rr,d

def depths(z):
    _,_,d=inputs(z)
    if z['role']=='H':return d['depth'],0.
    # Exact preserved per-appearance estimator: frozen asof evidence, no talent refit.
    sd=d['depth'];rows=[]
    for year,w in zip(range(z['year'],z['year']-3,-1),[3,2,1]):
        o=e.observation(z,year)
        if o['exposure'] and o['GP'] and o['GS']==0:rows.append((o['exposure'],o['GP'],w))
    rd=(sum(ip*w for ip,n,w in rows)+10)/(sum(n*w for ip,n,w in rows)+10)
    return float(sd),float(np.clip(rd,.25,3))

def slot_work(z,slots):
    sd,rd=depths(z)
    return slots.get('GP',0)*sd if z['role']=='H' else slots.get('GS',0)*sd+slots.get('RA',0)*rd

def structural(z):
    rr,_=forecast_role(z)
    if rr!='uncertain':return dict(SLOTS[rr]),None
    # An unknown role does not receive an everyday capacity or an arrival claim.
    return dict(SLOTS['bench' if z['role']=='H' else 'swingman']),'hypothetical bench/swingman fallback; broad role uncertainty'

def fitted_slots(model,z):
    X,rr,_=inputs(z);base,fb=structural(z);regs=model['full'].get(rr)
    if not regs:return base,fb or 'insufficient high-usage training rows; transparent role scenario'
    slots={k:float(np.clip(reg.predict(X[None,:])[0],0,162 if k=='GP' else 36 if k=='GS' else 85)) for k,reg in regs.items()}
    return slots,'fitted high-usage proxy; full medical availability unverified'

def fit(asof,fam):
    path=HERE/f'model-{fam}-{asof}.joblib'
    if path.exists():return joblib.load(path)
    raw=e.training(asof,calendar=fam=='H',family=fam)
    rows=[]
    for a in raw:
        lab=target_label(a['z'])
        if lab is not None and a['year']!=2020:
            X,rr,_=inputs(a['z']);rows.append((a,lab,X,rr))
    X=np.stack([r[2] for r in rows]);core=np.array([r[0]['z']['id']%5 in [1,2,3] for r in rows]);cal=~core
    y=np.array([r[1]['state'] for r in rows]);weights=np.array([r[0]['weight'] for r in rows])
    clf=HistGradientBoostingClassifier(**e.settings).fit(X[core],y[core],sample_weight=weights[core])
    model={'asof':asof,'family':fam,'classifier':clf,'calibrator':None,'full':{},'ratios':{},'empirical':{},'manifest':{}}
    if cal.sum()>=100 and len(set(y[cal]))==len(STATES) and min(np.bincount(y[cal],minlength=5))>=10:
        p=clf.predict_proba(X[cal]);model['calibrator']=LogisticRegression(C=1,max_iter=1000).fit(np.log(np.clip(p,1e-6,1)),y[cal],sample_weight=weights[cal])
    support={}
    for rr in ROLES[:-1]:
        mask=core&np.array([lab['proxy_eligible'] and rrole==rr for _,lab,_,rrole in rows]);support[rr]=int(mask.sum())
        if mask.sum()<60:continue
        keys=['GP'] if fam=='H' else ['GS','RA'];model['full'][rr]={}
        for key in keys:
            values=np.array([lab['observation']['GP'] if key=='GP' else lab['observation']['GS'] if key=='GS' else (lab['observation']['GP'] or 0)-(lab['observation']['GS'] or 0) for _,lab,_,_ in rows])
            model['full'][rr][key]=HistGradientBoostingRegressor(loss='squared_error',**e.settings).fit(X[mask],values[mask],sample_weight=weights[mask])
    for kind in ['structural','fitted']:
        den=np.array([slot_work(a['z'],structural(a['z'])[0] if kind=='structural' else fitted_slots(model,a['z'])[0]) for a,_,_,_ in rows])
        vals=np.array([a['raw_value'] for a,_,_,_ in rows]);ratio=vals/np.maximum(1,den)
        for state in range(1,5):
            globalmask=core&(y==state)
            gm=float(vals[globalmask].sum()/max(1,den[globalmask].sum()))
            for rr in ROLES:
                mask=globalmask&np.array([rrole==rr for _,_,_,rrole in rows]);n=int(mask.sum())
                emp=(float(vals[mask].sum())+30*gm)/(float(den[mask].sum())+30)
                model['empirical'][kind,rr,state]=emp
                if n>=60:
                    reg=make_pipeline(SimpleImputer(strategy='median',add_indicator=True),StandardScaler(),Ridge(alpha=250))
                    reg.fit(X[mask],ratio[mask],ridge__sample_weight=(weights*den**2)[mask]);model['ratios'][kind,rr,state]=reg
    model['manifest']={'asof':asof,'latest_target':max(a['year'] for a,_,_,_ in rows),'rows':len(rows),'core_rows':int(core.sum()),'cal_rows':int(cal.sum()),'states':dict(Counter(STATES[lab['state']] for _,lab,_,_ in rows)),'full_proxy_support':support,'calibrated':model['calibrator'] is not None,'clinical_full_availability_labels':False,'unknown_role_rows':int((y==4).sum()),'feature_sha256':hashlib.sha256(X.tobytes()).hexdigest(),'target_sha256':hashlib.sha256(y.tobytes()).hexdigest(),'protocol_sha256':hashlib.sha256((HERE/'Protocol_Freeze.json').read_bytes()).hexdigest()}
    assert model['manifest']['latest_target']<=min(asof,2025)
    e.legacy.prior.checkpoint(model,path)
    print('FIT',fam,asof,model['manifest']['rows'],support,flush=True)
    return model

def predict(model,z):
    X,rr,d=inputs(z);X=X[None,:];clf=model['classifier'];ps=clf.predict_proba(X)[0];classes=clf.classes_
    if model['calibrator'] is not None:
        cal=model['calibrator'];ps=cal.predict_proba(np.log(np.clip(ps[None,:],1e-6,1)))[0];classes=cal.classes_
    p=np.zeros(5)
    for j,c in enumerate(classes):p[int(c)]=ps[j]
    out={'role':rr,'probabilities':{s:float(p[j]) for j,s in enumerate(STATES)},'participation':float(1-p[0]),'role_retention_given_active':float((p[1]+p[2])/(1-p[0])) if p[0]<1 else 0,'medical_cause_identified':False}
    for kind in ['structural','fitted']:
        slots,fb=structural(z) if kind=='structural' else fitted_slots(model,z);full=slot_work(z,slots);parts={};ratios={}
        for state in range(1,5):
            reg=model['ratios'].get((kind,rr,state));ratio=float(reg.predict(X)[0]) if reg is not None else model['empirical'][kind,rr,state]
            # Changed roles can legitimately exceed the specified role scenario.
            # Bound absolute workload, never an arbitrary common retention ratio.
            ratio=float(np.clip(ratio,0,(754 if z['role']=='H' else 251)/max(full,1e-12)));ratios[STATES[state]]=ratio;parts[STATES[state]]=float(p[state]*full*ratio)
        expected=sum(parts.values());q=1-p[0]
        # Telescoping attribution. Order is declared, not a causal decomposition.
        loss_absence=-p[0]*full;loss_reduced=p[2]*full*(ratios['retained_reduced']-1);change=p[3]*full*(ratios['changed']-1);high=p[1]*full*(ratios['retained_high_usage']-1);unknown=p[4]*full*(ratios['unknown_role']-1)
        out[kind]={'slots':slots,'full_role_workload':full,'fallback':fb,'ratios':ratios,'contributions':parts,'expected':expected,'conditional_active':expected/q if q else 0,'absence_adjustment':float(loss_absence),'retained_reduced_adjustment':float(loss_reduced),'changed_role_adjustment':float(change),'high_usage_adjustment':float(high),'unknown_role_adjustment':float(unknown),'reconciliation_error':float(full+loss_absence+loss_reduced+change+high+unknown-expected)}
        assert abs(out[kind]['reconciliation_error'])<1e-8
    return out

def groups(z,original=()):
    rr,_=forecast_role(z);c=e.cohort_key(z);out=list(original)+['all',z['role'],rr,c]
    if z['x'][13]>=33:out+=['aging33plus']
    if rr=='uncertain' or c in ['unstable','unknown']:out+=['uncertain_role']
    return list(dict.fromkeys(out))

def evaluate():
    cases=e.read(PRIOR/'Chronological_Cases.json.gz');results=[];coverage=[]
    for year in sorted({a['anchor'] for a in cases}):
        for fam in ['H','P']:
            xs=[a for a in cases if a['anchor']==year and (a['role']=='H')==(fam=='H') and a['target_season']!=2020]
            if not xs:continue
            model=fit(year,fam)
            for a in xs:
                z=e.historical_z(a['mlbam_id'],year,a['role']);c=predict(model,z);lab=target_label(z)
                assert lab is not None and abs(lab['observation']['exposure']-a['actual'])<1e-7
                row={k:a[k] for k in ['mlbam_id','name','anchor','target_season','role','actual','production','frozen_hybrid','strong_prior','repair']}
                row.update(groups=groups(z,a['groups']),evaluation='exposed exploratory',previous_evaluation=a['evaluation'],target_role=lab['target_role'],actual_state=STATES[lab['state']],proxy_eligible=lab['proxy_eligible'],forecast_role=c['role'],participation=c['participation'],prior_participation=a['participation'],prior_conditional_active=a['conditional_active'],conditional_active=c['fitted']['conditional_active'],role_retention_given_active=c['role_retention_given_active'],actual_active=int(a['actual']>0),component=c)
                for kind in ['structural','fitted']:row['full_'+kind]=c[kind]['full_role_workload'];row['expected_'+kind]=c[kind]['expected']
                results.append(row)
            coverage.append(model['manifest'])
            print('SCORE exploratory',year,fam,len(xs),flush=True)
    put('Chronological_Cases.json.gz',results);put('Training_Coverage.json',coverage)
    csvout('Chronological_Player_Comparisons.csv',[{k:v for k,v in a.items() if k not in {'component','groups'}}|{'groups':'|'.join(a['groups'])} for a in results])
    methods=['production','frozen_hybrid','strong_prior','repair','expected_structural','expected_fitted'];metrics=[];calibration=[]
    for window in ['all_exposed','pre2026_exposed','2026_exposed']:
        xs=[a for a in results if window=='all_exposed' or (a['target_season']==2026)==(window=='2026_exposed')]
        for fam in ['H','P']:
            fs=[a for a in xs if (a['role']=='H')==(fam=='H')]
            for g in sorted({g for a in fs for g in a['groups']}):
                ys=[a for a in fs if g in a['groups']]
                for mode in ['expected_all','conditional_high_usage_proxy']:
                    zs=ys if mode=='expected_all' else [a for a in ys if a['proxy_eligible']]
                    for method in methods if mode=='expected_all' else ['full_structural','full_fitted']:
                        metrics.append({'window':window,'family':fam,'group':g,'evaluation':mode,'method':method,**e.metric([(a[method],a['actual']) for a in zs])})
                active=[a for a in ys if a['actual_active']]
                calibration.append({'window':window,'family':fam,'group':g,'n':len(ys),'predicted_participation':float(np.mean([a['participation'] for a in ys])),'observed_participation':float(np.mean([a['actual_active'] for a in ys])),'Brier':float(np.mean([(a['participation']-a['actual_active'])**2 for a in ys])),'prior_Brier':float(np.mean([(a['prior_participation']-a['actual_active'])**2 for a in ys])),'conditional_active_bias':float(np.mean([a['conditional_active']-a['actual'] for a in active])) if active else None,'prior_conditional_active_bias':float(np.mean([a['prior_conditional_active']-a['actual'] for a in active])) if active else None,'joint_state_Brier':float(np.mean([sum((a['component']['probabilities'][s]-int(a['actual_state']==s))**2 for s in STATES) for a in ys])),'role_retention_Brier_known_active':float(np.mean([(a['role_retention_given_active']-int(a['actual_state'].startswith('retained')))**2 for a in active if a['actual_state']!='unknown_role'])) if any(a['actual_state']!='unknown_role' for a in active) else None})
    csvout('Chronological_Validation.csv',metrics);csvout('Probability_Calibration.csv',calibration)
    bins=[];deciles=[]
    for fam in ['H','P']:
        xs=[a for a in results if (a['role']=='H')==(fam=='H')]
        for state in STATES:
            for b in range(10):
                ys=[a for a in xs if min(9,int(a['component']['probabilities'][state]*10))==b]
                bins.append({'family':fam,'state':state,'bin':b,'n':len(ys),'predicted':float(np.mean([a['component']['probabilities'][state] for a in ys])) if ys else None,'observed':float(np.mean([a['actual_state']==state for a in ys])) if ys else None})
        ordered=sorted(xs,key=lambda a:e.observation(e.historical_z(a['mlbam_id'],a['anchor'],a['role']),a['anchor'])['exposure'] or 0)
        for dec,inds in enumerate(np.array_split(np.arange(len(ordered)),10),1):
            ys=[ordered[i] for i in inds]
            for method in methods:deciles.append({'family':fam,'historical_workload_decile':dec,'method':method,**e.metric([(a[method],a['actual']) for a in ys])})
    csvout('State_Calibration_Bins.csv',bins);csvout('Workload_Deciles.csv',deciles)
    gates=e.read(PRIOR/'Release_Gates.json');put('Preserved_Release_Gates.json',gates)
    # Re-evaluate exact inherited populations/limits without redefining cohorts.
    original={(a['mlbam_id'],a['anchor']) for a in e.read(HERE.parent.parent.parent/'Historical_Cases.json')}
    expanded={(a['mlbam_id'],a['anchor'],a['role']) for a in e.read(HERE.parent/'first-year-repair/P_Cases.json.gz')[:1084]}
    retrospective=[a for a in results if a['previous_evaluation']=='exposed retrospective']
    populations={'original94':[a for a in retrospective if a['role']!='H' and (a['mlbam_id'],a['anchor']) in original],'expandedP':[a for a in retrospective if (a['mlbam_id'],a['anchor'],a['role']) in expanded],'H_standard':[a for a in retrospective if a['role']=='H']}
    populations['originalSP']=[a for a in populations['original94'] if a['role']=='SP'];populations['additional_expandedSP']=[a for a in populations['expandedP'] if a['role']=='SP'];populations['additional_youngSP']=[a for a in populations['expandedP'] if a['role']=='SP' and 'young_SP' in a['groups']];populations['additional_stableSP_vs_strong']=[a for a in populations['expandedP'] if 'stable_rotation' in a['groups']];populations['additional_durableH_vs_strong']=[a for a in populations['H_standard'] if 'durable_four_years' in a['groups']]
    out=[]
    hitter_original=e.read(HERE.parent/'roster-opportunity/Integrated_H_Cases.json.gz')
    hidx={(a['mlbam_id'],a['anchor']):a for a in hitter_original}
    for method in ['expected_structural','expected_fitted']:
        for g in gates['gates']:
            if g['gate'] in populations:
                v=e.metric([(a[method],a['actual']) for a in populations[g['gate']]])['MAE'];out.append({'method':method,'gate':g['gate'],'n':len(populations[g['gate']]),'value':v,'limit':g['limit'],'pass':v is not None and v<=g['limit']})
            elif g['gate'].startswith('additional_') and 'anchor_' in g['gate']:
                year=int(g['gate'].split('_')[-2]);fam='P' if '_P_' in g['gate'] else 'H';ys=[a for a in (populations['expandedP'] if fam=='P' else populations['H_standard']) if a['anchor']==year]
                clusters={}
                for a in ys:clusters.setdefault(a['mlbam_id'],[]).append(abs(a[method]-a['actual'])-abs(a['strong_prior']-a['actual']))
                arr=list(clusters.values());sizes=np.array([len(v) for v in arr]);sums=np.array([sum(v) for v in arr]);rng=np.random.default_rng(2718);ix=rng.integers(0,len(arr),(1500,len(arr)));ci=np.quantile(sums[ix].sum(1)/sizes[ix].sum(1),[.025,.975]).tolist();v=e.metric([(a[method],a['actual']) for a in ys])['MAE'];old=e.metric([(a['strong_prior'],a['actual']) for a in ys])['MAE'];out.append({'method':method,'gate':g['gate'],'n':len(ys),'value':v,'prior':old,'paired_player_cluster95':ci,'rule':'fail if MAE>1.1*prior and paired95 lower>0','pass':not(v>1.1*old and ci[0]>0)})
            elif g['gate']=='comparable_high_RBI_bias':
                ys=[a for a in retrospective if 'high_RBI_comparable62' in a['groups']];errors=[]
                for a in ys:
                    olda=hidx[a['mlbam_id'],a['anchor']];b=olda['baseline'];errors.append(b['RBI']*a[method]/b['PA']-olda['actual'].get('RBI',0))
                v=float(np.mean(errors));out.append({'method':method,'gate':g['gate'],'n':len(ys),'value':v,'limit':g['limit'],'pass':abs(v)<=g['limit']})
    out.extend([{'gate':'untouched_evaluation_sample','pass':False},{'gate':'verified_historical_daily_availability_and_role','pass':False},{'gate':'historical_allocator_accuracy_identifiable','pass':False}]);put('Release_Gates.json',{'gates':out,'all_gates_pass':False,'numerical_release_authorized':False,'model_selection_performed':False})
    return results

def roster_inputs():
    membership={};budgets={}
    for p in (PRIOR/'verified').glob('roster-*.json.gz'):
        team=int(p.name.split('-')[1].split('.')[0])
        for a in e.read(p)['roster']:membership.setdefault(a['person']['id'],set()).add(team)
    rosters={i:next(iter(ts)) for i,ts in membership.items() if len(ts)==1}
    for fam,group in [('H','hitting'),('P','pitching')]:
        for a in e.read(PRIOR/'verified'/f'team-{group}2026.json.gz')['stats'][0]['splits']:
            s=a['stat'];fac=162/max(1,float(s['gamesPlayed']));b=budgets.setdefault(a['team']['id'],{})
            if fam=='H':b['PA']=float(s['plateAppearances'])*fac
            else:b.update(GS=float(s['gamesStarted'])*fac,IP=float(s['outs'])/3*fac)
    return rosters,budgets

def component_for(c,z,pred,kind):
    # Preserve existing talent/per-appearance and QA3 estimators; alter workload only.
    key='PA' if z['role']=='H' else 'IP';out=copy.deepcopy(c);target=pred[kind]['expected'];oldq=1-out['probabilities']['absent'];q=pred['participation']
    # The opportunity mixture supplies absence. Prior probabilities supply only
    # relative rate-role composition, normalized *within* active outcomes.
    for role in ['part_time','regular'] if key=='PA' else ['SP','RP']:
        out['probabilities'][role]=out['probabilities'][role]/oldq*q if oldq else q/2
    out['probabilities']['absent']=1-q
    if key=='PA':
        cond=target/q if q else 0
        for state in out['conditional'].values():state['PA']=cond
        out.update(PA=target,conditional_PA=cond,conditional_part_PA=cond,conditional_regular_PA=cond)
    else:
        source=sum(out['probabilities']['RP' if st=='1' else 'SP']*s['IP'] for st,s in out['conditional'].items())
        scale=target/source if source else 0
        for state in out['conditional'].values():
            state['GS']=min(36,state['GS']*scale);state['RA']=min(85-state['GS'],state['RA']*scale)
            state['IP']=state['GS']*state['IP_per_start']+state['RA']*state['IP_per_relief']
            state['QA3']=min(state['IP']/5,state['GS']+state['RA'],state['QA3']*scale)
        for k in ['IP','GS','RA','QA3']:out[k]=sum(out['probabilities']['RP' if st=='1' else 'SP']*s[k] for st,s in out['conditional'].items())
    # The scenario's joint probabilities are reported separately. This adapter
    # only preserves the prior conditional composition for rate/allocator QA.
    out['opportunity_layer']['scenario_joint_probabilities']=pred['probabilities'];out['opportunity_layer']['absence_applied_count']=1
    out['opportunity_layer']['participation_probability']=q
    out['opportunity_layer']['healthy_role_capacity']=pred[kind]['slots'].get('GP',pred[kind]['slots'].get('GS',0));out['opportunity_layer']['conditional_active_workload']=target/pred['participation'] if pred['participation'] else 0
    out['opportunity_layer']['count_feasibility_adjustment']=out[key]-target
    out['opportunity_layer']['probability_adapter_note']='Scenario absence applied once; prior within-active rate-role composition only. Count bounds are a separately attributed adapter sensitivity, not a validated candidate adjustment.'
    return out

def current():
    assets=e.read(PRIOR/'Repair_League.json.gz');zs=[];preds=[]
    models={f:fit(2026,f) for f in ['H','P']}
    for a in assets:
        p=e.old.players[a['id']];rr=a['role'];hs=e.v.seasons(p,rr);z={'id':a['mlbam_id'],'year':2026,'role':rr,'history_override':hs,'x':e.base['features'](hs,rr,2026,a['mlbam_id']),'bounded_x':e.base['features'](hs,rr,2026,a['mlbam_id'],True)}
        zs.append(z);preds.append(predict(models['H' if rr=='H' else 'P'],z))
    rosters,budgets=roster_inputs();rows=[];allstats=[];ledgers=[];decomp=[];evidence=e.read(PRIOR/'Availability_Evidence.json')
    for kind in ['structural','fitted']:
        components=[]
        for a,z,c in zip(assets,zs,preds):
            template=copy.deepcopy(a['before_roster'])
            if z['role']!='H':
                # The saved pre-roster opportunity template has QA3 placeholders.
                # Restore frozen league-rule yields from the completed prior replay.
                for st,s in template['conditional'].items():
                    old=a['component']['conditional'][st];n=old['GS']+old['RA'];yield0=old['QA3']/n if n else 0
                    s['QA3']=min(s['IP']/5,(s['GS']+s['RA'])*yield0)
                template['QA3']=sum(template['probabilities']['RP' if st=='1' else 'SP']*s['QA3'] for st,s in template['conditional'].items())
            components.append(component_for(template,z,c,kind))
        allocated,ledger=e.allocate_verified(components,zs,rosters,budgets);ledgers.extend([a|{'candidate':kind} for a in ledger])
        for a,z,c,pre,post in zip(assets,zs,preds,components,allocated):
            key='PA' if z['role']=='H' else 'IP';p=c[kind];o=e.observation(z,2026);med=e.apply_verified_availability(post,z,evidence);role,reason=forecast_role(z);sd,rd=depths(z)
            final=med[key];stats=e.legacy.prior.stats(a['production'],med,z['role'],z)
            if key=='IP':
                for k in ['SV','HLD']:stats[k]=min(stats.get(k,0),med['RA'])
            # Full-role production uses the same independent rate adapter and is
            # explicitly hypothetical, never fed to dynasty valuation.
            fullc=copy.deepcopy(pre);ratio=p['full_role_workload']/max(1e-12,pre[key])
            for k in ['PA'] if key=='PA' else ['IP','GS','RA','QA3']:fullc[k]*=ratio
            if key=='IP':
                fullc['GS']=p['slots'].get('GS',0);fullc['RA']=p['slots'].get('RA',0)
                # QA3 yields stay frozen; scenario counts, not a workload-only
                # rescaling of the old starts count, define full-role production.
                sd0=pre['IP_per_start'];rd0=pre['IP_per_relief']
                spqa=pre['conditional']['2']['QA3']/max(1e-12,pre['conditional']['2']['GS']+pre['conditional']['2']['RA'])
                rpqa=pre['conditional']['1']['QA3']/max(1e-12,pre['conditional']['1']['GS']+pre['conditional']['1']['RA'])
                fullc['QA3']=min(fullc['IP']/5,fullc['GS']*spqa+fullc['RA']*rpqa)
                for state in fullc['conditional'].values():state.update(GS=fullc['GS'],RA=fullc['RA'],IP=fullc['IP'],QA3=fullc['QA3'])
            fullstats=e.legacy.prior.stats(a['production'],fullc,z['role'],z)
            if key=='IP' and fullc['RA']==0:
                fullstats['SV']=0.;fullstats['HLD']=0.
            row={'id':a['id'],'mlbam_id':z['id'],'name':a['name'],'prior_role':z['role'],'forecast_role':role,'candidate':kind,'role_evidence':reason,'latest_verified_workload':o['exposure'],'latest_GP':o['GP'],'latest_GS':o['GS'],'observation_status':o['status'],'complete':o['complete'],'source_date':o['source_date'],'statistical_cutoff':o['statistical_cutoff'],'full_role_GP':p['slots'].get('GP'),'full_role_GS':p['slots'].get('GS'),'full_role_RA':p['slots'].get('RA'),'work_per_game_or_start':sd,'work_per_relief':rd,'full_role_PA_IP':p['full_role_workload'],'full_role_basis':'structural role scheduling scenario' if kind=='structural' else 'high-usage proxy fit or disclosed structural fallback; not medical full availability','conditional_given_MLB_participation':p['conditional_active'],'participation_probability':c['participation'],'role_retention_given_active':c['role_retention_given_active'],'expected_before_allocation':pre[key],'team_allocation_adjustment':post[key]-pre[key],'medical_envelope_adjustment':med[key]-post[key],'final_expected':final,'expected_without_allocator':pre[key],'production':a['production'][key],'previous_frozen_benchmark':a['frozen_hybrid'][key],'previous_targeted_repair':a['repair'][key],'delta_vs_production':final-a['production'][key],'delta_vs_previous_repair':final-a['repair'][key],'fallback':p['fallback'],'uncertainty':'joint state uncertainty; medical cause and daily role retention unidentifiable','team_id':rosters.get(z['id']),'allocator_executed':post['opportunity_layer']['roster_allocation_executed'],'arrival_label':'MLB participant/return scenario; not guaranteed full-season retention','absence_adjustment':p['absence_adjustment'],'retained_reduced_adjustment':p['retained_reduced_adjustment'],'changed_role_adjustment':p['changed_role_adjustment'],'high_usage_adjustment':p['high_usage_adjustment'],'unknown_role_adjustment':p['unknown_role_adjustment'],'reconciliation_error':p['reconciliation_error']}
            row.update({'probability_'+k:v for k,v in c['probabilities'].items()})
            row.update(raw_expected_before_count_adapter=p['expected'],count_feasibility_adjustment=pre[key]-p['expected'],conditional_given_MLB_after_count_adapter=pre[key]/c['participation'] if c['participation'] else 0)
            row.update(expected_GP_equivalent=final/sd if key=='PA' else None,expected_GS=med.get('GS'),expected_RA=med.get('RA'),count_composition_basis='H appearance equivalents; P preserved independent role composition scaled to compatible unconditional workload',prior_probability_SP=pre['probabilities'].get('SP'),prior_probability_RP=pre['probabilities'].get('RP'))
            row['final_reconciliation_error']=p['full_role_workload']+sum(row[k] for k in ['absence_adjustment','retained_reduced_adjustment','changed_role_adjustment','high_usage_adjustment','unknown_role_adjustment','count_feasibility_adjustment','team_allocation_adjustment','medical_envelope_adjustment'])-final
            assert abs(row['final_reconciliation_error'])<1e-8
            rows.append(row);decomp.append({'id':a['id'],'name':a['name'],'candidate':kind,'prediction':c,'previous_component':a['before_roster'],'final_component':med,'latest_observation':o})
            allstats.append({'id':a['id'],'name':a['name'],'role':role,'candidate':kind,**{'production_'+k:v for k,v in a['production'].items()},**{'full_role_'+k:v for k,v in fullstats.items()},**{'expected_'+k:v for k,v in stats.items()}})
    csvout('League_1900_Comparison.csv',[a for a in rows if a['candidate']=='fitted']);csvout('League_All_Candidates.csv',rows);csvout('League_All_Statistics.csv',allstats);put('League_Components.json.gz',decomp);csvout('Team_Allocation_Ledger.csv',ledgers)
    diagnosticids=set(e.read(PRIOR/'Protocol_Freeze.json')['reserved_excluded_known_diagnostic_ids']);named=[a for a in rows if a['mlbam_id'] in diagnosticids];assert len(named)==24
    csvout('Diagnostic_12_Comparisons.csv',named)
    history=[]
    for a,z in zip(assets,zs):
        if z['id'] in diagnosticids:
            for year in range(2026,2021,-1):history.append({'id':a['id'],'mlbam_id':z['id'],'name':a['name'],**e.observation(z,year)})
    csvout('Diagnostic_12_Historical_Inputs.csv',history)
    # No prospect arrival/research path is replaced by a hypothetical MLB year.
    other=[a for a in e.read(HERE.parent/'roster-opportunity/Hybrid_League.json.gz') if a['status']!='supported_MLB']
    csvout('Unsupported_And_Prospect_Fallbacks.csv',[{'id':a['id'],'name':a['name'],'role':a['role'],'status':a['status'],'full_role_workload':None,'expected_workload':a.get('baseline',{}).get('PA' if a['role']=='H' else 'IP'),'fallback':'preserved production/prospect arrival forecast unchanged; no supported full-role estimate','uncertainty':'MLB arrival and specified role not verified'} for a in other])
    summary=[]
    for kind in ['structural','fitted']:
        for role in ['H','SP','RP']:
            xs=[a for a in rows if a['candidate']==kind and a['prior_role']==role]
            summary.append({'candidate':kind,'role':role,'n':len(xs),**{k:float(np.mean([a[k] for a in xs])) for k in ['full_role_PA_IP','raw_expected_before_count_adapter','count_feasibility_adjustment','expected_before_allocation','final_expected','production','previous_frozen_benchmark','previous_targeted_repair','absence_adjustment','retained_reduced_adjustment','changed_role_adjustment','high_usage_adjustment','unknown_role_adjustment','team_allocation_adjustment','medical_envelope_adjustment']}})
    csvout('Population_Component_Attribution.csv',summary)
    put('Integrity.json',{'supported_players':len(assets),'other_players_preserved':len(other),'candidate_rows':len(rows),'diagnostic_players':len(named)//2,'max_decomposition_error':max(abs(a['final_reconciliation_error']) for a in rows),'production_unchanged':True,'dynasty_unchanged':True,'deployment_authorized':False,'untouched_holdout_available':False,'selection_performed':False})
    return rows

if __name__=='__main__':
    evaluate();current()
    for name,digest in PROTOCOL['preserved_hashes'].items():assert hashlib.sha256((PRIOR/name).read_bytes()).hexdigest()==digest
    print('COMPLETE research only; prior hashes unchanged',flush=True)
