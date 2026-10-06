"""Stage-local verification and Boolean-only final decision."""
import sys,subprocess,re
from stage3i_common import *
from stage3i_selection import decide

def verify(predecision=False):
 r=subprocess.run([sys.executable,'-m','unittest','discover','-s',str(ROOT/'tests'),'-p','test_stage3i.py','-v'],capture_output=True,text=True);log=r.stdout+r.stderr;prefix='predecision_' if predecision else '';(E/(prefix+'test_run.txt')).write_text(log);match=re.search(r'Ran (\d+) tests',log);n=int(match[1]) if match else 0;good=r.returncode==0 and n==27 and 'skipped=' not in log
 preserved=read(E/'prior_preservation_manifest.json');assert all(sha(ROOT/f)==h for f,h in preserved.items());out=dict(tests_run=n,tests_passed=n if good else None,passed=good,historical_artifacts_unchanged=len(preserved));save(prefix+'test_summary.json',out);assert good,'Inspect test log'
 if predecision:return
 assert read(E/'reproduction_check.json')['decision_unchanged'];assert read(E/'final_figures_visual_review.json')['passed']
 from stage3i_report import main as report
 report();traces={}
 for f in M.glob('*.nc'):
  assert subprocess.run(['git','check-ignore','-q',str(f)],cwd=ROOT).returncode==0
  traces[str(f.relative_to(ROOT))]=dict(bytes=f.stat().st_size,sha256=sha(f),git_ignored=True,protected=True)
 files=list(E.glob('*'))+list(F.glob('*.png'))+list((ROOT/'scripts').glob('stage3i_*.py'))+[ROOT/'tests/test_stage3i.py',ROOT/'docs/stage3i_residual_adequacy.md']
 save('build_manifest.json',dict(built_at=now(),protocol_sha256=sha(E/'model_protocol.json'),environment=read(ROOT/'docs/stage3f_evidence/environment.json'),traces=traces,artifacts={str(f.relative_to(ROOT)):sha(f) for f in files if f.is_file() and f.name not in ['build_manifest.json','verification_run.txt']},tests=out,committed=False,pushed=False,stage3g_executed=False));print(out)

def freeze():
 assert read(E/'predecision_test_summary.json')['passed'];assert not (E/'stage3i_decision.json').exists();authorize()
 prior=read(E/'prior_predictive_summary.json')['I3']['passed'];d=read(E/'i3_diagnostics.json');s=d.get('sampler_pass',False)
 a=read(E/'i3_conditional_accuracy_ppc.json').get('gate_pass') if s else None;o=read(E/'i3_joint_opportunity_ppc.json').get('gate_pass') if s else None
 result=decide(s,a if s else False,o if s else False,prior);result.update(frozen_at=now(),protocol_sha256=sha(E/'model_protocol.json'),I3_prior=prior,I3_sampler=s if prior else None,I3_accuracy=a,I3_opportunity=o,historical_decisions_unchanged=True,reason=('I3 prior prerequisite failed; posterior adequacy unassessed' if not prior else 'I3 sampler failed after its allowed recovery; PPC unassessed' if not s else 'I3 assessed under the unchanged accuracy and opportunity gates; I1/I2 are diagnostic only'))
 save('stage3i_decision.json',result);save('stage3g_authorization.json',dict(authorized=result['stage3g_authorized'],purpose='ESTIMAND REVIEW ONLY',candidate=result['selected_candidate'],scientific_effect_release_authorized=False,executed=False,decision_sha256=sha(E/'stage3i_decision.json')))
 import pandas as pd
 rows=[]
 for c in ['I0','I1','I2','I3']:
  k=c.lower();d=read(E/(k+'_diagnostics.json'));a=read(E/(k+'_conditional_accuracy_ppc.json'));o=read(E/(k+'_joint_opportunity_ppc.json'))
  rows.append(dict(candidate='H2 (I0 saved)' if c=='I0' else c,sampler_pass=d.get('sampler_pass'),max_rhat=d.get('max_rhat'),min_bulk_ESS=d.get('min_bulk_ESS'),min_tail_ESS=d.get('min_tail_ESS'),accuracy_pass=a.get('gate_pass'),opportunity_pass=o.get('gate_pass'),FTA_bin_failures=a.get('FTA_bin_99_fail_count'),systematic_volume_pattern=a.get('systematic_volume_pattern'),total_quantile_failures=o.get('quantile_99_fail_count'),positive_quantile_failures=o.get('positive_quantile_99_fail_count'),eligible_for_selection=c=='I3'))
 pd.DataFrame(rows).to_csv(E/'model_adequacy_comparison.csv',index=False);print(result)
if __name__=='__main__':freeze() if sys.argv[1]=='decision' else verify(sys.argv[1]=='predecision')
