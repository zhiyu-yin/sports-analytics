"""Prospective freeze of exactly three independent residual adequacy models."""
from stage3i_common import *
import copy,shutil

def main():
 assert not (E/'model_protocol.json').exists()
 preserved=read(ROOT/'docs/stage3h_evidence/prior_preservation_manifest.json')
 for folder in ['docs/stage3h_evidence','docs/stage3h_figures','models/stage3h']:
  for f in (ROOT/folder).glob('*'):
   if f.is_file():preserved[str(f.relative_to(ROOT))]=sha(f)
 for f in list((ROOT/'scripts').glob('*stage3h*.py'))+[ROOT/'tests/test_stage3h.py',ROOT/'docs/stage3h_shared_opportunity_factor.md']:preserved[str(f.relative_to(ROOT))]=sha(f)
 for n,h in preserved.items():assert sha(ROOT/n)==h,n
 save('prior_preservation_manifest.json',preserved)
 baseline={}
 for suffix in ['diagnostics.json','conditional_accuracy_ppc.json','joint_opportunity_ppc.json','conditional_PPC_metrics.csv','joint_PPC_metrics.csv']:
  source=ROOT/'docs/stage3h_evidence'/('h2_'+suffix);target=E/('i0_'+suffix);shutil.copyfile(source,target);baseline[str(source.relative_to(ROOT))]=dict(sha256=sha(source),copy=str(target.relative_to(ROOT)))
 a=read(E/'i0_conditional_accuracy_ppc.json');o=read(E/'i0_joint_opportunity_ppc.json')
 assert read(E/'i0_diagnostics.json')['sampler_pass']
 assert a['pooled_rate_99_pass'] and a['global_metrics_99_fail_count']==1 and a['season_rate_99_fail_count']==0 and a['FTA_bin_99_fail_count']==0 and a['systematic_volume_pattern'] and not a['gate_pass']
 assert o['zero_frequency_99_pass'] and o['quantile_99_fail_count']==2 and o['positive_quantile_99_fail_count']==2 and o['season_totals_outside_99_low']==o['season_totals_outside_99_high']==0 and not o['gate_pass']
 save('i0_baseline_manifest.json',dict(source='Exact saved H2; no refit or new PPC',files=baseline,trace_sha256=sha(ROOT/'models/stage3h/h2_attempt1_trace.nc')))
 d=fixed_data();w=observed_within(d);sd=float(w.std(ddof=1));z=w/sd;center=float(np.mean(z*z))
 save('within_quadratic_basis.json',dict(s_W=sd,ddof=1,row_weighting='Equal weight for every frozen panel row, including zero FTA',rows=len(w),quadratic_center=center,centered_quadratic_mean=float(np.mean(z*z-center)),source_sha256=sha(ROOT/'docs/stage3f_evidence/opportunity_decomposition.csv'),outcome_independent=True,definition='zW=w/s_W; qW=zW**2-quadratic_center',joint_prediction='Recompute within from generated FTA by frozen decomposition, then apply the fixed observed-panel s_W and quadratic_center; never rescale or recenter on generated data'))
 old=read(ROOT/'docs/stage3h_evidence/prior_protocol.json');prior=copy.deepcopy(old);prior.pop('H2');prior.update(frozen_at=now(),I1=dict(gamma_W1=['Normal',0,.25],gamma_W2=['Normal',0,.25]),I2=dict(theta_W=['Normal',0,.5],c_player=['Normal',0,1],sigma_count_resid=['HalfNormal',.5]),I3='Exact union of I1 accuracy and I2 independent count residual',independent_count_residual=True)
 save('prior_protocol.json',prior)
 oldmodel=read(ROOT/'docs/stage3h_evidence/model_protocol.json')
 model={k:copy.deepcopy(oldmodel[k]) for k in ['panel_sha256','rows','players','seasons','FTA','positive_rows','zero_rows','positions','seasons_list','height_center','GP_offset_coefficient','sampling','recovery','max_recoveries','diagnostics','all_latent_elements_checked','PPC','positive_count_gate','decomposition_csv_sha256','decomposition_metadata_sha256']}
 code=list((ROOT/'scripts').glob('stage3i_*.py'))+[ROOT/'scripts'/n for n in ['stage3f_common.py','stage3f_model.py','stage3d_model.py','stage3d_protocol.py','stage3d_selection.py','stage3dr_ppc.py','stage3c_results.py']]
 model.update(frozen_at=now(),candidates=dict(I1='Exact H2 except standardized linear plus centered quadratic within terms in accuracy',I2='Exact H2 plus independent standard-normal count-only player residual with HalfNormal(.5) scale',I3='Exact union of I1 and I2 modifications'),candidate_order=['I1','I2','I3'],eligible_candidates=['I3'],I0='Exact saved H2; never refit',hypotheses=dict(A='Simple quadratic within curvature may explain residual accuracy-volume bias',B='Independent count-specific persistent heterogeneity may repair positive FTA shape'),latent_formula=oldmodel['latent_formula'],count_residual='c independent of o and e; sigma_count_resid*c enters positive-count log mean only',theta_B_absent=True,no_new_correlations=True,no_I4=True,prior_protocol_sha256=sha(E/'prior_protocol.json'),basis_sha256=sha(E/'within_quadratic_basis.json'),frozen_code={str(f.relative_to(ROOT)):sha(f) for f in code},selection='Only I3 all gates plus protocol/firewall pass authorizes estimand review. I1/I2 failures do not block independently predeclared I3. I3 sampler failure stops; no I4.',prior_failure='All prior checks precede all fits; I3 failure stops without tuning. A diagnostic prior failure is recorded and prevents that diagnostic fit, without preventing independently predeclared I3 if its prior passes.',scientific_parameter_status='SEALED',stage3g_executed=False,no_commit=True,no_push=True)
 save('model_protocol.json',model);save('freeze_receipt.json',dict(frozen_at=model['frozen_at'],model_protocol_sha256=sha(E/'model_protocol.json'),prior_protocol_sha256=sha(E/'prior_protocol.json')))
 save('input_audit.json',dict(panel_sha256=sha(PANEL),rows=len(d),historical_artifacts_preserved=len(preserved),reports_read=['stage3h_shared_opportunity_factor.md','stage3fr_f2_identification_reparameterization.md','stage3f_hurdle_within_between_adequacy.md','stage3dr_opportunity_prior_and_adequacy.md'],historical_decisions_unchanged=True))
 print('Frozen',sha(E/'model_protocol.json'),'historical artifacts',len(preserved),flush=True)
if __name__=='__main__':main()
