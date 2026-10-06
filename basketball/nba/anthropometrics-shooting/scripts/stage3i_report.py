"""Report only permitted summaries and immutable adequacy evidence."""
from stage3i_common import *
def get(k,s):return read(E/(k+'_'+s+'.json'))
def diagnostic(k):
 d=get(k,'diagnostics')
 if 'max_rhat' not in d:return d.get('status','Not run')
 return f"Attempt {d['attempt']}; sampler pass {d.get('sampler_pass')}; max R-hat {d['max_rhat']:.6f}; minimum bulk/tail ESS {d['min_bulk_ESS']:.2f}/{d['min_tail_ESS']:.2f}; divergences {d['divergences']}; depth hits {d['max_depth_hits']}; BFMI {', '.join(f'{v:.3f}' for v in d['BFMI'])}; finite covariance {d['finite_covariance']}."
def accuracy(k):
 d=get(k,'conditional_accuracy_ppc')
 if 'status' in d:return d['status']+'; predictive adequacy unassessed.'
 return f"Pass {d['gate_pass']}; pooled pass {d['pooled_rate_99_pass']}; global failures {d['global_metrics_99_fail_count']}/7; season failures {d['season_rate_99_fail_count']}/13; FTA-bin failures {d['FTA_bin_99_fail_count']}/5; systematic directional pattern {d['systematic_volume_pattern']}."
def opportunity(k):
 d=get(k,'joint_opportunity_ppc')
 if 'status' in d:return d['status']+'; predictive adequacy unassessed.'
 z=d['zero_frequency'];s=f"Pass {d['gate_pass']}; zero-frequency pass {d['zero_frequency_99_pass']}; observed zero {z['observed']:.6%}, predictive mean {z['replicated_mean']:.6%}, 99% interval [{z['predictive_99_low']:.6%}, {z['predictive_99_high']:.6%}]. Total-FTA quantile failures {d['quantile_99_fail_count']}/5; positive-count failures {d['positive_quantile_99_fail_count']}/3; season totals below/above 99% {d['season_totals_outside_99_low']}/{d['season_totals_outside_99_high']}."
 for r in d['positive_quantiles']:s+=f"\n\n{r['metric']}: observed {r['observed']:.2f}, predictive mean {r['replicated_mean']:.2f}, 99% [{r['predictive_99_low']:.2f}, {r['predictive_99_high']:.2f}], outside {r['outside_99']}."
 return s

def parameters(k,s):
 p=E/(k+'_'+s+'.json')
 if not p.exists():return ''
 d=read(p)
 if 'status' in d:return d['status']
 text='| Parameter | Mean | Median | SD | 95% CrI |\n|---|---:|---:|---:|---|\n'
 for n,r in d.items():text+=f"| {n} | {r['mean']:.6f} | {r['median']:.6f} | {r['SD']:.6f} | [{r['CI95'][0]:.6f}, {r['CI95'][1]:.6f}] |\n"
 return text

def curvature_interpretation():
 text=''
 for k in ['i1','i3']:
  if not get(k,'diagnostics').get('sampler_pass'):continue
  r=get(k,'within_parameters')['gamma_W2'];lo,hi=r['CI95']
  text+='\n\n'+k.upper()+(': the quadratic 95% interval includes zero, giving little evidence that simple quadratic curvature explains the residual pattern.' if lo<=0<=hi else ': the quadratic 95% interval excludes zero, indicating that the linear within term was incomplete under this conditional model.')
  text+=' The accuracy gate '+('passes.' if get(k,'conditional_accuracy_ppc')['gate_pass'] else 'still fails; this is not a verified accuracy repair.')
 return text

def shape_tables():
 import csv
 text=''
 for k in ['i2','i3']:
  if not get(k,'diagnostics').get('sampler_pass'):continue
  text+='\n\n'+k.upper()+' descriptive positive-count shape:\n\n| Metric | Observed | Predictive mean | 99% predictive interval |\n|---|---:|---:|---|\n'
  with (E/(k+'_positive_count_shape.csv')).open() as f:
   for r in csv.DictReader(f):text+=f"| {r['metric']} | {float(r['observed']):.3f} | {float(r['replicated_mean']):.3f} | [{float(r['predictive_99_low']):.3f}, {float(r['predictive_99_high']):.3f}] |\n"
 return text

def main():
 decision=read(E/'stage3i_decision.json');basis=read(E/'within_quadratic_basis.json');sections=[]
 def add(title,body):sections.append(f'## {len(sections)+1}. {title}\n\n{body}\n')
 add('Stage 3H residual failures','Historical decisions remain permanent. Stage 3H remains SHARED-FACTOR ADEQUACY UNRESOLVED. I0 reuses exact saved H2 diagnostics and PPCs, with no refit or resimulation. The saved H2 sampler passed.\n\n'+accuracy('i0')+'\n\n'+opportunity('i0'))
 add('Stage 3I objective','Diagnose two preidentified residual failures separately and together: nonlinear within-player opportunity in accuracy, and independent persistent count-specific heterogeneity. This is model-adequacy work. I1 and I2 are diagnostic only; I3 is the only eligible model. All three were frozen before any prior simulation or fit; no I4 exists.')
 add('Scientific firewall','The scientific wingspan coefficient remains SEALED. No sign, location, uncertainty, odds ratio, probability, contrast, plot or correlation is exported or used for selection. Only anonymous convergence information enters aggregate sampler gates. Decision code accepts typed Booleans only. Traces remain local and Git-ignored.')
 add('Frozen panel',f'Exactly 4,117 player-seasons, 857 players, 13 seasons, 469,099 FTA, 3,980 positive rows and 137 zero rows. SHA256 `{EXPECTED}`. All rows enter the hurdle; positive rows enter count and accuracy likelihoods. No 2013–14, threshold, player exclusion, residualization refit, recoding, MIN or additional confounder.')
 add('Hypothesis A: nonlinear within effect','The single H2 within slope may leave curvature in the conditional accuracy-volume relationship. A predeclared centered quadratic tests that hypothesis without splines, cubic terms, raw FTA or a between-player observed opportunity term.')
 add('Hypothesis B: count-specific heterogeneity','The shared opportunity factor may not capture all persistent positive-count variation. An independent standard-normal player residual c enters only positive counts. It is independent of o and e, with no additional correlation parameter.')
 add('I1 model',f"Exact H2 except theta_W*within is replaced by gamma_W1*zW + gamma_W2*qW. Frozen within values are unchanged. Equal-row sample SD (ddof=1) s_W={basis['s_W']:.16g}; zW=w/s_W; qW=zW²−{basis['quadratic_center']:.16g}. The quadratic mean is {basis['centered_quadratic_mean']:.3g}. Scaling uses every accounting row, including zero FTA, and no FTM outcome. All opportunity and latent components remain H2.")
 add('I2 model','Exact H2 linear accuracy term theta_W*within and shared structure, plus sigma_count_resid*c_i in positive-count log mean. c_i~Normal(0,1) independently of o/e. The hurdle remains lambda_h*o. Accuracy effect remains sigma_accuracy*(rho_AO*o+sqrt(1−rho_AO²)*e). Positive counts retain coefficient-one log(GP), original fixed terms and exact Stage 3F zero-truncated NB.')
 add('I3 combined model','Exactly I1 accuracy plus I2 count residual; unchanged H2 hurdle and shared accuracy/opportunity structure. The three candidates were independently predeclared. I1/I2 sampler or PPC failure does not block I3. I3 sampler failure ends the stage. No model or prior was changed after simulation.')
 add('Priors','gamma_W1 and gamma_W2 independently Normal(0,0.25), on standardized bases; sigma_count_resid HalfNormal(0.5); c_i Normal(0,1). I2 theta_W Normal(0,0.5). All other H2 priors remain exact: accuracy intercept Normal(0,2.5), exposure/height Normal(0,0.5), position/season Normal(0,1), log kappa Normal(3,2); positive intercept Normal(log(2),1), exposure/height Normal(0,0.15), position Normal(0,0.35), season Normal(0,0.25), log alpha Normal(log(2),1); hurdle intercept Normal(logit(0.95),1), exposure/height Normal(0,0.25), position Normal(0,0.5), season Normal(0,0.35). Shared priors: o/e independent Normal(0,1), sigma_accuracy HalfNormal(1), sigma_opportunity HalfNormal(0.5), lambda_h Normal(0,1), rho_AO Uniform(−1,1).')
 prior=[]
 for c,r in read(E/'prior_predictive_summary.json').items():prior.append(f"{c}: pass {r['passed']}; 5,000 draws, seed 20260930; rate >100/game mass {r['fraction_positive_rate_over_100']:.6%}; count >1,000,000 mass {r['fraction_total_FTA_over_1000000']:.8%}; zero-fraction 95% {r['zero_fraction_95_interval']}; extreme-zero mass {r['zero_fraction_extreme_mass']:.4%}; accuracy tails below .01 / above .99 {r['accuracy_fraction_below_001']:.4%}/{r['accuracy_fraction_above_099']:.4%}; finite {r['finite']}.")
 add('Prior predictive checks','\n\n'.join(prior)+'\n\nAll prior checks preceded all fits. Gates are unchanged: ≤1% positive conditional mean rates >100/game, ≤0.1% counts >one million, ≤90% combined extreme-zero mass, finite predictions, and ≤25% accuracy mass in either extreme tail. Broad zero-range review did not tune to outcomes. Gross prior passes do not establish adequacy.')
 for c in ['I1','I2','I3']:
  k=c.lower();body=diagnostic(k)+'\n\nConditional accuracy: '+accuracy(k)+'\n\nJoint opportunity: '+opportunity(k)
  for suffix in ['within_parameters','count_residual_parameter']:
   value=parameters(k,suffix)
   if value:body+='\n\n'+('Within parameters' if suffix=='within_parameters' else 'Count residual scale')+':\n\n'+value
  for f in sorted(E.glob(k+'_attempt*_diagnostics.json')):
   r=read(f);body+=f"\n\nAttempt {r['attempt']} numeric gate {r['numeric_gate_pass']}: R-hat {r['max_rhat']:.6f}, bulk/tail ESS {r['min_bulk_ESS']:.2f}/{r['min_tail_ESS']:.2f}; divergences {r['divergences']}; depth hits {r['max_depth_hits']}."
  add(c+' diagnostics and PPC',body)
 add('Within curvature interpretation','The permitted quadratic summaries describe conditional association. A nonzero quadratic coefficient indicates that the linear within specification was incomplete under this model; it does not establish causal benefit from more attempts. Predictive repair requires the complete unchanged accuracy gate, including the directional MCSE rule.'+curvature_interpretation()+'\n\n'+accuracy('i1')+'\n\n'+accuracy('i3'))
 add('Positive-count residual interpretation','The scale measures unobserved count-specific persistent player variation. It is not usage, aggression, star quality, rim pressure, or a biological trait. A nonzero scale alone does not prove a repaired distribution. The predeclared descriptive checks are positive mean, SD and Q10/Q25/Q50/Q75/Q90/Q95, with no new release thresholds. Neither I2 nor I3 passed sampling, so their scale estimates, shape statistics and PPCs are withheld. Their required CSVs contain explicit withholding status only. Whether count-specific heterogeneity repairs Q50/Q75 therefore remains unassessed.'+shape_tables())
 add('Accuracy-volume comparison','Exactly 2,000 replications, seed 20260930, observed FTA fixed. Same pooled rate, seven global metrics, 13 season rates and five bins. Failure rules: pooled outside 99%, ≥3 global misses, ≥5 season misses, ≥2 bin misses, or the frozen opposite low/high bias beyond 2.576 MCSE (40 batches of 50 in chain-major order).\n\n'+'\n\n'.join(c+': '+accuracy(c.lower()) for c in ['I0','I1','I2','I3'])+f'\n\n![Accuracy comparison](<{F}/01_accuracy_comparison.png>)')
 add('Opportunity-distribution comparison','For sampler-valid candidates, the frozen joint simulation generates hurdle state, exact zero-truncated positive FTA, then makes using the same posterior latent draw. Generated within values use the exact frozen decomposition. The I1/I3 protocol specifies that generated z/q use the frozen observed-panel SD and quadratic center; conditional prediction holds observed bases fixed. The gate is unchanged: zero outside 99%, ≥3/5 total-count quantile misses, ≥5 season totals outside in the same direction, or ≥2/3 positive quartile misses. Position summaries and extra positive shape metrics are descriptive.\n\n'+f'![Positive FTA comparison](<{F}/02_positive_FTA_distribution.png>)\n\n![Within terms](<{F}/03_within_parameters.png>)\n\n![Count residual](<{F}/04_count_residual.png>)')
 add('Stage 3I classification',decision['classification']+'. '+decision['reason']+'. Only I3 sampler and both PPC gates determine this classification after protocol/firewall verification. Invalid samplers have withheld PPCs, not fabricated predictive failures. No AIC, WAIC, LOO or scientific-effect information enters selection.')
 add('Stage 3G authorization',f"Authorized: {decision['stage3g_authorized']}. Purpose: ESTIMAND REVIEW ONLY. Scientific-effect release authorized: False. Stage 3G executed: False.")
 add('Scientific estimand caveat','I3 conditions accuracy on realized within-player opportunity. Role, health, team context, ability, foul drawing, playing time and unmeasured factors may affect that opportunity. Predictive adequacy cannot establish that this conditioning set answers the scientific question. Any future estimand review remains separate from scientific-effect release.')
 add('Remaining limitations','These are in-sample checks for observed players. Selection into combine measurement, NBA survival, measurement error, unbalanced observed careers and unmeasured factors remain. The quadratic is deliberately limited; independent normal residuals and the count family remain assumptions. No causal claim or multi-season replication claim is made. Failure ends this stage without another candidate.')
 tests=read(E/'test_summary.json') if (E/'test_summary.json').exists() else read(E/'predecision_test_summary.json')
 add('Reproducibility',f"Protocol frozen {protocol()['frozen_at']}; SHA256 `{sha(E/'model_protocol.json')}`. Initial sampling: four chains, 2,000 tune/2,000 retained, target .95, seed 20260930. One generic recovery per model: 4,000/4,000, target .99, unchanged model/prior. Gates: R-hat≤1.01, bulk/tail ESS≥400, BFMI≥.3, no divergences/depth hits, finite covariance, acceptable visual mixing. All fixed effects, dispersions, latent o/e/c elements, scales and induced effects are checked; the scientific coefficient is anonymous only. Backend gradients match the reference before fitting. The pinned environment and exact validated Stage 3F likelihood are reused without installation. Tests {tests['tests_passed']}/{tests['tests_run']}; {tests['historical_artifacts_unchanged']} historical artifacts unchanged. Saved-trace I1 PPC replay matched every saved permitted parameter/PPC artifact exactly, without new MCMC; the decision hash remained unchanged. Final artifact hashes are recorded separately. No commit, push or Stage 3G execution.")
 (ROOT/'docs/stage3i_residual_adequacy.md').write_text('# Stage 3I — Residual Adequacy Diagnosis\n\n**'+decision['classification']+'**. Scientific wingspan coefficient: **SEALED**.\n\nI1 sampled reliably but did not repair the directional accuracy bias. I2 and I3 failed after their single allowed recoveries, leaving their predictive adequacy unassessed.\n\n'+'\n'.join(sections))
if __name__=='__main__':main()
