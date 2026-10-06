"""Post-diagnostic summaries/PPC; immutable primary freeze precedes secondary fit."""
import argparse
import numpy as np,pandas as pd,arviz as az
from scipy.special import expit
import matplotlib;matplotlib.use('Agg')
import matplotlib.pyplot as plt
from stage3c_model import data,protocol,KEY
from stage3c_setup import *
def summary(x):
 x=np.asarray(x).reshape(-1);return dict(mean=float(x.mean()),median=float(np.median(x)),SD=float(x.std(ddof=1)),CI95=[float(v) for v in np.quantile(x,[.025,.975])])
def flatten(post,name):
 v=post[name].values;return v.reshape((-1,)+v.shape[2:])
def predictive_metrics(y,n,frame):
 rates=y/n;out={'pooled_rate':float(y.sum()/n.sum()),'rate_SD':float(rates.std(ddof=1)),'rate_q05':float(np.quantile(rates,.05)),'rate_q50':float(np.quantile(rates,.5)),'rate_q95':float(np.quantile(rates,.95)),'rate_zero_fraction':float((rates==0).mean()),'rate_one_fraction':float((rates==1).mean())}
 for low,hi,label in [(1,9,'1-9'),(10,49,'10-49'),(50,99,'50-99'),(100,299,'100-299'),(300,np.inf,'300+')]:
  m=(n>=low)&(n<=hi)
  for key,val in [('pooled',y[m].sum()/n[m].sum()),('SD',rates[m].std(ddof=1)),('q05',np.quantile(rates[m],.05)),('q95',np.quantile(rates[m],.95)),('zero_fraction',(rates[m]==0).mean()),('one_fraction',(rates[m]==1).mean())]:out[f'FTA_{label}_{key}']=float(val)
 for season in sorted(frame.season.unique()):
  m=(frame.season==season).to_numpy();out['season_'+season]=float(y[m].sum()/n[m].sum())
 codes=pd.factorize(frame.player_id,sort=True)[0];ny=np.bincount(codes,weights=y);nn=np.bincount(codes,weights=n);out['between_player_pooled_rate_SD']=float((ny/nn).std(ddof=1));num=np.bincount(codes);sr=np.bincount(codes,weights=rates);sr2=np.bincount(codes,weights=rates*rates);m=num>1;within=np.sqrt(np.maximum(0,(sr2[m]-sr[m]*sr[m]/num[m])/(num[m]-1)));out['mean_within_player_rate_SD']=float(within.mean());return out

def analyze(kind,attempt):
 diag=read(E/f'{kind}_attempt{attempt}_diagnostics.json');review=read(E/f'{kind}_attempt{attempt}_visual_review.json');assert diag['numeric_gate_pass'] and review['chains_mix'] and review['energy_acceptable']
 p=protocol();idata=az.from_netcdf(M/f'{kind}_attempt{attempt}_trace.nc');post=idata.posterior;arrays={k:flatten(post,k) for k in KEY+['u_player']};d,y,info,idx,Xp,Xs,rw,h=data(kind);ndraw=len(arrays['beta_RW']);n=y.fta.to_numpy(dtype=int);observed=y.ftm.to_numpy(dtype=int)
 q25,q75=np.quantile(d.residual_wingspan,[.25,.75]);conditional=[[],[]];zero=[[],[]]
 for start in range(0,ndraw,128):
  stop=min(ndraw,start+128);sl=slice(start,stop)
  fixed=arrays['beta_0'][sl,None]+arrays['beta_H'][sl,None]*h+arrays['position_effect'][sl]@Xp.T+arrays['season_effect'][sl]@Xs.T
  random=arrays['u_player'][sl][:,idx]
  for k,q in enumerate([q25,q75]):
   base=fixed+arrays['beta_RW'][sl,None]*q;conditional[k].extend(expit(base+random).mean(axis=1));zero[k].extend(expit(base).mean(axis=1))
 def contrast(v):
  diff=(np.array(v[1])-v[0])*100;return dict(Q25=summary(v[0]),Q75=summary(v[1]),difference_percentage_points=summary(diff),P_difference_negative=float((diff<0).mean()))
 con=dict(Q25_inches=float(q25),Q75_inches=float(q75),quantile_population='all accounting player-seasons in this panel; repeated seasons weight players accordingly',conditional=contrast(conditional),zero_random_effect_reference_player=contrast(zero),interpretation='Adjusted model-based association contrast; equal player-season averaging; zero-random-effect version is not marginalization over a new-player distribution.')
 save(f'{kind}_probability_contrast.json',con)
 fixedrows=[]
 for name in ['beta_0','beta_RW','beta_H']:
  s=summary(arrays[name]);fixedrows.append(dict(parameter=name,mean=s['mean'],median=s['median'],SD=s['SD'],CI_low=s['CI95'][0],CI_high=s['CI95'][1]))
 for j,label in enumerate(info['position_nonreference']):
  s=summary(arrays['position_effect'][:,j]);fixedrows.append(dict(parameter='position_'+label,mean=s['mean'],median=s['median'],SD=s['SD'],CI_low=s['CI95'][0],CI_high=s['CI95'][1]))
 pd.DataFrame(fixedrows).to_csv(E/f'{kind}_fixed_effects.csv',index=False)
 if kind=='full':pd.DataFrame(fixedrows).to_csv(E/'full_panel_fixed_effects.csv',index=False)
 seasonrows=[dict(season=p['season_reference'],mean=0,median=0,SD=0,CI_low=0,CI_high=0,reference=True)]
 for j,label in enumerate(info['season_nonreference']):
  s=summary(arrays['season_effect'][:,j]);seasonrows.append(dict(season=label,mean=s['mean'],median=s['median'],SD=s['SD'],CI_low=s['CI95'][0],CI_high=s['CI95'][1],reference=False))
 pd.DataFrame(seasonrows).sort_values('season').to_csv(E/f'{kind}_season_effects.csv',index=False)
 variance={k:summary(arrays[k]) for k in ['sigma_player','kappa','rho','log_kappa']};variance['probability_scale_at_reference_mu_075']=dict(minus_one_sigma=summary(expit(np.log(3)-arrays['sigma_player'])),plus_one_sigma=summary(expit(np.log(3)+arrays['sigma_player'])),interpretation='Illustrative logit-scale random intercept spread around fixed baseline probability .75, not individual player rankings.')
 save(f'{kind}_variance_components.json',variance)
 rng=np.random.default_rng(20260929);indices=np.linspace(0,ndraw-1,1000,dtype=int);obsmetrics=predictive_metrics(observed,n,y);repmetrics=[];min_alpha=float('inf');min_beta=float('inf')
 for index in indices:
  eta=arrays['beta_0'][index]+arrays['beta_RW'][index]*rw+arrays['beta_H'][index]*h+Xp@arrays['position_effect'][index]+Xs@arrays['season_effect'][index]+arrays['u_player'][index,idx];mu=expit(eta);alpha=mu*arrays['kappa'][index];beta=(1-mu)*arrays['kappa'][index];min_alpha=min(min_alpha,float(alpha.min()));min_beta=min(min_beta,float(beta.min()));prob=rng.beta(alpha,beta);yp=rng.binomial(n,prob);repmetrics.append(predictive_metrics(yp,n,y))
 rows=[]
 for key,value in obsmetrics.items():
  v=np.array([x[key] for x in repmetrics]);lo,hi=np.quantile(v,[.005,.995]);rows.append(dict(metric=key,observed=value,replicated_mean=float(v.mean()),replicated_median=float(np.median(v)),predictive_95_low=float(np.quantile(v,.025)),predictive_95_high=float(np.quantile(v,.975)),predictive_99_low=float(lo),predictive_99_high=float(hi),outside_99=bool(value<lo or value>hi),posterior_predictive_tail_fraction=float((v>=value).mean())))
 pd.DataFrame(rows).to_csv(E/f'{kind}_PPC_metrics.csv',index=False);lookup={x['metric']:x for x in rows};globalkeys=['rate_SD','rate_q05','rate_q50','rate_q95','rate_zero_fraction','rate_one_fraction'];globalfails=sum(lookup[k]['outside_99'] for k in globalkeys);seasonfails=sum(x['outside_99'] for x in rows if x['metric'].startswith('season_'));serious=lookup['pooled_rate']['outside_99'] or globalfails>=3 or seasonfails>=np.ceil(len(info['seasons'])/3)
 ppc=dict(draws=1000,seed=20260929,replicated_makes_summary=summary([v['pooled_rate']*n.sum() for v in repmetrics]),observed_total_FTM=int(observed.sum()),FTA=int(n.sum()),pooled_rate=lookup['pooled_rate'],global_distribution_outside_99=globalfails,season_rates_outside_99=seasonfails,metrics_outside_99=[x['metric'] for x in rows if x['outside_99']],serious_failure_by_frozen_rule=bool(serious),minimum_alpha=min_alpha,minimum_beta=min_beta,visual_review='PENDING',scope='Conditional replication for observed players/attempt denominators, not an out-of-sample validation',metric_table=f'{kind}_PPC_metrics.csv')
 save(f'{kind}_posterior_predictive_summary.json',ppc)
 # Restrained model-check figure, safe to evaluate before narrative interpretation.
 selected=['pooled_rate']+globalkeys+['between_player_pooled_rate_SD','mean_within_player_rate_SD'];fig,axes=plt.subplots(3,3,figsize=(11,8))
 for ax,key in zip(axes.ravel(),selected):
  vals=[v[key] for v in repmetrics];ax.hist(vals,bins=30,color='#6a879b',alpha=.8);ax.axvline(obsmetrics[key],color='#a53b36',lw=1.6);ax.set_title(key.replace('_',' '),fontsize=9)
 fig.suptitle(f'{kind.title()} posterior predictive checks: red = observed');fig.tight_layout();F.mkdir(exist_ok=True);fig.savefig(F/f'{kind}_04_PPC.png',dpi=150);plt.close(fig)
 diag.update(visual_review=review,scientific_summary_released=True);save(f'{kind}_diagnostics.json',diag)
 result=dict(panel_hash=panel(kind)[1]['sha256'],model_protocol_hash=sha(E/'model_protocol.json'),software_environment=read(E/'environment.json'),seed=20260928,sampling=read(E/f'{kind}_attempt{attempt}_sampling.json')['settings'],beta_RW=summary(arrays['beta_RW']),OR_per_residual_inch=summary(np.exp(arrays['beta_RW'])),P_beta_RW_negative=float((arrays['beta_RW']<0).mean()),probability_contrast=con,variance_components=variance,diagnostics=diag,PPC=ppc,model_code_sha256=read(E/f'{kind}_attempt{attempt}_sampling.json')['code_sha256'],summary_code_sha256=sha(Path(__file__)),trace_sha256=sha(M/f'{kind}_attempt{attempt}_trace.nc'),attempt=attempt)
 # Exact replay compares all numerical summaries, excluding a later visual review attachment.
 existing=E/f'{kind}_pending_result.json'
 if existing.exists():
  old=read(existing);comparison=result.copy();comparison['summary_code_sha256']=old['summary_code_sha256']
  assert old==comparison,'Exact saved-trace summary reproduction failed'
  save(f'{kind}_replay_code_record.json',dict(original_code_sha256=old['summary_code_sha256'],replay_code_sha256=result['summary_code_sha256'],exact_all_other_fields=True,reason='Freeze path extended to preserve failed PPC results without granting scientific authorization; original provenance hash retained.'))
 else:save(f'{kind}_pending_result.json',result)
 print(json.dumps(dict(kind=kind,diagnostic_gate=True,PPC_serious_failure=bool(serious),PPC_outside_99=ppc['metrics_outside_99'],scientific_summary='written; primary result awaits PPC review/freeze'),indent=2))

def freeze(kind):
 result=read(E/f'{kind}_pending_result.json');review=read(E/f'{kind}_PPC_visual_review.json');result['PPC']['visual_review']=review
 result['scientifically_reportable']=bool(not result['PPC']['serious_failure_by_frozen_rule'] and review['acceptable'])
 result['scientific_status']='ADEQUATE_UNDER_FROZEN_GATES' if result['scientifically_reportable'] else 'INADEQUATE_PPC_FAILED'
 result['summary_use']='Scientific association summary' if result['scientifically_reportable'] else 'Diagnostic record only; posterior conditional on a model that failed the frozen PPC gate'
 name='primary_replication_result.json' if kind=='primary' else 'full_panel_result.json'
 if (E/name).exists():
  old=read(E/name);result['frozen_at']=old['frozen_at'];assert old==result
 else:result['frozen_at']=now();save(name,result)
 save(f'{kind}_posterior_predictive_summary.json',result['PPC'])
 # Scientific figures generated only after result is frozen.
 idata=az.from_netcdf(M/f"{kind}_attempt{result['attempt']}_trace.nc");br=idata.posterior.beta_RW.values.ravel();fig,ax=plt.subplots(figsize=(6,4));ax.hist(br,bins=50,density=True,color='#4d748c');ax.axvline(0,color='black',lw=1);ax.set(xlabel='Residual-wingspan coefficient (log odds per inch)',ylabel='Posterior density',title=f'{kind.title()} residual-wingspan association');fig.tight_layout();ax.set_title('Diagnostic only: PPC failed\n'+ax.get_title()) if not result['scientifically_reportable'] else None;fig.tight_layout();fig.savefig(F/f'{kind}_01_beta_RW.png',dpi=160);plt.close(fig)
 c=result['probability_contrast']['conditional'];med=[c[k]['median']*100 for k in ['Q25','Q75']];ci=np.array([c[k]['CI95'] for k in ['Q25','Q75']])*100;fig,ax=plt.subplots(figsize=(5,4));ax.errorbar([0,1],med,yerr=[np.array(med)-ci[:,0],ci[:,1]-med],fmt='o',capsize=5,color='#4d748c');ax.set_xticks([0,1],['Q25 residual wingspan','Q75 residual wingspan']);ax.set(ylabel='Adjusted expected FT probability (%)',title='Conditional association contrast');fig.tight_layout();ax.set_title('Diagnostic only: PPC failed\n'+ax.get_title()) if not result['scientifically_reportable'] else None;fig.tight_layout();fig.savefig(F/f'{kind}_02_contrast.png',dpi=160);plt.close(fig)
 s=pd.read_csv(E/f'{kind}_season_effects.csv');fig,ax=plt.subplots(figsize=(8,4));ax.errorbar(range(len(s)),s['median'],yerr=[s['median']-s.CI_low,s.CI_high-s['median']],fmt='o',capsize=3,color='#4d748c');ax.axhline(0,color='gray',lw=.8);ax.set_xticks(range(len(s)),s.season,rotation=45);ax.set(ylabel='Season adjustment (log odds)',title='Season fixed effects; 95% equal-tail intervals');fig.tight_layout();ax.set_title('Diagnostic only: PPC failed\n'+ax.get_title()) if not result['scientifically_reportable'] else None;fig.tight_layout();fig.savefig(F/f'{kind}_03_seasons.png',dpi=160);plt.close(fig)
 print(name,'frozen at',result['frozen_at'])
if __name__=='__main__':
 a=argparse.ArgumentParser();a.add_argument('action',choices=['analyze','freeze']);a.add_argument('--kind',default='primary',choices=['primary','full']);a.add_argument('--attempt',type=int,default=1);args=a.parse_args();analyze(args.kind,args.attempt) if args.action=='analyze' else freeze(args.kind)
