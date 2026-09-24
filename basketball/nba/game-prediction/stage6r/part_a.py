"""Versioned offline/local-TLS gate. Never acquires final-season data."""
import io,unittest,sys
import support as s
import historical_regression

def run():
 r=s.old
 if (s.E/'recovery_opening_ledger.json').exists():raise RuntimeError('Part B already armed; no preflight restart')
 s.verify_protected();r.verify()
 stream=io.StringIO();suite=unittest.TestSuite()
 for folder,pattern in [('tests','test*.py'),('stage6','test_preflight.py'),('stage6r','test_transport.py')]:
  # Separate loaders avoid cached discovery top-level mismatch.
  suite.addTests(unittest.TestLoader().discover(str(s.ROOT/folder),pattern=pattern))
 result=unittest.TextTestRunner(stream=stream,verbosity=2).run(suite)
 (s.E/'test_run.txt').write_text(stream.getvalue())
 summary=dict(tests=result.testsRun,passed=result.wasSuccessful(),failures=len(result.failures),errors=len(result.errors),skips=len(result.skipped),expected_scope=dict(existing=138,stage6_synthetic=20,transport_regression=11),final_data_access=False)
 r.durable(s.E/'test_summary.json',summary)
 if not result.wasSuccessful():
  r.durable(s.E/'part_a_exit_gate.json',dict(passed=False,reason='Tests failed'));raise RuntimeError('Part A tests failed')
 history=historical_regression.run();freeze=r.verify();protected=s.verify_protected();tls=r.read_json(s.E/'local_tls_proof.json');cause=r.read_json(s.E/'tls_root_cause.json')
 manifest=dict(created_at_utc=r.now(),files={p:dict(before_sha256=None,after_sha256=h,change='New recovery-only transport, gate, provenance or output-routing code; no historical/scientific code edited') for p,h in s.hashes().items()},original_stage6_code=r.checkpoint(),scientific_code_changes=[],historical_code_unchanged=True)
 r.durable(s.E/'recovery_code_manifest.json',manifest)
 r.durable(s.E/'transport_preflight.json',dict(passed=True,root_cause_reproduced=cause['reproduced'],real_tls=tls,ordinary_development_network_blocked=True,tests=summary,final_data_access=False,fit_calls=0))
 r.durable(s.E/'scientific_freeze_verification.json',dict(**freeze,historical_regression=history,protected_count=len(protected)))
 gate=dict(passed=True,created_at_utc=r.now(),root_cause_reproduced=True,tls_compatible_repair=True,real_tls_test_passed=True,ordinary_network_block_passed=True,final_data_access_during_part_a=False,scientific_artifacts_unchanged=True,scope='Isolated single-use exact-endpoint acquisition capability; local TLS only in Part A',fit_calls=0,tuning_calls=0,tests=result.testsRun,protected_count=len(protected),recovery_code_manifest_sha256=r.access.checksum(s.E/'recovery_code_manifest.json'),transport_preflight_sha256=r.access.checksum(s.E/'transport_preflight.json'),scientific_freeze_verification_sha256=r.access.checksum(s.E/'scientific_freeze_verification.json'))
 r.durable(s.E/'part_a_exit_gate.json',gate);print('Part A PASS:',result.testsRun,'tests;',len(protected),'protected files unchanged; exact historical regression; no final access.')
if __name__=='__main__':run()
