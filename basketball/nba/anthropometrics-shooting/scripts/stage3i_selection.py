"""Pure Boolean adequacy decision: only I3 can authorize estimand review."""
def decide(sampler,accuracy,opportunity,protocol_firewall):
 for x in [sampler,accuracy,opportunity,protocol_firewall]:
  if type(x) is not bool:raise TypeError('Boolean gates only')
 if not sampler or not protocol_firewall:code='D'
 elif accuracy and opportunity:code='A'
 elif opportunity:code='B'
 elif accuracy:code='C'
 else:code='D'
 labels={'A':'RESIDUAL ADEQUACY RESOLVED — I3 PASSES','B':'ACCURACY RESIDUAL REMAINS','C':'OPPORTUNITY RESIDUAL REMAINS','D':'RESIDUAL ADEQUACY UNRESOLVED'}
 return dict(classification_code=code,classification=labels[code],selected_candidate='I3' if code=='A' else None,stage3g_authorized=code=='A',stage3g_purpose='ESTIMAND REVIEW ONLY',scientific_effect_release_authorized=False,scientific_parameter_status='SEALED',stage3g_executed=False)
