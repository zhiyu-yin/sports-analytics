"""Render report and figures only after numerical robustness result freeze."""
import json
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from stage2_analysis import ROOT,E,STATEMENT,save

def table(df):
 def fmt(v): return f'{v:.6g}' if isinstance(v,(float,np.floating)) else str(v)
 return '| '+' | '.join(map(str,df.columns))+' |\n| '+' | '.join(['---']*len(df.columns))+' |\n'+'\n'.join('| '+' | '.join(fmt(v) for v in row)+' |' for row in df.itertuples(index=False,name=None))
p=json.loads((E/'primary_robustness_result.json').read_text()); comp=pd.read_csv(E/'robust_model_comparison.csv'); loo=pd.read_csv(E/'loo_player_results.csv'); alt=pd.read_csv(E/'alternate_exposure_robustness.csv'); threshold=pd.read_csv(E/'fta_threshold_robustness.csv'); validation=json.loads((E/'beta_binomial_validation.json').read_text()); bb=json.loads((E/'beta_binomial_result.json').read_text()); plan=json.loads((E/'analysis_plan.json').read_text())
base=p['stage1_M2']; q=p['quasi']; b=p['beta_binomial']; h=p['HC0']; l=p['loo']; high=p['high_leverage']; c=p['probability_contrasts']
major=[q,b,h]
if any(r['beta']>=0 for r in major): classification='NOT ROBUST'
elif any(r['ci_includes_zero'] for r in major) or l['failed'] or l['sign_reversals'] or high['relative_beta_change']>.5 or any(not .5<=abs(r['beta']/base['beta'])<=1.5 for r in major): classification='UNCERTAIN DIRECTION'
else: classification='STRONG DIRECTIONAL ROBUSTNESS'
save('robustness_classification.json',dict(classification=classification,rule=plan['classification'],reason='All tested estimates remain negative and major robust intervals exclude zero, but removing the predeclared 42 high-leverage players changes magnitude by 59%, exceeding the frozen 50% materiality rule. Sign stability is stronger than magnitude stability.'))
folder=ROOT/'docs/stage2_figures'; folder.mkdir(exist_ok=True)
plt.rcParams.update({'font.size':10,'axes.spines.top':False,'axes.spines.right':False,'savefig.dpi':200,'svg.hashsalt':'stage2-fixed'})
def finish(fig,name):
 fig.tight_layout(); fig.savefig(folder/f'{name}.png'); fig.savefig(folder/f'{name}.svg',metadata={'Date':None}); plt.close(fig)
labels=['Stage 1 binomial','Quasi (same estimate)','Beta-binomial','HC0 sensitivity','Grouped positions (quasi)','Exclude unknown (quasi)','FTA ≥50 (quasi)','FTA ≥50 (beta-binomial)','FTA ≥100 (quasi)','FTA ≥100 (beta-binomial)','Remove high leverage (exploratory)']
fig,ax=plt.subplots(figsize=(9,6)); y=np.arange(len(comp))[::-1]; ax.errorbar(comp.beta,y,xerr=np.vstack([comp.beta-comp.ci_low,comp.ci_high-comp.beta]),fmt='o',color='#416783',capsize=3); ax.axvline(0,color='gray',ls='--'); ax.axhline(7.5,color='gray',lw=.7); ax.set(yticks=y,yticklabels=labels,xlabel='Residual-wingspan coefficient (log odds / inch)',title='Uncertainty and specification sensitivity · 95% Wald intervals'); finish(fig,'01_forest')
fig,ax=plt.subplots(figsize=(7,4)); ax.hist(loo.beta,bins=24,color='#416783',edgecolor='white'); ax.axvline(base['beta'],color='#a04d36',label='Frozen Stage 1 M2'); ax.axvline(0,color='gray',ls='--'); ax.set(xlabel='M2 coefficient after deleting one player',ylabel='Refits',title='Leave-one-player-out stability · 299 successful fits'); ax.legend(frameon=False); finish(fig,'02_loo')
ct=pd.DataFrame([dict(model=k,**v) for k,v in c.items()]); ct.to_csv(E/'probability_contrast_comparison.csv',index=False)
fig,ax=plt.subplots(figsize=(7,4)); y=np.arange(4)[::-1]; ax.errorbar(ct.difference*100,y,xerr=np.vstack([(ct.difference-ct.ci_low)*100,(ct.ci_high-ct.difference)*100]),fmt='o',color='#416783',capsize=4); ax.axvline(0,color='gray',ls='--'); ax.set(yticks=y,yticklabels=['Stage 1 binomial','Quasi','HC0 sensitivity','Beta-binomial'],xlabel='Q75 − Q25 predicted FT probability (percentage points)',title='Adjusted association contrast · 95% intervals',ylim=(-.5,3.5)); finish(fig,'03_probability_contrast')
ratio=alt[alt.exposure=='wingspan_ratio'].copy(); scale_cols=['beta','se','ci_low','ci_high']; ratio[scale_cols]*=.01
for new,old in [('odds_ratio','beta'),('or_low','ci_low'),('or_high','ci_high')]: ratio[new]=np.exp(ratio[old])
ratio['reported_unit']=.01; ratio.to_csv(E/'ratio_per_001_robustness.csv',index=False)
smallcols=['model','beta','se','ci_low','ci_high','odds_ratio','or_low','or_high','dispersion_or_overdispersion','n','FTA','converged']
report=f'''# Stage 2 — Robust inference for residual wingspan × FT accuracy

## 1. Objective
Assess uncertainty and influence robustness of the frozen single-season M2 association without changing the scientific question, primary exposure, or primary population. This is a robustness stage, not a search for a favorable p-value.

{STATEMENT}

## 2. Why Stage 2 was needed
Stage 1 M2 Pearson dispersion was 5.561570 (M0 7.618; M1 6.168), well above binomial variance. Conventional coefficient uncertainty was therefore too narrow if the systematic component did not explain player heterogeneity. Stage 2 separates point-estimate stability from uncertainty width.

## 3. Frozen Stage 1 result
Stage 1 M2 beta={base['beta']:.9f} per inch, OR={base['odds_ratio']:.6f}, conventional 95% CI [{base['ci_low']:.6f}, {base['ci_high']:.6f}]. Exact frozen data: 311 accounting players, 299 FTA>0 likelihood players, 42,587 attempts. Twelve zero-attempt players remain in accounting. The saved residual is read directly; the 960-person reference is neither modified nor refitted.

All Stage 1 artifacts and other pre-existing project files are protected by a SHA-256 preservation manifest. Primary adjustment remains intercept + residual wingspan + barefoot height + original combine positions, including distinct hybrids and unknown, reference C. No new confounder is added. [Predeclared analysis plan](stage2_evidence/analysis_plan.json) fixes variance methods, grouping, sensitivity rules and interpretation criteria.

## 4. Quasi-binomial result
Keep beta unchanged and multiply the original full covariance by phi=Pearson chi-square / residual df =1573.924290/283=5.561570. Scaled SE={q['se']:.6f}, normal-Wald CI [{q['ci_low']:.6f}, {q['ci_high']:.6f}], OR CI [{q['or_low']:.6f}, {q['or_high']:.6f}], p={q['p']:.6f}. The interval excludes zero. This is an uncertainty correction, not an independent point-estimate fit. Normal rather than t inference was declared before fitting; phi estimation uncertainty is not separately propagated.

## 5. Beta-binomial result
The documented likelihood is log choose(n,y) + log B(y+mu*kappa,n−y+(1−mu)*kappa) − log B(mu*kappa,(1−mu)*kappa), where mu=expit(X beta). One common kappa>0 is estimated jointly with all regression coefficients; rho=1/(1+kappa). Each player contributes one grouped-count likelihood term, including the combinatorial constant.

Beta={b['beta']:.9f}, SE={b['se']:.6f}, 95% CI [{b['ci_low']:.6f}, {b['ci_high']:.6f}], OR={b['odds_ratio']:.6f}, OR CI [{b['or_low']:.6f}, {b['or_high']:.6f}], p={b['p']:.6f}. The coefficient interval excludes zero. Estimated kappa={b['kappa']:.6f}, rho={b['dispersion_or_overdispersion']:.6f}. Log likelihood={b['log_likelihood']:.6f}; AIC={b['AIC']:.6f}, counting 16 mean coefficients plus one precision parameter. Converged from all three predeclared starts; positive observed information and stable Hessian step checks passed.

The pinned statsmodels GLM family interface does not provide this beta-binomial regression. A small custom regression wrapper uses SciPy's standard L-BFGS-B optimizer, an analytic digamma score, and central differences of that score for the observed information. The full joint information is inverted before extracting coefficient covariance, accounting for precision estimation. Internal centering/scaling is an invertible numerical reparameterization; estimates/covariance are transformed back to original units. No custom optimizer was written. [SciPy's documented PMF](https://docs.scipy.org/doc/scipy-1.15.3/reference/generated/scipy.stats.betabinom.html) supplies an independent numerical reference.

## 6. Comparison of point estimates
Primary quasi and HC0 retain Stage 1 beta exactly. Beta-binomial moves magnitude by {abs(b['beta']/base['beta']-1)*100:.2f}% and remains negative. It estimates a distribution of latent player probabilities and changes the relative information contributed by high-attempt players, so identical coefficients are not required.

{table(comp[smallcols])}

Dispersion column means phi for quasi rows, rho for beta-binomial rows, fixed binomial scale=1 for Stage 1, and unavailable/not applicable for HC0. These parameters are not interchangeable. Binomial M2 AIC=2878.091 and beta-binomial AIC=2076.659 use the same 299 grouped outcomes and full count likelihood constants, so those two likelihood criteria are comparable. Quasi has no normalized probability likelihood/AIC. AICs across different FTA subsets must not be ranked; no model was chosen by p-value or AIC.

## 7. Comparison of uncertainty
Relative to Stage 1, coefficient SE/interval width is **{q['se']/base['se']:.3f}× quasi**, **{b['se']/base['se']:.3f}× beta-binomial**, and **{h['se']/base['se']:.3f}× HC0**. Point estimates remain similar while uncertainty grows substantially. All three major intervals exclude zero under their respective assumptions; that is descriptive evidence, not the stage execution criterion.

HC0 uses one score s_i=X_i(FTM_i−FTA_i*p_i) per player and sandwich B(sum s_i s_iᵀ)B, with B the inverse binomial information. It matches statsmodels HC0 numerically. This is meaningful under independent players and a correct conditional mean, without pretending the attempts are independent score rows. It adds no invented cluster structure. HC0 can understate uncertainty under high leverage; a singleton indicator has no replication to estimate its own robust variation. HC2/HC3 were not forced at leverage one. HC0 is a sensitivity, not the sole evidentiary basis.

![Robustness forest](stage2_figures/01_forest.png)

## 8. Overdispersion interpretation
Quasi uses one constant multiplier. Beta-binomial variance is n*mu*(1−mu)*[1+(n−1)*rho]; inflation depends on attempt count. At n=100, fitted rho implies inflation {1+99*b['dispersion_or_overdispersion']:.3f}; at n=500 it is {1+499*b['dispersion_or_overdispersion']:.3f}. Rho represents latent extra-binomial heterogeneity under this model, not evidence of a particular behavioral mechanism. A common rho is an assumption, and robust variance does not repair omitted covariates or selection.

## 9. Leave-one-out stability
All **299/299** exact M2 deletion refits succeeded; failed fits=0, sign reversals=0. Beta range [{l['minimum']:.9f}, {l['maximum']:.9f}], median={l['median']:.9f}, Q1={l['q1']:.9f}, Q3={l['q3']:.9f}. Each refit removes exactly one ID and preserves saved residuals and original observed position labels. When the singleton is removed, only its all-zero indicator is omitted; no categories are merged. LOO diagnoses the frozen binomial point-estimate influence; it is not a beta-binomial jackknife or a new exclusion rule.

{table(loo.loc[loo.beta.isin([loo.beta.min(),loo.beta.max()]),['removed_name','beta','n','FTA']])}

![LOO distribution](stage2_figures/02_loo.png)

## 10. Singleton unknown-position sensitivity
Excluding Danny Granger only is secondary: n=298, attempts=42,520, beta={p['exclude_unknown']['beta']:.9f}, quasi CI [{p['exclude_unknown']['ci_low']:.6f}, {p['exclude_unknown']['ci_high']:.6f}]. The shared slope and scaled uncertainty are effectively unchanged. His dedicated intercept can fit his observed probability without constraining the common slope; removing both that row and its indicator leaves residual df unchanged. This explains the numerical equivalence; it does not validate inference about unknown-position players generally.

The separately predeclared exploratory group removal uses Stage 1 hat>2p/n =32/299≈0.1070. It removes 42 players, leaving **257 and 28,127 attempts**, beta={high['beta']:.6f}, quasi CI [{high['ci_low']:.6f}, {high['ci_high']:.6f}]. Magnitude increases **{high['relative_beta_change']*100:.1f}%**, crossing the predeclared 50% materiality rule, with no reversal. This simultaneously removes 34.0% of attempts and changes population/role support; it is not a justified replacement sample. The primary model retains every valid FTA>0 player.

## 11. Position-grouping sensitivity
The outcome-independent map was frozen before refitting: Guard=PG, SG, PG-SG, SG-PG; Wing=SF, SG-SF, SF-SG, PF-SF, SF-PF; Big=PF, C, C-PF, PF-C; Unknown=unknown. All original labels are covered. Alphabetical Big is reference for this secondary model only.

Grouped-position beta={p['grouped_position']['beta']:.9f}, quasi CI [{p['grouped_position']['ci_low']:.6f}, {p['grouped_position']['ci_high']:.6f}]. Its magnitude and direction are very close to original-position M2. Primary robustness fits retain the original categories.

## 12. Alternate exposure robustness
Both frozen alternates receive quasi and beta-binomial fits; neither can replace residual wingspan. Raw ratio coefficients in the evidence are per full ratio unit.

{table(alt[alt.exposure=='wingspan_advantage'][['model','beta','ci_low','ci_high','odds_ratio']])}

Advantage and residual are algebraically equivalent given height and intercept; the tiny beta-binomial numerical difference is optimization tolerance, not independent replication. For interpretability, ratio below is per **0.01** ratio increase:

{table(ratio[['model','beta','ci_low','ci_high','odds_ratio','or_low','or_high']])}

All estimates remain negative; these robust intervals exclude zero under the specified variance models. This is qualitative consistency, not multiple independent primary confirmations.

## 13. FTA-threshold robustness
The only thresholds are the previously frozen 50 and 100 attempts. Both quasi and beta-binomial versions retain M2 adjustment among observed categories. Unknown is absent at FTA≥100 and its empty indicator is omitted; no level is merged.

{table(threshold[['model','n','FTA','beta','ci_low','ci_high','odds_ratio']])}

All point estimates are negative. The FTA≥100 quasi upper bound is −0.0000433, effectively at zero for practical interpretation; its p≈0.04974 should not be presented as qualitatively different from 0.05. These are population sensitivities, not grounds to select a threshold.

## 14. Robust probability contrast
Reuse Q25=−1.433029 and Q75=1.569988 inches from the full 311-player residual distribution. Average equally over the same 299 observed heights/positions, substituting only residual wingspan. The paired delta method uses the full appropriate mean-coefficient covariance. Beta-binomial predicts mean mu, not a simulated latent individual probability.

{table(pd.DataFrame([{'method':k,'difference_pp':v['difference']*100,'CI_low_pp':v['ci_low']*100,'CI_high_pp':v['ci_high']*100} for k,v in c.items()]))}

Preferred beta-binomial contrast is **{c['beta_binomial']['difference']*100:.3f} percentage points** (95% CI {c['beta_binomial']['ci_low']*100:.3f} to {c['beta_binomial']['ci_high']*100:.3f}). Quasi retains the Stage 1 −1.912-point contrast with widened uncertainty. These are adjusted association contrasts, not causal effects; synthetic covariate combinations and reference-fit uncertainty remain limitations.

![Probability contrast](stage2_figures/03_probability_contrast.png)

## 15. Scientific interpretation
Under the predeclared operational rule, classification is **{classification}**, driven by **magnitude sensitivity to joint high-leverage removal**, not an observed sign reversal or a major robust interval crossing zero. Direction is consistently negative across all tested models and every individual deletion; quasi/beta-binomial/HC0 uncertainty is roughly 2.3–2.6 times the original. Removing 42 players together increases magnitude by 59%, so the strict “strong directional robustness” category is not awarded under the frozen criterion. This wording should not obscure that sign stability is stronger than magnitude stability.

The evidence supports a carefully protocolized multi-season/hierarchical follow-up to assess generalizability and player heterogeneity, but does not require it or settle the association. No such analysis has started. Execution success does not depend on this classification or a p-value.

## 16. What remains unresolved
Conditional mean misspecification; heterogeneous dispersion across roles or attempt volumes; player dependence not represented by an invented cluster; small categories and singleton uncertainty; asymptotic Wald intervals rather than profile/bootstrap intervals; informative shooting opportunity; sensitivity to joint influence; residualization uncertainty held fixed; historical combine role versus current role; age/experience remain unvalidated and absent. Beta-binomial modeling addresses one form of extra-binomial variation, not these other issues.

## 17. Selection-bias limitation
Measurement coverage remains 311/482 positive-minute players; 171 are unmeasured. Previously approved median minutes were 1338.77 measured versus 971.02 unmeasured; median games 63 versus 55. Combine participation, NBA selection and measurement availability remain the largest generalizability limitation. No FT-accuracy-based selection comparison or correction is introduced.

{STATEMENT}

## 18. Reproducibility
Reuse the isolated Stage 1 environment and pinned requirements-stage1.txt; no dependencies or earlier artifacts were changed. Python 3.10, statsmodels 0.14.5 and SciPy 1.15.3. From this subproject:

```sh
.venv-stage1/bin/python scripts/stage2_validation.py
.venv-stage1/bin/python scripts/stage2_analysis.py
MPLCONFIGDIR=/private/tmp/stage2-mpl .venv-stage1/bin/python scripts/stage2_report.py
.venv-stage1/bin/python scripts/verify_stage2.py
```

Validation compares the full PMF with SciPy (max log-probability error {validation['scipy_logpmf_max_error']:.2g}) and independent beta-mixture quadrature (error {validation['independent_mixture_quadrature_error']:.2g}), verifies the binomial limit, increasing variance, invalid-count rejection, analytic score derivatives, three-start convergence and Hessian step stability. Seed 20260928 simulates 5,000 players; all known coefficients and precision recover within four estimated SEs. Forced maxiter=0 failures are rejected rather than hidden. These checks support implementation validity, not truth of the model assumptions.

[Primary robustness result](stage2_evidence/primary_robustness_result.json) was persisted before narrative interpretation and must reproduce exactly on rerun. An initial exploratory high-leverage mask used CSV integer IDs against Parquet string IDs and removed zero players. Before narrative writing, this was corrected with explicit string normalization and a 42-removal assertion. The invalid first artifact is retained with an [implementation correction record](stage2_evidence/implementation_correction.md); all unaffected results are verified identical. No statistical formula, grouping, threshold or interpretation rule changed.

[Build manifest](stage2_evidence/build_manifest.json), [test log](stage2_evidence/test_run.txt), numerical validation and the preservation manifest provide the verification record. Figures are matplotlib; no dashboard or new exposure-outcome exploration was added. Source code and full coefficient covariance, optimizer diagnostics, all LOO results and secondary tables are retained.

## 19. Stage 2 exit criteria
Execution PASS requires verified frozen inputs/results, transparent Pearson scaling, validated beta-binomial, all 299 recorded influence fits, predeclared grouping and threshold sensitivities, no outcome-driven primary exclusions, numerical result freeze preceding narrative, passing tests and deterministic rerun. The verification script records these outcomes. The scientific classification is independent of execution success.

## 20. Recommended next step
Review the dispersion model and the 59% joint-influence magnitude change before any expansion. If authorized later, predeclare a multi-season/hierarchical protocol with explicit selection/role limitations, variance checks and influence reporting. The current result is sufficient motivation for that follow-up, not a causal or broadly generalizable conclusion. **No Stage 3, multi-season/hierarchical longitudinal model, shot-context data, new confounder, commit or push was performed.**
'''
(ROOT/'docs/stage2_robust_inference.md').write_text(report)
print(classification)
