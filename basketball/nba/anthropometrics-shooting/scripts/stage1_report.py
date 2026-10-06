"""Render interpretation only from the persisted Stage 1 results."""
import json
import numpy as np
import pandas as pd
from stage1_analysis import ROOT,E,STATEMENT

def table(df):
    def fmt(v):
        if isinstance(v,(float,np.floating)): return f'{v:.5g}'
        return str(v)
    return '| '+' | '.join(map(str,df.columns))+' |\n| '+' | '.join(['---']*len(df.columns))+' |\n'+'\n'.join('| '+' | '.join(fmt(v) for v in row)+' |' for row in df.itertuples(index=False,name=None))
p=json.loads((E/'primary_result.json').read_text()); g=json.loads((E/'residualization_model.json').read_text()); s=json.loads((E/'analysis_sample_summary.json').read_text())
models=pd.read_csv(E/'primary_model_comparison.csv'); alt=pd.read_csv(E/'alternate_exposure_sensitivity.csv'); th=pd.read_csv(E/'fta_threshold_sensitivity.csv'); fits=pd.read_csv(E/'model_fit_summary.csv'); chars=pd.read_csv(E/'sample_characteristics.csv').rename(columns={'Unnamed: 0':'measure'}); pos=pd.read_csv(E/'position_descriptive.csv'); bins=pd.read_csv(E/'binned_descriptive.csv'); cov=pd.read_csv(E/'selection_coverage.csv').rename(columns={'Unnamed: 0':'group'}); mc=p['marginal_contrast']
text=f'''# Stage 1 — 2013-14 FT × residual wingspan

## 1. Objective
Estimate the association between relative wingspan and free-throw accuracy in the validated single-season candidate population.

{STATEMENT}

## 2. Frozen protocol
The Stage 0C PASS released the Stage 0B candidate for inference. Exact candidate and reference SHA-256 checks passed before loading outcomes. [Analysis plan](stage1_evidence/analysis_plan.json) records decisions before fitting: grouped-binomial logit; residual wingspan primary; M0 → M1 → M2; original positions; C reference; unscaled model-based Wald inference. FTA is the binomial denominator, never an additional predictor. No exposure or threshold was selected from its p-value. Secondary analyses cannot replace the primary result.

## 3. Analysis population
311 players remain in accounting; 299 with FTA>0 contribute 42,587 attempts. Twelve zero-attempt players remain in the saved analysis dataset with undefined FT%. Primary fitting has no minimum FTA threshold. Exact IDs, measurements, years, and original membership are unchanged. Model 3: **not run — prerequisite not validated**. Stage 0B provenance does not provide independently validated age/experience; none was fetched.

## 4. Residual-wingspan construction
OLS in the frozen 960-person reference gives wingspan = **{g['intercept']:.9f} + {g['slope']:.9f} × barefoot height**, in inches; R²={g['r_squared']:.9f}. Reference residual mean={g['residual_mean']:.3g}, sample SD={g['residual_sd']:.6f} inches. Only height and wingspan enter this geometric transformation. No shooting, NBA survival, position, or post-2013 measurements enter it.

The residual-height correlation in the 311-player candidate sample is **{s['residual_height_correlation']:.6f}**, not assumed zero. Candidate residual SD={s['residual_sd']:.6f} inches. Inference below conditions on this geometric fit and does not propagate reference-fit uncertainty.

## 5. Sample characteristics
Table 1. Anthropometric descriptions, calculated before shooting fits. SD uses ddof=1; quartiles use linear interpolation.

{table(chars)}

Original position counts appear in Table 4. Separately, FTA median=89, Q1=29.5, Q3=196; 203 players have FTA≥50 and 145 have FTA≥100. [Shooting distribution](stage1_evidence/shooting_descriptive.csv) gives FTM/FTA counts and individual FT% distribution among positive-attempt players; no average individual percentage is used as an accuracy estimate.

![Residual distribution](stage1_figures/01_distribution.png)

## 6. Descriptive association
The scatter has point area increasing with attempts and no unweighted regression line. Quintile cutpoints were computed from all 311 residuals, before fitting or plotting the shooting relationship, using linear interpolation. Exact edges are in [bin_cutpoints.json](stage1_evidence/bin_cutpoints.json). Bins retain zero-attempt players in n; rates are pooled FTM / pooled FTA.

![Descriptive scatter](stage1_figures/02_scatter.png)

{table(bins)}

![Descriptive bins](stage1_figures/03_binned.png)

These are descriptive summaries, with heterogeneous roles and shooting opportunity within each bin.

## 7. Model 0
Grouped-binomial logit(p)=intercept + residual_wingspan. Table 2 reports the primary ladder; coefficient and OR scales are per inch, with conventional binomial 95% intervals. All models use 299 players and 42,587 attempts.

{table(models[['model','beta','se','ci_low','ci_high','odds_ratio','or_low','or_high','p','or_per_sd']])}

M0 estimates a negative pooled association. OR per SD uses the fixed 311-person residual SD. These p-values are conditional on binomial variance and are not robust to the substantial overdispersion below.

## 8. Model 1
Adds barefoot height. The residual coefficient changes from -0.051244 to -0.040048, a 21.8% reduction in magnitude. The direction remains negative. Orthogonality in the 960-person geometric reference does not imply orthogonality in this selected analysis population or in an attempt-weighted logistic likelihood.

## 9. Model 2
Adds original combine-position indicators, preserving all hybrids; blank/missing is unknown. C is the alphabetically first reference category. Residual coefficient=-0.035310, OR=0.965306 per inch. **The conventional 95% coefficient interval [-0.047163, -0.023456] excludes zero**; the OR interval excludes one.

All seven primary/secondary fits converge with full-rank designs and finite covariance. Mixed-success/failure observations span each design, ruling out complete or quasi separation. Fitted probabilities are not near numerical boundaries. Full coefficient and covariance matrices, player-level leverage/Pearson/Cook diagnostics, and model fit records are saved.

{table(fits[['model','n','total_fta','log_likelihood','deviance','aic','dispersion','min_probability','max_probability','max_hat']])}

The unknown category contains Danny Granger alone (63/67). Its M2 leverage is essentially one; its deletion diagnostic is undefined because deleting the only member removes that estimable category. The finite singleton estimate is retained under the predeclared policy, not merged. It is not a separation failure, but position-specific interpretation is fragile. There are 42 M2 observations above 2p/n leverage. Raw uncentered design condition number is approximately 5,228; units and intercept contribute to this value, while rank and covariance remain finite. No position-policy change was made. Inspect [M2 influence](stage1_evidence/M2_influence.csv) before treating any one-player result as stable.

## 10. Position adjustment / Simpson's paradox question
M0→M2 reduces the negative coefficient magnitude by **31.1%**, with no sign reversal; M1→M2 adds 11.8% attenuation. M0→M2 includes both height and position adjustments, so its full change cannot be assigned solely to position. This is compatible with role/height structure in the pooled association, not proof of a causal mechanism; logistic noncollapsibility also limits a pure confounding interpretation. There is no observed Simpson sign reversal in this ladder.

Table 4. Original positions; pooled rates use summed makes and attempts. No separate tiny-category regressions were fitted.

{table(pos)}

![Primary coefficient comparison](stage1_figures/05_primary_coefficients.png)

## 11. Marginal probability interpretation
Set residual wingspan to Q25={mc['q25']:.6f} or Q75={mc['q75']:.6f} inches, defined in all 311 candidates. Preserve each of the 299 likelihood players' observed height and position, then average predicted probabilities equally across players. Predicted FT probability is {mc['p25']:.6%} at Q25 and {mc['p75']:.6%} at Q75. Q75−Q25 is **{mc['difference']*100:.3f} percentage points**, model-based 95% CI [{mc['ci_low']*100:.3f}, {mc['ci_high']*100:.3f}]. The paired delta-method contrast uses the full covariance matrix.

This is an association-based model contrast, not a causal treatment effect. Some synthetic residual/height/position combinations are sparsely supported. The curve spans the observed residual range; its pointwise delta-method bands condition on the model and omit extra-binomial variance and geometric-fit uncertainty.

![Adjusted probability](stage1_figures/04_adjusted_probability.png)

## 12. Alternate exposure sensitivity
Table 3a. Secondary M2 structure; ratio coefficients below are per 1.0 ratio unit.

{table(alt[['model','beta','ci_low','ci_high','odds_ratio','p']])}

Advantage remains negative. With height and intercept included, advantage and residual wingspan are exact linear reparameterizations: their identical exposure coefficient and likelihood are expected algebraically, not independent corroboration. Ratio per **0.01** increase gives beta={alt.iloc[1].beta*.01:.6f}, CI [{alt.iloc[1].ci_low*.01:.6f}, {alt.iloc[1].ci_high*.01:.6f}], OR={np.exp(alt.iloc[1].beta*.01):.6f}, OR CI [{np.exp(alt.iloc[1].ci_low*.01):.6f}, {np.exp(alt.iloc[1].ci_high*.01):.6f}]. Direction remains negative. Residual wingspan remains primary.

## 13. FTA-threshold sensitivity
Table 3b. Secondary M2 residual-wingspan fits.

{table(th[['threshold','n','total_fta','beta','ci_low','ci_high','odds_ratio']])}

Both estimates remain negative and slightly larger in magnitude than primary M2. At FTA≥100, unknown has no observations and its indicator is not estimable or included; all observed original categories remain distinct and C remains reference. This is an absent level, not a merged category. Thresholds alter the target sample and do not resolve overdispersion.

## 14. Overdispersion diagnostic
Predeclared Pearson chi-square / residual degrees of freedom >1.5 flags substantial overdispersion. M0=7.618, M1=6.168, **M2=5.562** (1573.924/283). Every sensitivity also exceeds the threshold. The frozen binomial likelihood remains primary, but conventional SEs/intervals and small p-values can substantially overstate precision when remaining player heterogeneity violates binomial variance. The excluded-zero interval alone is not robust evidence against a population null under a more adequate variance model. No new model family was fitted opportunistically.

## 15. Selection-coverage limitation
Reuse the approved Stage 0B positive-minute coverage summary; no FT accuracy comparison is introduced here.

{table(cov)}

Only 311/482 (64.5%) positive-minute players have usable measurements; 171 do not. Measured players have higher median minutes (1338.77 versus 971.02) and games (63 versus 55). Box-position availability is incomplete and not equivalent to validated combine role. Selection into the combine, NBA, measured sample, and shooting opportunities limits generalizability. This analysis does not correct selection bias.

## 16. Main scientific result
The estimated association is negative throughout the primary ladder and attenuates after adjustment. M2 estimates about 3.47% lower FT odds per additional residual inch and a 1.91-percentage-point lower adjusted predicted probability from Q25 to Q75. Its conventional interval excludes zero, but substantial overdispersion means uncertainty requires further robustness analysis before stronger inferential conclusions.

## 17. What the analysis does NOT establish
{STATEMENT}

The analysis does not establish a biomechanical mechanism, a population-wide association for all NBA players, or a result that generalizes across seasons. It does not distinguish all role-related selection and unmeasured confounding.

## 18. Limitations
Single season; combine availability and NBA survival selection; historical combine position may differ from current role; small hybrid groups and one unknown; incomplete uniform validation of role, age and experience; unmeasured skill and training; unequal shooting opportunity; conventional binomial variance poorly fits remaining heterogeneity; linear log-odds form; conditional geometric transformation; marginal extrapolation; unresolved prior cross-source identity links remain unapplied. Influence outputs are diagnostic only: no outcome-driven player exclusion or refit was performed.

## 19. Reproducibility
Run from this subproject:

```sh
python3 -m venv .venv-stage1
.venv-stage1/bin/pip install -r requirements-stage1.txt
.venv-stage1/bin/pip check
MPLCONFIGDIR=/private/tmp/stage1-mpl .venv-stage1/bin/python scripts/stage1_analysis.py
.venv-stage1/bin/python scripts/stage1_report.py
.venv-stage1/bin/python -m unittest discover -s tests -p test_stage1.py -v
```

Isolated Python 3.10 environment; statsmodels 0.14.5, numpy 2.2.6, scipy 1.15.3, pandas 2.2.3, matplotlib 3.10.3 and pyarrow 21.0.0; all installed dependencies are pinned in requirements-stage1.txt. pip check passes. [Statsmodels GLM documentation](https://www.statsmodels.org/v0.14.4/generated/statsmodels.genmod.generalized_linear_model.GLM.html) documents the two-column successes/failures response used here. Model code supplies [FTM, FTA−FTM] without frequency weights. No other project's environment changed.

[Primary result](stage1_evidence/primary_result.json) was written before this report or interpretation. It freezes model estimates, hashes and marginal contrast; reruns assert exact equality before continuing. Initial implementation checks corrected a syntax typo and the blank-string representation of missing position before the first successful ladder; no formula or exposure was changed. [Build manifest](stage1_evidence/build_manifest.json) records inputs, environment, scripts and outputs. [Tests](stage1_evidence/test_run.txt) cover A–R plus denominator and integrity checks. Arrow CPU-cache discovery warnings under sandboxing do not prevent verified Parquet round trips.

Candidate hash: `{p['candidate_hash']}`. Reference hash: `{p['reference_hash']}`. Analysis hash: `{p['analysis_dataset_hash']}`. Numerical code hash: `{p['code_hash']}`. Analysis Parquet remains local and ignored. Prior-stage data, code and evidence are preserved.

## 20. Stage 1 exit criteria
Execution PASS is contingent on the saved test summary passing: frozen inputs verified; correct reference-only residualization; grouped-count outcome; exact primary ladder; result frozen before interpretation; no outcome-driven selection; secondary analyses labeled; position question addressed; dispersion and coverage reported; fixed-environment rerun reproduces primary estimates. Scientific significance is not an execution criterion. Tests and the build receipt provide the final verification record.

## 21. Recommended next step
Review this single-season prototype, especially overdispersion and leverage. A separately authorized robustness stage should assess beta-binomial, quasi-binomial or hierarchical logistic uncertainty and influence sensitivity under a documented protocol. **No Stage 2, multi-season model, hierarchical model, C&S or pull-up expansion was run. No commit or push was made.**
'''
(ROOT/'docs/stage1_ft_residual_wingspan_analysis.md').write_text(text)
