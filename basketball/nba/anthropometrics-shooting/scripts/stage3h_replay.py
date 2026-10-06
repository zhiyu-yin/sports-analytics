"""Exact PPC replay from valid saved traces; no extra MCMC."""
import subprocess,sys
from stage3h_common import *
def main():
 decision=E/'stage3h_decision.json';initial=sha(decision);results={}
 for key in ['h1','h2']:
  f=E/(key+'_diagnostics.json')
  if not f.exists() or not read(f).get('sampler_pass'):continue
  suffixes=['conditional_PPC_metrics.csv','joint_PPC_metrics.csv','conditional_accuracy_ppc.json','joint_opportunity_ppc.json','latent_factor_parameters.json']+(['within_parameter.json'] if key=='h2' else [])
  before={s:sha(E/(key+'_'+s)) for s in suffixes};attempt=read(f)['attempt']
  with (E/(key+'_replay_run.txt')).open('w') as out:r=subprocess.run([sys.executable,str(ROOT/'scripts/stage3h_ppc.py'),key.upper(),'--attempt',str(attempt)],stdout=out,stderr=subprocess.STDOUT)
  assert r.returncode==0;after={s:sha(E/(key+'_'+s)) for s in suffixes};assert before==after;results[key]=dict(exact_match=True,artifacts=before)
 assert sha(decision)==initial
 save('reproduction_check.json',dict(checked_at=now(),decision_unchanged=True,no_additional_MCMC=True,candidates=results,status='EXACT_SAVED_TRACE_PPC_REPLAY' if results else 'NOT_RUN_NO_VALID_SAMPLER'))
if __name__=='__main__':main()
