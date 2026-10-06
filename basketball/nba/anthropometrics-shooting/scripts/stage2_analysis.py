"""Stage 2 robustness; immutable Stage 1 data, no geometric refit."""
from pathlib import Path
import json,hashlib
import numpy as np
import pandas as pd
import statsmodels.api as sm
from scipy.special import expit
from stage1_analysis import ROOT,H,PRIMARY,sha,STATEMENT
from stage2_models import fit_bb,effect,hc0,Z
E=ROOT/'docs/stage2_evidence'; S1=ROOT/'docs/stage1_evidence'
DATA=ROOT/'data/processed/stage1_ft_2013_14_analysis.parquet'
PLAN=json.loads((E/'analysis_plan.json').read_text())
def save(name,obj): (E/name).write_text(json.dumps(obj,indent=2,allow_nan=False)+'\n')
def load():
    prior=json.loads((E/'prior_preservation_manifest.json').read_text())
    assert all(sha(ROOT/p)==h for p,h in prior.items()),'STOP: prior artifact changed'
    frozen=json.loads((S1/'primary_result.json').read_text())
    assert sha(DATA)==frozen['analysis_dataset_hash']
    assert sha(ROOT/'data/interim/residual_reference_pre2013.csv')==frozen['reference_hash']
    assert sha(ROOT/'data/processed/ft_2013_14_stage1_dataset.parquet')==frozen['candidate_hash']
    d=pd.read_parquet(DATA); assert len(d)==311 and (d.fta==0).sum()==12 and d.fta.sum()==42587
    return d,d[d.fta>0].copy(),frozen

def design(d,exposure=PRIMARY,group=False):
    x=pd.DataFrame({'const':1.,exposure:d[exposure],H:d[H]},index=d.index)
    pos=d.position.map(PLAN['group_map']) if group else d.position
    assert pos.notna().all()
    for c in sorted(pos.unique())[1:]: x['position_'+c]=(pos==c).astype(float)
    return x.astype(float)

def glm(d,exposure=PRIMARY,group=False,cov_type='nonrobust'):
    x=design(d,exposure,group)
    assert np.linalg.matrix_rank(x)==x.shape[1]
    mixed=(d.ftm>0)&(d.ftm<d.fta)
    assert np.linalg.matrix_rank(x.loc[mixed])==x.shape[1],'separation not ruled out'
    m=sm.GLM(np.column_stack([d.ftm,d.fta-d.ftm]),x,family=sm.families.Binomial()).fit(maxiter=200,tol=1e-10,cov_type=cov_type)
    assert m.converged and np.isfinite(m.cov_params()).all().all()
    return m

def row(name,d,b,cov,dispersion,converged=True):
    return dict(model=name,**effect(np.asarray(b),np.asarray(cov)),dispersion_or_overdispersion=dispersion,n=len(d),FTA=int(d.fta.sum()),converged=converged)

def quasi(name,d,exposure=PRIMARY,group=False):
    m=glm(d,exposure,group); phi=float(m.pearson_chi2/m.df_resid); covariance=np.asarray(m.cov_params())*phi
    return row(name,d,m.params,covariance,phi),m,covariance

def bb(name,d,exposure=PRIMARY):
    m=glm(d,exposure); out=fit_bb(design(d,exposure),d.ftm,d.fta,m.params)
    r=row(name,d,out['beta'],out['cov'],out['rho']); r.update(log_likelihood=out['ll'],AIC=out['aic'],kappa=out['kappa'],dispersion_parameter='rho')
    details={k:v for k,v in out.items() if k not in ['beta','cov']}; details.update(r); details['coefficients']=dict(zip(out['names'],out['beta'].tolist()))
    pd.DataFrame(out['cov'],index=out['names'],columns=out['names']).to_csv(E/f'{name}_covariance.csv')
    save(f'{name}_diagnostics.json',details)
    return r,out

def contrast(b,cov,d,q):
    means=[]; grads=[]
    for value in q:
        x=design(d.assign(residual_wingspan=value)).to_numpy(); p=expit(x@b)
        means.append(float(p.mean())); grads.append((x*(p*(1-p))[:,None]).mean(axis=0))
    diff=means[1]-means[0]; gradient=grads[1]-grads[0]; se=float(np.sqrt(gradient@cov@gradient))
    return dict(q25=float(q[0]),q75=float(q[1]),p25=means[0],p75=means[1],difference=diff,se=se,ci_low=diff-Z*se,ci_high=diff+Z*se,averaging_players=len(d),method='paired delta method, equal player average, fixed observed height/position')

def main():
    assert json.loads((E/'beta_binomial_validation.json').read_text())['passed']
    all_data,d,frozen=load()
    qr,m,qcov=quasi('quasi_binomial_M2',d)
    assert effect(m.params.to_numpy(),m.cov_params().to_numpy())['beta']==frozen['models']['M2']['beta']
    base=row('Stage1_binomial_M2',d,m.params,m.cov_params(),1.)
    save('quasi_binomial_result.json',dict(**qr,phi=qr['dispersion_or_overdispersion'],pearson_chi2=float(m.pearson_chi2),df_resid=int(m.df_resid),point_estimate_unchanged=True,covariance_rule='phi times original binomial covariance'))
    br,bm=bb('beta_binomial_M2',d); save('beta_binomial_result.json',json.loads((E/'beta_binomial_M2_diagnostics.json').read_text()))
    sandwich=hc0(m,d.ftm,d.fta); api=glm(d,cov_type='HC0')
    np.testing.assert_allclose(sandwich,api.cov_params(),rtol=2e-7,atol=1e-9)
    hr=row('HC0_M2_sensitivity',d,m.params,sandwich,None)
    save('hc0_result.json',dict(**hr,independent_score_rows=299,not_clustered=True,statsmodels_covariance_max_error=float(np.max(abs(sandwich-api.cov_params().to_numpy()))),caution='singleton group has no replication; HC0 can underestimate variance with high leverage; no HC2/3 forced'))
    pd.DataFrame(sandwich,index=m.params.index,columns=m.params.index).to_csv(E/'HC0_covariance.csv')
    loo=[]
    for _,player in d.iterrows():
        subset=d[d.player_id!=player.player_id]
        assert len(subset)==298 and set(d.player_id)-set(subset.player_id)=={player.player_id}
        assert subset[PRIMARY].equals(d.loc[subset.index,PRIMARY])
        record=dict(removed_id=int(player.player_id),removed_name=player.player_name_nba,n=len(subset),FTA=int(subset.fta.sum()),removed_position=player.position,omitted_empty_categories=';'.join(sorted(set(d.position)-set(subset.position))),exposure_unchanged=True)
        try:
            lm=glm(subset); record.update(beta=float(lm.params[PRIMARY]),converged=True,error='',design_columns=';'.join(lm.model.exog_names))
        except Exception as error: record.update(beta=None,converged=False,error=str(error),design_columns=';'.join(design(subset).columns))
        loo.append(record)
    lf=pd.DataFrame(loo); lf.to_csv(E/'loo_player_results.csv',index=False)
    good=lf.loc[lf.converged,'beta']; ls=dict(fits=len(lf),successful=len(good),failed=int((~lf.converged).sum()),minimum=float(good.min()),maximum=float(good.max()),median=float(good.median()),q1=float(good.quantile(.25)),q3=float(good.quantile(.75)),sign_reversals=int((good>=0).sum()))
    save('loo_summary.json',ls)
    ex,_,_=quasi('exclude_unknown_sensitivity',d[d.position!='unknown']); pd.DataFrame([ex]).to_csv(E/'exclude_unknown_sensitivity.csv',index=False)
    grouped,_,_=quasi('grouped_position_sensitivity',d,group=True); pd.DataFrame([grouped]).to_csv(E/'grouped_position_sensitivity.csv',index=False)
    high=pd.read_csv(S1/'M2_influence.csv'); ids=set(high.loc[high.high_leverage,'player_id'].astype(str)); assert len(ids)==42
    subset=d[~d.player_id.astype(str).isin(ids)]
    assert len(subset)==len(d)-42, 'high-leverage deletion must remove exactly 42 players'
    highrow,_,_=quasi('high_leverage_group_removal_exploratory',subset)
    highrow.update(removed_players=len(ids),removed_ids=sorted(map(int,ids)),absent_categories=sorted(set(d.position)-set(subset.position)),relative_beta_change=abs(highrow['beta']/base['beta']-1))
    save('high_leverage_sensitivity.json',highrow)
    alt=[]; thresholds=[]
    for exposure in ['wingspan_advantage','wingspan_ratio']:
        ar,_,_=quasi('quasi_'+exposure,d,exposure); abr,_=bb('BB_'+exposure,d,exposure)
        for r in [ar,abr]: r.update(exposure=exposure,analysis='secondary',reported_unit=1.0)
        alt.extend([ar,abr])
    for threshold in [50,100]:
        sub=d[d.fta>=threshold]; tr,_,_=quasi(f'FTA{threshold}_robust',sub); tbr,_=bb(f'FTA{threshold}_beta_binomial',sub)
        for r in [tr,tbr]: r.update(threshold=threshold,analysis='secondary')
        thresholds.extend([tr,tbr])
    pd.DataFrame(alt).to_csv(E/'alternate_exposure_robustness.csv',index=False)
    pd.DataFrame(thresholds).to_csv(E/'fta_threshold_robustness.csv',index=False)
    q=[frozen['marginal_contrast'][k] for k in ['q25','q75']]
    contrasts={'Stage1_binomial':contrast(m.params.to_numpy(),m.cov_params().to_numpy(),d,q),'quasi':contrast(m.params.to_numpy(),qcov,d,q),'HC0':contrast(m.params.to_numpy(),sandwich,d,q),'beta_binomial':contrast(bm['beta'],bm['cov'],d,q)}
    save('robust_probability_contrast.json',contrasts)
    rows=[base,qr,br,hr,grouped,ex]+thresholds+[highrow]
    pd.DataFrame(rows).drop(columns=['removed_ids','absent_categories'],errors='ignore').to_csv(E/'robust_model_comparison.csv',index=False)
    result=dict(primary_exposure=PRIMARY,stage1_M2=base,quasi=qr,beta_binomial=br,HC0=hr,loo=ls,exclude_unknown=ex,grouped_position=grouped,FTA_thresholds=thresholds,probability_contrasts=contrasts,high_leverage=highrow,analysis_hash=sha(DATA),stage1_primary_hash=sha(S1/'primary_result.json'),plan_hash=sha(E/'analysis_plan.json'),code_hashes={p.name:sha(p) for p in [Path(__file__),ROOT/'scripts/stage2_models.py',ROOT/'scripts/stage2_validation.py']})
    # Persist numerical results before interpretation; formula/results cannot drift on rerun.
    target=E/'primary_robustness_result.json'
    if target.exists(): assert json.loads(target.read_text())==result,'STOP: frozen robustness result changed'
    else: save('primary_robustness_result.json',result)
    print('Numerical robustness results frozen; narrative not generated by this script.')
if __name__=='__main__': main()
