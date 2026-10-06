"""Exact deterministic reanalysis of saved MCMC draws, without refitting or overwriting results."""
import subprocess,sys
from stage3c_setup import *
def main():
 checks={}
 for kind,name in [('primary','primary_replication_result.json'),('full','full_panel_result.json')]:
  if kind=='full' and not read(E/name).get('model_fitted',True):
   checks['full_exact_saved_trace_replay']=None;checks['full_not_run_reason']=read(E/name)['status'];continue
  path=E/name;before=sha(path);attempt=read(path)['attempt']
  for action in ['analyze','freeze']:
   run=subprocess.run([sys.executable,str(ROOT/'scripts/stage3c_results.py'),action,'--kind',kind,'--attempt',str(attempt)],capture_output=True,text=True)
   (E/f'{kind}_replay_{action}.txt').write_text(run.stdout+run.stderr);assert run.returncode==0,run.stderr
  assert sha(path)==before,'Frozen result changed';checks[kind+'_exact_saved_trace_replay']=True
 repeat=read(E/'sampling_reproduction.json');assert repeat['status']=='COMPLETE' and repeat['means_within_predeclared_MCSE_tolerance']
 save('reproduction_check.json',dict(**checks,checked_at=now(),method='Exact reanalysis of stored posterior draws and seeded posterior predictive simulations; result-file SHA256 unchanged; separate same-seed primary refit',independent_MCMC_refit_performed=True,sampler_reproduction_passed=True,posterior_arrays_exact_in_same_environment=repeat['all_posterior_arrays_exact'],scope='Same-environment numerical reproduction; not a claim of bit-identical sampling across software/hardware',posterior_MCSE_available_in='sampling_reproduction_parameters.csv'))
 print(json.dumps(read(E/'reproduction_check.json'),indent=2))
if __name__=='__main__':main()
