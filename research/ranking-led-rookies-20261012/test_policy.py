import unittest,json,csv,math
from pathlib import Path
from ranking_policy import listed_value,graduated_value,effective_rank
D=Path(__file__).resolve().parent
class PolicyTests(unittest.TestCase):
 def test_uploaded_rookies_have_supported_identity_and_source_anchor(self):
  rows=list(csv.DictReader((D/'Debuted_Examples.csv').read_text().splitlines()));self.assertEqual(len(rows),44)
  for x in rows:self.assertGreater(float(x['reference_source_weight']),.5);self.assertGreaterEqual(float(x['reference_value']),0)
 def test_adapter_replays_every_supported_current_value(self):
  curve=json.loads((D/'Rank_Value_Curve.json').read_text())['curve']
  for x in csv.DictReader((D/'Current_Comparison.csv').read_text().splitlines()):
   if not x.get('reference_value'):continue
   entry={k:float(x[k]) for k in ['source_rank','minimum_adjusted_rank','maximum_adjusted_rank']}
   result=listed_value(entry,curve,float(x['model_rank_signal']),float(x['career_exposure']),600 if x['role']=='H' else 170,supported=float(x['reference_model_weight'])>0)
   self.assertAlmostEqual(result['policy_value'],float(x['reference_value']),places=8)
 def test_first_exposure_does_not_switch_routes(self):
  for rank,mr,k in [(3,95,600),(41,255,600),(9,80,170)]:
   self.assertAlmostEqual(effective_rank(rank,mr,0,k)[0],rank)
   self.assertAlmostEqual(effective_rank(rank,mr,1e-9,k)[0],rank,places=8)
 def test_graduation_counts_only_new_exposure_and_cannot_reset_value(self):
  self.assertEqual(graduated_value(25.85,128,128,600,15.8,True)['policy_value'],25.85)
  self.assertAlmostEqual(graduated_value(25.85,128,128+1e-9,600,15.8,True)['policy_value'],25.85,places=8)
  x=graduated_value(25.85,128,728,600,15.8,True);self.assertEqual(x['new_evidence_weight'],.5)
  self.assertAlmostEqual(x['policy_value'],(25.85+15.8)/2)
 def test_omission_is_not_graduation_or_zero_value(self):
  x=graduated_value(25.85,128,2000,600,0,False);self.assertEqual(x['policy_value'],25.85)
 def test_anchor_curve_is_monotone_and_not_refitted_on_debut(self):
  curve=json.loads((D/'Rank_Value_Curve.json').read_text())['curve'];before=json.dumps(curve)
  self.assertTrue(all(a['value']>=b['value'] for a,b in zip(curve,curve[1:])))
  entry={'source_rank':3,'minimum_adjusted_rank':1,'maximum_adjusted_rank':15}
  for exposure in [0,1,42,128,600,1200]:listed_value(entry,curve,95,exposure,600)
  self.assertEqual(json.dumps(curve),before)
if __name__=='__main__':unittest.main()
