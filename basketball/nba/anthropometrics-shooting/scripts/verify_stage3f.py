"""Predecision and final integrity tests; trace and artifact hashes."""
import subprocess,sys,re,argparse
from stage3f_common import *
def main(predecision=False):
 result=subprocess.run([sys.executable,'-m','unittest','discover','-s',str(ROOT/'tests'),'-p','test_stage3f.py','-v'],capture_output=True,text=True);log=result.stdout+result.stderr
 prefix='predecision_' if predecision else ''
 (E/(prefix+'test_run.txt')).write_text(log);match=re.search(r'Ran (\d+) tests',log);n=int(match[1]) if match else 0;good=result.returncode==0 and 'skipped=' not in log
 preserved=read(E/'prior_preservation_manifest.json');assert all(sha(ROOT/f)==h for f,h in preserved.items())
 out=dict(tests_run=n,tests_passed=n if good else None,passed=good,historical_artifacts_unchanged=len(preserved),scope='Protocol, likelihood, decomposition, data and firewall tests; predictive adequacy is separate')
 save(prefix+'test_summary.json',out);assert good,log
 if predecision:print(json.dumps(out,indent=2));return
 assert read(E/'reproduction_check.json')['decision_unchanged']
 from stage3f_report import main as report
 report()
 traces={}
 for path in M.glob('*trace.nc'):
  ignored=subprocess.run(['git','check-ignore','-q',str(path)],cwd=ROOT).returncode==0;assert ignored
  traces[str(path.relative_to(ROOT))]=dict(bytes=path.stat().st_size,sha256=sha(path),git_ignored=True,scientific_parameter_sealed=True)
 files=list(E.glob('*'))+list(F.glob('*.png'))+list((ROOT/'scripts').glob('*stage3f*.py'))+[ROOT/'tests/test_stage3f.py',ROOT/'docs/stage3f_hurdle_within_between_adequacy.md']
 save('build_manifest.json',dict(built_at=now(),environment=read(E/'environment.json'),decision=read(E/'stage3f_decision.json'),traces=traces,artifacts={str(f.relative_to(ROOT)):sha(f) for f in files if f.is_file() and f.name not in {'build_manifest.json','verification_run.txt'}},tests=out,reproduction=read(E/'reproduction_check.json'),committed=False,pushed=False,stage3g_executed=False))
 print(json.dumps(out,indent=2))
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--predecision',action='store_true');args=p.parse_args();main(args.predecision)
