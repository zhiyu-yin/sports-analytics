"""Stage 3 projected, sealed-season-aware inputs and frozen pregame Elo."""
import json
from pathlib import Path
import numpy as np
import pandas as pd
from .features import GAME_FEATURES
from .policy import TRAIN,VALIDATION,require_open
from .evaluation import verify_inputs,FEATURE_PATH,OUTCOME_PATH,IDENTITY
from .elo import Parameters,replay,INPUT
from .multiseason import digest
FROZEN={'K':20.0,'H':50.0,'alpha':0.5}
MODELS={'basketball_features_logistic':tuple(GAME_FEATURES),'elo_logistic':('elo_logit',),'features_plus_elo_logistic':tuple(GAME_FEATURES)+('elo_logit',)}

def verify_frozen(root):
    root=Path(root)
    for p,h in json.loads((root/'docs/stage3_evidence/protected_before.json').read_text()).items():
        if digest(root/p)!=h:raise ValueError('Protected Stage 1/2 provenance mismatch: '+p)
    spec=json.loads((root/'docs/stage2_evidence/selected_elo_parameters.json').read_text())
    enforce_frozen(spec['parameters'])
    verify_inputs(root)
    return spec

def enforce_frozen(params):
    if params!=FROZEN:raise ValueError('Stage 2 Elo parameters must remain frozen')

def load_modeling_data(root,seasons):
    seasons=tuple(seasons);require_open(seasons) # before provenance or file access
    if len(set(seasons))!=len(seasons):raise ValueError('Repeated season request')
    root=Path(root);verify_frozen(root)
    f=pd.read_parquet(root/FEATURE_PATH,columns=IDENTITY+GAME_FEATURES,filters=[('season','in',list(seasons))])
    y=pd.read_parquet(root/OUTCOME_PATH,columns=['game_id','home_win'],filters=[('season','in',list(seasons))])
    joined=f.merge(y,on='game_id',how='left',validate='one_to_one')
    if len(joined)!=len(y) or joined.home_win.isna().any():raise ValueError('Stage 3 outcome join mismatch')
    return joined.sort_values(['season','game_date','game_id']).reset_index(drop=True)

def add_frozen_elo(data,params=None):
    require_open(data.season.unique());params=FROZEN if params is None else params;enforce_frozen(params)
    a=replay(data[INPUT],Parameters(**params))
    p=a.predicted_home_probability.to_numpy()
    q=np.clip(p,1e-15,1-1e-15)
    extra=a[['game_id']].copy();extra['raw_elo_probability']=p;extra['elo_logit']=np.log(q/(1-q))
    result=data.merge(extra,on='game_id',how='left',validate='one_to_one').sort_values(['season','game_date','game_id']).reset_index(drop=True)
    if result.elo_logit.isna().any():raise ValueError('Missing Elo feature')
    return result

def matrix(data,model):
    require_open(data.season.unique())
    if model not in MODELS:raise ValueError('Unknown model')
    if not data.columns.is_unique:raise ValueError('Duplicate input column')
    x=data.loc[:,list(MODELS[model])].astype(float)
    if np.isinf(x.to_numpy()).any():raise ValueError('Infinite predictor')
    if 'elo_logit' in x and x.elo_logit.isna().any():raise ValueError('Missing Elo feature')
    return x
