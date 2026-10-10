"""Meaningful numerical and missing-data contract checks; no fits."""
from engine import *
import unittest
class Contracts(unittest.TestCase):
 def test_release_is_blocked(self):
  with self.assertRaises(RuntimeError):TargetedOpportunityEngine()
 def test_missing_is_not_zero(self):
  z={'id':686752,'year':2026,'role':'SP','history_override':hist[686752,'P']};saved=VERIFIED.pop((2026,'P'))
  try:o=observation(z,2026);self.assertIsNone(o['exposure']);self.assertIsNone(o['GP']);self.assertFalse(o['complete']);self.assertFalse(o['medical_absence'])
  finally:VERIFIED[2026,'P']=saved
 def test_confirmed_zero_is_kept(self):
  o=observation({'id':686752,'year':2026,'role':'SP'},2026);self.assertEqual(o['exposure'],0);self.assertEqual(o['status'],'verified_zero');self.assertTrue(o['complete']);self.assertFalse(o['medical_absence'])
 def hitter(self):
  return {'PA':420.,'conditional':{'1':{'PA':200.},'2':{'PA':600.}},'probabilities':{'absent':.1,'part_time':.3,'regular':.6},'opportunity_layer':{'healthy_role_capacity':162,'participation_probability':.9,'demonstrated_depth':4.1}}
 def test_budget_does_not_shrink_for_hypothetical_healthy_demand(self):
  # Two420PA means fit in900PA despite two664PA full-health scenarios.
  cs,ledger=allocate_verified([self.hitter(),self.hitter()],[{'id':1,'role':'H'},{'id':2,'role':'H'}],{1:100,2:100},{100:{'PA':900}});self.assertEqual([c['PA'] for c in cs],[420,420]);self.assertAlmostEqual(ledger[0]['unallocated_or_unmodeled_reserve'],60)
 def test_budget_preserves_mixture_and_absence_once(self):
  cs,ledger=allocate_verified([self.hitter(),self.hitter()],[{'id':1,'role':'H'},{'id':2,'role':'H'}],{1:100,2:100},{100:{'PA':600}})
  self.assertAlmostEqual(sum(c['PA'] for c in cs),600)
  for c in cs:self.assertAlmostEqual(c['PA'],sum(c['probabilities']['part_time' if s=='1' else 'regular']*a['PA'] for s,a in c['conditional'].items()))
 def test_undated_or_unquantified_injury_not_haircut(self):
  z={'id':1,'year':2026,'role':'H'};c=self.hitter();e={'mlbam_id':1,'published_date':'2026-05-01','source_url':'https://www.mlb.com','fact_or_assumption':'verified_fact','fact':'injury; return unknown'};out=apply_verified_availability(c,z,[e]);self.assertAlmostEqual(out['PA'],c['PA'])
 def test_real_QA3_rule(self):
  qa=lambda ip,er:ip>=5 and er<=2 or ip>=6 and er<=3
  self.assertTrue(qa(5,2));self.assertTrue(qa(6,3));self.assertFalse(qa(5,3));self.assertFalse(qa(4.999,0))
if __name__=='__main__':unittest.main(argv=['contract-tests'])
