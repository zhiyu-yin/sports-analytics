"""Frozen single-season grouped-binomial analysis. Run from any directory."""
from pathlib import Path
import hashlib, json, warnings
import numpy as np
import pandas as pd
import statsmodels.api as sm
from scipy.special import expit
ROOT = Path(__file__).resolve().parents[1]
E = ROOT/'docs/stage1_evidence'
CAND = ROOT/'data/processed/ft_2013_14_stage1_dataset.parquet'
REF = ROOT/'data/interim/residual_reference_pre2013.csv'
HASHES = ('4656da551e99fc7a8fc26d6f7847f956134a9da15ed47ccd13bbf0f982fbf735','14537d9c1cec20b388fc2cf5c86d7ea9ec2e435117c62da499f2b2fa2820d85a')
H = 'height_wo_shoes_inches'
PRIMARY = 'residual_wingspan'
STATEMENT = 'This analysis estimates associations within NBA players with available combine measurements. It does not identify a causal effect of arm length on shooting, because combine participation, NBA selection, role assignment and other factors may jointly affect the observed sample.'
def sha(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def save(name, obj): (E/name).write_text(json.dumps(obj, indent=2, allow_nan=False)+'\n')
def inputs():
    assert (sha(CAND), sha(REF)) == HASHES, 'STOP: frozen hash mismatch'
    d, r = pd.read_parquet(CAND), pd.read_csv(REF)
    assert len(d)==311 and len(r)==960 and r.player_id.is_unique and d.player_id.is_unique
    assert (r.combine_year<=2013).all() and (r.player_id>0).all()
    assert (d.ftm>=0).all() and (d.fta>=d.ftm).all()
    assert np.equal(d[['ftm','fta']], np.floor(d[['ftm','fta']])).all().all()
    return d,r

def geometry(r):
    # Explicit projection prevents any outcome or selection variable entering OLS.
    x=sm.add_constant(r[[H]], has_constant='add')
    return sm.OLS(r['wingspan_inches'],x).fit()

def prepare(d,r):
    g=geometry(r); d=d.copy()
    d[PRIMARY]=d.wingspan_inches-g.predict(sm.add_constant(d[[H]],has_constant='add'))
    d['position']=d.combine_position.replace('',np.nan).fillna('unknown')
    d['ft_pct']=d.ftm/d.fta.replace(0,np.nan)
    return d,g

def design(d, level, exposure=PRIMARY):
    x=pd.DataFrame({'const':np.ones(len(d)),exposure:d[exposure]},index=d.index)
    if level>=1: x[H]=d[H]
    if level>=2:
        cats=sorted(d.position.unique())
        assert cats[0]=='C'
        for cat in cats[1:]: x['position_'+cat]=(d.position==cat).astype(float)
    return x.astype(float)

def fit(d, level, exposure=PRIMARY):
    assert (d.fta>0).all()
    x=design(d,level,exposure)
    assert np.linalg.matrix_rank(x)==x.shape[1], 'STOP: singular design'
    mixed=(d.ftm>0)&(d.ftm<d.fta)
    assert np.linalg.matrix_rank(x.loc[mixed])==x.shape[1], 'STOP: separation not ruled out'
    with warnings.catch_warnings(record=True) as w:
        result=sm.GLM(np.column_stack([d.ftm,d.fta-d.ftm]),x,family=sm.families.Binomial()).fit(maxiter=200,tol=1e-10)
    assert result.converged and np.isfinite(result.cov_params()).all().all(), 'STOP: unstable estimation'
    assert not any('separation' in str(a.message).lower() for a in w), 'STOP: separation warning'
    return result

def effect(m,exposure=PRIMARY,scale=1.):
    b=float(m.params[exposure])*scale; se=float(m.bse[exposure])*scale
    lo,hi=b-1.959963984540054*se,b+1.959963984540054*se
    return dict(exposure=exposure,scale=scale,beta=b,se=se,ci_low=lo,ci_high=hi,p=float(m.pvalues[exposure]),odds_ratio=float(np.exp(b)),or_low=float(np.exp(lo)),or_high=float(np.exp(hi)))

def marginal(m,d,values):
    means=[]; gradients=[]
    for v in values:
        x=design(d.assign(residual_wingspan=v),2).to_numpy(); p=expit(x@m.params.to_numpy())
        means.append(float(p.mean())); gradients.append((x*(p*(1-p))[:,None]).mean(axis=0))
    cov=m.cov_params().to_numpy()
    se=[float(np.sqrt(g@cov@g)) for g in gradients]
    return np.array(means),np.array(se),np.array(gradients)

def main():
    d,r=inputs(); d,g=prepare(d,r)
    save('residualization_model.json',dict(intercept=float(g.params['const']),slope=float(g.params[H]),r_squared=float(g.rsquared),n=len(r),residual_mean=float(g.resid.mean()),residual_sd=float(g.resid.std(ddof=1)),reference_hash=sha(REF),code_hash=sha(__file__),predictors=[H],response='wingspan_inches'))
    cols=[H,'wingspan_inches',PRIMARY,'wingspan_advantage','wingspan_ratio']
    d[cols].describe().T.to_csv(E/'sample_characteristics.csv')
    d.position.value_counts().sort_index().rename('n').to_csv(E/'position_counts.csv')
    edges=d[PRIMARY].quantile(np.linspace(0,1,6)).to_numpy()
    save('bin_cutpoints.json',dict(rule='all 311 residual quintiles; linear interpolation',edges=edges.tolist()))
    d[['ftm','fta','ft_pct']].describe().T.to_csv(E/'shooting_descriptive.csv')
    d.to_parquet(ROOT/'data/processed/stage1_ft_2013_14_analysis.parquet',index=False)
    sample=dict(total_players=len(d),fta_zero=int((d.fta==0).sum()),likelihood_players=int((d.fta>0).sum()),total_fta=int(d.fta.sum()),median_fta=float(d.fta.median()),q1_fta=float(d.fta.quantile(.25)),q3_fta=float(d.fta.quantile(.75)),fta_ge_50=int((d.fta>=50).sum()),fta_ge_100=int((d.fta>=100).sum()),residual_height_correlation=float(d[[PRIMARY,H]].corr().iloc[0,1]),residual_sd=float(d[PRIMARY].std()))
    save('analysis_sample_summary.json',sample)
    positive=d[d.fta>0].copy(); models=[fit(positive,i) for i in range(3)]
    q=d[PRIMARY].quantile([.25,.75]).to_numpy(); prob,se,grad=marginal(models[2],positive,q)
    diff=float(prob[1]-prob[0]); ds=float(np.sqrt((grad[1]-grad[0])@models[2].cov_params()@(grad[1]-grad[0])))
    primary=dict(primary_exposure=PRIMARY,primary_outcome='FTM out of FTA',models={f'M{i}':effect(m) for i,m in enumerate(models)},marginal_contrast=dict(q25=float(q[0]),q75=float(q[1]),p25=float(prob[0]),p75=float(prob[1]),difference=diff,ci_low=diff-1.95996398454*ds,ci_high=diff+1.95996398454*ds,averaging_players=len(positive)),n_players=len(positive),total_fta=int(positive.fta.sum()),reference_hash=sha(REF),candidate_hash=sha(CAND),analysis_dataset_hash=sha(ROOT/'data/processed/stage1_ft_2013_14_analysis.parquet'),code_hash=sha(__file__),plan_hash=sha(E/'analysis_plan.json'))
    # Freeze BEFORE any narrative interpretation. Reruns must reproduce identical results.
    target=E/'primary_result.json'
    if target.exists(): assert json.loads(target.read_text())==primary, 'STOP: primary freeze changed'
    else: save('primary_result.json',primary)
    fits=[]; allmodels=[(f'M{i}',m,positive,PRIMARY) for i,m in enumerate(models)]
    alternate=[]; thresholds=[]
    for exposure in ['wingspan_advantage','wingspan_ratio']:
        m=fit(positive,2,exposure); alternate.append(dict(analysis='secondary',model=exposure,n=len(positive),total_fta=int(positive.fta.sum()),**effect(m,exposure)))
        allmodels.append((exposure,m,positive,exposure))
    for threshold in [50,100]:
        subset=d[d.fta>=threshold]; m=fit(subset,2)
        thresholds.append(dict(analysis='secondary',threshold=threshold,n=len(subset),total_fta=int(subset.fta.sum()),absent_positions=';'.join(sorted(set(d.position)-set(subset.position))),**effect(m)))
        allmodels.append((f'FTA{threshold}',m,subset,PRIMARY))
    pd.DataFrame(alternate).to_csv(E/'alternate_exposure_sensitivity.csv',index=False)
    pd.DataFrame(thresholds).to_csv(E/'fta_threshold_sensitivity.csv',index=False)
    for name,m,frame,exposure in allmodels:
        x=m.model.exog; p=m.fittedvalues.to_numpy(); w=frame.fta.to_numpy()*p*(1-p)
        hat=np.einsum('ij,jk,ik->i',x,m.cov_params().to_numpy(),x)*w
        pearson=(frame.ftm.to_numpy()-frame.fta.to_numpy()*p)/np.sqrt(w)
        cook=np.full(len(frame),np.nan); valid=hat<1-1e-8
        cook[valid]=pearson[valid]**2*hat[valid]/(x.shape[1]*(1-hat[valid])**2)
        influence=frame[['player_id','player_name_nba','position','fta']].copy()
        influence['fitted_probability']=p; influence['hat']=hat; influence['pearson_residual']=pearson; influence['cooks_distance']=cook
        influence['high_leverage']=hat>2*x.shape[1]/len(frame)
        influence.to_csv(E/f'{name}_influence.csv',index=False)
        coeff=pd.DataFrame({'term':m.params.index,'beta':m.params,'se':m.bse,'ci_low':m.conf_int()[0],'ci_high':m.conf_int()[1],'p':m.pvalues})
        coeff.to_csv(E/(f'model{name[1:]}_coefficients.csv' if name.startswith('M') else f'{name}_coefficients.csv'),index=False)
        m.cov_params().to_csv(E/f'{name}_covariance.csv')
        fits.append(dict(model=name,n=len(frame),total_fta=int(frame.fta.sum()),log_likelihood=float(m.llf),deviance=float(m.deviance),aic=float(m.aic),converged=bool(m.converged),df_resid=int(m.df_resid),pearson_chi2=float(m.pearson_chi2),dispersion=float(m.pearson_chi2/m.df_resid),covariance='nonrobust unscaled binomial',min_probability=float(p.min()),max_probability=float(p.max()),max_hat=float(hat.max()),high_leverage_count=int((hat>2*x.shape[1]/len(frame)).sum()),undefined_deletion_diagnostics=int((~valid).sum()),condition_number=float(np.linalg.cond(x)),separation='ruled out: mixed-outcome rows span design'))
    pd.DataFrame(fits).to_csv(E/'model_fit_summary.csv',index=False)
    save('overdispersion_diagnostic.json',dict(rule='Pearson chi-square / residual df > 1.5',models={a['model']:{'dispersion':a['dispersion'],'substantial':a['dispersion']>1.5} for a in fits}))
    pos=d.groupby('position').agg(n=('player_id','size'),mean_residual=(PRIMARY,'mean'),median_residual=(PRIMARY,'median'),total_fta=('fta','sum'),total_ftm=('ftm','sum'))
    pos['pooled_ft_pct']=pos.total_ftm/pos.total_fta; pos.to_csv(E/'position_descriptive.csv')
    bins=d.groupby(pd.cut(d[PRIMARY],edges,include_lowest=True),observed=True).agg(n=('player_id','size'),total_fta=('fta','sum'),total_ftm=('ftm','sum'),mean_residual=(PRIMARY,'mean'))
    bins['pooled_ft_pct']=bins.total_ftm/bins.total_fta; bins.to_csv(E/'binned_descriptive.csv')
    prior=json.loads((ROOT/'docs/stage0b_evidence/ft_2013_14_dataset_summary.json').read_text())
    pd.DataFrame(prior['selection_coverage']).T.to_csv(E/'selection_coverage.csv')
    pd.DataFrame([dict(model=f'M{i}',or_per_sd=float(np.exp(m.params[PRIMARY]*sample['residual_sd'])),**effect(m)) for i,m in enumerate(models)]).to_csv(E/'primary_model_comparison.csv',index=False)
    plots(d,positive,models,bins)

def plots(d,positive,models,bins):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    plt.rcParams.update({'font.size':10,'axes.spines.top':False,'axes.spines.right':False,'figure.dpi':120,'savefig.dpi':200})
    folder=ROOT/'docs/stage1_figures'; folder.mkdir(exist_ok=True)
    def finish(fig,name):
        fig.tight_layout(); fig.savefig(folder/f'{name}.png'); fig.savefig(folder/f'{name}.svg'); plt.close(fig)
    fig,ax=plt.subplots(figsize=(7,4)); ax.hist(d[PRIMARY],bins=18,color='#416783',edgecolor='white'); ax.set(xlabel='Residual wingspan (inches)',ylabel='Players',title='Residual wingspan · 311 measured players'); finish(fig,'01_distribution')
    fig,ax=plt.subplots(figsize=(7,4)); ax.scatter(positive[PRIMARY],positive.ft_pct,s=8+positive.fta*.12,alpha=.45,color='#416783',linewidths=0); ax.set(xlabel='Residual wingspan (inches)',ylabel='FT makes / attempts',title='Descriptive association · point area increases with FTA',ylim=(0,1.04)); finish(fig,'02_scatter')
    fig,ax=plt.subplots(figsize=(7,4)); ax.plot(bins.mean_residual,bins.pooled_ft_pct,'o-',color='#416783');
    for _,row in bins.iterrows(): ax.annotate(f"n={int(row['n'])}\nFTA={int(row.total_fta):,}",(row.mean_residual,row.pooled_ft_pct),xytext=(0,12),textcoords='offset points',ha='center',fontsize=8)
    ax.set(xlabel='Mean residual wingspan in predeclared quintile (inches)',ylabel='Pooled FTM / FTA',title='Descriptive pooled free-throw accuracy',ylim=(min(bins.pooled_ft_pct)-.03,max(bins.pooled_ft_pct)+.06)); finish(fig,'03_binned')
    grid=np.linspace(d[PRIMARY].min(),d[PRIMARY].max(),151); mean,se,_=marginal(models[2],positive,grid)
    pd.DataFrame({'residual_wingspan':grid,'probability':mean,'ci_low':mean-1.95996398454*se,'ci_high':mean+1.95996398454*se}).to_csv(E/'adjusted_probability_curve.csv',index=False)
    fig,ax=plt.subplots(figsize=(7,4)); ax.plot(grid,mean,color='#416783'); ax.fill_between(grid,mean-1.95996398454*se,mean+1.95996398454*se,color='#416783',alpha=.2); ax.plot(d[PRIMARY],np.repeat(ax.get_ylim()[0],len(d)),'|',alpha=.2,color='gray'); ax.set(xlabel='Residual wingspan (inches)',ylabel='Average predicted FT probability',title='Model 2 adjusted association · model-based 95% CI'); finish(fig,'04_adjusted_probability')
    fig,ax=plt.subplots(figsize=(7,4)); b=[m.params[PRIMARY] for m in models]; se=[m.bse[PRIMARY]*1.95996398454 for m in models]; ax.errorbar(b,[2,1,0],xerr=se,fmt='o',color='#416783',capsize=4); ax.axvline(0,color='gray',ls='--'); ax.set(yticks=[2,1,0],yticklabels=['M0: residual','M1: + height','M2: + position'],xlabel='Residual-wingspan coefficient (log odds / inch)',title='Primary model ladder · binomial 95% intervals',ylim=(-.5,2.5)); finish(fig,'05_primary_coefficients')
if __name__=='__main__': main()
