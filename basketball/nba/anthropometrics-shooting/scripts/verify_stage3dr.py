"""Final checks preserve historical decisions and the coefficient firewall."""
import subprocess,sys,re
from stage3dr_common import *
def main():
 result=subprocess.run([sys.executable,'-m','unittest','discover','-s',str(ROOT/'tests'),'-p','test_stage3dr.py','-v'],capture_output=True,text=True);log=result.stdout+result.stderr;(E/'test_run.txt').write_text(log);match=re.search(r'Ran (\d+) tests',log);n=int(match[1]) if match else 0;good=result.returncode==0
 preserved=read(E/'prior_preservation_manifest.json');assert all(sha(ROOT/name)==h for name,h in preserved.items())
 replay=read(E/'reproduction_check.json');assert replay['decision_unchanged']
 save('test_summary.json',dict(tests_run=n,tests_passed=n if good else None,passed=good,historical_artifacts_unchanged=len(preserved),scope='Amendment/provenance/model invariants/firewall/frozen gate checks; adequacy remains a separate decision'))
 from stage3dr_report import main as report
 report()
 traces={}
 for x in M.glob('*trace.nc'):
  ignored=subprocess.run(['git','check-ignore','-q',str(x)],cwd=ROOT).returncode==0
  assert ignored,'Protected trace must remain Git-ignored'
  traces[str(x.relative_to(ROOT))]=dict(bytes=x.stat().st_size,sha256=sha(x),git_ignored=ignored,scientific_parameter_sealed=True)
 files=list(E.glob('*'))+list(F.glob('*.png'))+list((ROOT/'scripts').glob('*stage3dr*.py'))+[ROOT/'tests/test_stage3dr.py',ROOT/'docs/stage3dr_opportunity_prior_and_adequacy.md']
 save('build_manifest.json',dict(built_at=now(),decision=read(E/'model_adequacy_decision.json'),environment=read(E/'environment.json'),traces=traces,artifacts={str(x.relative_to(ROOT)):sha(x) for x in files if x.is_file() and x.name not in {'build_manifest.json','verification_run.txt'}},test_summary=read(E/'test_summary.json'),reproduction=replay,committed=False,pushed=False,stage3e_executed=False))
 print(json.dumps(read(E/'test_summary.json'),indent=2));assert good,log
if __name__=='__main__':main()
