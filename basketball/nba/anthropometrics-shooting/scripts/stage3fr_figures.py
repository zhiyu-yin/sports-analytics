"""Selected-model figure links and conditional PPC from permitted public artifacts."""
from stage3fr_common import *
import matplotlib;matplotlib.use('Agg')
import matplotlib.pyplot as plt

def main():
 path=E/'f2_conditional_accuracy_ppc.json'
 if path.exists():
  a=read(path);bins=a['bin_checks'];x=np.arange(5);m=np.array([b['replicated_mean']*100 for b in bins]);low=np.array([b['predictive_99_low']*100 for b in bins]);high=np.array([b['predictive_99_high']*100 for b in bins]);obs=[b['observed']*100 for b in bins]
  fig,ax=plt.subplots(figsize=(8,5));ax.errorbar(x,m,yerr=[m-low,high-m],fmt='o',capsize=5,label='Predictive mean and 99% interval');ax.scatter(x,obs,color='#b43a3a',marker='x',s=65,label='Observed');ax.set_xticks(x,['1–9','10–49','50–99','100–299','300+']);ax.set_xlabel('FTA bin');ax.set_ylabel('Pooled FT accuracy (%)');ax.set_title('Equivalent F2: frozen conditional accuracy PPC');ax.legend();fig.tight_layout();fig.savefig(F/'05_F2_accuracy_PPC.png',dpi=150);plt.close(fig)
if __name__=='__main__':main()
