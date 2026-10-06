"""Read-only verification of preserved evidence; writes Stage 3B receipts only."""
import subprocess,sys,re,platform
from stage3b_release import *
def main():
 run=subprocess.run([sys.executable,'-m','unittest','discover','-s',str(ROOT/'tests'),'-p','test_stage3b.py','-v'],capture_output=True,text=True)
 output=run.stdout+run.stderr;(E/'test_run.txt').write_text(output);n=int(re.search(r'Ran (\d+) tests',output)[1])
 summary=dict(tests_run=n,tests_passed=n if run.returncode==0 else None,passed=run.returncode==0,historical_files_preserved=len(read(E/'historical_preservation_manifest.json')),classification=read(E/'amended_gate_decision.json')['classification'],part_b_authorized=read(E/'part_b_authorization.json')['part_b_authorized'],part_b_executed=False,scientific_association_calculated=False)
 save('test_summary.json',summary)
 paths=list(E.glob('*'))+list((ROOT/'scripts').glob('*stage3b*.py'))+[ROOT/'tests/test_stage3b.py',ROOT/'docs/stage3b_protocol_amendment.md']
 save('build_manifest.json',dict(built_at=now(),environment=dict(python=platform.python_version(),executable=sys.executable,requirements_sha256=sha(ROOT/'requirements-stage3-partA.txt')),test_summary=summary,artifacts={str(p.relative_to(ROOT)):sha(p) for p in sorted(paths) if p.is_file() and p.name!='build_manifest.json'},historical_decisions_modified=False,part_b_executed=False))
 print(json.dumps(summary,indent=2));assert run.returncode==0,output
if __name__=='__main__':main()
