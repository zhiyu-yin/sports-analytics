"""Continuation ledger, pre-scoring gates and routing to separate outputs."""
import os,json,inspect
from unittest.mock import patch
import pandas as pd
import common as c
import reconcile as rec
r=c.r
PRED=c.ROOT/'data/processed/stage6r2_predictions_2025_26.parquet'

class Session(r.Session):
 def __init__(self,e=c.E):super().__init__(e);self.ledger=e/'final_evaluation_continuation_ledger.json'
 def score_start(self,validation,features_verified):
  if self.phase!='preflight' or not validation.get('passed') or validation.get('accepted_games')!=1230 or not features_verified:raise RuntimeError('Validation/features gate required')
  d=r.read_json(self.ledger)
  if d['status']!='armed' or d['first_final_model_scoring_at_utc'] is not None:raise RuntimeError('Continuation consumed')
  d['first_final_model_scoring_at_utc']=r.now();d['status']='scoring';r.durable(self.ledger,d);self.phase='validated'
 def model_call(self,*a,**kw):
  if self.phase not in ('validated','replay'):raise RuntimeError('Ledger must precede model calls')
  d=r.read_json(self.ledger)
  if d['first_final_model_scoring_at_utc'] is None:raise RuntimeError('Scoring boundary absent')
  return super().model_call(*a,**kw)

def generate_features(teams,games):
 with r.scope_overlay(rec.SCOPE):
  tf,gf=r.features.build_features(teams,games,games[['game_id','home_pts','away_pts','home_win']])
  cutoff=games.game_date.sort_values().iloc[len(games)//2];pg=games[games.game_date<=cutoff];pt=teams[teams.game_id.isin(pg.game_id)]
  _,prefix=r.features.build_features(pt,pg,pg[['game_id','home_pts','away_pts','home_win']])
  pd.testing.assert_frame_equal(gf[gf.game_id.isin(pg.game_id)].reset_index(drop=True),prefix,check_exact=True)
  # Flip only last-date results with internally consistent canonical/team targets;
  # all pregame vectors, including those games, must remain unchanged.
  changed_g=games.copy(deep=True);changed_t=teams.copy(deep=True);last=games.game_date.max();mask=games.game_date.eq(last)
  for row in games[mask].itertuples():
   i=changed_g.game_id.eq(row.game_id);hp,ap=int(row.away_pts),int(row.home_pts)
   changed_g.loc[i,'home_pts']=hp;changed_g.loc[i,'away_pts']=ap;changed_g.loc[i,'home_win']=hp>ap
   for tid,pts,won in [(row.home_team_id,hp,hp>ap),(row.away_team_id,ap,ap>hp)]:
    m=changed_t.game_id.eq(row.game_id)&changed_t.team_id.eq(tid);changed_t.loc[m,'pts']=pts;changed_t.loc[m,'wl']='W' if won else 'L'
  _,mut=r.features.build_features(changed_t,changed_g,changed_g[['game_id','home_pts','away_pts','home_win']])
  pd.testing.assert_frame_equal(gf,mut,check_exact=True)
 if len(gf)!=1230 or len(r.features.GAME_FEATURES)!=32:raise ValueError('Feature coverage/allowlist mismatch')
 return gf,dict(passed=True,rows=len(gf),features=32,version=r.features.VERSION,prefix_invariance=True,target_and_future_result_invariance=True,season_reset=True,neutral_site_in_features=False)

def save_results(rt,pred,out,prediction_path):
 # A clean results directory avoids mixing reconciliation/context with evaluation.
 with patch.object(r,'E',out),patch.object(r,'PRED',prediction_path):hashes=r.save_results(rt,pred,out)
 # Report secondary cross-season deltas as requested, using existing frozen values.
 path=out/'cross_season_confirmation.csv';table=pd.read_csv(path,float_precision='round_trip')
 table['delta_accuracy']=table.model_c_accuracy-table.raw_elo_accuracy;table['delta_auc']=table.model_c_auc-table.raw_elo_auc;table.to_csv(path,index=False);hashes[path.name]=r.access.checksum(path)
 return hashes

def arm(validation,feature_proof):
 if r.access.checksum(c.E/'authorization.txt')!=c.AUTH:raise ValueError('Authorization changed')
 c.protected();gate=r.verify()
 r.durable(c.E/'scientific_freeze_verification.json',dict(**gate,final_scoring_not_started=True,source_outcomes_already_decoded=True,protected_count=len(c.protected())))
 links=['docs/stage6_evidence/authorization.txt','docs/stage6_evidence/execution_stop.json','docs/stage6r_evidence/authorization.txt','docs/stage6r_evidence/recovery_opening_ledger.json','docs/stage6r_evidence/acquisition.json','docs/stage6r_evidence/execution_stop.json','docs/stage6r2_evidence/authorization.txt','docs/stage6r2_evidence/official_schedule_source_manifest.json','docs/stage6r2_evidence/official_schedule_facts.json','docs/stage6r2_evidence/reconciliation_validation.json','docs/stage6r2_evidence/feature_validation.json','docs/stage6r2_evidence/test_summary.json']
 ledger=dict(status='armed',created_at_utc=r.now(),final_performance_previously_exposed=False,scientific_protocol_changed=False,model_recipe_changed=False,final_source_outcomes_already_structurally_decoded=True,first_final_model_scoring_at_utc=None,aggregate_results_persisted_at_utc=None,linked_artifact_sha256={p:r.access.checksum(c.ROOT/p) for p in links},final_freeze_sha256=gate['final_freeze_sha256'],protocol_sha256=gate['protocol_sha256'],saved_estimators_sha256=gate['saved_estimators_sha256'],code_sha256=c.checkpoint(),validation=validation,feature_gate=feature_proof,primary_comparison=list(r.PRIMARY),primary_metrics=['log_loss','brier_score'],uncertainty_protocol_sha256=gate['uncertainty_protocol_sha256'])
 for path in [c.E/'home_away_reconciliation_2025_26.csv',c.ROOT/'data/interim/home_away_reconciliation_2025_26.parquet']:
  with r.access._RAW_OPEN(path,'rb') as f:ledger.setdefault('reconciliation_artifact_sha256',{})[str(path.relative_to(c.ROOT))]=r.sha(f.read())
 session=Session();r.durable(session.ledger,ledger,True);return session
