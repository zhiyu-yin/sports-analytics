"""Adequacy decisions accept only explicit Boolean gate records."""
from dataclasses import dataclass
@dataclass(frozen=True)
class Gates:
 sampler:bool
 accuracy:bool=False
 opportunity:bool=False
 def __post_init__(self):
  if not all(type(v) is bool for v in [self.sampler,self.accuracy,self.opportunity]):raise TypeError('Boolean gates required')
 @property
 def passes(self):return self.sampler and self.accuracy and self.opportunity

def next_candidate(h1):return 'H2' if h1.sampler and not h1.passes else None

def decide(h1,h2=None,prior_pass=True):
 if not prior_pass:code='D';label='SHARED-FACTOR ADEQUACY UNRESOLVED';selected=None;reason='Prior-predictive prerequisite failed; posterior sampling not run'
 elif not h1.sampler:code='C';label='SHARED-FACTOR IDENTIFICATION UNRESOLVED';selected=None;reason='H1 sampler failed its single recovery'
 elif h1.passes:
  assert h2 is None;code='A';label='SHARED-FACTOR ADEQUACY RESOLVED — H1 PASSES';selected='H1';reason='H1 passed all gates'
 else:
  assert h2 is not None,'H2 required after valid H1 predictive failure'
  if h2.passes:code='B';label='SHARED-FACTOR ADEQUACY RESOLVED — H2 PASSES';selected='H2';reason='H2 passed all gates'
  else:code='D';label='SHARED-FACTOR ADEQUACY UNRESOLVED';selected=None;reason='H2 sampler failure' if not h2.sampler else 'H2 predictive inadequacy'
 return dict(classification_code=code,classification=label,selected_candidate=selected,reason=reason,stage3g_authorized=code in ['A','B'],stage3g_purpose='ESTIMAND REVIEW ONLY',scientific_effect_release_authorized=False,scientific_parameter_status='SEALED',stage3g_executed=False,stage3e_authorized=False)
