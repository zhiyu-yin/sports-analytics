"""Additional numerical and sampling audits; no specification modification."""
from stage3j_core import *
import ast

def main():
 p=authorize(True);d=load();checks={}
 # Time-invariant exposure/height/position within each observed player.
 for c in ['residual_wingspan','height_wo_shoes_inches','combine_position']:
  assert int(d.groupby('player_id')[c].nunique(dropna=False).max())==1,c
 checks['time_invariant_exposure_height_position']=True
 # Validate the exact HC1 implementation against statsmodels HC0 on synthetic rows.
 rng=np.random.default_rng(118);x=pd.DataFrame(dict(Intercept=np.ones(180),a=rng.normal(size=180),b=rng.normal(size=180)));n=rng.integers(10,70,180);y=rng.binomial(n,1/(1+np.exp(-(.8+.1*x.a-.2*x.b))))
 m,_,_=glm(x,y,n);cov,parts=sandwich(m,y,n,np.arange(180),hc1=True)
 ref=sm.GLM(np.c_[y,n-y],x,family=sm.families.Binomial()).fit(cov_type='HC0').cov_params().to_numpy()*180/177
 np.testing.assert_allclose(cov,ref,rtol=1e-7,atol=1e-9);checks['J3_HC1_vs_statsmodels_HC0_scaled_max_error']=float(np.max(np.abs(cov-ref)))
 # Saved full schedule audit, including failed replicates: RNG draws are never replaced.
 layout=player_layout(d);replay={}
 for tag,seed in [('j1',20260930),('j2',20260931)]:
  f=pd.read_csv(E/(tag+'_player_bootstrap.csv'));assert len(f)==2000;rng=np.random.default_rng(seed);schedule=[];success_checks=0
  for _,row in f.iterrows():
   selected,instances,draws=draw_clusters(layout,rng);digest=hashlib.sha256(draws.astype('<i8').tobytes()).hexdigest();positive=d.fta.to_numpy()[selected]>0
   schedule.append(dict(replicate=int(row.replicate),draws=857,accounting_rows=len(selected),positive_rows=int(positive.sum()),contributing_cluster_instances=len(np.unique(instances[positive])),sample_sha256=digest,status=row.status))
   if row.status=='PASS':
    assert row.sample_sha256==digest;assert row.accounting_rows==len(selected);assert row.positive_rows==positive.sum();assert row.contributing_cluster_instances==len(np.unique(instances[positive]));success_checks+=1
  pd.DataFrame(schedule).to_csv(E/(tag+'_complete_sample_schedule.csv'),index=False)
  replay[tag]=dict(replicates=2000,successful_draw_hashes_and_sizes_checked=success_checks,failed_draws_retained=2000-success_checks,all_draws=857,unique_instance_per_draw=True)
 checks['all_4000_sample_schedules']=replay
 # Old BB implementation remains byte-identical; classify recorded failures without repairing them.
 f=pd.read_csv(E/'j2_player_bootstrap.csv');kinds={};max_spread=0.;max_score=0.;all_opt_success=True
 for err in f.loc[f.status=='FAIL','error']:
  message=ast.literal_eval(err[len('RuntimeError('):-1]) if err.startswith('RuntimeError(') else err
  kind=message.split(':',1)[0];kinds[kind]=kinds.get(kind,0)+1
  if kind=='BB convergence failure':
   attempts=ast.literal_eval(message.split(': ',1)[1]);max_spread=max(max_spread,np.ptp([a['negative_log_likelihood'] for a in attempts]));max_score=max(max_score,max(a['score_max'] for a in attempts));all_opt_success=all_opt_success and all(a['success'] for a in attempts)
 checks['J2_failure_types']=kinds;checks['J2_failed_start_max_likelihood_spread']=max_spread;checks['J2_failed_start_max_score']=max_score;checks['J2_all_failed_start_optimizers_reported_success']=all_opt_success
 checks.update(passed=True,completed_at=now(),model_changed=False,failed_fits_replaced=False)
 save('supplementary_checks.json',checks,True);print('Supplementary audit PASS',flush=True)
if __name__=='__main__':main()
