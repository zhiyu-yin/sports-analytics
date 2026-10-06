"""Only adequacy predictions and whitelisted latent parameter plots."""
from stage3i_common import *
import matplotlib;matplotlib.use('Agg')
import matplotlib.pyplot as plt
import arviz as az

def ppc(candidate):
 key=candidate.lower();a=read(E/(key+'_conditional_accuracy_ppc.json'));o=read(E/(key+'_joint_opportunity_ppc.json'))
 fig,ax=plt.subplots(figsize=(8,4));b=a['bin_checks'];x=np.arange(5)
 means=np.array([r['replicated_mean'] for r in b])*100;lo=np.array([r['predictive_99_low'] for r in b])*100;hi=np.array([r['predictive_99_high'] for r in b])*100
 ax.errorbar(x,means,yerr=[means-lo,hi-means],fmt='o',capsize=4,label='Replicated mean / 99% interval');ax.plot(x,[r['observed']*100 for r in b],'kx',label='Observed');ax.set_xticks(x,[v[2] for v in BINS]);ax.set_xlabel('Observed FTA bin');ax.set_ylabel('Pooled FT%');ax.legend();ax.set_title(candidate+' conditional accuracy PPC');fig.tight_layout();fig.savefig(F/(key+'_accuracy_PPC.png'),dpi=140);plt.close(fig)
 fig,axes=plt.subplots(1,2,figsize=(10,4))
 for ax,rows,title,scale in [(axes[0],[o['zero_frequency']],'Zero-FTA fraction (%)',100),(axes[1],o['positive_quantiles'],'Positive FTA quartiles',1)]:
  xx=np.arange(len(rows));m=np.array([r['replicated_mean'] for r in rows])*scale;l=np.array([r['predictive_99_low'] for r in rows])*scale;h=np.array([r['predictive_99_high'] for r in rows])*scale
  ax.errorbar(xx,m,yerr=[m-l,h-m],fmt='o',capsize=5);ax.scatter(xx,[r['observed']*scale for r in rows],marker='x',color='black');ax.set_xticks(xx,['Zero'] if len(rows)==1 else ['Q25','Q50','Q75']);ax.set_title(title)
 fig.suptitle(candidate+' joint PPC: dots=replicated, crosses=observed, bars=99%');fig.tight_layout();fig.savefig(F/(key+'_joint_PPC.png'),dpi=140);plt.close(fig)

def final():
 read(E/'stage3i_decision.json')
 valid=[c for c in ['I1','I2','I3'] if read(E/(c.lower()+'_diagnostics.json')).get('sampler_pass')]
 for filename,candidates,suffix,field,labels,scale,ylabel in [
  ('01_accuracy_comparison',['I0']+[c for c in ['I1','I3'] if c in valid],'conditional_accuracy_ppc','bin_checks',[v[2] for v in BINS],100,'Pooled FT%'),
  ('02_positive_FTA_distribution',['I0']+[c for c in ['I2','I3'] if c in valid],'joint_opportunity_ppc','positive_quantiles',['Q25','Q50','Q75'],1,'Positive FTA')]:
  fig,ax=plt.subplots(figsize=(9,4))
  for j,c in enumerate(candidates):
   rows=read(E/(c.lower()+'_'+suffix+'.json'))[field];x=np.arange(len(rows))+.16*(j-(len(candidates)-1)/2)
   m=np.array([r['replicated_mean'] for r in rows])*scale;l=np.array([r['predictive_99_low'] for r in rows])*scale;h=np.array([r['predictive_99_high'] for r in rows])*scale
   ax.errorbar(x,m,yerr=[m-l,h-m],fmt='o',capsize=3,label='H2 (saved)' if c=='I0' else c)
  ax.scatter(np.arange(len(rows)),[r['observed']*scale for r in rows],marker='x',color='black',label='Observed');ax.set_xticks(np.arange(len(rows)),labels);ax.set_ylabel(ylabel);ax.set_title('Frozen PPC comparison: means and 99% predictive intervals');ax.legend();fig.tight_layout();
  omitted=[c for c in (['I1','I3'] if field=='bin_checks' else ['I2','I3']) if c not in valid]
  if omitted:
   fig.subplots_adjust(bottom=.21);fig.text(.5,.025,', '.join(omitted)+' PPC withheld: failed sampler gate',ha='center',fontsize=10)
  fig.savefig(F/(filename+'.png'),dpi=140);plt.close(fig)
 fig,axes=plt.subplots(1,2,figsize=(10,3.5))
 for ax,n in zip(axes,['gamma_W1','gamma_W2']):
  cs=[c for c in ['I1','I3'] if c in valid]
  for j,c in enumerate(cs):
   r=read(E/(c.lower()+'_within_parameters.json'))[n];lo,hi=r['CI95'];ax.errorbar(r['mean'],j,xerr=[[r['mean']-lo],[hi-r['mean']]],fmt='o',capsize=4)
  ax.axvline(0,color='gray',ls=':');ax.set_yticks(range(len(cs)),cs);ax.set_title(n);ax.set_xlabel('Posterior mean and 95% CrI');ax.xaxis.set_major_locator(plt.MaxNLocator(5))
  if not cs:ax.text(.5,.5,'Withheld: no valid sampler',transform=ax.transAxes,ha='center')
 fig.suptitle('Within-opportunity adequacy terms; no causal interpretation');fig.tight_layout(rect=[0,.08,1,1]);
 if 'I3' not in valid:fig.text(.5,.01,'I3 summaries withheld: failed sampler gate',ha='center',fontsize=10)
 fig.savefig(F/'03_within_parameters.png',dpi=140);plt.close(fig)
 fig,ax=plt.subplots(figsize=(7,3.5));cs=[c for c in ['I2','I3'] if c in valid]
 for c in cs:
  d=read(E/(c.lower()+'_diagnostics.json'));trace=az.from_netcdf(M/f"{c.lower()}_attempt{d['attempt']}_trace.nc");ax.hist(trace.posterior.sigma_count_resid.values.ravel(),bins=45,density=True,histtype='step',label=c);trace.close()
 if cs:ax.legend()
 else:ax.axis('off');ax.text(.5,.5,'I2 and I3 posterior withheld: failed sampler gates',transform=ax.transAxes,ha='center')
 ax.set_xlabel('sigma_count_resid');ax.set_ylabel('Posterior density');ax.set_title('Unobserved count-specific player residual scale');fig.tight_layout();fig.savefig(F/'04_count_residual.png',dpi=140);plt.close(fig)
if __name__=='__main__':
 import sys
 ppc(sys.argv[1]) if len(sys.argv)>1 else final()
