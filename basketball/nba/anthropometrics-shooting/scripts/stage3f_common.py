"""Stage 3F immutable input and decomposition helpers."""
from stage3d_protocol import ROOT,PANEL,EXPECTED,BINS,now,sha,read,fixed_data
import json,numpy as np
E=ROOT/'docs/stage3f_evidence';M=ROOT/'models/stage3f';F=ROOT/'docs/stage3f_figures'
def save(name,value): (E/name).write_text(json.dumps(value,indent=2,allow_nan=False)+'\n')
def original():return read(ROOT/'docs/stage3d_evidence/model_adequacy_protocol.json')
def protocol():
 p=E/'model_protocol.json';assert sha(p)==read(E/'freeze_receipt.json')['model_protocol_sha256'];return read(p)
def authorize():
 p=protocol();assert read(E/'prior_predictive_summary.json')['passed'],'Prior gate failed'
 for name,h in p['frozen_code'].items():assert sha(ROOT/name)==h,name
 assert sha(PANEL)==EXPECTED

def decomposition(n,gp,idx):
 x=np.log1p(np.asarray(n)/np.asarray(gp));num=np.bincount(idx);between=np.bincount(idx,weights=x)/num;center=float(between.mean())
 return between[idx]-center,x-between[idx],center,between

def summary(x):
 x=np.asarray(x).ravel();return dict(mean=float(x.mean()),median=float(np.median(x)),SD=float(x.std(ddof=1)),CI95=np.quantile(x,[.025,.975]).tolist())
def ztnb_random(mu,alpha,rng):
 from scipy.stats import nbinom
 mu,alpha=np.broadcast_arrays(mu,alpha);p=alpha/(alpha+mu);sf0=-np.expm1(-alpha*np.log1p(mu/alpha));q=np.maximum(rng.random(mu.shape),np.finfo(float).tiny)*sf0
 out=nbinom.isf(q,alpha,p)
 assert np.isfinite(out).all() and (out>=1).all()
 return out.astype('int64')
