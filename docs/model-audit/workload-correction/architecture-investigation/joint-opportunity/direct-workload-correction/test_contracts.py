import importlib.util,sys,json,gzip,csv,unittest,hashlib
from pathlib import Path
import numpy as np
import joblib
D=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('direct_comparison',D/'run.py');r=importlib.util.module_from_spec(spec);spec.loader.exec_module(r)
class Contracts(unittest.TestCase):
 def test_exact_error_attribution(self):
  for a in r.e.read(D/'Cases.json.gz'):self.assertAlmostEqual(a['frequency_error']+a['severity_error'],a['expected_fitted']-a['actual'])
 def test_full_population_no_extra_discount(self):
  rows=list(csv.DictReader((D/'League_1900_Comparison.csv').open()));self.assertEqual(len(rows),1900)
  for a in rows:self.assertEqual(a['direct_participation_multiplier'],'1');self.assertEqual(a['allocator_applied'],'False');self.assertEqual(a['medical_envelope_applied'],'False')
 def test_training_chronology_and_zero_targets(self):
  for p in D.glob('direct-*.joblib'):
   m=joblib.load(p)['manifest'];self.assertLessEqual(m['max_target'],min(m['asof'],2025));self.assertGreater(m['zeros'],0);self.assertTrue(m['unconditional_mean']);self.assertFalse(m['availability_multiplier'])
 def test_missing_is_not_zero(self):
  z=r.e.historical_z(621566,2025,'H');f=r.features(z);self.assertTrue(np.isfinite(f[0]))
  hs=r.e.hist[z['id'],'H'];zz=z|{'year':2027,'history_override':hs};f=r.features(zz);self.assertTrue(np.isnan(f[0]));self.assertNotEqual(r.e.observation(zz,2027)['status'],'verified_zero')
 def test_no_future_evidence_used(self):
  text=(D/'run.py').read_text();start=text.index('def features');end=text.index('def fetch');self.assertNotIn('verified/',text[start:end]);self.assertNotIn('bounded_evidence',text[start:end])
  self.assertFalse(json.loads((D/'Integrity.json').read_text())['production_changed'])
 def test_protected_limits_not_relaxed(self):
  prior=r.e.read(r.S/'Release_Gates.json');old={a['gate']:a['limit'] for a in prior['gates'] if a.get('method')=='expected_fitted' and 'limit' in a}
  for a in r.e.read(D/'Release_Gates.json')['gates']:
   if a['gate'] in old:self.assertEqual(a['limit'],old[a['gate']])
  self.assertFalse(r.e.read(D/'Release_Gates.json')['numerical_promotion'])
if __name__=='__main__':
 result=unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(Contracts));r.put('Contract_Test_Results.json',{'tests':result.testsRun,'errors':len(result.errors),'failures':len(result.failures),'pass':result.wasSuccessful()});sys.exit(not result.wasSuccessful())
