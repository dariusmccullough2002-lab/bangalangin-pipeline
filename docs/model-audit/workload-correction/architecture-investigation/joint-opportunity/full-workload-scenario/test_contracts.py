"""Run after run.py with the same recovery-directory and catalog arguments."""
from run import *
import unittest

class Contracts(unittest.TestCase):
    def test_complete_reconciled_population(self):
        a=list(csv.DictReader((HERE/'League_All_Candidates.csv').open()))
        self.assertEqual(len(a),3800)
        self.assertEqual(len({v['id'] for v in a}),1900)
        self.assertLess(max(abs(float(v['final_reconciliation_error'])) for v in a),1e-8)

    def test_joint_mixture_once(self):
        for a in e.read(HERE/'League_Components.json.gz'):
            c=a['prediction'];self.assertAlmostEqual(sum(c['probabilities'].values()),1)
            for kind in ['structural','fitted']:
                p=c[kind];self.assertAlmostEqual(sum(p['contributions'].values()),p['expected'])
                self.assertAlmostEqual(p['conditional_active']*c['participation'],p['expected'])

    def test_no_future_label_prediction_dependency(self):
        import run
        z=e.historical_z(621566,2025,'H');model=joblib.load(HERE/'model-H-2025.joblib')
        original=run.target_label
        def forbidden(z):raise AssertionError('future outcome reached predictor')
        run.target_label=forbidden
        try:self.assertGreaterEqual(run.predict(model,z)['fitted']['expected'],0)
        finally:run.target_label=original

    def test_missing_not_zero_or_medical(self):
        a=e.read(PRIOR/'Repair_League.json.gz')[0];rr=a['role'];hs=e.v.seasons(e.old.players[a['id']],rr)
        z={'id':a['mlbam_id'],'year':2026,'role':rr,'history_override':hs,'x':e.base['features'](hs,rr,2026,a['mlbam_id']),'bounded_x':e.base['features'](hs,rr,2026,a['mlbam_id'],True)}
        fam='H' if rr=='H' else 'P';cache=e.VERIFIED.pop((2026,fam))
        try:
            o=e.observation(z,2026);self.assertIsNone(o['exposure']);self.assertFalse(o['complete']);self.assertFalse(o['medical_absence'])
            _,d=e.evidence_features(z);self.assertTrue(np.isnan(e.evidence_features(z)[0][0]))
        finally:e.VERIFIED[2026,fam]=cache

    def test_chronology_and_truthful_availability(self):
        for p in HERE.glob('model-*.joblib'):
            m=joblib.load(p);self.assertLessEqual(m['manifest']['latest_target'],min(m['asof'],2025));self.assertFalse(m['manifest']['clinical_full_availability_labels'])
        self.assertFalse(e.read(HERE/'Release_Gates.json')['all_gates_pass'])

    def test_preserved_inputs(self):
        for name,digest in PROTOCOL['preserved_hashes'].items():self.assertEqual(hashlib.sha256((PRIOR/name).read_bytes()).hexdigest(),digest)

    def test_statistical_workload_bounds(self):
        for a in csv.DictReader((HERE/'League_All_Statistics.csv').open()):
            if a.get('expected_PA'):
                self.assertLessEqual(float(a['expected_HR']),float(a['expected_H'])+1e-8)
                self.assertLessEqual(sum(float(a['expected_'+k]) for k in ['AB','BB','HBP','SF']),float(a['expected_PA'])+1e-8)
            elif a.get('expected_IP'):
                self.assertLessEqual(float(a['expected_QA3']),float(a['expected_IP'])/5+1e-8)

    def test_count_adapter_and_qa3_yields(self):
        pitchers=[]
        for a in e.read(HERE/'League_Components.json.gz'):
            c=a['final_component'];self.assertAlmostEqual(c['probabilities']['absent'],a['prediction']['probabilities']['absent'])
            if 'IP' not in c:continue
            pitchers.append(c)
            self.assertAlmostEqual(sum(c['probabilities']['RP' if st=='1' else 'SP']*s['IP'] for st,s in c['conditional'].items()),c['IP'])
            for s in c['conditional'].values():
                self.assertLessEqual(s['GS'],36+1e-8);self.assertLessEqual(s['GS']+s['RA'],85+1e-8)
                self.assertAlmostEqual(s['IP'],s['GS']*s['IP_per_start']+s['RA']*s['IP_per_relief'])
        self.assertGreater(sum(c['QA3'] for c in pitchers),0)

if __name__=='__main__':
    suite=unittest.defaultTestLoader.loadTestsFromTestCase(Contracts)
    result=unittest.TextTestRunner(verbosity=2).run(suite)
    put('Contract_Test_Results.json',{'tests':result.testsRun,'failures':len(result.failures),'errors':len(result.errors),'pass':result.wasSuccessful()})
    sys.exit(not result.wasSuccessful())
