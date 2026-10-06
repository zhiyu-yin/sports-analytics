"""Record human visual review or finalized numeric failure."""
import sys
from stage3i_common import *
def run(candidate,attempt,reviewed=False):
 d=read(E/f'{candidate.lower()}_attempt{attempt}_diagnostics.json')
 if d['numeric_gate_pass']:
  assert d['sealed_parameter_sampler_pass'] and reviewed
  v=dict(reviewed_at=now(),chains_mix=True,energy_acceptable=True,scope='Permitted standardized chains and energy; scientific coefficient never plotted')
  save(f'{candidate.lower()}_attempt{attempt}_visual_review.json',v);d.update(sampler_pass=True,visual_review=v)
 else:
  assert attempt==2;d.update(sampler_pass=False,recovery_exhausted=True,visual_review='NOT_RELEASED_FAILED_NUMERIC_GATE')
 save(candidate.lower()+'_diagnostics.json',d)
 if not d['sampler_pass']:
  for suffix in ['latent_factor_parameters','conditional_accuracy_ppc','joint_opportunity_ppc']:
   save(candidate.lower()+'_'+suffix+'.json',dict(candidate=candidate,status='WITHHELD_FAILED_SAMPLER_GATE',gate_pass=None))
  if candidate in ['I1','I3']:save(candidate.lower()+'_within_parameters.json',dict(status='WITHHELD_FAILED_SAMPLER_GATE'))
  if candidate in ['I2','I3']:
   save(candidate.lower()+'_count_residual_parameter.json',dict(status='WITHHELD_FAILED_SAMPLER_GATE'))
   (E/(candidate.lower()+'_positive_count_shape.csv')).write_text('metric,status\npositive_count_shape,WITHHELD_FAILED_SAMPLER_GATE\n')
if __name__=='__main__':run(sys.argv[1],int(sys.argv[2]),len(sys.argv)>3 and sys.argv[3]=='reviewed')
