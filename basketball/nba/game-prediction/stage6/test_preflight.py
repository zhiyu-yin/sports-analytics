import io,json,tempfile,unittest,pickle
from pathlib import Path
from unittest.mock import patch
import numpy as np
import pandas as pd
import runtime as r

class Preflight(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.gate=r.verify();cls.gate['preflight_passed']=True;cls.auth=(r.E/'authorization.txt').read_bytes()
    def setUp(self):self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup);self.s=r.Session(Path(self.temp.name))
    def arm(self):self.s.arm(self.auth,self.gate)
    def fixture(self):
        return pd.DataFrame(dict(season=['2023-24']*5,game_id=list('abcde'),game_date=pd.to_datetime(['2023-11-01']*3+['2023-11-02','2023-11-03']),home_win=[1,0,1,0,1],features_plus_elo_logistic_probability=[.8,.3,.5,.6,.9],raw_elo_probability=[.6,.4,.5,.5,.8]))
    def test_A_authorization(self):
        for a in [b'',b'other']:
            with self.assertRaises(ValueError):self.s.arm(a,self.gate)
    def test_B_ledger_before_access(self):
        with self.assertRaises(RuntimeError):self.s.access_start()
        self.arm();self.s.access_start();d=r.read_json(self.s.ledger)
        self.assertIsNotNone(d['first_physical_data_access_at_utc']);self.assertIsNone(d['first_outcome_decode_at_utc'])
        self.s.decode_start();self.assertIsNotNone(r.read_json(self.s.ledger)['first_outcome_decode_at_utc'])
    def test_C_scope(self):
        for season,kind in [('2024-25','Regular Season'),('2025-26','Playoffs')]:
            with self.assertRaises(ValueError):self.s.arm(self.auth,self.gate,season,kind)
    def test_D_candidates(self):self.assertEqual(list(r.NAMES),r.read_json(r.E5/'final_holdout_freeze.json')['candidates'])
    def test_E_C_recipe(self):
        f=r.read_json(r.E5/'final_holdout_freeze.json');self.assertEqual(r.canonical_hash(f['model_c_recipe']),f['model_c_recipe_sha256']);self.assertEqual(f['model_c_recipe']['C'],.01);self.assertEqual(f['model_c_recipe']['features'],r.features.GAME_FEATURES+['elo_logit'])
    def test_F_Elo_recipe(self):
        f=r.read_json(r.E5/'final_holdout_freeze.json');self.assertEqual(r.canonical_hash(f['raw_elo_recipe']),f['raw_elo_recipe_sha256']);self.assertEqual(f['raw_elo_recipe']['parameters'],dict(K=20.,H=50.,alpha=.5))
    def test_G_saved_estimators(self):self.assertEqual(r.access.checksum(r.ROOT/'docs/stage5_evidence/frozen_estimators.pkl'),self.gate['saved_estimators_sha256'])
    def test_H_fit_rejected(self):
        from sklearn.linear_model import LogisticRegression
        for phase in ['preflight','armed','validated','replay','synthetic']:
            self.s.phase=phase
            with self.s.activate(),self.assertRaises(RuntimeError):LogisticRegression().fit([[0],[1]],[0,1])
    def test_I_selection_rejected(self):
        rt=r.runtime(self.s)
        for call in [rt.elo.select_parameters,rt.logistic.fit_model,rt.logistic.fit_final,rt.boosting.select_hgb,rt.boosting.fit_model]:
            with self.assertRaises(RuntimeError):call(None)
    def test_J_metrics_exact(self):
        self.s.phase='synthetic';rt=r.runtime(self.s);f=self.fixture();m=rt.metrics.evaluate(f,r.NAMES[r.PRIMARY[0]])
        y=f.home_win.to_numpy();p=f[r.NAMES[r.PRIMARY[0]]].to_numpy();self.assertEqual(m['brier_score'],float(np.mean((p-y)**2)));self.assertEqual(m['log_loss'],float(-(y*np.log(p)+(1-y)*np.log1p(-p)).mean()));self.assertEqual(r.access.checksum(r.ROOT/self.gate['metrics_implementation']['path']),self.gate['metrics_implementation']['sha256'])
    def test_K_L_M_bootstrap_reference_whole_dates_shared_draw(self):
        f=self.fixture();got=r.bootstrap(f);y=f.home_win.to_numpy();p=f.iloc[:,-2].to_numpy();e=f.iloc[:,-1].to_numpy()
        d=np.column_stack([-(y*np.log(p)+(1-y)*np.log1p(-p))+(y*np.log(e)+(1-y)*np.log1p(-e)),(p-y)**2-(e-y)**2]);clusters=[np.array([0,1,2]),np.array([3]),np.array([4])];rng=np.random.default_rng(0)
        ref=np.array([d[np.concatenate([clusters[k] for k in rng.integers(0,3,size=3)])].mean(axis=0) for _ in range(10000)])
        np.testing.assert_allclose(got.bootstrap_mean,ref.mean(axis=0),atol=1e-15);np.testing.assert_allclose(got.bootstrap_standard_error,ref.std(axis=0,ddof=1),atol=1e-15);np.testing.assert_allclose(got.ci_lower_2_5,np.quantile(ref,.025,axis=0,method='linear'),atol=1e-15);np.testing.assert_allclose(got.ci_upper_97_5,np.quantile(ref,.975,axis=0,method='linear'),atol=1e-15)
    def test_N_bins(self):
        self.s.phase='synthetic';rt=r.runtime(self.s);t=rt.metrics.calibration(self.fixture(),r.NAMES[r.PRIMARY[0]])
        self.assertEqual(t.lower_bound.tolist(),[i/10 for i in range(10)]);self.assertEqual(t.upper_bound.tolist(),[i/10 for i in range(1,11)]);self.assertEqual(int(t['count'].sum()),5)
    def test_O_no_individual_inspection(self):
        self.arm()
        with self.assertRaises(RuntimeError):self.s.inspect_individual_errors()
    def test_P_duplicate_opening(self):
        self.arm()
        with self.assertRaises(FileExistsError):r.Session(self.s.e).arm(self.auth,self.gate)
        self.s.access_start()
        with self.assertRaises(RuntimeError):self.s.access_start()
    def test_Q_replay_not_independent(self):
        with self.assertRaises(RuntimeError):self.s.begin_replay()
        r.durable(self.s.e/'build_manifest.json',dict(passed=True));self.s.begin_replay();self.assertFalse(r.read_json(self.s.e/'replay_started.json')['independent_confirmation'])
        with self.assertRaises(FileExistsError):self.s.begin_replay()
    def test_invalid_bootstrap_inputs(self):
        f=self.fixture()
        bad=[pd.concat([f,f.iloc[:1]]),f.assign(game_date=pd.NaT),f.assign(game_date=pd.Timestamp('2023-11-01')),f.assign(features_plus_elo_logistic_probability=np.nan)]
        for x in bad:
            with self.assertRaises(ValueError):r.bootstrap(x)
    def test_network_mock_ledger_and_decode_order(self):
        self.arm()
        class Response:
            _status_code=200
            def get_response(self):return '{"synthetic":true}'
            def get_url(self):return 'https://stats.nba.com/stats/leaguegamelog'
        def request(*a,**kw):
            self.assertIsNotNone(r.read_json(self.s.ledger)['first_physical_data_access_at_utc']);self.assertIsNone(r.read_json(self.s.ledger)['first_outcome_decode_at_utc']);return Response()
        from nba_api.stats.library.http import NBAStatsHTTP
        with patch.object(r,'E',self.s.e),patch.object(r,'RAW',self.s.e/'synthetic_response.json'),patch.object(NBAStatsHTTP,'send_api_request',request):
            # Mock raw path relative_to(ROOT) is isolated under a fake ROOT as well.
            with patch.object(r,'ROOT',self.s.e):self.assertEqual(r.acquire(self.s),b'{"synthetic":true}')
    def test_saved_estimators_synthetic_predictions_zero_fit(self):
        self.s.phase='synthetic';rt=r.runtime(self.s);bundle=pickle.loads((r.ROOT/'docs/stage5_evidence/frozen_estimators.pkl').read_bytes());fits=bundle['fits'];before=r.sha(pickle.dumps(fits,protocol=5))
        f=self.fixture();f['home_team_id']=9000001;f['away_team_id']=9000002
        for col in r.features.GAME_FEATURES:f[col]=np.nan
        f['elo_logit']=0.;f['raw_elo_probability']=.5
        with self.s.activate(),r.threadpool_limits(limits=1):pred=r.prediction_frame(rt,fits,f,bundle['prior'])
        self.assertEqual(len(pred),5);self.assertEqual(list(pred),r.IDENTITY+['home_win']+list(r.NAMES.values()));self.assertEqual(before,r.sha(pickle.dumps(fits,protocol=5)));self.assertEqual(self.s.fit_calls,[])
    def test_full_synthetic_output_and_replay_identity(self):
        self.s.phase='synthetic';rt=r.runtime(self.s);pred=self.fixture();pred['home_team_id']=9000001;pred['away_team_id']=9000002
        for m,col in r.NAMES.items():
            if col not in pred:pred[col]=.55
        pred=pred[r.IDENTITY+['home_win']+list(r.NAMES.values())]
        first=self.s.e/'first';second=self.s.e/'second'
        h1=r.save_results(rt,pred,first);h2=r.save_results(rt,pred,second)
        self.assertEqual(h1,h2);self.assertIn('date_cluster_bootstrap.csv',h1);self.assertIn('calibration_model_c.csv',h1)
    def test_no_opening_if_gate_fails(self):
        for key in ['passed','preflight_passed']:
            gate=dict(self.gate);gate[key]=False
            with self.assertRaises(ValueError):self.s.arm(self.auth,gate)
        self.assertFalse(self.s.ledger.exists())
