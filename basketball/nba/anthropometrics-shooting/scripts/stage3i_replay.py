"""Exact PPC replay from valid saved traces; no extra MCMC."""
import subprocess,sys
from stage3i_common import *
def main():
 decision=E/'stage3i_decision.json';initial=sha(decision);results={}
 for key in ['i1','i2','i3']:
  f=E/(key+'_diagnostics.json')
  if not f.exists() or not read(f).get('sampler_pass'):continue
  suffixes=['conditional_PPC_metrics.csv','joint_PPC_metrics.csv','conditional_accuracy_ppc.json','joint_opportunity_ppc.json','latent_factor_parameters.json']+(['within_parameters.json'] if key in ['i1','i3'] else [])+(['count_residual_parameter.json','positive_count_shape.csv'] if key in ['i2','i3'] else [])
  before={s:sha(E/(key+'_'+s)) for s in suffixes};attempt=read(f)['attempt']
  with (E/(key+'_replay_run.txt')).open('w') as out:r=subprocess.run([sys.executable,str(ROOT/'scripts/stage3i_ppc.py'),key.upper(),'--attempt',str(attempt)],stdout=out,stderr=subprocess.STDOUT)
  assert r.returncode==0;after={s:sha(E/(key+'_'+s)) for s in suffixes};assert before==after;results[key]=dict(exact_match=True,artifacts=before)
 assert sha(decision)==initial
 save('reproduction_check.json',dict(checked_at=now(),decision_unchanged=True,no_additional_MCMC=True,candidates=results,status='EXACT_SAVED_TRACE_PPC_REPLAY' if results else 'NOT_RUN_NO_VALID_SAMPLER'))
if __name__=='__main__':main()
