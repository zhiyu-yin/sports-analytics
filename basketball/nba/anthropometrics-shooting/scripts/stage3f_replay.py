"""Exact saved-trace replay without further sampling or scientific summaries."""
import sys,subprocess
from stage3f_common import *
def main():
 before=sha(E/'stage3f_decision.json');checks={}
 for key in ['f1','f2']:
  d=read(E/(key+'_diagnostics.json'))
  if not d.get('sampler_pass',False):checks[key]='SKIPPED_FAILED_SAMPLER';continue
  names=[key+suffix for suffix in ['_diagnostics.json','_opportunity_parameters.csv','_between_within_parameters.json','_random_effect_correlations.json','_conditional_accuracy_ppc.json','_joint_opportunity_ppc.json','_conditional_PPC_metrics.csv','_joint_PPC_metrics.csv']]
  hashes={n:sha(E/n) for n in names if (E/n).exists()}
  with (E/(key+'_replay_run.txt')).open('w') as log:r=subprocess.run([sys.executable,str(ROOT/'scripts/stage3f_ppc.py'),key.upper(),'--attempt',str(d['attempt'])],stdout=log,stderr=subprocess.STDOUT)
  assert r.returncode==0,key
  assert all(sha(E/n)==h for n,h in hashes.items()),key+' replay mismatch'
  checks[key]='EXACT_REPLAY_PASS'
 assert sha(E/'stage3f_decision.json')==before
 save('reproduction_check.json',dict(checked_at=now(),decision_unchanged=True,candidates=checks,method='Exact permitted summaries and fixed-seed conditional/joint predictive replay from saved traces; no additional MCMC fit'))
if __name__=='__main__':main()
