"""Verify the prior-stop investigation, without claiming posterior execution."""
import subprocess,sys,re
from stage3d_protocol import *
def main():
 result=subprocess.run([sys.executable,'-m','unittest','discover','-s',str(ROOT/'tests'),'-p','test_stage3d.py','-v'],capture_output=True,text=True)
 output=result.stdout+result.stderr;(E/'test_run.txt').write_text(output);match=re.search(r'Ran (\d+) tests',output);count=int(match[1]) if match else 0;passed=result.returncode==0
 preserved=read(E/'prior_preservation_manifest.json');assert all(sha(ROOT/n)==h for n,h in preserved.items())
 summary=dict(tests_run=count,tests_passed=count if passed else None,passed=passed,prior_artifacts_unchanged=len(preserved),scope='Provenance, model graphs/prior validity, firewall, gate logic and mandatory-stop enforcement; no posterior diagnostics claimed',posterior_candidates_fitted=0)
 save('test_summary.json',summary)
 decision=read(E/'model_adequacy_decision.json');save('execution_status.json',dict(classification=decision['classification'],stop_phase=decision['stop_phase'],verification_passed=passed,adequacy_resolved=False,stage3e_authorized=False,posterior_fits=0,committed=False,pushed=False))
 from stage3d_report import main as report
 report()
 paths=list(E.glob('*'))+list(F.glob('*.png'))+list((ROOT/'scripts').glob('*stage3d*.py'))+[ROOT/'tests/test_stage3d.py',ROOT/'requirements-stage3d.txt',ROOT/'docs/stage3d_attempt_volume_model_adequacy.md']
 save('build_manifest.json',dict(built_at=now(),protocol_hash=sha(E/'model_adequacy_protocol.json'),decision_hash=sha(E/'model_adequacy_decision.json'),environment=read(E/'environment.json'),test_summary=summary,posterior_traces=[],prior_predictive_storage={str(x.relative_to(ROOT)):dict(bytes=x.stat().st_size,sha256=sha(x),git_ignored=True) for x in M.glob('*.npz')},artifacts={str(x.relative_to(ROOT)):sha(x) for x in sorted(paths) if x.is_file() and x.name not in {'build_manifest.json','verification_run.txt'}},preservation_manifest_sha256=sha(E/'prior_preservation_manifest.json'),notes='No candidate posterior exists; prior storage is not a posterior trace. Active verifier log and manifest itself excluded to avoid self-referential hashes.'))
 print(json.dumps(summary,indent=2));assert passed,output
if __name__=='__main__':main()
