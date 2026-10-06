"""Prospective numerical-only amendment after sealed first-ladder diagnostics."""
from stage3jr_common import *
p=read(E/'ladder_v1/numerical_protocol.json');ladder=read(E/'ladder_v1/remediation_ladder.json')
assert read(E/'ladder_v1/failed_retry_summary.json')['remaining_failures']==4
assert not (E/'full_bootstrap_summary.json').exists()
ladder['frozen_at']=now();ladder['R4']='Only if R1/R2/R3 fail, scipy root(method=lm) solves the same score=0 equations from the same original R0 endpoint, with the validated observed-information Jacobian; ftol=xtol=gtol=1e-12, maxiter=500. Numerical Levenberg-Marquardt damping acts in the equation solver, not as a statistical penalty or modified likelihood. Require solver success plus all unchanged score, boundary, multi-start, Hessian and covariance gates.'
ladder['selection']=ladder['selection'].replace('No methods after R3.','No methods after R4.')
ladder['uniform_final']=ladder['uniform_final'].replace('R1/R2/R3','R1/R2/R3/R4')
save('remediation_ladder.json',ladder)
p.update(frozen_at=now(),version=2,ladder_sha256=sha(E/'remediation_ladder.json'),amendment='First sealed numerical-only trial repaired 295/299. Preserve its protocol, code and raw results. Add deterministic LM score-equation fallback prospectively before second retry; no coefficient distribution inspected. All scientific fields and acceptance gates unchanged.',execution='Four independent spawned processes for full rerun, single BLAS thread each; ordered results, identical immutable samples; no RNG in fitting workers')
for name in list(p['code_hashes']):p['code_hashes'][name]=sha(ROOT/name)
p['code_hashes']['scripts/stage3jr_worker.py']=sha(ROOT/'scripts/stage3jr_worker.py');p['code_hashes']['scripts/stage3jr_amend.py']=sha(Path(__file__))
save('numerical_protocol.json',p);save('numerical_freeze_receipt.json',dict(frozen_at=p['frozen_at'],sha256=sha(E/'numerical_protocol.json')))
save('numerical_amendment.json',dict(frozen_at=p['frozen_at'],previous_protocol_sha256=sha(E/'ladder_v1/numerical_protocol.json'),new_protocol_sha256=sha(E/'numerical_protocol.json'),basis='Four numerical solver-status failures only; no scientific summary',acceptance_criteria_unchanged=True,model_unchanged=True,original_trial_preserved=True,scientific_firewall_intact=True))
print('Prospective numerical amendment frozen',sha(E/'numerical_protocol.json'),flush=True)
