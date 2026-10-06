"""Run offline audit tests and preserve machine-readable and full text results."""
import sys,unittest,io,datetime,platform
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from anthropometrics_shooting.stage0b_io import ROOT,E,dump

def main():
    stream=io.StringIO();suite=unittest.defaultTestLoader.discover(str(ROOT/'tests'))
    result=unittest.TextTestRunner(stream=stream,verbosity=2).run(suite)
    log=stream.getvalue();(E/'test_run.txt').write_text(log);print(log)
    dump(E/'test_summary.json',dict(run_at=datetime.datetime.now(datetime.timezone.utc).isoformat(),python=platform.python_version(),tests_run=result.testsRun,passed=result.testsRun-len(result.failures)-len(result.errors)-len(result.skipped),failures=len(result.failures),errors=len(result.errors),skipped=len(result.skipped),successful=result.wasSuccessful(),scope='7 Stage 0 tests plus Stage 0B eligibility, provenance, frozen-table and static no-model guard tests; offline local source files required'))
    return 0 if result.wasSuccessful() else 1
if __name__=='__main__':sys.exit(main())
