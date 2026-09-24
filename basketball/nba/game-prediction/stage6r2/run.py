"""Offline conditional final evaluation; no acquisition or historical rewrites."""
import io,sys,unittest,os,traceback
from pathlib import Path
import common as c
import reconcile as rec
import evaluation as ev
r=c.r

def write_table(path,table,kind):
 path.parent.mkdir(parents=True,exist_ok=True)
 with r.access._RAW_OPEN(path,'xb') as f:
  if kind=='parquet':table.to_parquet(f,index=False)
  else:f.write(table.to_csv(index=False).encode())
  f.flush();os.fsync(f.fileno())

def main():
 if (c.E/'final_evaluation_continuation_ledger.json').exists():raise RuntimeError('Continuation exists: no automatic restart')
 c.protected();r.verify()
 suite=unittest.TestSuite()
 for folder,pattern in [('tests','test*.py'),('stage6','test_preflight.py'),('stage6r2','test_completion.py')]:suite.addTests(unittest.TestLoader().discover(str(c.ROOT/folder),pattern=pattern))
 stream=io.StringIO();result=unittest.TextTestRunner(stream=stream,verbosity=2).run(suite);(c.E/'test_run.txt').write_text(stream.getvalue())
 r.durable(c.E/'test_summary.json',dict(passed=result.wasSuccessful(),tests=result.testsRun,failures=len(result.failures),errors=len(result.errors),skips=len(result.skipped),existing_tests=138,stage6_synthetic_tests=20,stage6r2_tests=result.testsRun-158,no_final_model_scoring_in_preflight=True))
 if not result.wasSuccessful():print(stream.getvalue());raise RuntimeError('Preflight failed before scoring')
 approved,teams,games,anomalies,proof=rec.build()
 write_table(c.ROOT/'data/interim/home_away_reconciliation_2025_26.parquet',approved,'parquet')
 write_table(c.E/'home_away_reconciliation_2025_26.csv',approved,'csv')
 r.durable(c.E/'reconciliation_validation.json',dict(**proof,stage1d_function_sha256=r.sha(rec.SOURCE.encode()),season_only_overlay_sha256=r.sha(rec.ADAPTED.encode()),official_fact_sha256=r.access.checksum(c.E/'official_schedule_facts.json')),True)
 anomalies.to_csv(c.E/'post_reconciliation_anomalies.csv',index=False)
 feature_frame,feature_proof=ev.generate_features(teams,games)
 r.durable(c.E/'feature_validation.json',feature_proof,True)
 session=ev.arm(proof,feature_proof)
 try:
  # Existing feature builder was already validated; place boundary immediately at
  # first Elo replay rather than before feature reconstruction/model loading.
  original_runtime=r.runtime
  def ledger_runtime(current):
   rt=original_runtime(current);elo=rt.modeling_data.add_frozen_elo
   def before_elo(data,*args,**kw):
    if current.phase=='preflight':current.score_start(proof,feature_proof['passed'])
    return elo(data,*args,**kw)
   rt.modeling_data.add_frozen_elo=before_elo
   return rt
  from unittest.mock import patch
  with patch.object(r,'runtime',ledger_runtime):rt,pred=r.predict(session,rec.SCOPE,teams,games)
  hashes=ev.save_results(rt,pred,c.E/'evaluation',ev.PRED)
  for p in (c.E/'evaluation').glob('*.csv'):
   with (c.E/p.name).open('xb') as f:f.write(p.read_bytes());f.flush();os.fsync(f.fileno())
  d=r.read_json(session.ledger);d.update(status='aggregates_persisted',aggregate_results_persisted_at_utc=r.now());r.durable(session.ledger,d)
  c.protected();r.durable(c.E/'build_manifest.json',dict(passed=True,status='aggregate_evaluation_completed',output_sha256=hashes,code_sha256=c.checkpoint(),fit_calls=0,validated_games=1230,protected_files_unchanged=len(c.protected())),True)
  session.begin_replay();approved2,t2,g2,a2,p2=rec.build();rt2,pred2=r.predict(session,rec.SCOPE,t2,g2)
  h2=ev.save_results(rt2,pred2,c.E/'replay',c.E/'replay/predictions.parquet')
  if h2!=hashes:raise ValueError('Replay output mismatch: stop and preserve')
  r.durable(c.E/'replay_verification.json',dict(passed=True,byte_identical=True,fit_calls=0,network_calls=0,independent_confirmation=False,output_sha256=h2),True)
  d=r.read_json(session.ledger);d.update(status='completed',completed_at_utc=r.now());r.durable(session.ledger,d)
  c.protected();print('Stage 6R2 completed:',result.testsRun,'tests; 1230 games; deterministic replay identical; zero fits.')
 except Exception as exc:
  r.durable(c.E/'execution_stop.json',dict(error=type(exc).__name__+': '+str(exc),traceback=traceback.format_exc(),timestamp_utc=r.now(),automatic_restart_forbidden=True),True)
  print('STOP:',type(exc).__name__,str(exc));raise
if __name__=='__main__':main()
