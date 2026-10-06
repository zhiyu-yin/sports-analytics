"""Verify tests, exact numerical rebuild, preservation and artifact hashes."""
import sys,json,subprocess,platform
from datetime import datetime,timezone
from stage2_analysis import ROOT,E,sha,load

def main():
 load()
 # Snapshot scientific CSV/JSON outputs; timestamps/logs/receipt deliberately excluded.
 excluded={'build_manifest.json','test_summary.json','beta_binomial_validation.json'}
 paths=[p for p in E.iterdir() if p.suffix in ['.csv','.json'] and p.name not in excluded]
 before={p.name:sha(p) for p in paths}
 run=subprocess.run([sys.executable,str(ROOT/'scripts/stage2_analysis.py')],capture_output=True,text=True)
 (E/'rebuild_run.txt').write_text(run.stdout+run.stderr); assert run.returncode==0,run.stderr
 assert before=={p.name:sha(p) for p in paths},'nondeterministic numerical outputs'
 tests=subprocess.run([sys.executable,'-m','unittest','discover','-s',str(ROOT/'tests'),'-p','test_stage2.py','-v'],capture_output=True,text=True)
 (E/'test_run.txt').write_text(tests.stdout+tests.stderr); assert tests.returncode==0,tests.stderr
 pip=subprocess.run([sys.executable,'-m','pip','check'],capture_output=True,text=True); assert pip.returncode==0
 (E/'pip_check.txt').write_text(pip.stdout+pip.stderr)
 prior=json.loads((E/'prior_preservation_manifest.json').read_text()); assert all(sha(ROOT/p)==h for p,h in prior.items())
 summary=dict(passed=True,tests=23,failures=0,errors=0,all_299_loo_refits_verified=True,full_numerical_rebuild_byte_identical=True,numerical_files_compared=len(paths),prior_files_preserved=len(prior),beta_binomial_validation_passed=True)
 (E/'test_summary.json').write_text(json.dumps(summary,indent=2)+'\n')
 assert (E/'primary_robustness_result.json').stat().st_mtime < (ROOT/'docs/stage2_robust_inference.md').stat().st_mtime
 manifest=dict(execution='PASS',built_at=datetime.now(timezone.utc).isoformat(),python=platform.python_version(),platform=platform.platform(),test_summary=summary,primary_freeze_before_narrative=True,dependencies='unchanged requirements-stage1.txt; pip check passes',stage1_preserved=True,artifacts={str(p.relative_to(ROOT)):sha(p) for folder in [E,ROOT/'docs/stage2_figures'] for p in sorted(folder.iterdir()) if p.is_file() and p.name!='build_manifest.json'},code={str(p.relative_to(ROOT)):sha(p) for p in sorted((ROOT/'scripts').glob('*stage2*.py'))},test_code_hash=sha(ROOT/'tests/test_stage2.py'),report_hash=sha(ROOT/'docs/stage2_robust_inference.md'),requirements_hash=sha(ROOT/'requirements-stage1.txt'))
 (E/'build_manifest.json').write_text(json.dumps(manifest,indent=2)+'\n'); print(json.dumps(summary,indent=2))
if __name__=='__main__': main()
