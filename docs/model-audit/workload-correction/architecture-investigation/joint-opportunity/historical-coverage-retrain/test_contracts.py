"""Contract tests for chronology, source matching and unchanged targets/settings."""
import importlib.util,unittest,csv,json,sys,hashlib
from pathlib import Path
import numpy as np,joblib
D=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('coverage_research',D/'run.py');r=importlib.util.module_from_spec(spec);spec.loader.exec_module(r);r.activate()
class Contracts(unittest.TestCase):
 def test_matched_population_and_unchanged_targets(self):
  old={(a['mlbam_id'],a['anchor'],a['role']):a for a in r.BASE};xs=r.e.read(D/'Matched_Cases.json.gz');self.assertEqual(len(xs),4004)
  for a in xs:
   b=old[a['mlbam_id'],a['anchor'],a['role']];self.assertEqual(a['actual'],b['actual']);self.assertEqual(a['groups'],b['groups']);self.assertEqual(a['protected_groups'],b['protected_groups']);self.assertFalse(a['future_inputs_used'])
 def test_GP_repairs_match_exact_PA_without_zero_inference(self):
  for a in csv.DictReader((D/'Correction_Log.csv').open()):
   if a['correction_status'] in ['missing_GP_recovered','GP_disagreement_corrected']:
    self.assertEqual(float(a['source_PA']),float(a['original_exposure']));self.assertGreater(float(a['corrected_GP']),0);self.assertTrue(a['source']);self.assertEqual(a['medical_label_added'],'False')
   if a['original_exposure'] in ['', '0.0']:self.assertEqual(a['original_GP'],a['corrected_GP'])
 def test_future_GP_cannot_enter_prediction(self):
  a=next(a for a in r.BASE if a['role']=='H');z=r.e.historical_z(a['mlbam_id'],a['anchor'],'H');before=r.p.features(z).copy();key=z['id'],z['year']+1;original=r.CENSUS.get(key)
  r.CENSUS[key]={'stat':{'plateAppearances':1,'gamesPlayed':1}}
  try:
   with r.prediction_only(z):
    np.testing.assert_equal(before,r.p.features(z));
    with self.assertRaises(AssertionError):r.corrected(z,z['year']+1)
  finally:
   if original is None:r.CENSUS.pop(key)
   else:r.CENSUS[key]=original
 def test_retrained_settings_chronology_and_zero_targets(self):
  for path in D.glob('direct-H-*.joblib'):
   m=joblib.load(path);old=joblib.load(r.PREV/path.name);self.assertEqual(m['reg'].get_params(),old['reg'].get_params());self.assertGreater(m['manifest']['zeros'],0);self.assertLessEqual(m['manifest']['max_target'],min(m['manifest']['asof'],2025));self.assertTrue(m['manifest']['unconditional_mean']);self.assertFalse(m['manifest']['availability_multiplier'])
  for path in D.glob('model-H-*.joblib'):
   m=joblib.load(path);old=joblib.load(r.FULL/path.name);self.assertEqual(m['classifier'].get_params(),old['classifier'].get_params());self.assertLessEqual(m['manifest']['latest_target'],min(m['asof'],2025));self.assertEqual(m['manifest']['rows'],old['manifest']['rows'])
 def test_unaffected_pitchers_exactly_preserved(self):
  for path in list(D.glob('direct-P-*.joblib'))+list(D.glob('model-P-*.joblib')):
   parent=r.PREV if path.name.startswith('direct') else r.FULL;self.assertEqual(path.read_bytes(),(parent/path.name).read_bytes())
  for a in r.e.read(D/'Matched_Cases.json.gz'):
   if a['role']!='H':self.assertAlmostEqual(a['five_retrained'],a['expected_fitted'],places=9);self.assertAlmostEqual(a['direct_retrained'],a['direct_mean'],places=9)
 def test_full_population_no_additional_risk_discount(self):
  xs=list(csv.DictReader((D/'League_1900_Comparison.csv').open()));self.assertEqual(len(xs),1900);self.assertEqual(len(list(csv.DictReader((D/'Diagnostic_12_Comparisons.csv').open()))),12)
  for a in xs:self.assertEqual(a['allocator_applied'],'False');self.assertEqual(a['medical_envelope_applied'],'False');self.assertEqual(a['direct_participation_multiplier'],'1');self.assertEqual(a['full_role_used_as_unconditional'],'False')
 def test_protected_gates_unchanged(self):
  old={a['gate']:a['limit'] for a in r.e.read(r.FULL/'Release_Gates.json')['gates'] if a.get('method')=='expected_fitted' and 'limit' in a}
  for method in ['five_retrained','direct_retrained']:
   for a in r.e.read(D/f'Release_Gates_{method}.json')['gates']:
    if a['gate'] in old:self.assertEqual(a['limit'],old[a['gate']])
 def test_attribution_and_state_semantics(self):
  for a in r.e.read(D/'Matched_Cases.json.gz'):
   self.assertAlmostEqual(a['retrained_frequency_error']+a['retrained_severity_error'],a['five_retrained']-a['actual']);self.assertNotIn('unknown_role',a['retrained_probabilities']);self.assertIn('retention_unidentifiable',a['retrained_probabilities'])
if __name__=='__main__':
 result=unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(Contracts));r.iv.dump('Contract_Test_Results.json',{'tests':result.testsRun,'errors':len(result.errors),'failures':len(result.failures),'pass':result.wasSuccessful()});sys.exit(not result.wasSuccessful())
