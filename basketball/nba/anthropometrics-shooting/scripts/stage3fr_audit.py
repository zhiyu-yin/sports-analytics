"""Outcome-free design audit and explicitly permitted failed-trace geometry."""
import pandas as pd,arviz as az
from scipy.stats import rankdata
from stage3fr_common import *
from stage3d_model import design
import matplotlib;matplotlib.use('Agg')
import matplotlib.pyplot as plt

def main():
 for p in [E,M,F]:p.mkdir(exist_ok=True,parents=True)
 assert not (E/'reparameterization_protocol.json').exists()
 old=read(ROOT/'docs/stage3f_evidence/prior_preservation_manifest.json')
 for sub in ['docs/stage3f_evidence','docs/stage3f_figures','models/stage3f']:
  for f in (ROOT/sub).glob('*'):
   if f.is_file():old[str(f.relative_to(ROOT))]=sha(f)
 for f in list((ROOT/'scripts').glob('*stage3f*.py'))+[ROOT/'tests/test_stage3f.py',ROOT/'docs/stage3f_hurdle_within_between_adequacy.md']:
  if 'stage3fr' not in f.name:old[str(f.relative_to(ROOT))]=sha(f)
 assert all(sha(ROOT/n)==h for n,h in old.items());save('prior_preservation_manifest.json',old)
 assert sha(PANEL)==EXPECTED
 d,ids,idx,xp,xs,rw,height,_=design();b,w,c,u=decomposition(d.fta.to_numpy(),d.games_played.to_numpy(),idx)
 n=np.bincount(idx);variation=np.bincount(idx,weights=w*w)>1e-24
 def desc(x):return dict(n=len(x),mean=float(x.mean()),SD=float(x.std(ddof=1)),quantiles=dict(zip(['min','q01','q05','q25','median','q75','q95','q99','max'],np.quantile(x,[0,.01,.05,.25,.5,.75,.95,.99,1]).tolist())))
 labels=['intercept','residual_wingspan_predictor','height']+['position_'+x for x in original()['positions'] if x!='C']+['season_'+x for x in original()['seasons'] if x!=original()['season_reference']]+['centered_between','within']
 X=np.column_stack([np.ones(len(d)),rw,height,xp,xs,b,w]);sv=np.linalg.svd(X,compute_uv=False);rank=np.linalg.matrix_rank(X)
 std=X[:,1:].std(axis=0,ddof=1);Z=np.column_stack([np.ones(len(d)),(X[:,1:]-X[:,1:].mean(axis=0))/std]);sz=np.linalg.svd(Z,compute_uv=False)
 C=np.corrcoef(X[:,1:],rowvar=False);pairs=sorted([dict(a=labels[i+1],b=labels[j+1],correlation=float(C[i,j])) for i in range(len(C)) for j in range(i)],key=lambda v:abs(v['correlation']),reverse=True)
 pd.DataFrame(C,index=labels[1:],columns=labels[1:]).to_csv(E/'predictor_correlations.csv')
 save('design_identification_audit.json',dict(checked_at=now(),panel_sha256=sha(PANEL),rows=len(d),players=len(ids),FTA=int(d.fta.sum()),centered_between=desc(b),between_unique_players=desc(u-c),within=desc(w),scaling_rule='Sample SD ddof=1 across all 4117 frozen rows for both predictors; no outcomes used',scales=dict(B=float(b.std(ddof=1)),W=float(w.std(ddof=1))),player_season_counts={'1':int((n==1).sum()),'2':int((n==2).sum()),'3-4':int(((n>=3)&(n<=4)).sum()),'5+':int((n>=5).sum())},single_season_within_zero=bool(np.all(w[n[idx]==1]==0)),players_with_actual_within_variation=int(variation.sum()),observations_in_varying_players=int(variation[idx].sum()),observations_with_nonzero_within=int((np.abs(w)>1e-12).sum()),strongest_predictor_correlations=pairs[:15],shooting_outcomes_used=False))
 save('fixed_effect_conditioning.json',dict(columns=labels,shape=list(X.shape),rank=int(rank),singular_values=sv.tolist(),condition_number=float(sv[0]/sv[-1]),standardized_singular_values=sz.tolist(),standardized_condition_number=float(sz[0]/sz[-1]),full_rank=bool(rank==X.shape[1]),no_columns_removed=True,outcome_independent=True))
 fig,ax=plt.subplots(1,2,figsize=(10,4));ax[0].hist(b,bins=35);ax[0].set_title('Centered between opportunity');ax[1].hist(w,bins=35);ax[1].set_title('Within-player opportunity');fig.tight_layout();fig.savefig(F/'03_predictor_distributions.png',dpi=140);plt.close(fig)
 allrows=[];geometries={}
 for attempt in [1,2]:
  trace=az.from_netcdf(ROOT/f'models/stage3f/f2_attempt{attempt}_trace.nc');post=trace.posterior
  sealed=az.summary(trace,var_names=['beta_RW'],kind='diagnostics',round_to='none').iloc[0];sealedpass=gate(sealed.r_hat,sealed.ess_bulk,sealed.ess_tail)
  global_names=['theta_B','theta_W','beta_0','beta_H','beta_position','beta_season','a_0','a_RW','a_H','a_position','a_season','c_0','c_RW','c_H','c_position','c_season','sigma_accuracy','sigma_positive_opportunity','sigma_hurdle','corr_uv','corr_uh','corr_vh','kappa','alpha_FTA']
  s=az.summary(trace,var_names=global_names+['z_player','player_effects'],kind='diagnostics',round_to='none')[['r_hat','ess_bulk','ess_tail']]
  s.insert(0,'parameter',s.index);s.insert(0,'attempt',attempt);allrows.extend(s.to_dict('records'))
  blocks=[]
  for name in global_names+['z_player','player_effects']:
   block=s[s.parameter.str.match('^'+name+r'(\[|$)')];blocks.append(dict(block=name,max_rhat=float(block.r_hat.max()),min_bulk_ESS=float(block.ess_bulk.min()),min_tail_ESS=float(block.ess_tail.min()),elements=len(block)))
  save(f'failed_f2_attempt{attempt}_block_diagnostics.json',dict(blocks=blocks,sealed_parameter_sampler_pass=sealedpass))
  arr=[];names=[]
  for name in global_names:
   a=post[name].values.reshape(4,post.sizes['draw'],-1)
   for j in range(a.shape[-1]):arr.append(a[:,:,j]);names.append(name if a.shape[-1]==1 else f'{name}[{j}]')
  values=np.stack(arr,axis=-1);corr=np.corrcoef(values.reshape(-1,len(names)),rowvar=False)
  pairs=sorted([dict(a=names[i],b=names[j],correlation=float(corr[i,j])) for i in range(len(names)) for j in range(i)],key=lambda v:abs(v['correlation']),reverse=True)
  theta={t:{name:float(corr[names.index(t),j]) for j,name in enumerate(names) if name!=t} for t in ['theta_B','theta_W']}
  # Rank-scale chain separation avoids reporting location or scale of failed estimates.
  rankchains={name:(rankdata(values[:,:,j].ravel()).reshape(4,-1)/(4*post.sizes['draw']+1)).mean(axis=1).tolist() for j,name in enumerate(names)}
  boundary={name:dict(fraction_abs_over_095=float((np.abs(post[name].values)>.95).mean()),fraction_abs_over_099=float((np.abs(post[name].values)>.99).mean())) for name in ['corr_uv','corr_uh','corr_vh']}
  sdhealth={name:dict(fraction_below_005=float((post[name].values<.05).mean()),fraction_above_3=float((post[name].values>3).mean())) for name in ['sigma_accuracy','sigma_positive_opportunity','sigma_hurdle']}
  effects=post.player_effects.values;zs=post.z_player.values;funnel={}
  for j,name in enumerate(['sigma_accuracy','sigma_positive_opportunity','sigma_hurdle']):
   sd=post[name].values.ravel();funnel[name]=dict(corr_log_SD_latent_RMS=float(np.corrcoef(np.log(sd),np.sqrt((effects[:,:,:,j]**2).mean(axis=2)).ravel())[0,1]),corr_log_SD_standard_latent_RMS=float(np.corrcoef(np.log(sd),np.sqrt((zs[:,:,:,j]**2).mean(axis=2)).ravel())[0,1]))
  geometries[str(attempt)]=dict(sealed_parameter_sampler_pass=sealedpass,strongest_permitted_correlations=pairs[:25],theta_correlations=theta,correlation_boundary_mass=boundary,SD_boundary_mass=sdhealth,chain_mean_normalized_ranks=rankchains,funnel_indicators=funnel,interpretation_limit='Failed-chain geometry is descriptive, not a reliable posterior estimate; rank separation is evidence of incomplete mixing, not proof of distinct modes')
  if attempt==2:
   pd.DataFrame(corr,index=names,columns=names).to_csv(E/'permitted_global_correlations.csv');top=sorted(blocks,key=lambda v:v['max_rhat'],reverse=True)[:15]
   fig,ax=plt.subplots(1,2,figsize=(12,6));ax[0].barh([v['block'] for v in top],[v['max_rhat'] for v in top]);ax[0].axvline(1.01,color='red');ax[0].set_title('Failed F2 recovery: R-hat');ax[1].barh([v['block'] for v in top],[v['min_bulk_ESS'] for v in top]);ax[1].axvline(400,color='red');ax[1].set_title('Minimum bulk ESS');fig.tight_layout();fig.savefig(F/'01_failed_convergence.png',dpi=140);plt.close(fig)
   chosen=['theta_B','theta_W','beta_0','beta_H','sigma_accuracy','sigma_positive_opportunity','sigma_hurdle','corr_uv','corr_uh','corr_vh','kappa','alpha_FTA'];ix=[names.index(k) for k in chosen];fig,ax=plt.subplots(figsize=(10,8));im=ax.imshow(corr[np.ix_(ix,ix)],vmin=-1,vmax=1,cmap='coolwarm');ax.set_xticks(range(len(ix)),chosen,rotation=70,ha='right');ax.set_yticks(range(len(ix)),chosen);fig.colorbar(im,ax=ax);ax.set_title('Failed-chain geometry: permitted parameters only');fig.tight_layout();fig.savefig(F/'02_permitted_correlations.png',dpi=140);plt.close(fig)
  trace.close()
 pd.DataFrame(allrows).to_csv(E/'failed_f2_parameter_diagnostics.csv',index=False);save('posterior_geometry_summary.json',dict(checked_at=now(),attempts=geometries,scientific_parameter_locations_scales_and_correlations_exported=False))
 print('Audits complete; historical files',len(old))
if __name__=='__main__':main()
