"""Record failed numerical gate without reporting an invalid bootstrap interval."""
from stage3j_core import *
p=authorize(True);s=read(E/'j2_bootstrap_summary.json');assert s['replicates']==2000 and s['failed']>20
r=read(E/'j2_original_fit_audit.json');r.update(status='POINT_FIT_VALID_BOOTSTRAP_INTERVAL_WITHHELD',primary=False,ci_low=None,ci_high=None,bootstrap=s,bootstrap_interval_reportable=False,reason='More than 20/2000 bootstrap fits failed frozen unchanged Stage 2 numerical checks; no replacement or tuning',finished_at=now())
save('j2_beta_binomial_result.json',r,True)
print('J2 final numerical failures',s['failed'],'of',s['replicates'],'; interval withheld',flush=True)
