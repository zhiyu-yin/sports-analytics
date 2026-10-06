"""Exact deterministic predictive replay; never refit or unseal scientific summaries."""
import subprocess,sys
from stage3dr_common import *
def main():
 before=sha(E/'model_adequacy_decision.json');checks={}
 for key in ['d1','d2','d3']:
  diag=read(E/(key+'_diagnostics.json'))
  if not diag['sampler_pass']:checks[key]='SKIPPED_FAILED_SAMPLER';continue
  names=[key+'_diagnostics.json',key+'_attempt_volume_parameter.json',key+'_dispersion_parameter.json',key+'_random_effect_correlation.json',key+'_ppc_summary.json',key+'_conditional_accuracy_ppc.json',key+'_joint_opportunity_ppc.json',key+'_conditional_PPC_metrics.csv',key+'_joint_PPC_metrics.csv']
  hashes={n:sha(E/n) for n in names if (E/n).exists()}
  with (E/(key+'_replay_run.txt')).open('w') as f:run=subprocess.run([sys.executable,str(ROOT/'scripts/stage3dr_ppc.py'),key.upper(),'--attempt',str(diag['attempt'])],stdout=f,stderr=subprocess.STDOUT)
  assert run.returncode==0,key
  assert all(sha(E/n)==h for n,h in hashes.items()),'Predictive replay changed an artifact'
  checks[key]='EXACT_REPLAY_PASS'
 assert sha(E/'model_adequacy_decision.json')==before
 save('reproduction_check.json',dict(checked_at=now(),candidates=checks,decision_unchanged=True,method='Exact saved-trace permitted summaries and seeded predictive simulations; no additional posterior fit'))
if __name__=='__main__':main()
