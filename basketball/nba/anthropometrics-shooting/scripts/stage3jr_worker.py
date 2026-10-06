"""Independent deterministic full-rerun worker; no RNG or scientific selection."""
from stage3jr_solver import *
BUNDLE=None
def initialize():
 global BUNDLE
 protocol();BUNDLE=inputs()
def run_one(rep):
 s=sample(BUNDLE,rep);r0=reference(s,prefix='full_reference');original=np.load(M/f'full_reference_{rep:04d}.npz');r,fit=polish(s,original['theta'])
 (M/f'full_{rep:04d}_diagnostics.json').write_text(json.dumps(clean(dict(reference=r0,remediated=r)),indent=2)+'\n')
 if fit is not None:np.savez(M/f'full_{rep:04d}.npz',**fit)
 row={k:v for k,v in r.items() if k!='attempts'};row.update(replicate=rep,sample_sha256=s['sample_sha256'],original_status=r0['status'])
 comparison=None
 if r0['status']=='PASS' and fit is not None:
  old_b=float(original['beta'][1]);best=min(r0['attempts'],key=lambda a:-a['log_likelihood'])
  comparison=dict(replicate=rep,old_beta=old_b,beta_absolute_difference=abs(float(fit['beta'][1])-old_b),loglik_absolute_difference=abs(r['log_likelihood']-best['log_likelihood']),score_absolute_difference=abs(r['best_score_max']-best['score_max']))
 return row,comparison
