"""Ordered execution; immutable primary receipt gates every secondary analysis."""
from stage3j_core import *
import shutil

def primary():
 p=authorize();assert not (E/'primary_result.json').exists()
 save('j1_execution_start.json',dict(started_at=now(),protocol_sha256=sha(E/'analysis_protocol.json'),implementation_tests_sha256=sha(E/'implementation_test_summary.json')),True)
 d=load();result,m,cov,parts=estimate(d,p)
 save('j1_cluster_validation.json',result['covariance_validation'],True)
 save('j1_cluster_covariance.json',dict(names=list(m.params.index),covariance=cov,**parts),True)
 pd.DataFrame([dict(term=name,**effect(np.asarray(m.params),cov,index=i)) for i,name in enumerate(m.params.index)]).to_csv(E/'j1_model_coefficients.csv',index=False)
 boot=bootstrap(d,p,'j1',20260930)
 result.update(panel_sha256=PH,protocol_sha256=sha(E/'analysis_protocol.json'),bootstrap=boot,frozen_at=now(),software=read(E/'environment.json'),code_hashes=p['frozen_code'],primary=True)
 save('primary_result.json',result,True)
 save('primary_freeze_receipt.json',dict(frozen_at=result['frozen_at'],sha256=sha(E/'primary_result.json')),True)
 print('PRIMARY FROZEN',json.dumps(clean(result)),flush=True)

def sensitivities():
 p=authorize(True);assert not (E/'sensitivities_start.json').exists()
 save('sensitivities_start.json',dict(started_at=now(),primary_sha256=sha(E/'primary_result.json'),protocol_sha256=sha(E/'analysis_protocol.json')),True)
 d=load();positive=d[d.fta>0];m,x,drop=glm(design(positive,p),positive.ftm,positive.fta)
 fit=fit_bb(x,positive.ftm,positive.fta,np.asarray(m.params),maxiter=3000)
 bb=dict(beta=float(fit['beta'][1]),odds_ratio=float(np.exp(fit['beta'][1])),kappa=fit['kappa'],rho=fit['rho'],attempts=fit['attempts'],min_information_eigenvalue=fit['min_information_eigenvalue'],hessian_step_relative_difference=fit['hessian_step_relative_difference'],dropped_columns=drop,primary=False,method='Unchanged Stage 2 fixed-effect beta-binomial',**counts(d))
 boot=bootstrap(d,p,'j2',20260931,True);bb.update(bootstrap=boot,ci_low=boot['percentile_CI'][0],ci_high=boot['percentile_CI'][1],finished_at=now());save('j2_beta_binomial_result.json',bb,True)
 first=d.sort_values(['player_id','season'],kind='stable').drop_duplicates('player_id',keep='first')
 first[['player_id','season','fta']].to_csv(E/'j3_selected_first_seasons.csv',index=False)
 r,*_=estimate(first,p,hc1=True);save('j3_first_season_result.json',r,True)
 r,*_=estimate(d,p,balanced=True);save('j4_player_balanced_result.json',r,True)
 out=[]
 for season in p['seasons']:
  r,*_=estimate(d[d.season!=season],p);out.append(dict(omitted_season=season,**r))
 pd.DataFrame(out).drop(columns=['covariance_validation']).to_csv(E/'j5_leave_one_season_out.csv',index=False)
 out=[]
 for threshold in p['sensitivities']['J6']:
  r,*_=estimate(d[d.fta>=threshold],p);out.append(dict(threshold=threshold,**r))
 pd.DataFrame(out).drop(columns=['covariance_validation']).to_csv(E/'j6_fta_thresholds.csv',index=False)
 out=[]
 for exposure in p['sensitivities']['alternate_exposures']:
  r,m,cov,_=estimate(d,p,exposure=exposure)
  if exposure=='wingspan_ratio':r['per_001']=effect(np.asarray(m.params),cov,scale=.01)
  out.append(r)
 pd.DataFrame(out).drop(columns=['covariance_validation']).to_csv(E/'alternate_exposures.csv',index=False)
 save('alternate_exposures_detail.json',out,True)
 authorize(True);save('full_panel_start.json',dict(started_at=now(),primary_sha256=sha(E/'primary_result.json')),True)
 r,*_=estimate(load(True),p,full=True);r.update(panel_sha256=FH,independent_replication=False,development_season_included=True);save('full_panel_secondary_result.json',r,True)
 diagnostics(d,p)
 print('All predeclared sensitivities completed',flush=True)

def diagnostics(d,p):
 result,m,*_=estimate(d,p);z=d[d.fta>0].copy();z['fitted_makes']=z.fta*np.asarray(m.fittedvalues)
 def row(q,label):return dict(group=label,player_seasons=len(q),FTA=int(q.fta.sum()),FTM=int(q.ftm.sum()),observed_rate=float(q.ftm.sum()/q.fta.sum()),fitted_rate=float(q.fitted_makes.sum()/q.fta.sum()),observed_minus_fitted=float((q.ftm.sum()-q.fitted_makes.sum())/q.fta.sum()))
 rows=[row(z[(z.fta>=lo)&(True if hi is None else z.fta<=hi)],name) for lo,hi,name in BINS]
 pd.DataFrame(rows).to_csv(E/'residual_diagnostics_by_fta_bin.csv',index=False)
 pd.DataFrame([row(q,s) for s,q in z.groupby('season')]).to_csv(E/'residual_diagnostics_by_season.csv',index=False)
 save('residual_diagnostics_overall.json',dict(**row(z,'overall'),min_fitted_probability=float(m.fittedvalues.min()),max_fitted_probability=float(m.fittedvalues.max()),fitted_below_001=int((m.fittedvalues<.01).sum()),fitted_above_099=int((m.fittedvalues>.99).sum()),descriptive_only=True),True)
 shutil.copyfile(ROOT/'docs/stage3_evidence/selection_coverage_by_season.csv',E/'selection_coverage_by_season.csv')
 unique=d.drop_duplicates('player_id');unique[['height_wo_shoes_inches','wingspan_inches','residual_wingspan']].describe().T.to_csv(E/'sample_anthropometrics_unique_players.csv')
 pd.DataFrame([dict(panel='primary',**counts(d)),dict(panel='full_secondary',**counts(load(True)))]).to_csv(E/'sample_characteristics.csv',index=False)

def replay():
 p=authorize(True);d=load();x=design(d,p);layout=player_layout(d);result={}
 for tag,seed,bb in [('j1',20260930,False),('j2',20260931,True)]:
  original=pd.read_csv(E/(tag+'_player_bootstrap.csv'));rng=np.random.default_rng(seed);errors=[]
  for i in range(3):
   r=bootstrap_once(d,x,layout,rng,bb);assert original.iloc[i].status=='PASS'
   assert r['sample_sha256']==original.iloc[i].sample_sha256
   error=abs(r['beta']-original.iloc[i].beta);assert error<1e-10;errors.append(error)
  result[tag]=dict(first_N=3,max_beta_difference=max(errors),sample_hashes_equal=True)
 save('bootstrap_reproduction.json',dict(passed=True,checked_at=now(),**result),True)
 print('Bootstrap first-three replay PASS',flush=True)
if __name__=='__main__':
 {'primary':primary,'sensitivities':sensitivities,'replay':replay}[sys.argv[1]]()
