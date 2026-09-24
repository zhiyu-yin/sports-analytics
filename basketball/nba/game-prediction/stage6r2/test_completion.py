import copy,io,json,tempfile,unittest,pickle
from pathlib import Path
from unittest.mock import patch
import numpy as np
import pandas as pd
import common as c
import reconcile as rec
import evaluation as ev
from schedule_facts import IDS,extract_facts
r=c.r

class CompletionTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.values,cls.manifest=rec.facts()
  rows=[];headers=['SEASON_ID','TEAM_ID','TEAM_NAME','TEAM_ABBREVIATION','GAME_ID','GAME_DATE','MATCHUP','WL','PTS']
  for f in cls.values:
   for side,other,wl,pts in [('homeTeam','awayTeam','W',101),('awayTeam','homeTeam','L',99)]:
    t=f[side];o=f[other];rows.append(['22025',t['teamId'],t['teamTricode'],t['teamTricode'],f['gameId'],f['gameDateEst'][:10],t['teamTricode']+' @ '+o['teamTricode'],wl,pts])
  body=json.dumps(dict(resultSets=[dict(name='LeagueGameLog',headers=headers,rowSet=rows)]))
  with r.scope_overlay(rec.SCOPE):cls.norm=r.normalize.normalize(body,season='2025-26')
  cls.approved=rec.mapping(cls.norm,cls.values,cls.manifest)
 def setUp(self):self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup);self.out=Path(self.temp.name)
 def test_A_only_five(self):self.assertEqual(sorted(self.approved.game_id),list(IDS))
 def test_B_stored_authoritative_mapping(self):
  for row in self.approved.itertuples():
   f=next(x for x in self.values if x['gameId']==row.game_id);self.assertEqual(row.reconciled_home_team_id,f['homeTeam']['teamId']);self.assertEqual(row.reconciled_away_team_id,f['awayTeam']['teamId'])
  bad=self.approved.copy();bad.loc[0,'reconciled_home_team_id']=9000001
  with self.assertRaises((ValueError,AssertionError)):rec.reconcile(self.norm,bad,self.values,self.manifest)
 def test_C_only_canonical_designation(self):
  fixed,applied=rec.reconcile(self.norm,self.approved,self.values,self.manifest);pd.testing.assert_frame_equal(self.norm.drop(columns='is_home'),fixed.drop(columns='is_home'),check_exact=True);self.assertEqual(int(fixed.is_home.sum()),5);self.assertEqual(sorted(applied),list(IDS))
 def test_D_matchup_unchanged(self):
  fixed,_=rec.reconcile(self.norm,self.approved,self.values,self.manifest);pd.testing.assert_series_equal(fixed.matchup,self.norm.matchup);self.assertTrue(fixed.matchup.str.contains(' @ ').all())
 def test_E_scores_wl_unchanged(self):
  fixed,_=rec.reconcile(self.norm,self.approved,self.values,self.manifest);pd.testing.assert_frame_equal(fixed[['pts','wl','_observed']],self.norm[['pts','wl','_observed']])
 def test_F_unknown_fails(self):
  bad=self.approved.copy();bad.loc[0,'game_id']='0022599999'
  with self.assertRaises(ValueError):rec.reconcile(self.norm,bad,self.values,self.manifest)
 def test_G_conflict_unresolved_fails(self):
  for status in ['conflicted','unresolved']:
   bad=self.approved.copy();bad.loc[0,'confidence']=status
   with self.assertRaises((ValueError,AssertionError)):rec.reconcile(self.norm,bad,self.values,self.manifest)
 def test_H_complete_season_gate(self):
  fixed,_=rec.reconcile(self.norm,self.approved,self.values,self.manifest)
  with r.scope_overlay(rec.SCOPE):teams,games,a=r.validate.validate_and_pair(fixed,season='2025-26')
  with self.assertRaises(ValueError):rec.complete_validation(self.norm,teams,games,a)
  session=ev.Session(self.out)
  with self.assertRaises(RuntimeError):session.score_start(dict(passed=True,accepted_games=1225),True)
 def test_I_fit_forbidden(self):
  from sklearn.linear_model import LogisticRegression
  from sklearn.ensemble import HistGradientBoostingClassifier
  session=ev.Session(self.out);session.phase='validated';r.durable(session.ledger,dict(first_final_model_scoring_at_utc='synthetic'))
  with session.activate():
   for model in [LogisticRegression(),HistGradientBoostingClassifier()]:
    with self.assertRaises(RuntimeError):model.fit([[0],[1]],[0,1])
 def test_J_estimator_artifact_exact(self):self.assertEqual(r.access.checksum(c.ROOT/'docs/stage5_evidence/frozen_estimators.pkl'),r.read_json(r.E5/'final_holdout_freeze.json')['saved_estimators_sha256'])
 def synthetic_pred(self):
  f=pd.DataFrame(dict(season=['2023-24']*4,game_id=list('abcd'),game_date=pd.to_datetime(['2023-11-01']*2+['2023-11-02']*2),home_team_id=[9000001]*4,away_team_id=[9000002]*4,home_win=[1,0,1,0]))
  for model,col in r.NAMES.items():f[col]=[.8,.3,.6,.4] if model==r.PRIMARY[0] else [.6,.4,.6,.4]
  return f
 def test_K_primary_and_output_replay_exact(self):
  session=r.Session(self.out);session.phase='synthetic';rt=r.runtime(session);pred=self.synthetic_pred()
  out1=self.out/'a';out2=self.out/'b';out1.mkdir();out2.mkdir()
  h1=ev.save_results(rt,pred,out1,out1/'prediction.parquet');h2=ev.save_results(rt,pred,out2,out2/'prediction.parquet');self.assertEqual(h1,h2)
  delta=pd.read_csv(out1/'primary_comparison.csv').iloc[0];mc=rt.metrics.evaluate(pred,r.NAMES[r.PRIMARY[0]]);me=rt.metrics.evaluate(pred,r.NAMES[r.PRIMARY[1]])
  self.assertAlmostEqual(delta.delta_log_loss,mc['log_loss']-me['log_loss']);self.assertAlmostEqual(delta.delta_brier,mc['brier_score']-me['brier_score']);self.assertEqual(delta.directional_replication_status,'replicated')
 def test_L_frozen_bootstrap(self):
  # Independent explicit whole-cluster expansion, same draw for both losses.
  f=self.synthetic_pred();got=r.bootstrap(f);y=f.home_win.to_numpy();pc=f[r.NAMES[r.PRIMARY[0]]].to_numpy();pe=f[r.NAMES[r.PRIMARY[1]]].to_numpy()
  ll=lambda p:-(y*np.log(p)+(1-y)*np.log1p(-p))
  d=np.column_stack([ll(pc)-ll(pe),(pc-y)**2-(pe-y)**2]);rng=np.random.default_rng(0);clusters=[np.array([0,1]),np.array([2,3])]
  reps=np.array([d[np.concatenate([clusters[i] for i in rng.integers(0,2,2)])].mean(axis=0) for _ in range(10000)])
  np.testing.assert_allclose(got.bootstrap_mean,np.array([reps[:,j].mean() for j in range(2)]),rtol=0,atol=1e-15);np.testing.assert_allclose(got.bootstrap_standard_error,np.array([reps[:,j].std(ddof=1) for j in range(2)]),rtol=0,atol=1e-15);np.testing.assert_allclose(got.ci_lower_2_5,np.quantile(reps,.025,axis=0,method='linear'),rtol=0,atol=1e-15);np.testing.assert_allclose(got.ci_upper_97_5,np.quantile(reps,.975,axis=0,method='linear'),rtol=0,atol=1e-15)
 def test_M_prior_evidence_unchanged(self):self.assertEqual(len(c.protected()),360)
 def test_N_ledger_before_scoring(self):
  session=ev.Session(self.out)
  with self.assertRaises(FileNotFoundError):session.score_start(dict(passed=True,accepted_games=1230),True)
  r.durable(session.ledger,dict(status='armed',first_final_model_scoring_at_utc=None),True)
  session.score_start(dict(passed=True,accepted_games=1230),True)
  self.assertIsNotNone(r.read_json(session.ledger)['first_final_model_scoring_at_utc'])
  with self.assertRaises(RuntimeError):session.score_start(dict(passed=True,accepted_games=1230),True)
 def test_conflicting_official_id_date_or_code(self):
  for key,value in [('gameDateEst','2025-11-02T00:00:00Z'),('gameCode','20251101/DETDAL')]:
   bad=copy.deepcopy(self.values);bad[0][key]=value
   with self.assertRaises(ValueError):rec.mapping(self.norm,bad,self.manifest)
 def test_unrelated_structural_error_rejected(self):
  bad=self.norm.copy(deep=True);bad.at[0,'_errors']=['invalid_pts']
  with self.assertRaises(ValueError):rec.reconcile(bad,self.approved,self.values,self.manifest)
 def test_input_copy_not_mutated(self):
  before=self.norm.copy(deep=True);rec.reconcile(self.norm,self.approved,self.values,self.manifest);pd.testing.assert_frame_equal(before,self.norm,check_exact=True)
 def test_schedule_projection(self):
  games=[]
  for f in self.values:
   g=copy.deepcopy(f);g['homeTeam']['score']=999;g['awayTeam']['wins']=100;g['pointsLeaders']=[{'points':999}];games.append(g)
  body=json.dumps(dict(leagueSchedule=dict(leagueId='00',seasonYear='2025-26',gameDates=[dict(gameDate='synthetic',games=games)])))
  result=extract_facts(body);text=json.dumps(result);self.assertNotIn('score',text);self.assertNotIn('wins',text);self.assertNotIn('pointsLeaders',text)
 def test_source_function_only_season_changes(self):self.assertEqual(rec.ADAPTED,rec.SOURCE.replace("'2024-25'","'2025-26'"))
 def test_verified_real_tls_schedule_transport(self):
  p=r.read_json(c.E/'transport_preflight_final.json');self.assertTrue(p['real_tls_handshake']);self.assertTrue(p['revocation_blocks_socket']);self.assertFalse(p['final_data_access']);self.assertTrue(r.read_json(c.E/'schedule_transport_result.json')['passed'])
