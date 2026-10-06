"""Stage 3J-R input protection and exact sample reconstruction."""
from stage3j_core import ROOT,PH,PANEL,sha,read,clean,now,load,design,player_layout,glm
import numpy as np,pandas as pd,json,hashlib
from pathlib import Path
import stage2_models as old
from scipy.special import expit
E=ROOT/'docs/stage3jr_evidence';M=ROOT/'models/stage3jr';J=ROOT/'docs/stage3j_evidence'
def save(name,value,immutable=True):
 E.mkdir(exist_ok=True)
 with (E/name).open('x' if immutable else 'w') as f:json.dump(clean(value),f,indent=2,allow_nan=False);f.write('\n')
def setup():
 E.mkdir(exist_ok=True);M.mkdir(parents=True,exist_ok=True)
 assert not (E/'input_receipt.json').exists()
 preserved=read(J/'prior_preservation_manifest.json')
 for folder in [J,ROOT/'docs/stage3j_figures']:
  for f in folder.glob('*'):
   if f.is_file():preserved[str(f.relative_to(ROOT))]=sha(f)
 for f in list((ROOT/'scripts').glob('stage3j_*.py'))+[ROOT/'tests/test_stage3j.py',ROOT/'docs/stage3j_simplified_multiseason_inference.md']:preserved[str(f.relative_to(ROOT))]=sha(f)
 for f,h in preserved.items():assert sha(ROOT/f)==h,f
 save('prior_preservation_manifest.json',preserved)
 # Existing records store hashes, not full draw vectors. Replay only the exact old stream.
 d=load();layout=player_layout(d);schedule=pd.read_csv(J/'j2_complete_sample_schedule.csv');rng=np.random.default_rng(20260931);draws=[]
 for _,row in schedule.iterrows():
  draw=rng.integers(0,857,857);digest=hashlib.sha256(draw.astype('<i8').tobytes()).hexdigest();assert digest==row.sample_sha256
  indices=np.concatenate([layout[1][g] for g in draw]);assert len(indices)==row.accounting_rows;assert int((d.fta.to_numpy()[indices]>0).sum())==row.positive_rows
  draws.append(draw)
 np.save(M/'frozen_draw_indices.npy',np.array(draws,dtype='<i8'))
 oldrecords=pd.read_csv(J/'j2_player_bootstrap.csv',usecols=['replicate','status','error']);failed=oldrecords.loc[oldrecords.status=='FAIL','replicate'].astype(int).tolist();success=oldrecords.loc[oldrecords.status=='PASS','replicate'].astype(int).to_numpy();comparison=success[np.linspace(0,len(success)-1,100,dtype=int)].tolist()
 assert len(failed)==299 and len(draws)==2000
 save('diagnostic_plan.json',dict(frozen_at=now(),failed_replicates=failed,successful_comparison_replicates=comparison,comparison_rule='100 evenly spaced ascending replicate indices among 1701 old successes, fixed before reference replay',reference='Exact Stage 2 fit_bb unchanged, intercept/scale and starts unchanged; record additional optimizer metadata only',diagnosis_before_remedy=True,scientific_coefficient_distribution_sealed=True))
 save('input_receipt.json',dict(created_at=now(),panel_sha256=sha(PANEL),schedule_sha256=sha(J/'j2_complete_sample_schedule.csv'),draw_vectors_sha256=sha(M/'frozen_draw_indices.npy'),samples=2000,draws_per_sample=857,new_samples_drawn=False,reconstruction='Exact existing PCG64 stream reconstruction from seed 20260931; all 2000 original sample hashes matched before use',primary_result_sha256=sha(J/'primary_result.json'),old_likelihood_sha256=sha(ROOT/'scripts/stage2_models.py'),historical_artifacts=len(preserved)))
 print('Inputs protected; all 2000 old sample hashes verified',flush=True)
def inputs():
 receipt=read(E/'input_receipt.json');assert sha(PANEL)==PH;assert sha(M/'frozen_draw_indices.npy')==receipt['draw_vectors_sha256'];assert sha(ROOT/'scripts/stage2_models.py')==receipt['old_likelihood_sha256']
 d=load();p=read(J/'analysis_protocol.json');return d,design(d,p),player_layout(d),np.load(M/'frozen_draw_indices.npy')
def sample(bundle,rep):
 d,x,layout,draws=bundle;draw=draws[rep-1];rows=np.concatenate([layout[1][g] for g in draw]);r=rows[d.fta.to_numpy()[rows]>0]
 xx=x.iloc[r].reset_index(drop=True);y=d.ftm.to_numpy()[r].astype(float);n=d.fta.to_numpy()[r].astype(float)
 m,xx,dropped=glm(xx,y,n);raw=np.asarray(xx);means=raw.mean(0);scales=raw.std(0);means[0]=0;scales[0]=1;z=(raw-means)/scales
 T=np.diag(1/scales);T[0,:]=-means/scales;T[0,0]=1;initial=np.linalg.solve(T,np.asarray(m.params))
 return dict(x=xx,z=z,y=y,n=n,T=T,initial=initial,dropped=dropped,replicate=rep,sample_sha256=hashlib.sha256(draw.astype('<i8').tobytes()).hexdigest())
def numeric_record(opt,s,k):
 z,y,n=s['z'],s['y'],s['n'];value,grad=old.objective(opt.x,z,y,n);theta=opt.x;H=old.hessian(theta,z,y,n);eigen=np.linalg.eigvalsh(H);mu=expit(z@theta[:-1]);beta=s['T']@theta[:-1]
 return dict(start_kappa=k,optimizer_success=bool(opt.success),optimizer_status=int(opt.status),optimizer_message=str(opt.message),iterations=int(opt.nit),function_evaluations=int(opt.nfev),gradient_evaluations=int(opt.njev),log_likelihood=-float(value),score_max=float(np.max(np.abs(grad))),score_norm=float(np.linalg.norm(grad)),kappa=float(np.exp(theta[-1])),coefficient_norm=float(np.linalg.norm(beta)),scaled_coefficient_norm=float(np.linalg.norm(theta[:-1])),design_rank=int(np.linalg.matrix_rank(z)),raw_condition=float(np.linalg.cond(s['x'])),scaled_condition=float(np.linalg.cond(z)),absent_category=bool(s['dropped']),dropped_columns='|'.join(s['dropped']),minimum_information_eigenvalue=float(eigen.min()),information_condition=float(eigen.max()/eigen.min()),separation_like=bool(mu.min()<1e-8 or mu.max()>1-1e-8 or np.max(np.abs(z@theta[:-1]))>25),boundary=bool(not -9.99<theta[-1]<15.99),nonfinite=bool(not np.isfinite(value) or not np.isfinite(grad).all()),score_gate_pass=bool(np.max(np.abs(grad))<1e-3))
def reference(s):
 collected=[];native=old.minimize
 def capture(*args,**kwargs):
  opt=native(*args,**kwargs);collected.append(opt);return opt
 old.minimize=capture
 try:
  fitted=old.fit_bb(s['x'],s['y'],s['n'],s['T']@s['initial']);status='PASS';error=''
 except Exception as e:fitted=None;status='FAIL';error=repr(e)
 finally:old.minimize=native
 records=[numeric_record(opt,s,k) for opt,k in zip(collected,[10.,50.,200.])]
 np.savez(M/f"reference_{s['replicate']:04d}.npz",theta=np.array([o.x for o in collected]),beta=np.array([]) if fitted is None else fitted['beta'])
 return dict(replicate=s['replicate'],status=status,error=error,sample_sha256=s['sample_sha256'],attempts=records)
if __name__=='__main__':setup()
