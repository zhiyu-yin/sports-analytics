"""Binary probability metrics with explicit temporal guard and no NaN dropping."""
import numpy as np
import pandas as pd
from .policy import require_open
EPSILON=1e-15

def checked(frame,column):
    require_open(frame['season'].unique())
    if frame.empty:raise ValueError('Empty evaluation')
    if frame[['home_win',column]].isna().any().any():raise ValueError('Missing outcome/probability')
    y=frame.home_win.to_numpy(dtype=float);p=frame[column].to_numpy(dtype=float)
    if not np.isfinite(y).all() or not np.isfinite(p).all():raise ValueError('Nonfinite outcome/probability')
    if not np.isin(y,[0,1]).all() or not ((p>=0)&(p<=1)).all():raise ValueError('Invalid outcome/probability')
    return y,p

def evaluate(frame,column):
    from .sealed_access import no_model_execution
    no_model_execution()
    y,p=checked(frame,column);q=np.clip(p,EPSILON,1-EPSILON)
    npos=int(y.sum());nneg=len(y)-npos
    # Mann–Whitney rank statistic; average ranks assign half credit to ties.
    auc=None if npos==0 or nneg==0 else float((pd.Series(p).rank(method='average').to_numpy()[y==1].sum()-npos*(npos+1)/2)/(npos*nneg))
    return dict(n_games=len(y),log_loss=float(-(y*np.log(q)+(1-y)*np.log1p(-q)).mean()),brier_score=float(np.mean((p-y)**2)),accuracy=float(np.mean((p>=0.5)==y)),roc_auc=auc,roc_auc_defined=auc is not None)

def calibration(frame,column,equal_frequency=False):
    from .sealed_access import no_model_execution
    no_model_execution()
    y,p=checked(frame,column)
    if equal_frequency:
        labels=np.zeros(len(p),dtype=int) if len(np.unique(p))==1 else pd.qcut(p,q=10,labels=False,duplicates='drop')
        bins=range(int(np.max(labels))+1)
    else:
        edges=np.array([i/10 for i in range(11)]);labels=np.minimum(np.searchsorted(edges,p,side='right')-1,9);bins=range(10)
    records=[]
    for i in bins:
        mask=labels==i;n=int(mask.sum())
        records.append(dict(bin=int(i),lower_bound=float(p[mask].min()) if equal_frequency and n else (None if equal_frequency else i/10),upper_bound=float(p[mask].max()) if equal_frequency and n else (None if equal_frequency else (i+1)/10),count=n,mean_predicted_probability=float(p[mask].mean()) if n else None,observed_home_win_rate=float(y[mask].mean()) if n else None))
    return pd.DataFrame(records)

def calibration_summary(table):
    t=table[table['count']>0]
    return {'fixed_bin_ece':float((t['count']*(t.mean_predicted_probability-t.observed_home_win_rate).abs()).sum()/t['count'].sum()),'populated_bins':len(t),'bins_below_30':int((t['count']<30).sum())}
