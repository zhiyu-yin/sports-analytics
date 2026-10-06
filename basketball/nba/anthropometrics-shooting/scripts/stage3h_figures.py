"""Only adequacy predictions and whitelisted latent parameter plots."""
from stage3h_common import *
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
 decision=read(E/'stage3h_decision.json');valid=[]
 for c in ['H1','H2']:
  d=E/(c.lower()+'_diagnostics.json')
  if d.exists() and read(d).get('sampler_pass'):valid.append(c)
 if not valid:
  for name,title in [('01_accuracy_comparison','Accuracy PPC unavailable'),('02_opportunity_PPC','Opportunity PPC unavailable'),('03_rho_AO','Latent correlation withheld'),('04_latent_loadings','Latent loadings withheld')]:
   fig,ax=plt.subplots(figsize=(8,3));ax.axis('off');ax.text(.5,.5,title+'\nNo valid shared-factor sampler',ha='center',va='center');fig.savefig(F/(name+'.png'),dpi=120);plt.close(fig)
  return
 fig,ax=plt.subplots(figsize=(9,4));candidates=['F1']+valid
 for j,c in enumerate(candidates):
  source=ROOT/'docs/stage3f_evidence/f1_conditional_accuracy_ppc.json' if c=='F1' else E/(c.lower()+'_conditional_accuracy_ppc.json');rows=read(source)['bin_checks'];x=np.arange(5)+.16*(j-(len(candidates)-1)/2);m=np.array([r['replicated_mean'] for r in rows])*100;l=np.array([r['predictive_99_low'] for r in rows])*100;h=np.array([r['predictive_99_high'] for r in rows])*100
  ax.errorbar(x,m,yerr=[m-l,h-m],fmt='o',capsize=3,label=c)
 ax.scatter(np.arange(5),[r['observed']*100 for r in rows],marker='x',color='black',label='Observed');ax.set_xticks(np.arange(5),[v[2] for v in BINS]);ax.set_ylabel('Pooled FT%');ax.set_xlabel('Observed FTA bin');ax.set_title('Frozen adequacy comparison: 99% predictive intervals');ax.legend();fig.tight_layout();fig.savefig(F/'01_accuracy_comparison.png',dpi=140);plt.close(fig)
 # Candidate-specific opportunity plots are retained; the final panel identifies all assessed candidates.
 fig,axes=plt.subplots(len(valid),2,figsize=(10,4*len(valid)),squeeze=False)
 for row,c in zip(axes,valid):
  o=read(E/(c.lower()+'_joint_opportunity_ppc.json'))
  for ax,rs,title,scale in [(row[0],[o['zero_frequency']],c+' zero-FTA (%)',100),(row[1],o['positive_quantiles'],c+' positive FTA',1)]:
   x=np.arange(len(rs));m=np.array([r['replicated_mean'] for r in rs])*scale;l=np.array([r['predictive_99_low'] for r in rs])*scale;h=np.array([r['predictive_99_high'] for r in rs])*scale;ax.errorbar(x,m,yerr=[m-l,h-m],fmt='o',capsize=4);ax.scatter(x,[r['observed']*scale for r in rs],marker='x',color='black');ax.set_xticks(x,['Zero'] if len(rs)==1 else ['Q25','Q50','Q75']);ax.set_title(title)
 fig.suptitle('Replicated means / 99% intervals; crosses = observed');fig.tight_layout();fig.savefig(F/'02_opportunity_PPC.png',dpi=140);plt.close(fig)
 arrays={}
 for c in valid:
  d=read(E/(c.lower()+'_diagnostics.json'));trace=az.from_netcdf(M/f"{c.lower()}_attempt{d['attempt']}_trace.nc")
  arrays[c]={k:trace.posterior[k].values.ravel().copy() for k in ['rho_AO','lambda_h','sigma_opportunity','sigma_accuracy']+(['theta_W'] if c=='H2' else [])};trace.close()
 for filename,keys in [('03_rho_AO',['rho_AO']),('04_latent_loadings',['lambda_h','sigma_opportunity','sigma_accuracy'])]+([('05_theta_W',['theta_W'])] if 'H2' in arrays else []):
  fig,axes=plt.subplots(1,len(keys),figsize=(5*len(keys),3.5),squeeze=False)
  for ax,k in zip(axes[0],keys):
   for c,values in arrays.items():
    if k in values:ax.hist(values[k],bins=45,density=True,histtype='step',label=c)
   ax.set_title(k);ax.set_ylabel('Posterior density');ax.legend()
  fig.suptitle('Model-adequacy parameters; statistical associations only');fig.tight_layout();fig.savefig(F/(filename+'.png'),dpi=140);plt.close(fig)
if __name__=='__main__':
 import sys
 ppc(sys.argv[1]) if len(sys.argv)>1 else final()
