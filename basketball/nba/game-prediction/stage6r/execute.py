"""Single authorized Part B recovery, using unchanged frozen Stage 6 math."""
import json,traceback
from unittest.mock import patch
import support as s
r=s.old
RAW=s.ROOT/'data/raw/stage6r/leaguegamelog_response.json'
PRED=s.ROOT/'data/processed/stage6r_predictions_2025_26.parquet'

def opening():
 gate=r.read_json(s.E/'part_a_exit_gate.json')
 if not gate['passed']:raise RuntimeError('Part A did not pass')
 manifest=r.read_json(s.E/'recovery_code_manifest.json')
 if {p:d['after_sha256'] for p,d in manifest['files'].items()}!=s.hashes():raise RuntimeError('Recovery code changed after gate')
 if r.access.checksum(s.E/'recovery_code_manifest.json')!=gate['recovery_code_manifest_sha256']:raise RuntimeError('Checkpoint changed')
 s.verify_protected();r.verify()
 # New ledger, preserving the exact original stopped attempt and all timestamps.
 d=r.read_json(r.E/'final_opening_ledger.json')
 links=['docs/stage6_evidence/authorization.txt','docs/stage6_evidence/final_opening_ledger.json','docs/stage6_evidence/acquisition_failure.json','docs/stage6_evidence/execution_stop.json','docs/stage6r_evidence/authorization.txt','docs/stage6r_evidence/recovery_code_manifest.json','docs/stage6r_evidence/part_a_exit_gate.json']
 d.update(status='armed',original_attempt_status='stopped_before_response',recovery_reason='TLS transport integration defect',scientific_protocol_changed=False,model_recipe_changed=False,final_outcome_previously_decoded=False,final_performance_previously_exposed=False,linked_artifact_sha256={p:r.access.checksum(s.ROOT/p) for p in links},recovery_authorization_sha256=s.AUTH,recovery_authorization_recorded_at_utc=r.now(),recovery_code_sha256=s.hashes(),first_physical_data_access_at_utc=None,first_outcome_decode_at_utc=None,aggregate_results_persisted_at_utc=None)
 r.durable(s.E/'recovery_opening_ledger.json',d,True)
 session=r.Session(s.E);session.ledger=s.E/'recovery_opening_ledger.json';session.phase='armed'
 return session

def run():
 session=opening()
 try:
  result,cap=s.launch('part_b');r.durable(s.E/'transport_result.json',dict(**result,capability_id=cap['id']),True)
  if not result.get('passed'):raise RuntimeError('Recovery transport failed: '+result.get('error',str(result)))
  meta=r.read_json(s.E/'acquisition.json')
  if meta['nba_api_version']!=r.version('nba_api'):raise RuntimeError('nba_api version mismatch')
  with r.access._RAW_OPEN(RAW,'rb') as f:body=f.read()
  if r.sha(body)!=meta['sha256']:raise ValueError('Raw cache hash mismatch')
  session.phase='accessed';session.decode_start()
  from nba_game_prediction.ingest import extract_table
  columns,rows=extract_table(body);r.durable(s.E/'response_schema.json',dict(schema=columns,raw_row_count=len(rows),sha256=meta['sha256'],transport_checkpoint_sha256=r.access.checksum(s.E/'recovery_code_manifest.json')),True)
  scope,teams,games=r.validate_body(body,s.E);session.phase='validated'
  rt,pred=r.predict(session,scope,teams,games)
  with patch.object(r,'E',s.E),patch.object(r,'PRED',PRED):hashes=r.save_results(rt,pred,s.E)
  d=r.read_json(session.ledger);d.update(status='aggregates_persisted',aggregate_results_persisted_at_utc=r.now());r.durable(session.ledger,d)
  s.verify_protected();r.durable(s.E/'build_manifest.json',dict(passed=True,status='evaluation_complete',output_sha256=hashes,code_sha256=s.hashes(),fit_calls=0,protected_files_unchanged=True,validated_games=len(games)),True)
  session.begin_replay();out=s.E/'replay';out.mkdir()
  with r.access._RAW_OPEN(RAW,'rb') as f:cached=f.read()
  if r.sha(cached)!=meta['sha256']:raise ValueError('Replay cache hash changed')
  scope2,t2,g2=r.validate_body(cached,out);rt2,p2=r.predict(session,scope2,t2,g2)
  with patch.object(r,'E',s.E),patch.object(r,'PRED',PRED):h2=r.save_results(rt2,p2,out)
  if hashes!=h2:raise ValueError('Deterministic replay mismatch; STOP')
  r.durable(s.E/'replay_verification.json',dict(passed=True,byte_identical=True,independent_confirmation=False,fit_calls=0,network_calls=0,output_sha256=h2),True)
  d=r.read_json(session.ledger);d.update(status='completed',completed_at_utc=r.now());r.durable(session.ledger,d)
  print('Stage 6R completed; replay identical.')
 except Exception as exc:
  error=type(exc).__name__+': '+str(exc)
  r.durable(s.E/'execution_stop.json',dict(error=error,traceback=traceback.format_exc(),timestamp_utc=r.now(),automatic_retry_forbidden=True),True)
  d=r.read_json(session.ledger);d.update(status='stopped',stopped_at_utc=r.now(),stop_reason=error);r.durable(session.ledger,d)
  if not (s.E/'build_manifest.json').exists():r.durable(s.E/'build_manifest.json',dict(passed=False,status='stopped',reason=error,code_sha256=s.hashes(),fit_calls=0,protected_files_unchanged=bool(s.verify_protected())),True)
  if not (s.E/'replay_verification.json').exists():r.durable(s.E/'replay_verification.json',dict(passed=False,status='not performed',independent_confirmation=False,reason='Recovery evaluation incomplete'),True)
  print('STOP:',error)
if __name__=='__main__':run()
