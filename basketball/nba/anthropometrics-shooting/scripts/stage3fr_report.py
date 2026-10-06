"""One evolving report; never reads protected posterior values."""
from stage3fr_common import *
def get(name):return read(E/name) if (E/name).exists() else {}
def ds(d):
 if not d:return 'Pending.'
 if 'max_rhat' not in d:return d.get('status','Pending')
 return f"Attempt {d['attempt']}: sampler pass {d.get('sampler_pass','pending visual review' if d['numeric_gate_pass'] else False)}; maximum R-hat {d['max_rhat']:.6f}; minimum bulk ESS {d['min_bulk_ESS']:.2f}; minimum tail ESS {d['min_tail_ESS']:.2f}; divergences {d['divergences']}; tree-depth hits {d['max_depth_hits']}; BFMI {', '.join(format(x,'.3f') for x in d['BFMI'])}; finite covariance {d['finite_covariance']}."
def param(v):return f"mean {v['mean']:.6f}, median {v['median']:.6f}, SD {v['SD']:.6f}, 95% CrI [{v['CI95'][0]:.6f}, {v['CI95'][1]:.6f}]"
def main():
 p=protocol();audit=get('design_identification_audit.json');cond=get('fixed_effect_conditioning.json');geo=get('posterior_geometry_summary.json')['attempts']['2'];decision=get('final_reparameterization_decision.json');tests=get('test_summary.json');diag={k:get('diag_'+k+'_result.json') for k in ['a','b','c']};rs={k:get(k.lower()+'_diagnostics.json') for k in ['R1','R2','R3']};selected=decision.get('selected_parameterization');acc=get('f2_conditional_accuracy_ppc.json');opp=get('f2_joint_opportunity_ppc.json');theta=get('f2_between_within_parameters.json');corr=get('f2_random_effect_correlations.json')
 if selected:
  for k in rs:
   if not rs[k]:rs[k]={'status':'Not run: an earlier equivalent parameterization passed, so the frozen sequence stopped.'}
 if all(diag.values()):
  source=[]
  if not diag['a'].get('sampler_pass'):source.append('DIAG-A fails, so accuracy/decomposition geometry itself contributes (case A).')
  if diag['a'].get('sampler_pass') and diag['b'].get('sampler_pass'):source.append('DIAG-A and DIAG-B pass while original F2 failed, implicating coupling through the correlated three-dimensional player structure (case B).')
  if not diag['c'].get('sampler_pass'):source.append('DIAG-C fails, so opportunity-side latent geometry also contributes (case C).')
  if all(v.get('sampler_pass') for v in diag.values()):source.append('All three diagnostic submodels pass, reinforcing coupled joint posterior geometry as the dominant issue (case D).')
  source=' '.join(source) or 'The diagnostic combination does not isolate a single source; multiple interacting blocks remain plausible.'
 else:source='Diagnostic submodels are still pending; no final source attribution is made.'
 if rs['R1'].get('sampler_pass') is False:source+=' Exact predictor scaling alone did not repair the sampler.'
 r3_initial=get('r3_attempt1_diagnostics.json')
 if rs['R2'].get('sampler_pass') is False and r3_initial:
  source+=' Fully centered R2 also had inadequate BFMI after recovery. R3\'s initial mixed representation restored BFMI above the threshold but still failed R-hat and ESS, distinguishing energy exploration from complete convergence. This comparison does not prove structural nonidentifiability or isolate a unique causal source of the geometry.'
 eq='\n'.join(f"- {k}: {get(k.lower()+'_equivalence_validation.json')}" for k in [] )
 eqrows=[]
 for k in ['R1','R2','R3']:
  v=get(k.lower()+'_equivalence_validation.json')
  if v:eqrows.append(f"| {k} | {v['passed']} | {v['maximum_absolute_errors']['log_density']:.3g} | {v['maximum_absolute_errors']['likelihood']:.3g} | {v['maximum_absolute_errors']['linear_predictor']:.3g} | {v['paired_prior_predictive_counts_exact']} |")
 eq='| Coordinates | Passed | Max density error | Max likelihood error | Max predictor error | Paired prior counts exact |\n|---|---|---|---|---|---|\n'+'\n'.join(eqrows)
 posterior='Withheld: no eligible equivalent sampler has passed.'
 if theta:posterior='\n'.join(f"- {k}: {param(theta[k])}." for k in ['theta_B','theta_W'])+'\n\nThese are associational diagnostics in original log1p(FTA/GP) units. Their magnitudes alone do not rank importance because predictor variation differs; they do not establish a causal mechanism.'
 correlations='Withheld until an eligible sampler passes.' if not corr else '\n'.join(f"- {k}: {param(v)}." for k,v in corr.items())
 ppctext='Not run: no eligible equivalent sampler has passed. This is unassessed predictive adequacy, not an observed PPC failure.'
 if acc:ppctext=f"Conditional accuracy pass: {acc['gate_pass']}; pooled pass {acc['pooled_rate_99_pass']}; global failures {acc['global_metrics_99_fail_count']}/7; season failures {acc['season_rate_99_fail_count']}/13; FTA-bin failures {acc['FTA_bin_99_fail_count']}/5; systematic low/high pattern {acc['systematic_volume_pattern']}. Joint opportunity pass: {opp['gate_pass']}; zero fraction pass {opp['zero_frequency_99_pass']}; total-FTA quantile failures {opp['quantile_99_fail_count']}/5; positive-count quantile failures {opp['positive_quantile_99_fail_count']}/3."
 selected_figures=''
 if selected:
  key=selected.lower();attempt=rs[selected]['attempt'];selected_figures=f'![Selected standardized trace diagnostics](<{F}/{key}_attempt{attempt}_mixing.png>)\n\n![Selected energy diagnostic](<{F}/{key}_attempt{attempt}_energy.png>)'
 if acc:ppctext+=f'\n\n![F2 conditional accuracy PPC](<{F}/05_F2_accuracy_PPC.png>)'
 text=f'''# Stage 3F-R — F2 Identification and Reparameterization

**{decision.get('classification','IN PROGRESS — no final classification')}**. Scientific parameter: **SEALED**. No causal claim or scientific replication claim is made.

## 1. Historical F2 sampler failure

Stage 3F permanently remains STRUCTURAL ADEQUACY UNRESOLVED. Its F2 recovery had maximum R-hat 1.115705, minimum bulk ESS 28.77, and minimum tail ESS 54.36 for its major-parameter gate. Stage 3C, Stage 3D and Stage 3D-R failures remain unchanged. Stage 3E remains NOT AUTHORIZED. Existing trace diagnostics are reused; no historical model is refitted or decision relabeled.

## 2. Objective

Diagnose fixed-effect, covariance and latent-effect geometry and test only scientifically equivalent computational coordinates for F2. R1 scales the two opportunity terms with exactly transformed priors. R2 centers the same multivariate latent distribution. R3, conditionally eligible after R1/R2 failure, uses a proved mixed representation. No R4, changed conditioning set, narrowed prior, predictor addition/removal, or eligible-model simplification is allowed.

## 3. Scientific firewall

The scientific wingspan coefficient is never plotted, correlated with other posterior parameters, or summarized. It contributes an anonymous sampler-pass Boolean and internal aggregate convergence checks only. Diagnostic models cannot become scientific models. Selection uses ordered eligible-model sampler Booleans and frozen PPC Booleans, not scientific-effect location or direction. Permitted failed-chain geometry is explicitly distinguished from valid posterior inference.

## 4. Failed-trace diagnosis

Both saved original F2 attempts were audited. The recovery's worst blocks are accuracy–positive opportunity correlation (R-hat 1.115705, bulk ESS 28.77), between-opportunity slope (R-hat 1.110817, bulk ESS 29.74), player effects (maximum R-hat 1.102644), standardized player effects (1.101512), and accuracy–hurdle correlation (1.095655). Accuracy SD also misses the ESS gate. The within-opportunity term is not a dominant poor-mixing block.

The failed chains show movement correlation between theta_B and corr(u,v) of {geo['theta_correlations']['theta_B']['corr_uv']:.6f}, with corr(u,h) {geo['theta_correlations']['theta_B']['corr_uh']:.6f}, with accuracy SD {geo['theta_correlations']['theta_B']['sigma_accuracy']:.6f}, and with accuracy intercept {geo['theta_correlations']['theta_B']['beta_0']:.6f}. These describe the available failed trajectories, not a trustworthy converged posterior correlation estimate. No correlation involving the sealed coefficient was computed for publication.

All scalar non-sealed global and latent convergence results are in failed_f2_parameter_diagnostics.csv; block summaries and chain mean normalized ranks are saved separately. Theta_W has R-hat 1.000400, bulk ESS 16,578.79 and tail ESS 12,111.04. Theta_B mean normalized ranks span 0.368–0.572 across chains, while theta_W spans 0.491–0.507. Rank separation diagnoses incomplete mixing without publishing failed original-unit slope estimates. Neither rank separation nor a trace excursion proves distinct modes.

Absolute covariance correlations exceed 0.95 in {geo['correlation_boundary_mass']['corr_vh']['fraction_abs_over_095']:.3%} of the failed recovery draws for the positive-opportunity/hurdle pair, but not for the two accuracy pairs. No marginal SD draw falls below 0.05 or above 3. These findings do not support a simple SD-to-zero funnel as the sole explanation. Scale–latent-RMS correlations are saved as funnel indicators; persistent coupling is more evident than a uniquely diagnosed funnel.

![Failed convergence](<{F}/01_failed_convergence.png>)
![Permitted geometry](<{F}/02_permitted_correlations.png>)

## 5. Predictor identification audit

Exactly 4,117 player-seasons, 857 players, 13 seasons and 469,099 FTA; panel SHA256 `{EXPECTED}`. No rows or players were removed. The frozen FTA/GP decomposition and its zero rows were reused unchanged. No FTM or FT-percentage association was calculated for this design audit.

Row-weighted sample SDs (ddof=1): between {audit['scales']['B']:.15f}, within {audit['scales']['W']:.15f}. Global between centering remains the original equal-unique-player center; it is not recentered by rows. Player counts by observed seasons: one {audit['player_season_counts']['1']}, two {audit['player_season_counts']['2']}, three–four {audit['player_season_counts']['3-4']}, five or more {audit['player_season_counts']['5+']}. All 112 single-season players have within=0. Actual variation is supplied by {audit['players_with_actual_within_variation']} players and {audit['observations_in_varying_players']} observations. Distribution quantiles and complete predictor-only correlations, including height and residual-wingspan predictors, are saved in the audit artifacts.

![Predictor distributions](<{F}/03_predictor_distributions.png>)

## 6. Fixed-effect conditioning

Accuracy design rank {cond['rank']} of {cond['shape'][1]}; raw condition number {cond['condition_number']:.6f}; standardized condition number {cond['standardized_condition_number']:.6f}. All singular values are saved. There is no exact aliasing or severe standardized near-collinearity. The larger raw condition number partly reflects units and sparse category indicators. Height and point-guard encoding correlate approximately −0.651. Original position and season coding and references remain unchanged. No column was dropped or orthogonalized.

## 7. DIAG-A accuracy-only result

{ds(diag['a'])}

Initial run: {ds(get('diag-a_attempt1_diagnostics.json'))}

This retains the complete F2 accuracy predictor and its original priors, with a HalfNormal(1) accuracy SD and a non-centered univariate player intercept. It omits opportunity likelihoods solely to diagnose computation. It cannot authorize inference or become selected F2.

## 8. DIAG-B independent-covariance result

{ds(diag['b'])}

Initial run: {ds(get('diag-b_attempt1_diagnostics.json'))}

This retains all F2 likelihoods and marginal SD priors but fixes cross-effect correlations to zero for diagnosis only. This altered model is never eligible for selection or scientific reporting.

## 9. DIAG-C opportunity-only result

{ds(diag['c'])}

Initial run: {ds(get('diag-c_attempt1_diagnostics.json'))}

Only the Bernoulli hurdle and exact zero-truncated NB likelihood enter. No accuracy outcome enters its likelihood. Its two-dimensional opportunity correlation uses LKJ eta=2.5, which is the marginal pair distribution induced by the original three-dimensional LKJ eta=2; marginal SD priors are unchanged. This is a diagnostic submodel, not an eligible replacement for full F2.

## 10. Source of poor geometry

{source}

The failed-chain coupling and the outcome-free design audit distinguish posterior geometry from predictor-matrix rank. A computational pass does not prove full statistical identification or predictive adequacy. Conclusions here concern sampling under the frozen model, not causality.

## 11. R1 exact reparameterization

between_std=centered_between/sB and within_std=within/sW. theta_B_std=sB*theta_B and theta_W_std=sW*theta_W, with Normal(0,0.5*sB) and Normal(0,0.5*sW) priors. Dividing each coefficient by its predictor SD recovers the original coefficient. The two-coordinate Jacobian is sB*sW. Covariance, non-centered player effects, likelihoods, categorical coding and every other prior remain original F2.

## 12. R1 diagnostics

{ds(rs['R1'])}

Initial run: {ds(get('r1_attempt1_diagnostics.json'))}

Initial plan: four chains, 2,000 warmup and 2,000 retained draws each, target acceptance 0.95, seed 20260928. Only one recovery is allowed: 4,000/4,000 at 0.99. The same generic plan applies to R2/R3. DIAG models use 1,500/1,500 initially and a single 3,000/3,000 recovery. Recovery is triggered only by sampler failure.

## 13. R2 if needed

{ds(rs['R2'])}

Initial run: {ds(get('r2_attempt1_diagnostics.json'))}

R2 retains R1 scaling and samples player effects directly as MVNormal(0,L*L.T). The covariance prior is identical. From original standard coordinates, r=Lz; inverse z=L^(-1)r; forward latent Jacobian det(L) per player. The centered MVNormal log density plus N*log(det(L)) equals the original standard-normal latent log density. The covariance-coordinate transformation is unchanged.

## 14. R3 if needed

{ds(rs['R3'])}

Initial run: {ds(get('r3_attempt1_diagnostics.json'))}

A mixed representation was derived and frozen before any new posterior fit. It centers (u,v), keeping the conditional hurdle residual standard normal. For A=L[:2,:2], q=A*z[:2] and e=z2; h=L20*z0+L21*z1+L22*e. Inverse and Jacobian det(A) per player are documented in r3_equivalence_derivation.md. Native normalized densities account for this Jacobian; no extra density factor is added. The induced full latent distribution and all likelihoods remain exact F2. This does not project effects away from opportunity predictors or estimate a centering coefficient.

## 15. Equivalence verification

{eq}

Each implemented eligible validation compares 12 perturbed matched points on the real design, independent SciPy latent-density fixtures, inverse transforms, coefficient-prior densities and all three deterministic predictors/likelihoods. Five hundred paired original-prior draws are mapped into new coordinates. Matching predictors and shared random streams yield paired identical opportunity counts and conditional makes, a stronger check than unpaired Monte Carlo mean agreement. Prior arrays remain protected locally; only numerical error checks are public. These checks preserve original-space priors, not merely similarly shaped priors.

## 16. Selected computational parameterization

{selected or 'None selected yet' if not decision else selected or 'None: no equivalent parameterization passed'}.

Selection follows R1, then R2 only after R1 failure, then predeclared R3 only after R2 failure. Numerical convergence requires maximum R-hat ≤1.01, minimum bulk/tail ESS ≥400, BFMI ≥0.3, zero unresolved divergences or tree-depth hits, finite covariance and acceptable visual mixing. Every native and induced latent scalar is checked, alongside major globals. The anonymous sealed check must also pass. No diagnostic model is selectable.

{selected_figures}

## 17. F2 PPC if sampler passed

{ppctext}

The existing Stage 3F F2 PPC implementation is reused verbatim with only stage-local paths and the equivalent model builder substituted. If reached, exactly 2,000 replications use seed 20260929. Conditional prediction fixes observed FTA and decomposition. Joint prediction generates hurdle/count outcomes, recomputes the decomposition and unique-player center, then generates makes. The seven globals, 13 seasons, five FTA bins, systematic directional MCSE rule, zero fraction, total-count quantiles and added positive-count quartile gates remain unchanged. No new release metric is introduced.

## 18. Between/within parameters if reportable

{posterior}

## 19. Random-effect correlations if reportable

{correlations}

## 20. Stage 3F-R classification

{decision.get('classification','Pending completion of the frozen sequence and final tests')}.

The only outcomes are A: equivalent sampler and both PPCs pass; B: equivalent sampler passes but PPC fails; C: no equivalent sampler passes. Verification tests do not override failed scientific adequacy. Historical Stage 3F remains unresolved regardless of this new stage's outcome.

## 21. Stage 3G authorization

Authorized: {decision.get('stage3g_authorized',False)}. Only classification A may authorize estimand review. No classification authorizes the sealed scientific coefficient's release. Stage 3G was not started. F2 still conditions on realized opportunity, and therefore differs from the original Stage 3C scientific conditioning set. Reparameterization changes none of F2's conditioning variables.

## 22. What remains unresolved

Predictive adequacy and scientific estimand validity are separate. A successful numerical representation does not remove selection, measurement, unbalanced-career or unobserved-factor limitations. Diagnostic restrictions on covariance cannot justify simplifying eligible F2. No causal claim is made. Opportunity diagnostic summaries, when available, are associational.

## 23. Reproducibility

Protocol frozen {p['frozen_at']}. Pinned Stage 3C environment reused without installation or modification. No prior report, trace or decision was overwritten. All new traces and prior arrays remain local and Git-ignored. Hashes cover frozen code, data, prior/decomposition inputs, attempts, equivalence checks, figures, tests and final outputs.

The user-reported usage-limit interruption was an infrastructure/session event, not a scientific gate. The diagnostic process remained alive; completed audits, R1 equivalence and DIAG-A attempt 1 were reused after integrity checks. No fit was restarted on resume. Full record: resume_after_usage_limit.md. No model, prior, threshold, data, draw budget or scientific rule changed because of the interruption.

R2's validator initially encountered an input-interface TypeError before an equivalence decision. The unfrozen checker was corrected to accept unused covariance inputs in the centered observed likelihood. The frozen model and all mathematical checks and tolerances remained unchanged; validation then passed. The original log and explanation are preserved in validator_input_handling_repair.md.

Tests: {tests.get('tests_passed','pending')}/{tests.get('tests_run','pending')}. Preserved historical artifacts: {tests.get('historical_artifacts_unchanged','pending')}. No commit, push, Stage 3G execution, FTA threshold filtering, player removal, 2013–14 inclusion, MIN predictor or new confounder occurred.
'''
 (ROOT/'docs/stage3fr_f2_identification_reparameterization.md').write_text(text)
if __name__=='__main__':main()
