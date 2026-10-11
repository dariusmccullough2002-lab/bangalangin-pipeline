"""Export preserved scenarios only; never fit or alter production/valuation data."""
import csv, json, gzip, hashlib, sys, copy
from pathlib import Path
root=Path(__file__).resolve().parents[1]
research=Path(sys.argv[1])
stats=list(csv.DictReader((research/'full-workload-scenario/League_All_Statistics.csv').open()))
latest={r['id']:r for r in csv.DictReader((research/'calibration-starter/League_1900_Comparison.csv').open())}
components={r['id']:r for r in json.load(gzip.open(research/'full-workload-scenario/League_Components.json.gz','rt')) if r['candidate']=='fitted'}
prior={r['id']:r for r in json.load(gzip.open(research/'targeted-repair/Repair_League.json.gz','rt'))}
records={}
for row in stats:
    if row['candidate']!='fitted' or row['role']!='starter':continue
    current=latest[row['id']]
    if current['repaired_forecast_role']!='starter':continue
    c=components[row['id']]; full=c['prediction']['fitted']
    ip=float(row['full_role_IP']);gs=float(row['full_role_GS']);ra=float(row['full_role_RA'])
    assert abs(ip-float(current['repaired_full_role_scenario']))<1e-8
    # Explicit saved starts/performance yield; not a QA3/IP extrapolation.
    # Replay only the original pre-allocation adapter (run.py:307–312,
    # component_for:267–285). Team allocation/medical sensitivities stay out.
    a=prior[row['id']];template=copy.deepcopy(a['before_roster'])
    for st,s in template['conditional'].items():
        old=a['component']['conditional'][st];n=old['GS']+old['RA']
        s['QA3']=min(s['IP']/5,(s['GS']+s['RA'])*(old['QA3']/n if n else 0))
    oldq=1-template['probabilities']['absent'];q=c['prediction']['participation']
    for role in ['SP','RP']:template['probabilities'][role]=template['probabilities'][role]/oldq*q if oldq else q/2
    total=sum(template['probabilities']['RP' if st=='1' else 'SP']*s['IP'] for st,s in template['conditional'].items())
    scale=full['expected']/total if total else 0
    for s in template['conditional'].values():
        s['GS']=min(36,s['GS']*scale);s['RA']=min(85-s['GS'],s['RA']*scale)
        s['IP']=s['GS']*s['IP_per_start']+s['RA']*s['IP_per_relief']
        s['QA3']=min(s['IP']/5,s['GS']+s['RA'],s['QA3']*scale)
    qsp=template['conditional']['2']; qrp=template['conditional']['1']
    sp_yield=qsp['QA3']/max(1e-12,qsp['GS']+qsp['RA'])
    rp_yield=qrp['QA3']/max(1e-12,qrp['GS']+qrp['RA'])
    qa=min(ip/5,gs*sp_yield+ra*rp_yield)
    assert abs(qa-float(row['full_role_QA3']))<1e-8
    line={k:float(row['full_role_'+k]) for k in ['IP','K','ER','H','BB','SV','HLD','QA3']}
    # Retain saved incidental relief appearances, but never more leverage
    # events than the scenario supports. Zero relief means zero SV/HLD.
    line['SV']=min(line['SV'],ra);line['HLD']=min(line['HLD'],max(0,ra-line['SV']))
    records[row['id']]={'name':row['name'],'role':'starter','starts':gs,'reliefAppearances':ra,'line':line,
       'qa3PerStart':sp_yield,'qa3PerRelief':rp_yield,'qa3Method':'Preserved conditional QA3 yields × starts/relief appearances, bounded by IP/5',
       'workloadMethod':full['fallback'],'observationStatus':current['observation_status'],
       'sourceDate':current['source_date'],'latestGS':float(current['latest_GS']) if current['latest_GS'] else None,
       'latestGP':float(current['latest_GP']) if current['latest_GP'] else None,
       'observations':c['previous_component']['opportunity_layer']['observations'],
       'hypothetical':not any(o['status']=='observed_positive' and o['GP'] and o['GS'] is not None and o['GS']>=10 and o['GS']/o['GP']>=.8 for o in c['previous_component']['opportunity_layer']['observations'][:3])}
out={'schemaVersion':1,'forecastYear':2027,'researchCheckpoint':'de28a48022fd204944b9fe3697fbfd2ac5cbfc3b',
     'scenarioSource':'Preserved fitted full-role high-usage proxy; full-workload-scenario checkpoint ade3f86, unchanged pitcher scenarios verified against de28a48',
     'expectedSource':'Existing website V2.3C identity-prior guard catalog; V2.3 recent-performance projection and inherited aging path',
     'qa3Definition':'At least 5 IP and no more than 2 ER, OR at least 6 IP and no more than 3 ER',
     'trainingLimitation':'Annual high usage supports a workload proxy; it does not verify medical availability throughout a season.',
     'valuationInput':False,'players':records,
     'sourceHashes':{str(p.relative_to(research)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [research/'full-workload-scenario/League_All_Statistics.csv',research/'full-workload-scenario/League_Components.json.gz',research/'calibration-starter/League_1900_Comparison.csv']}}
(root/'data/starter-display-scenarios.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
print('Exported',len(records),'display-only starter scenarios')
