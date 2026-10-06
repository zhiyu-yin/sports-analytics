"""Freeze both new structural candidates before any prior simulation."""
from stage3h_common import *
import copy

def main():
 assert not (E/'model_protocol.json').exists()
 preserved=read(ROOT/'docs/stage3fr_evidence/prior_preservation_manifest.json')
 for folder in ['docs/stage3fr_evidence','docs/stage3fr_figures','models/stage3fr']:
  for f in (ROOT/folder).glob('*'):
   if f.is_file():preserved[str(f.relative_to(ROOT))]=sha(f)
 for f in list((ROOT/'scripts').glob('*stage3fr*.py'))+[ROOT/'tests/test_stage3fr.py',ROOT/'docs/stage3fr_f2_identification_reparameterization.md']:preserved[str(f.relative_to(ROOT))]=sha(f)
 for n,h in preserved.items():assert sha(ROOT/n)==h,n
 save('prior_preservation_manifest.json',preserved)
 old=read(ROOT/'docs/stage3f_evidence/prior_protocol.json')
 prior=dict(frozen_at=now(),positive=old['positive'],hurdle=old['hurdle'],accuracy=old['accuracy'],latent=dict(o_player=['Normal',0,1],e_player=['Normal',0,1],sigma_opportunity=['HalfNormal',.5],sigma_accuracy=['HalfNormal',1],lambda_h=['Normal',0,1],rho_AO=['Uniform',-1,1]),H2=dict(theta_W=['Normal',0,.5]),draws=5000,seed=20260930,gates=dict(**old['gates'],max_accuracy_fraction_below_001=.25,max_accuracy_fraction_above_099=.25),accuracy_gate_source='Existing Stage 3D broad finite probability screen, not outcome-calibrated',no_tuning_after_simulation=True)
 save('prior_protocol.json',prior)
 oldmodel=read(ROOT/'docs/stage3f_evidence/model_protocol.json');ppc=copy.deepcopy(oldmodel['PPC']);ppc['seed']=20260930
 code=list((ROOT/'scripts').glob('stage3h_*.py'))
 dependencies=['stage3f_common.py','stage3f_model.py','stage3d_model.py','stage3d_protocol.py','stage3d_selection.py','stage3dr_ppc.py','stage3c_results.py']
 code += [ROOT/'scripts'/n for n in dependencies]
 model=dict(frozen_at=now(),new_structural_model=True,not_equivalent_to_F2=True,candidates={'H1':'One standardized opportunity factor shared by hurdle and positive counts; correlated accuracy effect plus independent residual; no realized opportunity in accuracy','H2':'H1 plus the original frozen within-player opportunity deviation; no between-player term'},candidate_order=['H1','H2'],latent_formula='u=sigma_accuracy*(rho_AO*o+sqrt(1-rho_AO^2)*e); positive effect=sigma_opportunity*o; hurdle effect=lambda_h*o',factor_sign_anchor='sigma_opportunity>0',hurdle_loading_unconstrained=True,theta_B_absent=True,panel_sha256=EXPECTED,rows=4117,players=857,seasons=13,FTA=469099,positive_rows=3980,zero_rows=137,positions=oldmodel['positions'],seasons_list=oldmodel['seasons_list'],height_center=oldmodel['height_center'],GP_offset_coefficient=1,sampling=dict(chains=4,tune=2000,draws=2000,target_accept=.95,random_seed=20260930),recovery=dict(tune=4000,draws=4000,target_accept=.99),max_recoveries=1,diagnostics=oldmodel['diagnostics'],all_latent_elements_checked=True,PPC=ppc,positive_count_gate=oldmodel['positive_count_gate'],H2_joint_generation='Generate FTA with the same posterior latent factor, recompute within by the exact frozen decomposition function, then generate FTM; conditional PPC holds observed FTA/within fixed',selection='H1 sampler fail after recovery => C and stop; H1 all gates pass => A and stop; H1 sampler pass plus PPC failure => H2; H2 all gates pass => B; any H2 failure => D, following explicit section 22; no H3',prior_failure='Stop without posterior fits or tuning; D prerequisite failure, not an observed PPC or sampler failure',prior_protocol_sha256=sha(E/'prior_protocol.json'),decomposition_csv_sha256=sha(ROOT/'docs/stage3f_evidence/opportunity_decomposition.csv'),decomposition_metadata_sha256=sha(ROOT/'docs/stage3f_evidence/opportunity_decomposition.json'),frozen_code={str(f.relative_to(ROOT)):sha(f) for f in code},scientific_parameter_status='SEALED',stage3g_executed=False,no_commit=True,no_push=True)
 save('model_protocol.json',model);save('freeze_receipt.json',dict(frozen_at=model['frozen_at'],model_protocol_sha256=sha(E/'model_protocol.json'),prior_protocol_sha256=sha(E/'prior_protocol.json')))
 save('input_audit.json',dict(panel_sha256=sha(PANEL),rows=len(fixed_data()),historical_artifacts_preserved=len(preserved),reports_read=['stage3f_hurdle_within_between_adequacy.md','stage3fr_f2_identification_reparameterization.md','stage3dr_opportunity_prior_and_adequacy.md','stage3c_primary_hierarchical_replication.md'],historical_decisions_unchanged=True,stage3f_likelihood_validation_sha256=sha(ROOT/'docs/stage3f_evidence/likelihood_validation.json') if (ROOT/'docs/stage3f_evidence/likelihood_validation.json').exists() else None))
 print('Frozen',sha(E/'model_protocol.json'),'historical artifacts',len(preserved))
if __name__=='__main__':main()
