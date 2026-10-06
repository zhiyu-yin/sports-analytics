"""Stage 3J estimation primitives. No historical posterior is read."""
import hashlib,json,platform,sys,warnings
from pathlib import Path
from datetime import datetime,timezone
import numpy as np,pandas as pd,statsmodels.api as sm
from scipy.stats import norm
from statsmodels.stats.sandwich_covariance import cov_cluster
from stage2_models import fit_bb,effect
ROOT=Path(__file__).resolve().parents[1]
E=ROOT/'docs/stage3j_evidence';F=ROOT/'docs/stage3j_figures'
PANEL=ROOT/'data/processed/stage3_primary_replication_panel.parquet'
FULL=ROOT/'data/processed/stage3_multiseason_ft_panel.parquet'
PH='1c34331385e459ac5da67105658730d31d96c8114bd25fcb3b31cea52f1a1871'
FH='5306ffd228fb71b34b174d18cf86e351b6fa48598579e4f49935078239662978'
FORMULA='1 + residual_wingspan + height_wo_shoes_inches + C(original_combine_position) + C(season)'
BINS=[(1,9,'1-9'),(10,49,'10-49'),(50,99,'50-99'),(100,299,'100-299'),(300,None,'300+')]
def now():return datetime.now(timezone.utc).isoformat()
def sha(p):
 h=hashlib.sha256()
 with open(p,'rb') as f:
  for b in iter(lambda:f.read(8*1024*1024),b''):h.update(b)
 return h.hexdigest()
def read(p):return json.loads(Path(p).read_text())
def clean(v):
 if isinstance(v,dict):return {str(k):clean(x) for k,x in v.items()}
 if isinstance(v,(list,tuple,np.ndarray)):return [clean(x) for x in v]
 if isinstance(v,np.generic):return v.item()
 return v

def save(name,v,immutable=False):
 E.mkdir(exist_ok=True);p=E/name
 with p.open('x' if immutable else 'w') as f:json.dump(clean(v),f,indent=2,allow_nan=False);f.write('\n')
def load(full=False):
 p=FULL if full else PANEL;assert sha(p)==(FH if full else PH)
 return pd.read_parquet(p).reset_index(drop=True)
def counts(d):return dict(player_seasons=len(d),players=int(d.player_id.nunique()),seasons=int(d.season.nunique()),positive_FTA_rows=int((d.fta>0).sum()),zero_FTA_rows=int((d.fta==0).sum()),contributing_players=int(d.loc[d.fta>0,'player_id'].nunique()),FTA=int(d.fta.sum()),FTM=int(d.ftm.sum()))
def positions(d):return d.combine_position.fillna('unknown').astype(str).str.strip().replace('','unknown')
def design(d,p,exposure='residual_wingspan',full=False):
 out={'Intercept':np.ones(len(d)),exposure:d[exposure].to_numpy(float),'height_wo_shoes_inches':d.height_wo_shoes_inches.to_numpy(float)}
 pos=positions(d)
 for x in p['positions'][1:]:out['position:'+x]=(pos==x).to_numpy(float)
 for x in (p['full_seasons'] if full else p['seasons'])[1:]:out['season:'+x]=(d.season==x).to_numpy(float)
 return pd.DataFrame(out,index=d.index)
def independent_columns(x):
 """Greedy ordered basis, retaining intercept/exposure/height first; no pooling."""
 a=np.asarray(x,float);q=[];keep=[]
 for j in range(a.shape[1]):
  v=a[:,j].copy();scale=np.linalg.norm(v)
  if scale==0:continue
  v/=scale
  for _ in range(2):
   for u in q:v-=u*np.dot(u,v)
  size=np.linalg.norm(v)
  if size>1e-10:q.append(v/size);keep.append(j)
 assert keep[:3]==[0,1,2], 'Exposure or height is not identified'
 return x.iloc[:,keep], [str(x.columns[j]) for j in range(a.shape[1]) if j not in keep]
def glm(x,y,n,weights=None):
 y=np.asarray(y,float);n=np.asarray(n,float)
 assert ((n>0)&(y>=0)&(y<=n)&(y%1==0)&(n%1==0)).all()
 x,dropped=independent_columns(x)
 with warnings.catch_warnings(record=True) as ws:
  m=sm.GLM(np.column_stack([y,n-y]),x,family=sm.families.Binomial(),freq_weights=weights).fit(method='IRLS',maxiter=200,tol=1e-10,atol=1e-10,rtol=0)
 if not m.converged or not np.isfinite(m.params).all():raise RuntimeError('GLM did not converge')
 if any('separation' in str(w.message).lower() for w in ws):raise RuntimeError('GLM separation warning')
 score=np.asarray(m.model.score(m.params));scaled=float(np.max(np.abs(score)/(1+np.sqrt(np.sum(np.asarray(x)**2,axis=0)))))
 if scaled>1e-5:raise RuntimeError('GLM score check failed')
 return m,x,dropped

def sandwich(m,y,n,groups,weights=None,hc1=False):
 x=np.asarray(m.model.exog);p=np.asarray(m.fittedvalues);w=np.ones(len(x)) if weights is None else np.asarray(weights)
 scores=x*(w*(np.asarray(y)-np.asarray(n)*p))[:,None]
 bread=np.linalg.inv(x.T@((w*np.asarray(n)*p*(1-p))[:,None]*x))
 ids,idx=np.unique(groups,return_inverse=True);summed=np.zeros((len(ids),x.shape[1]));np.add.at(summed,idx,scores)
 meat=summed.T@summed;N,K=x.shape;G=len(ids)
 correction=N/(N-K) if hc1 else G/(G-1)*(N-1)/(N-K)
 covariance=correction*bread@meat@bread
 return covariance,dict(N=N,K=K,G=G,correction=correction,method='HC1' if hc1 else 'CR1',bread=bread,meat=meat,cluster_scores=summed)
def validate_cov(m,y,n,groups,weights=None):
 independent,parts=sandwich(m,y,n,groups,weights)
 reference=cov_cluster(m,np.asarray(groups),use_correction=True)
 np.testing.assert_allclose(independent,reference,rtol=2e-6,atol=1e-9)
 uncorrected=cov_cluster(m,np.asarray(groups),use_correction=False)
 np.testing.assert_allclose(reference,uncorrected*parts['correction'],rtol=1e-10,atol=1e-10)
 _,idx=np.unique(groups,return_inverse=True);permuted=np.max(idx)-idx
 ordered=cov_cluster(m,permuted,use_correction=True)
 np.testing.assert_allclose(reference,ordered,rtol=1e-9,atol=1e-9)
 return independent,parts,dict(passed=True,max_absolute_error=float(np.max(np.abs(independent-reference))),relative_frobenius_error=float(np.linalg.norm(independent-reference)/np.linalg.norm(reference)),cluster_order_invariant=True,finite_sample_correction_verified=True,N=parts['N'],K=parts['K'],G=parts['G'],correction=parts['correction'])
def estimate(d,p,exposure='residual_wingspan',full=False,balanced=False,hc1=False):
 positive=d[d.fta>0];x=design(positive,p,exposure,full)
 w=1/positive.player_id.map(d.groupby('player_id').size()).to_numpy(float) if balanced else None
 m,x,dropped=glm(x,positive.ftm,positive.fta,w)
 if hc1:
  cov,parts=sandwich(m,positive.ftm,positive.fta,np.arange(len(positive)),hc1=True);validation={'passed':True,'method':'independent HC1'}
 else:cov,parts,validation=validate_cov(m,positive.ftm,positive.fta,positive.player_id.to_numpy(),w)
 result=dict(**counts(d),**effect(np.asarray(m.params),cov),method='grouped-binomial GLM',uncertainty='HC1' if hc1 else 'player-cluster CR1',dropped_nonidentifiable_columns=dropped,converged=True,started_or_finished_at=now(),exposure=exposure,exposure_unit='1 ratio unit' if exposure=='wingspan_ratio' else 'inch',covariance_validation=validation)
 return result,m,cov,parts

def player_layout(d):
 ids=sorted(d.player_id.unique(),key=int)
 return ids,[np.flatnonzero(d.player_id.to_numpy()==g) for g in ids]
def draw_clusters(layout,rng):
 ids,rows=layout;draws=rng.integers(0,len(ids),size=len(ids));selected=np.concatenate([rows[g] for g in draws]);instances=np.concatenate([np.full(len(rows[g]),j,dtype=int) for j,g in enumerate(draws)])
 return selected,instances,draws

def bootstrap_once(d,x,layout,rng,bb=False):
 rows,instances,draws=draw_clusters(layout,rng);positive=d.fta.to_numpy()[rows]>0;r=rows[positive]
 xb=x.iloc[r].reset_index(drop=True);y=d.ftm.to_numpy()[r];n=d.fta.to_numpy()[r]
 m,xx,dropped=glm(xb,y,n)
 fit=fit_bb(xx,y,n,np.asarray(m.params),maxiter=3000) if bb else None
 beta=float(fit['beta'][1] if bb else m.params.iloc[1])
 return dict(beta=beta,draws=len(draws),unique_sampled_players=len(np.unique(draws)),accounting_rows=len(rows),positive_rows=len(r),contributing_cluster_instances=len(np.unique(instances[positive])),sample_sha256=hashlib.sha256(draws.astype('<i8').tobytes()).hexdigest(),dropped_columns='|'.join(dropped))
def boot_summary(frame,seed):
 v=frame.loc[frame.status=='PASS','beta'].to_numpy(float);failed=int((frame.status!='PASS').sum())
 return dict(replicates=len(frame),successful=len(v),failed=failed,seed=seed,RNG='numpy.default_rng PCG64',mean=float(v.mean()),SD=float(v.std(ddof=1)),percentile_CI=np.quantile(v,[.025,.975],method='linear').tolist(),fraction_beta_negative=float((v<0).mean()),percentile_method='linear',no_failed_replicate_replacement=True,valid_for_interpretation=failed<=20)
def bootstrap(d,p,tag,seed,bb=False):
 path=E/(tag+'_player_bootstrap.csv');assert not path.exists(),'Refuse silent rerun/replacement'
 x=design(d,p);layout=player_layout(d);rng=np.random.default_rng(seed);out=[]
 for i in range(2000):
  try:row=dict(replicate=i+1,status='PASS',error='',**bootstrap_once(d,x,layout,rng,bb))
  except Exception as e:row=dict(replicate=i+1,status='FAIL',error=repr(e),beta=np.nan)
  out.append(row)
  pd.DataFrame([row]).reindex(columns=['replicate','status','error','beta','draws','unique_sampled_players','accounting_rows','positive_rows','contributing_cluster_instances','sample_sha256','dropped_columns']).to_csv(path,mode='w' if i==0 else 'a',header=i==0,index=False)
  if (i+1)%50==0:print(tag,'bootstrap',i+1,'/ 2000; failures',sum(v['status']=='FAIL' for v in out),flush=True)
 frame=pd.DataFrame(out);s=boot_summary(frame,seed);save(tag+'_bootstrap_summary.json',s,True)
 if s['failed']>20:raise RuntimeError('More than 1% bootstrap failures; STOP before interpretation')
 return s

def protocol():
 p=read(E/'analysis_protocol.json');assert sha(E/'analysis_protocol.json')==read(E/'freeze_receipt.json')['protocol_sha256']
 for name,h in p['frozen_code'].items():assert sha(ROOT/name)==h,name
 return p
def authorize(sensitivity=False):
 p=protocol();assert read(E/'implementation_test_summary.json')['passed']
 if sensitivity:
  assert sha(E/'primary_result.json')==read(E/'primary_freeze_receipt.json')['sha256']
 return p
