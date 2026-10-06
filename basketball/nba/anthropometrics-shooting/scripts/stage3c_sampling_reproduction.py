"""Repeat the frozen primary sampler; never select or replace scientific results."""
import time
import numpy as np
import pymc as pm
import arviz as az
from stage3c_model import build,KEY,progress_callback
from stage3c_setup import *

def main():
 result=read(E/'primary_replication_result.json');settings=result['sampling']
 trace=M/'primary_reproduction_trace.nc';assert not trace.exists()
 record=dict(started_at=now(),primary_result_sha256=sha(E/'primary_replication_result.json'),settings=settings,seed=20260928,status='RUNNING',purpose='Same-seed numerical reproducibility check; does not replace frozen inference',criterion='Each key-parameter mean within four combined MCSEs; exact posterior equality also checked',code_sha256=sha(Path(__file__)))
 save('sampling_reproduction.json',record);start=time.monotonic()
 try:
  with build('primary'):
   repeat=pm.sample(draws=settings['draws'],tune=settings['tune'],chains=4,cores=4,random_seed=20260928,target_accept=settings['target_accept'],nuts_sampler='pymc',blas_cores=1,mp_ctx='spawn',compile_kwargs={'mode':'NUMBA'},callback=progress_callback,progressbar=False,return_inferencedata=True,idata_kwargs={'log_likelihood':False})
  repeat.to_netcdf(trace)
  original=az.from_netcdf(M/f"primary_attempt{result['attempt']}_trace.nc")
  a=az.summary(original,var_names=KEY,round_to='none');b=az.summary(repeat,var_names=KEY,round_to='none')
  delta=np.abs(a['mean']-b['mean']);limit=4*np.sqrt(a.mcse_mean**2+b.mcse_mean**2)
  table=a[['mean','mcse_mean']].rename(columns={'mean':'original_mean','mcse_mean':'original_mcse'}).join(b[['mean','mcse_mean']].rename(columns={'mean':'repeat_mean','mcse_mean':'repeat_mcse'}))
  table['absolute_difference']=delta;table['four_combined_MCSE']=limit;table['within_tolerance']=delta<=limit;table.to_csv(E/'sampling_reproduction_parameters.csv')
  exact=all(np.array_equal(original.posterior[v],repeat.posterior[v]) for v in original.posterior.data_vars)
  passed=bool((delta<=limit).all())
  record.update(status='COMPLETE',completed_at=now(),elapsed_seconds=time.monotonic()-start,all_posterior_arrays_exact=exact,means_within_predeclared_MCSE_tolerance=passed,max_Rhat=float(b.r_hat.max()),minimum_bulk_ESS=float(b.ess_bulk.min()),minimum_tail_ESS=float(b.ess_tail.min()),divergences=int(repeat.sample_stats.diverging.sum()),trace_sha256=sha(trace),trace_bytes=trace.stat().st_size)
  assert sha(E/'primary_replication_result.json')==record['primary_result_sha256']
  assert passed,'Numerical reproduction failed; preserve results and investigate without selecting a preferred coefficient'
 except Exception as ex:
  record.update(status='FAILED',error=repr(ex));raise
 finally:save('sampling_reproduction.json',record)
 print(json.dumps(record,indent=2))
if __name__=='__main__':main()
