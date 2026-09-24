"""Stage 4: fixed native-missing HGB recipes and chronological selection."""
from dataclasses import dataclass
from itertools import product
import numpy as np
import pandas as pd
from sklearn.ensemble import HistGradientBoostingClassifier
from threadpoolctl import threadpool_limits
from .policy import TRAIN, INTERNAL, require_open
from .modeling_data import matrix as prior_matrix, MODELS as PRIOR_MODELS
from .metrics import evaluate
D='basketball_features_hgb'
E='features_plus_elo_hgb'
MAPPING={D:'basketball_features_logistic', E:'features_plus_elo_logistic'}
MODELS={m:PRIOR_MODELS[p] for m,p in MAPPING.items()}
FIXED=dict(max_iter=200,min_samples_leaf=30,max_bins=255,early_stopping=False,random_state=0,loss='log_loss')
GRID=tuple(dict(learning_rate=r,max_leaf_nodes=n,l2_regularization=l) for r,n,l in product((.03,.05,.10),(7,15,31),(0.,1.,5.)))

def validate_parameters(p):
    if set(p)!=set(GRID[0]) or any(isinstance(v,(bool,str)) for v in p.values()) or p not in GRID:
        raise ValueError('Parameters outside the exact predeclared HGB grid')
    return dict(p)

def new_estimator(p):
    return HistGradientBoostingClassifier(**validate_parameters(p),**FIXED)

def matrix(data,model):
    require_open(data.season.unique())
    if model not in MAPPING:raise ValueError('Unknown HGB model')
    return prior_matrix(data,MAPPING[model])

@dataclass
class Fitted:
    model:str
    estimator:HistGradientBoostingClassifier
    training_seasons:tuple
    training_games:int

def fit_model(training,model,parameters):
    require_open(training.season.unique())
    if not set(training.season).issubset(TRAIN):raise ValueError('HGB fit requires training seasons only')
    d=training.sort_values(['season','game_date','game_id']).reset_index(drop=True)
    if d.empty or not d.game_id.is_unique or d.home_win.isna().any() or not d.home_win.isin([0,1]).all() or d.home_win.nunique()!=2:raise ValueError('Invalid training targets/keys')
    x=matrix(d,model);est=new_estimator(parameters)
    with threadpool_limits(limits=1):est.fit(x,d.home_win.astype(int))
    return Fitted(model,est,tuple(sorted(d.season.unique())),len(d))

def predict(fitted,data):
    x=matrix(data,fitted.model)
    with threadpool_limits(limits=1):p=fitted.estimator.predict_proba(x)[:,1]
    if len(p)!=len(data) or not np.isfinite(p).all() or not ((p>=0)&(p<=1)).all():raise ValueError('Invalid HGB probabilities')
    return p

def fit_final(development,choices):
    require_open(development.season.unique())
    if set(choices)!=set(MODELS):raise ValueError('Exactly D and E required')
    training=development[development.season.isin(TRAIN)].copy()
    if set(training.season)!=set(TRAIN):raise ValueError('All training seasons required')
    return {m:fit_model(training,m,choices[m]) for m in MODELS}

def fold_prediction(development,model,parameters,season):
    require_open(development.season.unique())
    if season not in INTERNAL:raise ValueError('Not a training-internal scoring season')
    train=development[development.season.isin(TRAIN)&development.season.lt(season)]
    val=development[development.season.eq(season)].sort_values(['game_date','game_id']).copy()
    if val.empty:raise ValueError('Empty fold')
    fitted=fit_model(train,model,parameters)
    out=val[['season','game_id','game_date','home_win']].copy();out['probability']=predict(fitted,val)
    return out,fitted

def select_hgb(development,grid=GRID):
    require_open(development.season.unique())
    grid=tuple(validate_parameters(p) for p in grid)
    if not grid or len({tuple(sorted(p.items())) for p in grid})!=len(grid):raise ValueError('Empty/duplicate grid')
    train=development[development.season.isin(TRAIN)].copy()
    if set(train.season)!=set(TRAIN):raise ValueError('All training seasons required')
    rows=[];folds=[]
    for model in MODELS:
        for i,p in enumerate(grid):
            predictions=[]
            for season in INTERNAL:
                pred,fit=fold_prediction(train,model,p,season);predictions.append(pred)
                folds.append(dict(model=model,**p,validation_season=season,training_seasons='|'.join(fit.training_seasons),training_games=fit.training_games,iterations=int(fit.estimator.n_iter_),**evaluate(pred,'probability')))
            pooled=evaluate(pd.concat(predictions,ignore_index=True),'probability')
            rows.append(dict(model=model,**p,folds=len(INTERNAL),n_scored_games=pooled.pop('n_games'),**pooled))
            print(f'{model}: candidate {i+1}/{len(grid)} complete',flush=True)
    results=pd.DataFrame(rows).sort_values(['model','log_loss','brier_score','max_leaf_nodes','l2_regularization','learning_rate'],ascending=[True,True,True,True,False,True],kind='stable').reset_index(drop=True)
    choices={m:{k:(int(v) if k=='max_leaf_nodes' else float(v)) for k,v in results[results.model.eq(m)].iloc[0][list(GRID[0])].items()} for m in MODELS}
    return choices,results,pd.DataFrame(folds)
