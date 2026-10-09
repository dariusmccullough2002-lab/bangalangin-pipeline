"""Small verified public Steamer sample, never a fitting target.
Search-index snapshots of preseason-labelled2026 pages retrieved2026-10-09.
Exact publication/revision dates unavailable; not the user's full source table.
"""
from engine import *
SOURCES={
 'PIT':'https://www.fangraphs.com/projections?lg=all&players=0&pos=all&stats=sta&team=27&type=steamer',
 'two_young':'https://www.fangraphs.com/projections?pos=&sortcol=18&sortdir=desc&statgroup=standard&stats=pit&type=steamer',
 'Wheeler':'https://www.fangraphs.com/projections?pos=all&stats=pit&type=steamer'}
SAMPLE=[('Paul Skenes','194.0',32,32,'PIT'),('Mitch Keller','179.2',31,31,'PIT'),('Bubba Chandler','162.1',38,26,'PIT'),('Jared Jones','107.0',24,18,'PIT'),('Braxton Ashcraft','145.1',45,23,'PIT'),('Carmen Mlodzinski','108.2',61,11,'PIT'),('Hunter Barco','94.2',41,11,'PIT'),('José Urquidy','62.2',32,6,'PIT'),('Jacob Misiorowski','143.0',32,24,'two_young'),('Nolan McLean','149.0',26,26,'two_young'),('Zack Wheeler','154.2',26,26,'Wheeler')]
def outs_value(s):
 a,b=s.split('.');assert b in ['0','1','2'];return int(a)+int(b)/3

def run():
 current=read(HERE/'Current_League.json.gz');by={z['name']:z for z in current if z['status']=='supported_MLB' and z['role'] in ['SP','RP']};rows=[];unmatched=[]
 for name,ip,gp,gs,source in SAMPLE:
  if name not in by:unmatched.append(name);continue
  z=by[name];c=z['components'];a=c['conditional']['2'];b=c['conditional']['1'];reference=outs_value(ip);p=c['probabilities'];delta_cond=a['IP']-reference;absence=-p['absent']*a['IP'];transition=p['RP']*(b['IP']-a['IP']);reconstructed=reference+delta_cond+absence+transition;assert abs(reconstructed-c['IP'])<1e-7
  q={'name':name,'mlbam_id':z['mlbam_id'],'current_role':z['role'],'cohort':z['cohort'],'age':z['age'],'reference_forecast_year':2026,'pipeline_forecast_year':2027,'steamer_IP_notation':ip,'steamer_IP':reference,'steamer_GP':gp,'steamer_GS':gs,'production_IP':z['baseline']['IP'],'joint_IP':z['prior_joint']['IP'],'revised_IP':z['revised']['IP'],'production_gap':z['baseline']['IP']-reference,'revised_gap':z['revised']['IP']-reference,'conditional_SP_IP':a['IP'],'conditional_SP_GS':a['GS'],'model_IP_per_start':a['IP_per_start'],'conditional_workload_difference':delta_cond,'absence_contribution':absence,'role_transition_contribution':transition,'observed_latest_MLB_IP':z['feature_evidence']['latest_MLB_exposure'],'current_GS':z['feature_evidence']['current_GS'],'current_GP':z['feature_evidence']['current_GP'],'source_url':SOURCES[source],'source_asof':'Unknown revision date; indexed2026 preseason-labelled page','retrieved':'2026-10-09','no_extra_workload_aging_multiplier':True}
  rows.append(q)
 writecsv('Independent_Matched_Sample.csv',rows)
 summary={'sample_requested':len(SAMPLE),'matched':len(rows),'unmatched':unmatched,'sources':SOURCES,'mean_production_gap':float(np.mean([a['production_gap'] for a in rows])),'mean_revised_gap':float(np.mean([a['revised_gap'] for a in rows])),'mean_joint_gap':float(np.mean([a['joint_IP']-a['steamer_IP'] for a in rows])),'groups':{},'cautions':['Selected11-player sample, including PIT roster; not representative whole-league comparison','2026 reference vs2027 model has different age, season and data-cutoff information','Source update date unavailable; not an authenticated export of the user-provided benchmark','Some external names may have unsupported currentMLB identities; no fuzzy matching','2026 indexed sources differ from Update/RoS forecasts; those types excluded','Conditional/absence/transition terms exactly reconstruct model-reference gap, but are arithmetic architecture components, not causal age/injury/year attribution','No verified future injury diagnoses, lineup or team-year estimates were manufactured'],'remaining_input':'Dated complete2026Steamer export with stable IDs plus matched dated2027 forecasts and injury inputs; cannot causally apportion forecast-year/injury-method differences from this cross-year sample'}
 for group in sorted({a['cohort'] for a in rows}):
  xs=[a for a in rows if a['cohort']==group];summary['groups'][group]={'n':len(xs),'mean_production_gap':float(np.mean([a['production_gap'] for a in xs])),'mean_revised_gap':float(np.mean([a['revised_gap'] for a in xs]))}
 put('Independent_Comparison.json',summary);print('Independent',json.dumps(summary),flush=True)
if __name__=='__main__':run()
