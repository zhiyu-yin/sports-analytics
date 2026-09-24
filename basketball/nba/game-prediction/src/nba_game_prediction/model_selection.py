"""Expanding training-only season folds; freshly fitted pipelines every fold."""
import pandas as pd
from .policy import TRAIN,INTERNAL,require_open
from .modeling_data import MODELS
from .logistic import C_GRID,fit_model,predict,fitted_state
from .metrics import evaluate

def fold_prediction(development,model,C,season):
    require_open(development.season.unique())
    if season not in INTERNAL:raise ValueError('Not a training-internal scoring season')
    train=development[development.season.isin(TRAIN)&development.season.lt(season)]
    val=development[development.season.eq(season)].sort_values(['game_date','game_id']).copy()
    if train.empty or val.empty:raise ValueError('Empty fold')
    fitted=fit_model(train,model,C)
    out=val[['season','game_id','game_date','home_win']].copy();out['probability']=predict(fitted,val)
    return out,fitted

def select_logistic(development,grid=C_GRID):
    from .sealed_access import no_model_execution
    no_model_execution()
    require_open(development.season.unique())
    train=development[development.season.isin(TRAIN)].copy() # never consult external validation values
    if set(train.season)!=set(TRAIN):raise ValueError('All training seasons required')
    rows=[];folds=[];audit=[]
    for model in MODELS:
        for C in grid:
            predictions=[]
            for season in INTERNAL:
                pred,fitted=fold_prediction(train,model,C,season);predictions.append(pred)
                folds.append(dict(model=model,C=C,validation_season=season,**evaluate(pred,'probability')))
                state=fitted_state(fitted)
                audit.append(dict(model=model,C=C,validation_season=season,training_seasons=sorted(train.loc[train.season.lt(season),'season'].unique().tolist()),training_games=int(train.season.lt(season).sum()),transformed_features=len(state['transformed_names']),iterations=state['iterations']))
            pooled=evaluate(pd.concat(predictions,ignore_index=True),'probability')
            rows.append(dict(model=model,C=C,folds=len(INTERNAL),n_scored_games=pooled.pop('n_games'),**pooled))
    results=pd.DataFrame(rows).sort_values(['model','log_loss','brier_score','C'],kind='stable').reset_index(drop=True)
    choices={model:float(results[results.model.eq(model)].iloc[0].C) for model in MODELS}
    return choices,results,pd.DataFrame(folds),audit
