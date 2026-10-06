"""Final tests and provenance; protocol checks never override adequacy failure."""
import sys,subprocess,re,argparse
from stage3fr_common import *
from stage3fr_selection import Eligible,select,classify

def verify(predecision=False):
 from stage3fr_report import main as report
 report();r=subprocess.run([sys.executable,'-m','unittest','discover','-s',str(ROOT/'tests'),'-p','test_stage3fr.py','-v'],capture_output=True,text=True);log=r.stdout+r.stderr;prefix='predecision_' if predecision else '';(E/(prefix+'test_run.txt')).write_text(log);match=re.search(r'Ran (\d+) tests',log);n=int(match[1]) if match else 0;good=r.returncode==0 and 'skipped=' not in log and n==23
 preserved=read(E/'prior_preservation_manifest.json');assert all(sha(ROOT/f)==h for f,h in preserved.items());out=dict(tests_run=n,tests_passed=n if good else None,passed=good,historical_artifacts_unchanged=len(preserved));save(prefix+'test_summary.json',out)
 if not good:raise RuntimeError('Tests failed; inspect '+prefix+'test_run.txt')
 if predecision:return
 assert read(E/'reproduction_check.json')['decision_unchanged']
 report();traces={}
 for f in M.glob('*.nc'):
  assert subprocess.run(['git','check-ignore','-q',str(f)],cwd=ROOT).returncode==0
  traces[str(f.relative_to(ROOT))]=dict(bytes=f.stat().st_size,sha256=sha(f),git_ignored=True,protected=True)
 files=list(E.glob('*'))+list(F.glob('*.png'))+list((ROOT/'scripts').glob('*stage3fr*.py'))+[ROOT/'tests/test_stage3fr.py',ROOT/'docs/stage3fr_f2_identification_reparameterization.md']
 save('build_manifest.json',dict(built_at=now(),protocol_sha256=sha(E/'reparameterization_protocol.json'),environment=read(ROOT/'docs/stage3f_evidence/environment.json'),traces=traces,artifacts={str(f.relative_to(ROOT)):sha(f) for f in files if f.is_file() and f.name not in ['build_manifest.json','verification_run.txt']},tests=out,committed=False,pushed=False,stage3g_executed=False));print(json.dumps(out),flush=True)
def decide():
 assert not (E/'final_reparameterization_decision.json').exists();assert read(E/'predecision_test_summary.json')['passed'];eligible=[]
 for k in ['R1','R2','R3']:
  d=read(E/f'{k.lower()}_diagnostics.json') if (E/f'{k.lower()}_diagnostics.json').exists() else {}
  if not d or 'sampler_pass' not in d:break
  eligible.append(Eligible(k,bool(read(E/f'{k.lower()}_equivalence_validation.json')['passed']),d['sampler_pass']))
  if d['sampler_pass']:break
 selected=select(eligible)
 if selected is None:assert len(eligible)==3,'Complete all frozen justified eligible candidates'
 a=read(E/'f2_conditional_accuracy_ppc.json')['gate_pass'] if selected else False;o=read(E/'f2_joint_opportunity_ppc.json')['gate_pass'] if selected else False
 result=classify(selected,a,o,True);result.update(frozen_at=now(),protocol_sha256=sha(E/'reparameterization_protocol.json'),conditional_accuracy_pass=a if selected else None,joint_opportunity_pass=o if selected else None,eligible_order=[v.name for v in eligible],historical_decisions_unchanged=True)
 save('final_reparameterization_decision.json',result);save('stage3g_authorization.json',dict(authorized=result['stage3g_authorized'],purpose='ESTIMAND REVIEW ONLY',scientific_effect_release_authorized=False,executed=False,decision_sha256=sha(E/'final_reparameterization_decision.json')));print(json.dumps(result),flush=True)
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('action',choices=['predecision','decision','final']);a=p.parse_args();decide() if a.action=='decision' else verify(a.action=='predecision')
