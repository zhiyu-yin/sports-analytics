"""Presentation only: plot frozen aggregate losses; no project model imports."""
from pathlib import Path
import csv
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
R=Path(__file__).resolve().parents[1]
with (R/'docs/stage6r2_evidence/cross_season_confirmation.csv').open() as f:
    rows=list(csv.DictReader(f))
fig,axs=plt.subplots(1,2,figsize=(10,4.2))
for ax,key,title in zip(axs,['log_loss','brier'],['Log loss','Brier score']):
    for prefix,label,color in [('raw_elo','Raw Elo','#52677e'),('model_c','Model C','#087e8b')]:
        ax.plot(range(3),[float(r[f'{prefix}_{key}']) for r in rows],marker='o',linewidth=2,color=color,label=label)
    ax.set_xticks(range(3),['2023–24\nDevelopment','2024–25\nPre-holdout','2025–26\nFinal holdout'])
    ax.set_title(title+' · lower is better',fontsize=12)
    ax.grid(axis='y',alpha=.2); ax.spines[['top','right']].set_visible(False)
    ax.tick_params(axis='x',length=0,pad=8);ax.legend(frameon=False,fontsize=9)
fig.suptitle('NBA Game Prediction V1 · Frozen probability losses',fontsize=15,y=.98)
fig.text(.5,.025,'Separate season roles; final descriptive bootstrap intervals for C − Elo include zero.',ha='center',fontsize=9,color='#444444')
fig.tight_layout(rect=[0,.07,1,.92])
fig.savefig(R/'reports/figures/v1/three_season_comparison.png',dpi=180)
