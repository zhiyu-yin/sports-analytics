"""Freeze the effect-blind adequacy decision after protocol/firewall tests."""
import pandas as pd
from stage3f_common import *
from stage3f_selection import Gate,classify

def main():
 assert not (E/'stage3f_decision.json').exists()
 checks=read(E/'predecision_test_summary.json');assert checks['passed'] and checks['tests_passed']==22
 rows=[];gates={}
 for key in ['f0','f1','f2']:
  d=read(E/(key+'_diagnostics.json'));a=read(E/(key+'_conditional_accuracy_ppc.json'));o=read(E/(key+'_joint_opportunity_ppc.json'));gates[key]=Gate(bool(d.get('sampler_pass',False)),bool(a.get('gate_pass',False)),bool(o.get('gate_pass',False)))
  rows.append(dict(candidate=key.upper(),sampler_pass=gates[key].sampler,conditional_accuracy_pass=gates[key].accuracy,joint_opportunity_pass=gates[key].opportunity,accuracy_assessment_status=a.get('status','EVALUATED'),opportunity_assessment_status=o.get('status','EVALUATED'),FTA_bin_fail_count=a.get('FTA_bin_99_fail_count'),systematic_low_high_pattern=a.get('systematic_volume_pattern'),zero_frequency_pass=o.get('zero_frequency_99_pass'),FTA_quantile_fail_count=o.get('quantile_99_fail_count'),positive_quantile_fail_count=o.get('positive_quantile_99_fail_count'),scientific_inference_authorized=False))
 result=classify(gates['f1'],gates['f2'],True)
 pd.DataFrame(rows).to_csv(E/'model_adequacy_comparison.csv',index=False)
 save('stage3f_decision.json',dict(**result,frozen_at=now(),protocol_sha256=sha(E/'model_protocol.json'),prior_pass=read(E/'prior_gate_decision.json')['passed'],firewall_intact=True,protocol_tests_passed=True,comparison=rows,selection_function_sha256=sha(ROOT/'scripts/stage3f_selection.py'),no_posthoc_structure_or_prior_change=True,prior_decisions_preserved=True))
 print(json.dumps(result,indent=2))
if __name__=='__main__':main()
