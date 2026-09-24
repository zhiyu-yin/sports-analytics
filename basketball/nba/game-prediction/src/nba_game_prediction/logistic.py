"""Fixed sklearn recipes: training-only preprocessing and L2 logistic fit."""
from dataclasses import dataclass
import warnings
import numpy as np
import pandas as pd
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.exceptions import ConvergenceWarning
from threadpoolctl import threadpool_limits
from .policy import TRAIN,require_open
from .modeling_data import MODELS,matrix
C_GRID=(.01,.03,.10,.30,1.,3.,10.)
@dataclass
class Fitted:
    model:str
    C:float
    pipeline:Pipeline

def new_pipeline(C):
    if C not in C_GRID:raise ValueError('C outside predeclared grid')
    return Pipeline([('imputer',SimpleImputer(strategy='median',add_indicator=True)),('scaler',StandardScaler()),('logistic',LogisticRegression(C=C,penalty='l2',solver='lbfgs',class_weight=None,max_iter=5000,tol=1e-4,random_state=0))])

def fit_model(training,model,C):
    from .sealed_access import no_model_execution
    no_model_execution()
    require_open(training.season.unique())
    if not set(training.season).issubset(TRAIN):raise ValueError('Logistic fit requires training seasons only')
    d=training.sort_values(['season','game_date','game_id']).reset_index(drop=True)
    if d.empty or not d.game_id.is_unique or d.home_win.isna().any() or not d.home_win.isin([0,1]).all() or d.home_win.nunique()!=2:raise ValueError('Invalid training targets/keys')
    x=matrix(d,model)
    if x.isna().all().any():raise ValueError('All-missing training predictor; refuse silent feature removal')
    pipe=new_pipeline(C)
    with threadpool_limits(limits=1),warnings.catch_warnings():
        warnings.simplefilter('error',ConvergenceWarning)
        pipe.fit(x,d.home_win.astype(int))
    return Fitted(model,C,pipe)

def predict(model,data):
    from .sealed_access import no_model_execution
    no_model_execution()
    x=matrix(data,model.model)
    with threadpool_limits(limits=1):p=model.pipeline.predict_proba(x)[:,1]
    if len(p)!=len(data) or not np.isfinite(p).all() or not ((p>0)&(p<1)).all():raise ValueError('Invalid logistic probabilities')
    return p

def fit_final(development,choices):
    from .sealed_access import no_model_execution
    no_model_execution()
    require_open(development.season.unique())
    training=development[development.season.isin(TRAIN)].copy()
    return {m:fit_model(training,m,choices[m]) for m in MODELS}

def fitted_state(model):
    p=model.pipeline;i=p.named_steps['imputer'];s=p.named_steps['scaler'];l=p.named_steps['logistic']
    return dict(model=model.model,C=model.C,input_names=list(MODELS[model.model]),transformed_names=i.get_feature_names_out().tolist(),imputer_medians=i.statistics_.tolist(),indicator_indices=i.indicator_.features_.tolist(),scaler_mean=s.mean_.tolist(),scaler_scale=s.scale_.tolist(),coefficients=l.coef_[0].tolist(),intercept=float(l.intercept_[0]),iterations=int(l.n_iter_[0]),classes=l.classes_.tolist())

def coefficients(model):
    state=fitted_state(model);rows=[]
    for name,coef in zip(state['transformed_names'],state['coefficients']):
        indicator=name.startswith('missingindicator_')
        rows.append(dict(transformed_feature_name=name,source_feature_name=name.removeprefix('missingindicator_'),is_missingness_indicator=indicator,standardized_coefficient=coef,absolute_coefficient=abs(coef)))
    return pd.DataFrame(rows).sort_values(['absolute_coefficient','transformed_feature_name'],ascending=[False,True]).reset_index(drop=True)
