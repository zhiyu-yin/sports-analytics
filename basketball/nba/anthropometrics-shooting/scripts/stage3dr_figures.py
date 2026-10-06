"""Adequacy-only figures; no scientific-effect access."""
import pandas as pd,arviz as az
import matplotlib;matplotlib.use('Agg')
import matplotlib.pyplot as plt
from stage3dr_common import *
def comparison():
 fig,axes=plt.subplots(2,2,figsize=(10,7))
 for ax,key in zip(axes.ravel(),['D0','D1','D2','D3']):
  ax.set_title(key)
  if key=='D0':
   d=pd.read_csv(ROOT/'docs/stage3c_evidence/primary_PPC_metrics.csv');label='Saved D0: 1,000 replicates'
  else:
   path=E/(key.lower()+'_conditional_PPC_metrics.csv')
   if not path.exists():ax.text(.5,.5,'No valid PPC assessment',ha='center',transform=ax.transAxes);continue
   d=pd.read_csv(path);label='2,000 replicates'
  d=d.set_index('metric').loc[['FTA_'+b[2]+'_pooled' for b in BINS]];m=d.replicated_mean.to_numpy()*100;lo=d.predictive_99_low.to_numpy()*100;hi=d.predictive_99_high.to_numpy()*100;x=np.arange(5)
  ax.errorbar(x,m,yerr=[m-lo,hi-m],fmt='o',capsize=3,color='#52758c',label='Predictive mean / 99%');ax.scatter(x,d.observed*100,marker='x',color='#9c4235',label='Observed');ax.set_xticks(x,[b[2] for b in BINS]);ax.set_ylabel('Pooled FT accuracy (%)');ax.set_xlabel(label);ax.legend(fontsize=7)
 fig.tight_layout();fig.savefig(F/'01_FTA_bin_accuracy.png',dpi=150);plt.close(fig)
def d3_figures(attempt):
 path=E/'d3_joint_PPC_metrics.csv'
 if path.exists():
  d=pd.read_csv(path).set_index('metric');fig,axes=plt.subplots(1,2,figsize=(10,4))
  for ax,keys,title in [(axes[0],['FTA_q'+str(q) for q in [25,50,75,90,95]],'Season FTA distribution quantiles'),(axes[1],[k for k in d.index if k.startswith('season_') and k.endswith('_total')],'Season totals')]:
   v=d.loc[keys];x=np.arange(len(v));ax.errorbar(x,v.replicated_mean,yerr=[v.replicated_mean-v.predictive_99_low,v.predictive_99_high-v.replicated_mean],fmt='o',capsize=3);ax.scatter(x,v.observed,marker='x',color='#9c4235');ax.set_xticks(x,[k.replace('FTA_','').replace('season_','').replace('_total','') for k in keys],rotation=45);ax.set_title(title+'; 99% predictive intervals')
  fig.tight_layout();fig.savefig(F/'02_D3_joint_FTA_PPC.png',dpi=150);plt.close(fig)
 path=E/'d3_conditional_PPC_metrics.csv'
 if path.exists():
  d=pd.read_csv(path).set_index('metric');keys=['pooled_rate']+protocol()['PPC']['global_metrics']+['mean_within_player_rate_SD'];fig,axes=plt.subplots(3,3,figsize=(10,8))
  for ax,key in zip(axes.ravel(),keys):
   r=d.loc[key];ax.errorbar([0],[r.replicated_mean],yerr=[[r.replicated_mean-r.predictive_99_low],[r.predictive_99_high-r.replicated_mean]],fmt='o',capsize=5);ax.axhline(r.observed,color='#9c4235',lw=1.5);ax.set_title(key.replace('_',' '),fontsize=9);ax.set_xticks([])
  fig.suptitle('D3 conditional accuracy: red observed; 99% predictive intervals');fig.tight_layout();fig.savefig(F/'03_D3_conditional_accuracy.png',dpi=150);plt.close(fig)
 if read(E/'d3_diagnostics.json').get('sampler_pass'):
  post=az.from_netcdf(M/f'd3_attempt{attempt}_trace.nc').posterior;corr=post.corr_uv.values.ravel();fig,ax=plt.subplots(figsize=(6,4));ax.hist(corr,bins=40,density=True,color='#52758c');ax.axvline(0,color='black',lw=1);ax.set(xlabel='Latent opportunity–accuracy correlation',ylabel='Posterior density',title='D3 correlated player propensities');fig.tight_layout();fig.savefig(F/'04_D3_corr_uv.png',dpi=150);plt.close(fig)
if __name__=='__main__':
 comparison();d3_figures(read(E/'d3_diagnostics.json')['attempt'])
