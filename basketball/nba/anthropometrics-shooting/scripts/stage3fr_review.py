"""Record a completed manual review, or a mandatory numeric failure."""
import sys
from stage3fr_common import *
def finalize(candidate,attempt,visual_ok=False):
 d=read(E/f'{candidate.lower()}_attempt{attempt}_diagnostics.json')
 d['sealed_parameter_in_model']=candidate!='DIAG-C'
 if d['numeric_gate_pass']:
  assert d['sealed_parameter_sampler_pass'], 'Anonymous sealed-parameter sampler check failed'
  assert visual_ok,'Review permitted trace/energy plots before passing';review=dict(reviewed_at=now(),chains_mix=True,energy_acceptable=True,scope='Permitted standardized chains and energy; all non-sealed scalar convergence checks also passed; no scientific-effect plot');save(f'{candidate.lower()}_attempt{attempt}_visual_review.json',review);d.update(sampler_pass=True,visual_review=review)
 else:
  assert attempt==2,'One authorized recovery remains';d.update(sampler_pass=False,visual_review='NOT_RELEASED_FAILED_NUMERIC_GATE',recovery_exhausted=True)
 save(candidate.lower()+'_diagnostics.json',d)
 if candidate.startswith('DIAG'):save(candidate.lower().replace('-','_')+'_result.json',dict(**d,diagnostic_only=True,scientifically_eligible=False))
if __name__=='__main__':finalize(sys.argv[1],int(sys.argv[2]),len(sys.argv)>3 and sys.argv[3]=='reviewed')
