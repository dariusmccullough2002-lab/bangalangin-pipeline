import importlib.util,unittest,json,csv,hashlib,sys
from pathlib import Path
import numpy as np,joblib
D=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('calibration_trial',D/'run.py');t=importlib.util.module_from_spec(spec);spec.loader.exec_module(t)
class Contracts(unittest.TestCase):
 def test_supported_class_map_and_chronology(self):
  for p in D.glob('cal-*.joblib'):
   a=joblib.load(p);m=a['manifest'];self.assertEqual(m['IDmods'],[4]);self.assertLessEqual(m['latest_target'],min(m['asof'],2025));self.assertEqual(m['classes'],[0,1,2,3]);self.assertEqual(m['unsupported_targets'],[]);self.assertEqual(m['base_sha256'],hashlib.sha256((t.C/f'model-{m["family"]}-{m["asof"]}.joblib').read_bytes()).hexdigest())
   if a['calibrator'] is not None:self.assertEqual(a['calibrator'].classes_.tolist(),[0,1,2,3]);self.assertGreaterEqual(m['rows'],100);self.assertGreaterEqual(min(m['support'].values()),10)
 def test_workload_changes_are_probability_only(self):
  for a in t.e.read(D/'Cases.json.gz'):
   delta=sum((a['calibrated_probabilities'][st]-a['retrained_probabilities'][st])*a['retrained_state_means'][st] for st in t.STATES);self.assertAlmostEqual(delta,a['calibrated_workload']-a['five_retrained']);self.assertAlmostEqual(sum(a['calibrated_probabilities'].values()),1);self.assertEqual(a['calibrated_probabilities']['retention_unidentifiable'],0)
 def test_nonstarter_pitchers_unchanged_and_candidates_separate(self):
  for a in t.e.read(D/'Cases.json.gz'):
   if a['role']!='H':self.assertEqual(a['H_calibration_alone'],a['five_retrained'])
   else:self.assertEqual(a['P_starter_calibration_alone'],a['five_retrained'])
   if a['role']!='H' and a['repaired_forecast_role']!='starter':self.assertAlmostEqual(a['calibrated_workload'],a['five_retrained']);self.assertEqual(a['calibrated_probabilities'],a['retrained_probabilities'])
 def test_RBI_exact_decomposition_and_no_future_selection(self):
  rows=list(csv.DictReader((D/'RBI_Player_Decomposition.csv').open()))
  for a in rows:
   self.assertAlmostEqual(float(a['total_error']),float(a['workload_error_contribution'])+float(a['rate_error_at_actual_PA']));self.assertAlmostEqual(float(a['reconciliation_RBI_delta']),0)
   if a['high_RBI_gate']=='True':self.assertGreaterEqual(float(a['anchor_PA']),500);self.assertGreaterEqual(float(a['anchor_RBI']),90)
  self.assertEqual(sum(a['high_RBI_gate']=='True' and a['model']=='five_retrained' for a in rows),62)
 def test_gates_preserved(self):
  old={a['gate']:a.get('limit') for a in t.e.read(t.C/'Release_Gates_five_retrained.json')['gates']}
  for method in ['H_calibration_alone','P_starter_calibration_alone']:
   for a in t.e.read(D/f'Release_Gates_{method}.json')['gates']:
    if a['gate'] in old:self.assertEqual(a.get('limit'),old[a['gate']])
 def test_population_and_no_deployment(self):
  self.assertEqual(len(t.e.read(D/'Cases.json.gz')),4004);self.assertEqual(len(list(csv.DictReader((D/'League_1900_Comparison.csv').open()))),1900);self.assertEqual(len(list(csv.DictReader((D/'Diagnostic_12_Comparisons.csv').open()))),12);a=t.e.read(D/'Integrity.json');self.assertFalse(a['production_changed']);self.assertFalse(a['talent_rates_changed']);self.assertFalse(a['combined_candidate_selected']);self.assertFalse(a['deployment'])
if __name__=='__main__':
 result=unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(Contracts));t.put('Contract_Test_Results.json',{'tests':result.testsRun,'failures':len(result.failures),'errors':len(result.errors),'pass':result.wasSuccessful()});sys.exit(not result.wasSuccessful())
