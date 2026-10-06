"""Required adequacy figures, never scientific exposure plots."""
import pandas as pd
import matplotlib;matplotlib.use('Agg')
import matplotlib.pyplot as plt
from stage3f_common import *
def main():
 fig,axes=plt.subplots(1,3,figsize=(13,4),sharey=True)
 for ax,key in zip(axes,['f0','f1','f2']):
  path=E/(key+'_conditional_PPC_metrics.csv');ax.set_title(key.upper())
  if not path.exists():ax.text(.5,.5,'PPC unavailable',ha='center',transform=ax.transAxes);ax.set_axis_off();continue
  d=pd.read_csv(path).set_index('metric').loc[['FTA_'+b[2]+'_pooled' for b in BINS]];x=np.arange(5);mean=d.replicated_mean.to_numpy()*100
  ax.errorbar(x,mean,yerr=[mean-d.predictive_99_low.to_numpy()*100,d.predictive_99_high.to_numpy()*100-mean],fmt='o',capsize=3,label='Predictive mean / 99%');ax.scatter(x,d.observed*100,marker='x',color='#a94442',label='Observed');ax.set_xticks(x,[b[2] for b in BINS]);ax.set_xlabel('FTA bin');ax.legend(fontsize=7)
 axes[0].set_ylabel('Pooled FT accuracy (%)');fig.tight_layout();fig.savefig(F/'01_accuracy_FTA_bins.png',dpi=150);plt.close(fig)
 fig,axes=plt.subplots(2,3,figsize=(12,7))
 for i,key in enumerate(['f0','f1','f2']):
  path=E/(key+'_joint_PPC_metrics.csv')
  if not path.exists():
   for ax in axes[:,i]:ax.text(.5,.5,'PPC unavailable',ha='center',transform=ax.transAxes);ax.set_axis_off()
   continue
  d=pd.read_csv(path).set_index('metric');r=d.loc['FTA_zero_fraction'];mean=r.replicated_mean*100
  ax=axes[0,i];ax.errorbar([0],[mean],yerr=[[mean-r.predictive_99_low*100],[r.predictive_99_high*100-mean]],fmt='o',capsize=4);ax.axhline(r.observed*100,color='#a94442');ax.set_title(key.upper()+' zero-FTA fraction');ax.set_ylabel('%');ax.set_xticks([])
  ax=axes[1,i];keys=['positive_FTA_q'+str(q) for q in [25,50,75]]
  if not all(k in d.index for k in keys):ax.text(.5,.5,'Not saved for F0',ha='center',transform=ax.transAxes);ax.set_axis_off();continue
  v=d.loc[keys];m=v.replicated_mean.to_numpy();ax.errorbar(np.arange(3),m,yerr=[m-v.predictive_99_low.to_numpy(),v.predictive_99_high.to_numpy()-m],fmt='o',capsize=4);ax.scatter(np.arange(3),v.observed,marker='x',color='#a94442');ax.set_xticks(range(3),['Q25','Q50','Q75']);ax.set_title(key.upper()+' positive FTA quantiles');ax.set_ylabel('FTA')
 fig.suptitle('Observed red; predictive mean and 99% interval');fig.tight_layout();fig.savefig(F/'02_zero_positive_count_PPC.png',dpi=150);plt.close(fig)
 fig,ax=plt.subplots(figsize=(7,4));path=E/'f2_between_within_parameters.json'
 if path.exists() and 'theta_B' in read(path):
  d=read(path);means=[d[k]['mean'] for k in ['theta_B','theta_W']];lo=[d[k]['CI95'][0] for k in ['theta_B','theta_W']];hi=[d[k]['CI95'][1] for k in ['theta_B','theta_W']];ax.errorbar(means,[0,1],xerr=[np.array(means)-lo,np.array(hi)-means],fmt='o',capsize=5);ax.axvline(0,color='gray',ls='--');ax.set_yticks([0,1],['Between player','Within player']);ax.set_xlabel('Accuracy log-odds slope per log1p(FTA/GP) unit');ax.set_title('F2 diagnostic opportunity terms: mean and 95% CrI')
 else:ax.text(.5,.5,'No reportable F2 parameter estimates',ha='center',transform=ax.transAxes);ax.set_axis_off()
 fig.tight_layout();fig.savefig(F/'03_between_within_parameters.png',dpi=150);plt.close(fig)
 fig,axes=plt.subplots(1,2,figsize=(11,5))
 for ax,key in zip(axes,['f1','f2']):
  path=E/(key+'_random_effect_correlations.json')
  if not path.exists() or 'corr_uv' not in read(path):ax.text(.5,.5,'No reportable correlations',ha='center',transform=ax.transAxes);ax.set_axis_off();continue
  d=read(path);arr=np.eye(3);labels=['Accuracy','Positive opportunity','Hurdle']
  for i,j,n in [(0,1,'corr_uv'),(0,2,'corr_uh'),(1,2,'corr_vh')]:arr[i,j]=arr[j,i]=d[n]['mean']
  ax.imshow(arr,vmin=-1,vmax=1,cmap='coolwarm');ax.set_xticks(range(3),labels,rotation=25,ha='right');ax.set_yticks(range(3),labels);ax.set_title(key.upper()+' correlation means / 95% CrI')
  for i in range(3):
   for j in range(3):
    if i==j:label='1.00'
    else:
     n={(0,1):'corr_uv',(0,2):'corr_uh',(1,2):'corr_vh'}[tuple(sorted([i,j]))];v=d[n];label=f"{v['mean']:.2f}\n[{v['CI95'][0]:.2f}, {v['CI95'][1]:.2f}]"
    ax.text(j,i,label,ha='center',va='center',fontsize=9)
 fig.tight_layout();fig.savefig(F/'04_random_effect_correlations.png',dpi=150);plt.close(fig)
if __name__=='__main__':main()
