"""Tests, Boolean-only decision freeze, post-freeze comparison and provenance."""
import sys,subprocess,re
from stage3h_common import *
from stage3h_selection import Gates,decide

def verify(predecision=False):
 from stage3h_report import main as report
 report();r=subprocess.run([sys.executable,'-m','unittest','discover','-s',str(ROOT/'tests'),'-p','test_stage3h.py','-v'],capture_output=True,text=True);log=r.stdout+r.stderr;prefix='predecision_' if predecision else '';(E/(prefix+'test_run.txt')).write_text(log);match=re.search(r'Ran (\d+) tests',log);n=int(match[1]) if match else 0;good=r.returncode==0 and n==26 and 'skipped=' not in log
 preserved=read(E/'prior_preservation_manifest.json');assert all(sha(ROOT/f)==h for f,h in preserved.items());out=dict(tests_run=n,tests_passed=n if good else None,passed=good,historical_artifacts_unchanged=len(preserved));save(prefix+'test_summary.json',out);assert good,'Inspect test log'
 if predecision:return
 assert read(E/'reproduction_check.json')['decision_unchanged']
 assert read(E/'final_figures_visual_review.json')['passed']
 report();traces={}
 for f in M.glob('*.nc'):
  assert subprocess.run(['git','check-ignore','-q',str(f)],cwd=ROOT).returncode==0,'Trace must remain ignored'
  traces[str(f.relative_to(ROOT))]=dict(bytes=f.stat().st_size,sha256=sha(f),git_ignored=True,protected=True)
 files=list(E.glob('*'))+list(F.glob('*.png'))+list((ROOT/'scripts').glob('stage3h_*.py'))+[ROOT/'tests/test_stage3h.py',ROOT/'docs/stage3h_shared_opportunity_factor.md']
 save('build_manifest.json',dict(built_at=now(),protocol_sha256=sha(E/'model_protocol.json'),environment=read(ROOT/'docs/stage3f_evidence/environment.json'),traces=traces,artifacts={str(f.relative_to(ROOT)):sha(f) for f in files if f.is_file() and f.name not in ['build_manifest.json','verification_run.txt']},tests=out,committed=False,pushed=False,stage3g_executed=False));print(out)

def freeze():
 assert read(E/'predecision_test_summary.json')['passed'];assert not (E/'stage3h_decision.json').exists()
 prior=read(E/'h1_prior_predictive.json')['passed']
 def gates(key):
  d=read(E/(key+'_diagnostics.json'))
  if not d['sampler_pass']:return Gates(False)
  return Gates(True,read(E/(key+'_conditional_accuracy_ppc.json'))['gate_pass'],read(E/(key+'_joint_opportunity_ppc.json'))['gate_pass'])
 h1=gates('h1') if prior else Gates(False);h2=gates('h2') if (E/'h2_diagnostics.json').exists() else None
 if prior and not h1.sampler:assert read(E/'h1_diagnostics.json')['recovery_exhausted'] and h2 is None
 result=decide(h1,h2,prior);result.update(frozen_at=now(),protocol_sha256=sha(E/'model_protocol.json'),H1_sampler=h1.sampler,H1_accuracy=h1.accuracy if h1.sampler else None,H1_opportunity=h1.opportunity if h1.sampler else None,H2_run=h2 is not None,H2_sampler=h2.sampler if h2 else None,H2_accuracy=h2.accuracy if h2 and h2.sampler else None,H2_opportunity=h2.opportunity if h2 and h2.sampler else None,historical_decisions_unchanged=True)
 save('stage3h_decision.json',result);save('stage3g_authorization.json',dict(authorized=result['stage3g_authorized'],purpose='ESTIMAND REVIEW ONLY',candidate=result['selected_candidate'],scientific_effect_release_authorized=False,executed=False,decision_sha256=sha(E/'stage3h_decision.json')))
 compare();print(result)
def compare():
 import pandas as pd
 decision=read(E/'stage3h_decision.json');rows=[]
 for c,folder,dim in [('F1',ROOT/'docs/stage3f_evidence',3),('F2',ROOT/'docs/stage3f_evidence',3),('H1',E,2),('H2',E,2)]:
  key=c.lower();d=read(folder/(key+'_diagnostics.json')) if (folder/(key+'_diagnostics.json')).exists() else {}
  def ppc(suffix):
   f=folder/(key+'_'+suffix+'.json');return read(f) if f.exists() else {}
  a,o=ppc('conditional_accuracy_ppc'),ppc('joint_opportunity_ppc')
  rows.append(dict(candidate=c,status='ASSESSED' if d else 'NOT_RUN_STOPPING_RULE',sampler_pass=d.get('sampler_pass'),max_rhat=d.get('max_rhat'),min_bulk_ESS=d.get('min_bulk_ESS'),min_tail_ESS=d.get('min_tail_ESS'),accuracy_pass=a.get('gate_pass') if d.get('sampler_pass') else None,opportunity_pass=o.get('gate_pass') if d.get('sampler_pass') else None,FTA_bin_failures=a.get('FTA_bin_99_fail_count'),systematic_volume_pattern=a.get('systematic_volume_pattern'),latent_dimensions_per_player=dim))
 pd.DataFrame(rows).to_csv(E/'model_adequacy_comparison.csv',index=False);save('comparison_receipt.json',dict(created_at=now(),decision_sha256=sha(E/'stage3h_decision.json'),scope='Sampler/PPC/latent dimensionality only; no scientific parameter comparison'))
if __name__=='__main__':freeze() if sys.argv[1]=='decision' else verify(sys.argv[1]=='predecision')
