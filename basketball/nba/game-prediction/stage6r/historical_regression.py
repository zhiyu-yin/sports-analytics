"""Pre-recovery exact reproduction of already-open historical predictions; no fits."""
import pickle
import numpy as np
import pandas as pd
import support as s
r=s.old

def projected(path,columns):
 expected=s.verify_protected()[str(path.relative_to(s.ROOT))]
 if r.access.checksum(path)!=expected:raise ValueError('Historical input hash mismatch')
 token=r.access._ACTIVE.set(True)
 try:
  with r.access._RAW_OPEN(path,'rb') as f:return pd.read_parquet(f,columns=columns)
 finally:r.access._ACTIVE.reset(token)

def run():
 s.verify_protected();gate=r.verify();session=r.Session(s.E);session.phase='validated';rt=r.runtime(session)
 bundle=pickle.loads((s.ROOT/'docs/stage5_evidence/frozen_estimators.pkl').read_bytes());fits=bundle['fits'];before=r.sha(pickle.dumps(fits,protocol=5))
 cols=r.IDENTITY+r.features.GAME_FEATURES
 f=projected(s.ROOT/'data/processed/seasons/game_features_2024_25.parquet',cols)
 y=projected(s.ROOT/'data/interim/reconciled/game_outcomes_2024_25.parquet',['game_id','home_win'])
 past=f.merge(y,on='game_id',validate='one_to_one');full=pd.concat([bundle['history'],past],ignore_index=True)
 result=[]
 with session.activate(),r.threadpool_limits(limits=1):
  full=rt.modeling_data.add_frozen_elo(full)
  for season,predname,metricname in [('2023-24','stage4_predictions_2023_24.parquet','stage4_evidence/validation_metrics.csv'),('2024-25','stage5_predictions_2024_25.parquet','stage5_evidence/preholdout_metrics.csv')]:
   data=full[full.season.eq(season)].reset_index(drop=True);pred=r.prediction_frame(rt,fits,data,bundle['prior'])
   expected=projected(s.ROOT/'data/processed'/predname,list(pred)).sort_values(['season','game_date','game_id']).reset_index(drop=True)
   for col in list(pred):
    if not np.array_equal(pred[col].to_numpy(),expected[col].to_numpy()):raise ValueError('Historical prediction differs: '+season+' '+col)
   old=pd.read_csv(s.ROOT/'docs'/metricname,float_precision='round_trip').set_index('model')
   for model,column in r.NAMES.items():
    got=rt.metrics.evaluate(pred,column)
    for k,v in got.items():
     if v!=old.loc[model,k]:raise ValueError('Historical metric differs: '+season+' '+model+' '+k)
   result.append(dict(season=season,games=len(pred),seven_prediction_vectors_exact=True,all_metrics_exact=True))
 if r.sha(pickle.dumps(fits,protocol=5))!=before:raise ValueError('Estimator state mutated')
 s.verify_protected()
 proof=dict(passed=True,seasons=result,fit_calls=0,scientific_freeze_exact=True,estimator_state_unchanged=True,final_season_access=False)
 r.durable(s.E/'historical_regression.json',proof);return proof
if __name__=='__main__':print(run())
