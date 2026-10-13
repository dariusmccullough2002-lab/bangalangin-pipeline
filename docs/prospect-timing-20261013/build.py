"""Audit frozen prospect timing; conditional sensitivities are not forecasts."""
from pathlib import Path
import json,re,gzip,base64,hashlib,collections
ROOT=Path(__file__).resolve().parents[2]; OUT=Path(__file__).parent
html=(ROOT/'trade-analyzer-beta/index.html').read_text(); packed=re.search(r"const packed='([^']+)'",html)[1]
D=json.loads(gzip.decompress(base64.b64decode(packed))); E=json.loads((ROOT/'data/research/eta-evidence.json').read_text()); display=json.loads((ROOT/'docs/value-audit-20261012/inputs/model-evidence.json').read_text())['display_multiplier']
records={};counts=collections.Counter();rows=[]
for a in D['assets']:
 if a['audit']['kind']!='prospect':continue
 eta=a['audit']['eta']; e=E.get(a['id']); u=a['annual_expected_utility'];counts['prospects']+=1
 counts['published_eta' if e else 'untraced_eta']+=1
 if e and str(eta)!=str(e['value']):counts['eta_mismatch']+=1
 rec={'name':a['name'],'inherited_model_eta':eta,'published_evidence':e,'level':a.get('prospect_evidence',{}).get('snapshot',{}).get('level'),'status':'arrival_not_calibrated','neutral_dynasty_value':a['values']['neutral']['display'],'withdrawn_fit':{m:v['display'] for m,v in a['competitive_values'].items()},'scenarios':[]}
 if a['id']=='06ibo':rec['additional_evidence']=[{'value':'2029','source':'MLB Pipeline','url':'https://www.mlb.com/milb/prospects/dodgers','retrievedDate':'2026-10-13','kind':'published-current','meaning':'Published arrival estimate; not guaranteed regular MLB playing time'}]
 # Shift the frozen arrival-aligned trajectory, never reinterpret delay as probability.
 # If source moves earlier than 2027, missing pre-arrival years cannot be reconstructed.
 if e and int(e['value'])>=eta:
  anchors=[int(e['value'])]
  if a['id']=='06ibo':anchors=[2029,2030]
  for anchor in anchors:
   for lag in [0,1,2]:
    start=anchor+lag;shift=start-eta;annual=[0. if t<shift else u[t-shift] for t in range(8)]
    fit={}
    for m,disc in [('neutral',.88),('balanced',.88),('contender',.75),('rebuild',.94)]:
     w=[disc**t for t in range(8)];z=sum(.88**t for t in range(8))/sum(w);fit[m]=display*sum(x*y*z for x,y in zip(annual,w))
    rec['scenarios'].append({'published_anchor':anchor,'illustrative_regular_role_delay':lag,'regular_role_start':start,'annual_utility':annual,'fit':fit})
 records[a['id']]=rec;rows.append({'id':a['id'],**{k:rec[k] for k in ['name','inherited_model_eta','level']},'published_eta':e['value'] if e else None,'mismatch':bool(e and str(eta)!=str(e['value']))})
payload={'asOf':'2026-10-13','policy':'Prospect-only competitive point estimates withheld until debut and regular-role timing are separately calibrated. Missing fit is not zero value. Published ETAs are evidence, not regular-role dates. Conditional scenarios do not enter trade totals.','scenario_definition':'Frozen annual development utility shifted to a published ETA anchor plus an illustrative 0/1/2-year delay to regular playing time. Delays have no assigned probabilities; scenarios are not forecasts or confidence bounds. Non-arrival is not newly estimated. Finite 2027–2034 horizon retained.','counts':dict(counts),'players':records}
(ROOT/'data/prospect-timing-audit.json').write_text(json.dumps(payload,separators=(',',':'))+'\n');(OUT/'Audit.json').write_text(json.dumps(rows,indent=2)+'\n');(OUT/'Summary.json').write_text(json.dumps({'counts':dict(counts),'packed_catalog_sha256':hashlib.sha256(packed.encode()).hexdigest(),'neutral_value_changes':0,'central_fit_withheld':len(records),'new_arrival_probability_model':False,'display_multiplier':display},indent=2)+'\n')
print(json.dumps(dict(counts)));print('Morales conditional scores',[(s['regular_role_start'],round(s['fit']['contender'],2)) for s in records['06ibo']['scenarios']])
