"""Freeze adequacy using only typed gate inputs and permitted mechanism outputs."""
import pandas as pd
from stage3dr_common import *
from stage3d_selection import CandidateGate,select_future_model
def main():
 assert not (E/'model_adequacy_decision.json').exists();gates={};rows=[]
 prior_pass=bool(read(E/'prior_gate_decision.json')['passed'])
 no_change=sha(ROOT/'scripts/stage3dr_model.py')==amendment()['model_code_sha256']
 assert prior_pass and no_change
 for candidate in ['D1','D2','D3']:
  key=candidate.lower();diag=read(E/(key+'_diagnostics.json'));cp=read(E/('d3_conditional_accuracy_ppc.json' if candidate=='D3' else key+'_ppc_summary.json'));jp=read(E/'d3_joint_opportunity_ppc.json') if candidate=='D3' else {}
  gates[candidate]=CandidateGate(prior_pass,bool(diag.get('sampler_pass',False)),bool(cp.get('gate_pass',False)),bool(jp.get('gate_pass',False)),no_change,True)
  fields=['pooled_rate_99_pass','global_metrics_99_fail_count','season_rate_99_fail_count','FTA_bin_99_fail_count','systematic_volume_pattern']
  rows.append(dict(model=candidate,sampler_pass=diag.get('sampler_pass',False),**{x:cp.get(x) for x in fields},joint_FTA_PPC_pass=jp.get('gate_pass'),overall_adequacy=bool(diag.get('sampler_pass',False) and cp.get('gate_pass',False) and (candidate!='D3' or jp.get('gate_pass',False))),eligible_for_Stage3E=False))
 gates['D0']=CandidateGate(True,True,False,False,True,True);selected=select_future_model(gates)
 if selected['stage3e_authorized']:selected['selected_future_model']='D3_amended_prior';rows[-1]['eligible_for_Stage3E']=True
 d0=read(ROOT/'docs/stage3d_evidence/d0_saved_ppc_summary.json');columns=list(rows[0]);rows.insert(0,{k:('D0' if k=='model' else d0.get(k)) for k in columns});pd.DataFrame(rows).to_csv(E/'model_adequacy_comparison.csv',index=False)
 allowed={name:read(E/name) for name in ['d1_attempt_volume_parameter.json','d2_dispersion_parameter.json','d3_random_effect_correlation.json']}
 output=dict(**selected,frozen_at=now(),amendment_sha256=sha(E/'opportunity_prior_amendment.json'),original_protocol_sha256=amendment()['original_protocol_sha256'],prior_gate=read(E/'prior_gate_decision.json'),candidate_adequacy=rows,permitted_mechanism_summaries=allowed,scientific_coefficient_unsealed=False,firewall_intact=True,no_posthoc_structural_change=True,selection_input_schema=list(CandidateGate.__slots__),selection_function_sha256=sha(ROOT/'scripts/stage3d_selection.py'))
 save('model_adequacy_decision.json',output);save('stage3e_authorization.json',dict(stage3e_authorized=selected['stage3e_authorized'],selected_future_model=selected['selected_future_model'],scientific_parameter_status=selected['scientific_parameter_status'],decision_sha256=sha(E/'model_adequacy_decision.json'),stage3e_executed=False))
 print(json.dumps(selected,indent=2))
if __name__=='__main__':main()
