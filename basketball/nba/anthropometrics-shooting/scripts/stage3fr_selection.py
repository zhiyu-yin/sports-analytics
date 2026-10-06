"""Pure selection: no trace, coefficient or filesystem access."""
from dataclasses import dataclass
@dataclass(frozen=True)
class Eligible:
 name:str
 equivalent:bool
 sampler:bool
 def __post_init__(self):
  if self.name not in ('R1','R2','R3'):raise ValueError('Diagnostic models are never eligible')
  if type(self.equivalent) is not bool or type(self.sampler) is not bool:raise TypeError('Boolean gates required')
def select(candidates):
 for expected,c in zip(('R1','R2','R3'),candidates):
  if c.name!=expected:raise ValueError('Candidate order changed')
  if c.equivalent and c.sampler:return c.name
 return None
def classify(selected,accuracy,opportunity,tests):
 if any(type(v) is not bool for v in [accuracy,opportunity,tests]):raise TypeError('Boolean gates required')
 if selected not in (None,'R1','R2','R3'):raise ValueError('Ineligible candidate')
 if selected is None or not tests:code='C';label='IDENTIFICATION UNRESOLVED — NO EQUIVALENT F2 PARAMETERIZATION PASSES SAMPLER'
 elif accuracy and opportunity:code='A';label='IDENTIFICATION RESOLVED — F2 SAMPLER PASSES AND PPC PASSES'
 else:code='B';label='COMPUTATION RESOLVED — F2 SAMPLER PASSES BUT PPC FAILS'
 return dict(classification_code=code,classification=label,selected_parameterization=selected,stage3g_authorized=code=='A',stage3g_purpose='ESTIMAND REVIEW ONLY',stage3g_executed=False,scientific_parameter_status='SEALED',scientific_inference_authorized=False,stage3e_authorized=False)
