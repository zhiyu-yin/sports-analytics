"""Verify immutable results without rerunning historical builders."""
import subprocess,sys,re
from stage3c_setup import *
def main():
 run=subprocess.run([sys.executable,'-m','unittest','discover','-s',str(ROOT/'tests'),'-p','test_stage3c.py','-v'],capture_output=True,text=True)
 text=run.stdout+run.stderr;(E/'test_run.txt').write_text(text);n=int(re.search(r'Ran (\d+) tests',text)[1]);good=run.returncode==0
 preserved=read(E/'prior_preservation_manifest.json');assert all(sha(ROOT/p)==h for p,h in preserved.items())
 summary=dict(tests_run=n,tests_passed=n if good else None,passed=good,historical_files_preserved=len(preserved),no_stage3d=True,scope='data/model/diagnostic/PPC/freeze/replay verification; scientific sign is not a gate')
 save('test_summary.json',summary)
 primary=read(E/'primary_replication_result.json');full=read(E/'full_panel_result.json')
 execution_pass=good and primary['scientifically_reportable'] and full['scientifically_reportable']
 decision=dict(stage3c_execution='PASS' if execution_pass else 'FAIL',reason='All required gates passed' if execution_pass else 'Primary posterior predictive adequacy gate failed' if not primary['scientifically_reportable'] else 'Verification or secondary gate failed',verification_tests_passed=good,scientific_result_independent_of_execution=True,primary_frozen=True,primary_scientifically_reportable=primary['scientifically_reportable'],full_secondary_fitted=full.get('model_fitted',True),stage3d_executed=False,committed=False,pushed=False,reproduction='Exact posterior-summary replay from retained traces and separate same-seed primary sampler reproduction')
 save('execution_status.json',decision)
 from stage3c_report import main as render_report
 render_report()
 traces={str(p.relative_to(ROOT)):dict(bytes=p.stat().st_size,sha256=sha(p),git_ignored=True) for p in M.glob('*_trace.nc')}
 paths=list(E.glob('*'))+list(F.glob('*.png'))+list((ROOT/'scripts').glob('*stage3c*.py'))+list(M.glob('source*.py'))+[ROOT/'tests/test_stage3c.py',ROOT/'requirements-stage3c.txt',ROOT/'docs/stage3c_primary_hierarchical_replication.md']
 save('build_manifest.json',dict(built_at=now(),execution=decision,environment=read(E/'environment.json'),test_summary=summary,traces=traces,artifacts={str(p.relative_to(ROOT)):sha(p) for p in sorted(paths) if p.is_file() and p.name not in {'build_manifest.json','verification_run.txt'}},prior_preservation_sha256=sha(E/'prior_preservation_manifest.json')))
 print(json.dumps(dict(test_summary=summary,execution=decision),indent=2));assert good,text
if __name__=='__main__':main()
