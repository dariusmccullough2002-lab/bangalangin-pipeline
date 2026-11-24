import copy, importlib.util, unittest
from unittest.mock import patch
from pathlib import Path
spec=importlib.util.spec_from_file_location('winter',Path(__file__).resolve().parents[1]/'scripts/winter-ball.py');w=importlib.util.module_from_spec(spec);spec.loader.exec_module(w)
class WinterTests(unittest.TestCase):
 def hitting(self,**kwargs):
  s=dict(atBats=20,hits=5,doubles=1,triples=0,homeRuns=1,baseOnBalls=4,strikeOuts=5,plateAppearances=25,stolenBases=1,caughtStealing=1,hitByPitch=0,sacFlies=0,totalBases=9);s.update(kwargs);return w.normalize_stat(s,'hitting')
 def pitching(self,**kwargs):
  s=dict(atBats=20,hits=5,doubles=1,triples=0,homeRuns=1,baseOnBalls=2,strikeOuts=7,outs=20,battersFaced=25,earnedRuns=2,inningsPitched='6.2');s.update(kwargs);return w.normalize_stat(s,'pitching')
 def player(self,n=100,age=19,level=1.5,ops=.85):return dict(kind='hitting',age=age,levelRank=level,affiliated2026=True,pipelineMatch=False,stats=dict(plateAppearances=n,ops=ops))
 def test_rate_denominators_and_zeroes(self):
  x=self.hitting();self.assertEqual(x['kPct'],.2);self.assertEqual(x['bbPct'],.16);self.assertEqual(x['iso'],.2);self.assertEqual(x['sbSuccess'],.5);self.assertIsNone(self.hitting(strikeOuts=0)['bbPerK']);self.assertIsNone(self.hitting(stolenBases=0,caughtStealing=0)['sbSuccess'])
 def test_pitching_uses_outs_and_bf(self):
  x=self.pitching();self.assertEqual(x['kPct'],.28);self.assertEqual(x['bbPct'],.08);self.assertEqual(x['ip'],'6.2');self.assertEqual(x['era'],2.7);self.assertEqual(x['whip'],1.05)
  with self.assertRaises(ValueError):self.pitching(inningsPitched='6.3')
 def test_bad_counts_cannot_publish(self):
  for kwargs in [dict(hits=21),dict(strikeOuts=26),dict(totalBases=8),dict(plateAppearances=19),dict(atBats=-1)]:
   with self.assertRaises(ValueError):self.hitting(**kwargs)
 def test_invalid_or_duplicate_ids(self):
  row=dict(player=dict(id=123,fullName='Player'),stat=dict(atBats=20,hits=5,doubles=1,triples=0,homeRuns=1,baseOnBalls=4,strikeOuts=5,plateAppearances=25,stolenBases=1,caughtStealing=1,hitByPitch=0,sacFlies=0,totalBases=9))
  with self.assertRaises(ValueError):w.normalize_rows([row,row],'hitting',131)
  row['player']['id']=None
  with self.assertRaises(ValueError):w.normalize_rows([row],'hitting',131)
 def test_regression_and_disappearance_guard(self):
  old=dict(hitters=[dict(mlbamId=i,stats=self.hitting())for i in range(1,21)],pitchers=[dict(mlbamId=i,stats=self.pitching())for i in range(1,21)]);new=copy.deepcopy(old);new['hitters'][0]['stats']['plateAppearances']=24
  with self.assertRaises(ValueError):w.validate_transition(old,new)
  w.validate_transition(old,new,True)
  new=copy.deepcopy(old);new['pitchers']=new['pitchers'][:5]
  with self.assertRaises(ValueError):w.validate_transition(old,new)
 def test_age_jump_over_veteran_and_small_heater(self):
  base=dict(ops=.70);young=w.signal(self.player(),base,3.5);veteran=w.signal(self.player(age=28,level=3,ops=.90),base,3.5);heater=w.signal(self.player(n=15,ops=1.1),base,3.5)
  self.assertGreater(young['order'],veteran['order']);self.assertGreater(young['order'],heater['order']);self.assertFalse(veteran['prospectEligible']);self.assertEqual(heater['label'],'Encouraging small sample')
 def test_very_young_struggle_is_not_a_heavy_penalty(self):
  base=dict(ops=.70);young=w.signal(self.player(n=16,age=17,level=0,ops=.12),base,3);veteran=w.signal(self.player(n=16,age=25,level=3,ops=.12),base,3)
  self.assertGreater(young['order'],veteran['order']);self.assertEqual(young['label'],'Small sample — monitor')
 def test_unknown_context_is_not_fabricated(self):
  p=self.player();p['age']=None;p['levelRank']=None;x=w.signal(p,dict(ops=.70),3);self.assertFalse(x['prospectEligible']);self.assertEqual(x['label'],'Context incomplete — performance only')
 def test_partial_failure_retains_last_valid_league(self):
  old=w.read('data/winter/2026.json');prior={l['id']:l for l in old['leagues']};meta={lid:dict(id=lid)for lid in w.CONFIG};before=copy.deepcopy(prior)
  def fetch(m,season):
   if m['id']==132:raise ValueError('Upstream failed')
   return copy.deepcopy(prior[m['id']])
  with patch.object(w,'fetch_league',side_effect=fetch):rows,errors=w.refresh_leagues(meta,2026,prior,'new timestamp')
  retained=next(l for l in rows if l['id']==132);self.assertTrue(retained['stale']);self.assertEqual(retained['hitters'],before[132]['hitters']);self.assertEqual(retained['lastSuccessfulRefresh'],before[132]['lastSuccessfulRefresh']);self.assertEqual(prior,before);self.assertEqual(len(errors),1)
 def test_all_failure_and_initial_partial_abort(self):
  prior={l['id']:l for l in w.read('data/winter/2026.json')['leagues']};meta={lid:dict(id=lid)for lid in w.CONFIG}
  with patch.object(w,'fetch_league',side_effect=ValueError('Unavailable')):
   with self.assertRaises(RuntimeError):w.refresh_leagues(meta,2026,prior,'now')
   with self.assertRaises(RuntimeError):w.refresh_leagues(meta,2026,{},'now')
 def test_empty_pagination_and_wrong_season_rejected(self):
  response=dict(stats=[dict(group=dict(displayName='hitting'),totalSplits=2,splits=[])])
  with patch.object(w,'get',return_value=response):
   with self.assertRaises(ValueError):w.stat_rows(2026,'hitting',17,131)
  response['stats'][0]['totalSplits']=1;response['stats'][0]['splits']=[dict(season='2025',league=dict(id=131))]
  with patch.object(w,'get',return_value=response):
   with self.assertRaises(ValueError):w.stat_rows(2026,'hitting',17,131)
 def test_archive_guard_stops_network_calls(self):
  with patch('sys.argv',['winter-ball.py']),patch.object(w,'read',return_value=dict(status='archived')),patch.object(w,'get')as network:
   w.main();network.assert_not_called()
 def test_tiny_extreme_heater_has_capped_order(self):
  x=w.signal(self.player(n=15,ops=2.1),dict(ops=.70),3.5);self.assertLessEqual(x['order'],.5)
 def test_snapshot_contract(self):
  d=w.read('data/winter/2026.json');self.assertEqual({l['id']for l in d['leagues']},set(w.CONFIG));self.assertEqual(d['season'],'2026')
  for l in d['leagues']:
   for g in ['hitters','pitchers']:
    ids=[p['mlbamId']for p in l[g]];self.assertEqual(len(ids),len(set(ids)));self.assertTrue(ids)
    for p in l[g]:self.assertNotIn('organizationId',p);self.assertNotIn('fantraxId',p);self.assertNotIn('owner',p);self.assertIn(p['signal']['reliability'],[min(1,p['signal']['reliability'])])
if __name__=='__main__':unittest.main()
