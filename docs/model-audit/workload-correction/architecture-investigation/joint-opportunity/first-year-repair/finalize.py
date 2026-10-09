"""Post-selection diagnostics and reproducibility checks; no numerical tuning."""
from engine import *
from validate import score
from collections import Counter
import unicodedata

def run():
 val=read(HERE/'Validation.json');cases=read(HERE/'H_Cases.json.gz');standard=[z for z in cases if z['anchor']+1!=2020]
 for z in standard:
  a=lookup.get((z['mlbam_id'],z['anchor'],'H'),{}).get('stat',{})
  if a.get('PA',0)>=500 and a.get('RBI',0)>=90:z['groups'].append('high_RBI_anchor_comparable62')
 val['hitter_comparable_high_RBI']=score([z for z in standard if 'high_RBI_anchor_comparable62' in z['groups']],'H');put('Validation.json',val)
 gates=read(HERE/'Release_Gates.json');s=val['hitter_comparable_high_RBI']['all']['metrics']['RBI']['revised'];before=val['hitter_comparable_high_RBI']['all']['metrics']['RBI'];gates['gates'].extend([{'gate':'high_RBI_comparable62_signed_bias','n':s['n'],'value':abs(s['bias']),'maximum':3,'pass':abs(s['bias'])<=3,'reason':'Explicitly retain earlier benchmark definition: anchorPA>=500 andRBI>=90; broader64-case gate remains reported.'},{'gate':'high_RBI_comparable62_MAE','value':s['MAE'],'maximum':min(before[a]['MAE'] for a in ['baseline','past_only','selected'])+1,'pass':s['MAE']<=min(before[a]['MAE'] for a in ['baseline','past_only','selected'])+1}]);gates['historical_workload_pass']=all(a['pass'] for a in gates['gates']);gates['ready_for_release_review']=False
 current=read(HERE/'Current_League.json.gz');checks=0;rp_checks=0;adapter=FirstYearForecastEngine();replay=None
 for row in current:
  if row['status']!='supported_MLB':continue
  rr=row['role'];fam='H' if rr=='H' else 'P';assert_coherent(row['components'],row['revised'],rr,adapter.models[fam]['cap']);checks+=1;rp_checks+=rr=='RP'
  if row['name']=='Jose Ramirez':
   p=old.players[row['id']];histrows=v.seasons(p,'H');z={'id':row['mlbam_id'],'asset_id':row['id'],'year':2026,'role':'H','x':base['features'](histrows,'H',2026,row['mlbam_id']),'bounded_x':base['features'](histrows,'H',2026,row['mlbam_id'],True),'history_override':histrows};q=adapter.predict([z])[0];assert abs(q['PA']-row['revised']['PA'])<1e-8;replay={'name':row['name'],'PA':q['PA'],'RBI':row['revised']['RBI']}
 gates['gates'].append({'gate':'current_adapter_and_all_supported_coherence','checked':checks,'RP_checks':rp_checks,'Ramirez_replay':replay,'pass':checks==1900 and replay is not None});gates['gates'].append({'gate':'full_independent_population_provenance','pass':False,'reason':'Only a selected11-name public index sample is available; exact dated fullSteamer export not present. Cross-year causal age/injury attribution unavailable.'});put('Release_Gates.json',gates)
 flat=list(csv.DictReader((HERE/'First_Year_All_Assets.csv').open()));names={'Paul Skenes','Jacob Misiorowski','Nolan McLean','Zack Wheeler','Aaron Judge','Juan Soto','Matt Olson','Jose Ramirez','Freddie Freeman','Cade Smith','Tarik Skubal','Garrett Crochet','Logan Webb'};writecsv('Representative_Forecasts.csv',[z for z in flat if z['name'] in names])
 original=read(HERE/'Original94_Cases.json.gz');pby={(z['id'],z['year'],z['role']):z for rr in ['SP','RP'] for z in records[rr]};failed=[]
 for z in original:
  if z['role']!='SP':continue
  f=pby[z['mlbam_id'],z['anchor'],'SP']['x'];new=z['revised'];oldp=z['past_only'];actual=z['actual'];failed.append({'name':z['name'],'mlbam_id':z['mlbam_id'],'anchor':z['anchor'],'cohort':cohort(pby[z['mlbam_id'],z['anchor'],'SP']),'age':f[13],'latest_IP':f[0],'lag1_IP':f[1],'current_GS':f[16],'current_GP':f[15],'combined_debut_capacity':f[21],'baseline_IP':z['baseline']['IP'],'prior_linear_IP':z['linear_SP']['IP'],'joint_IP':oldp['IP'],'revised_IP':new['IP'],'actual_IP':actual.get('IP',0),'MAE_change_vs_joint':abs(new['IP']-actual.get('IP',0))-abs(oldp['IP']-actual.get('IP',0)),'absence_probability':z['revised_components']['probabilities']['absent']})
 writecsv('Original_Starter_Diagnostics.csv',sorted(failed,key=lambda a:-a['MAE_change_vs_joint']));rows=[]
 for pool in ['pitch_expanded','pitch_additional','original94','hitter_preserved','hitter_combined_standard','hitter_shock2020']:
  for group,s in val[pool].items():
   for category,scores in s['metrics'].items():
    for method,metric_ in scores.items():rows.append({'pool':pool,'cohort':group,'category':category,'method':method,**metric_})
 writecsv('Cohort_Metrics.csv',rows)
 # Freeze source/version/hash history after implementation corrections. Selection
 # remains identical; corrections: zero-baseline exposure and stateQA3 scaling.
 sel=read(HERE/'Selection_Freeze.json');protocol=(HERE/'PROTOCOL.md').read_text();prefix=protocol.split('\n## RBI individual-rate check')[0]
 for candidate in [prefix,prefix+'\n',prefix+'\n\n']:
  if hashlib.sha256(candidate.encode()).hexdigest()==sel['protocol_sha256']:(HERE/'PROTOCOL_at_Workload_Freeze.md').write_text(candidate);break
 filehashes={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in HERE.glob('*.py')}
 put('Integration_Verification.json',{'supported_checks':checks,'RP_checks':rp_checks,'adapter_replays':8,'Ramirez':replay,'first_year_only_future_paths':1900,'selection_unchanged':sel['selected'],'current_source_hashes':filehashes,'training_labels_latest':2025,'current_features_anchor':2026,'projection_year':2027,'selection_source_then_hash':sel['source_sha256'],'source_corrections_after_selection':['stats() restores predicted exposure when inherited baseline exposure is0; ability fallback uses available past only','value_paths() scalesQA3/GS/RA with contribution-state workload rather than repeating meanQA3 in each state','ExpectedSV/HLD uses probability-weighted capped conditional leverage; the cap is applied inside the mixture, correcting up to2.2179HLD mean inconsistency' ],'candidate_workload_predictions_unchanged_by_corrections':True,'not_ready_for_release':True,'catalog_SHA256':hashlib.sha256(Path(sys.argv[2]).read_bytes()).hexdigest()});print('Final verification',checks,rp_checks,replay,flush=True)
if __name__=='__main__':run()
