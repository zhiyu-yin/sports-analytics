"""Freeze a prior-gate stop, with no posterior or scientific-effect input."""
import pandas as pd
from stage3d_protocol import *
from stage3d_selection import CandidateGate,select_future_model
def main():
 p=protocol();priors={k:read(E/(k.lower()+'_prior_predictive.json')) for k in ['D1','D2','D3']}
 assert not priors['D3']['acceptable'] and not list(M.glob('*posterior*'))
 baseline=read(E/'d0_saved_ppc_summary.json')
 gates={'D0':CandidateGate(True,True,False,False,True,True)}
 for k in priors:gates[k]=CandidateGate(priors[k]['acceptable'],False,False,False,True,True)
 selected=select_future_model(gates)
 rows=[dict(model='D0 Stage3C baseline',sampler_pass=True,pooled_rate_99_pass=False,global_metrics_99_fail_count=2,season_rate_99_fail_count=0,FTA_bin_99_fail_count=4,systematic_volume_pattern=True,joint_FTA_PPC_pass=None,overall_adequacy=False,eligible_for_Stage3E=False,assessment_status='SAVED_FAILED_PPC')]
 for key,label in [('D1','mean-volume diagnostic'),('D2','dispersion-volume diagnostic'),('D3','joint opportunity-accuracy')]:
  reason='PRIOR_OPPORTUNITY_GATE_FAILED' if key=='D3' else 'NOT_FITTED_GLOBAL_PRIOR_STOP'
  rows.append(dict(model=key+' '+label,sampler_pass=None,pooled_rate_99_pass=None,global_metrics_99_fail_count=None,season_rate_99_fail_count=None,FTA_bin_99_fail_count=None,systematic_volume_pattern=None,joint_FTA_PPC_pass=None,overall_adequacy=False,eligible_for_Stage3E=False,assessment_status=reason))
  save(key.lower()+'_diagnostics.json',dict(status='NOT_RUN',reason=reason,posterior_fitted=False,sampler_pass=None))
  ppcnames=[key.lower()+'_ppc_summary.json'] if key!='D3' else ['d3_conditional_accuracy_ppc.json','d3_joint_opportunity_ppc.json']
  for name in ppcnames:save(name,dict(status='NOT_RUN',reason=reason,posterior_predictive_replicates=0,gate_pass=None))
 save('d1_attempt_volume_parameter.json',dict(status='NOT_ESTIMATED',parameter='gamma_FTA',reason='Posterior fitting stopped at D3 prior gate'))
 save('d2_dispersion_parameter.json',dict(status='NOT_ESTIMATED',parameter='gamma_k',representative_FTA=[5,25,75,200,400],rho_summaries=None,reason='Posterior fitting stopped at D3 prior gate'))
 save('d3_random_effect_correlation.json',dict(status='NOT_ESTIMATED',parameter='corr_uv',reason='No joint-model posterior exists; prior correlations are not posterior evidence'))
 (E/'d3_opportunity_parameters.csv').write_text('parameter,posterior_mean,posterior_median,CI95_low,CI95_high\n')
 pd.DataFrame(rows).to_csv(E/'model_adequacy_comparison.csv',index=False)
 decision=dict(**selected,frozen_at=now(),protocol_hash=sha(E/'model_adequacy_protocol.json'),candidate_definitions=p['candidates'],stop_phase='PRIOR_PREDICTIVE',reason='D3 opportunity prior fails both prospectively frozen gross-scale limits; user-required stop before outcome posterior fitting',D0_adequacy_status=rows[0],D1_adequacy_status=rows[1],D2_adequacy_status=rows[2],D3_adequacy_status=rows[3],D1_gamma_FTA_summary=None,D2_gamma_k_summary=None,D3_corr_uv_summary=None,D3_opportunity_model_summary=dict(prior_predictive=priors['D3']['opportunity'],posterior=None),all_PPC_gate_fields=rows,prior_checks={k:v['acceptable'] for k,v in priors.items()},posterior_fits=0,posthoc_model_changes=False,scientific_effect_accessed=False,classification_qualification='D3 failed its prior-predictive prerequisite; posterior adequacy was not evaluated. This is not evidence that every possible prior for this joint structure would fail.',selection_input_schema=list(CandidateGate.__slots__),selection_code_sha256=sha(ROOT/'scripts/stage3d_selection.py'))
 path=E/'model_adequacy_decision.json';assert not path.exists();save(path.name,decision)
 save('stage3e_authorization.json',dict(stage3e_authorized=False,selected_future_model='NONE',scientific_parameter_status='NOT_AUTHORIZED',decision_sha256=sha(path),reason='D3 prior gate failed; no posterior adequacy assessment',stage3e_executed=False))
 print(json.dumps({k:decision[k] for k in ['classification','stop_phase','selected_future_model','stage3e_authorized','scientific_parameter_status']},indent=2))
if __name__=='__main__':main()
