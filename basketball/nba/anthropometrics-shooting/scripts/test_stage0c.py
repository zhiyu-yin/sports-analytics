"""Run only Stage 0C tests: earlier tests read outcomes and are deliberately not run."""
import sys,unittest,io,platform
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from anthropometrics_shooting.stage0c import ROOT,E,dump,sha,now
import json

def main():
    stream=io.StringIO();suite=unittest.defaultTestLoader.discover(str(ROOT/'tests'),pattern='test_stage0c.py')
    result=unittest.TextTestRunner(stream=stream,verbosity=2).run(suite)
    (E/'test_run.txt').write_text(stream.getvalue());print(stream.getvalue())
    summary=dict(run_at=now(),tests_run=result.testsRun,passed=result.testsRun-len(result.failures)-len(result.errors)-len(result.skipped),failures=len(result.failures),errors=len(result.errors),skipped=len(result.skipped),successful=result.wasSuccessful(),python=platform.python_version(),scope='Stage 0C only; no earlier outcome-reading test suites executed')
    dump(E/'test_summary.json',summary)
    gate=json.loads((E/'validation_summary.json').read_text())
    decision=gate['decision_pending_tests'] if result.wasSuccessful() else 'PARTIAL — INSUFFICIENT DIRECT VALIDATION'
    dump(E/'release_gate_decision.json',dict(decision=decision,tests_passed=result.wasSuccessful(),criteria=gate['gate_criteria'],stage1_may_begin=decision=='PASS',stage1_executed=False,no_residual_fit=True,no_effect_estimate=True))
    build=json.loads((E/'build_manifest.json').read_text());build.update(final_decision=decision,test_summary_sha256=sha(E/'test_summary.json'),test_run_sha256=sha(E/'test_run.txt'),release_decision_sha256=sha(E/'release_gate_decision.json'))
    dump(E/'build_manifest.json',build)
    return 0 if result.wasSuccessful() else 1
if __name__=='__main__':sys.exit(main())
