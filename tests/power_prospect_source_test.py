import importlib.util, unittest
from pathlib import Path
spec=importlib.util.spec_from_file_location('source',Path(__file__).resolve().parents[1]/'scripts/build-power-prospect-universe.py');source=importlib.util.module_from_spec(spec);spec.loader.exec_module(source)
class SourceMaskTests(unittest.TestCase):
 def row(self,**extra):
  return dict(dict(id=123,MLBAMId=123,name='Test Player',season=2026,level='AAA',pa=200,pitches=800,swings=300,whiffs=90,opitches=400,bip=100,chaserate=25,whiffrate=30,hhrate=40,barrelbbe=0,ev=90),**extra)
 def test_observed_zero_barrels_is_not_missing(self):
  r=source.normalize_ps(self.row(),{'key':'fixture'});self.assertEqual(r['barrel'],0);self.assertTrue(r['adequate'])
 def test_untracked_zero_placeholders_cannot_pass(self):
  for fields in [dict(level='AA'),dict(level='A+'),dict(level='A',aball_src='agg'),dict(level='Rk',rk_src='dsl')]:
   row=self.row();row.update(fields);r=source.normalize_ps(row,{'key':'fixture'});self.assertIsNone(r['hard_hit']);self.assertIsNone(r['barrel']);self.assertFalse(r['adequate'])
 def test_complex_observation_keeps_rates_but_rejects_unknown_sample(self):
  row=self.row();row.update(level='Rk',rk_src='cpx',opitches=0,bip=0);r=source.normalize_ps(row,{'key':'fixture'});self.assertEqual(r['hard_hit'],40);self.assertEqual(r['barrel'],0);self.assertFalse(r['adequate'])
 def test_reported_rates_survive_unknown_denominators(self):
  row=self.row();row.update(swings=0,opitches=0);r=source.normalize_ps(row,{'key':'fixture'});self.assertEqual(r['chase'],25);self.assertEqual(r['whiff'],30);self.assertFalse(r['adequate'])
 def test_inconsistent_identity_is_rejected(self):
  row=self.row();row['MLBAMId']=456;self.assertIsNone(source.normalize_ps(row,{'key':'fixture'}))
if __name__=='__main__':unittest.main()
