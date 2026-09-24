"""Win/loss Elo: pregame prediction, zero-sum update, offseason shrinkage."""
from dataclasses import dataclass
from itertools import product
import math
import pandas as pd
import numpy as np
from .policy import require_open,TRAIN,INTERNAL
from .seasons import get_scope,date_in_scope
from .metrics import evaluate
INITIAL=1500.0
GRID={'K':[10,20,30,40],'H':[0,50,75,100,125],'alpha':[0.50,0.75,0.90,1.00]}
INPUT=['season','game_id','game_date','home_team_id','away_team_id','home_win']
@dataclass(frozen=True)
class Parameters:
    K:float
    H:float
    alpha:float
    def __post_init__(self):
        if not all(math.isfinite(v) for v in [self.K,self.H,self.alpha]) or self.K<=0 or self.H<0 or not 0<=self.alpha<=1:raise ValueError('Invalid Elo parameters')

def probability(home,away,H):
    p=1/(1+10**(-(home+H-away)/400))
    if not math.isfinite(p) or not 0<p<1:raise ValueError('Numerically saturated Elo probability')
    return p

def regress(rating,alpha):return INITIAL+alpha*(rating-INITIAL)

def ordered(frame):
    require_open(frame.season.unique())
    f=frame[INPUT].copy()
    if f.empty or f.isna().any().any() or not f.game_id.is_unique:raise ValueError('Missing/duplicate Elo input')
    if not f.home_win.isin([0,1]).all():raise ValueError('Nonbinary outcome')
    if not pd.api.types.is_datetime64_any_dtype(f.game_date):raise ValueError('Dates must already be parsed')
    if f.home_team_id.eq(f.away_team_id).any():raise ValueError('Repeated team')
    for season,g in f.groupby('season'):
        scope=get_scope(season)
        if not g.game_date.map(lambda d:date_in_scope(d,scope)).all() or not g.game_id.str.startswith(scope.game_prefix).all():raise ValueError('Season/date/ID mismatch')
    sides=pd.concat([f[['season','game_date','home_team_id']].rename(columns={'home_team_id':'team'}),f[['season','game_date','away_team_id']].rename(columns={'away_team_id':'team'})])
    if sides.duplicated(['season','game_date','team']).any():raise ValueError('Same-team/date ambiguity')
    return f.sort_values(['season','game_date','game_id']).reset_index(drop=True)

def replay(frame,params):
    from .sealed_access import no_model_execution
    no_model_execution()
    f=ordered(frame);ratings={};previous=None;records=[]
    for season,gid,date,h,a,y in f.itertuples(index=False,name=None):
        if previous is not None and season!=previous:ratings={tid:regress(r,params.alpha) for tid,r in ratings.items()}
        previous=season;rh=ratings.get(h,INITIAL);ra=ratings.get(a,INITIAL)
        p=probability(rh,ra,params.H);delta=params.K*(int(y)-p)
        records.append((season,gid,date,h,a,rh,ra,p,bool(y),delta,rh+delta,ra-delta))
        ratings[h]=rh+delta;ratings[a]=ra-delta
    return pd.DataFrame(records,columns=['season','game_id','game_date','home_team_id','away_team_id','home_rating_before','away_rating_before','predicted_home_probability','home_win','rating_delta','home_rating_after','away_rating_after'])

def select_parameters(development,grid=None):
    from .sealed_access import no_model_execution
    no_model_execution()
    require_open(development.season.unique())
    # Slice before inspecting any outcomes. External validation never enters tuning.
    train=development[development.season.isin(TRAIN)][INPUT].copy()
    if set(train.season)!=set(TRAIN):raise ValueError('All eight training seasons required for parameter selection')
    grid=GRID if grid is None else grid;rows=[];fold_rows=[]
    for K,H,alpha in product(grid['K'],grid['H'],grid['alpha']):
        audit=replay(train,Parameters(K,H,alpha));scored=audit[audit.season.isin(INTERNAL)]
        metrics=evaluate(scored,'predicted_home_probability')
        rows.append(dict(K=K,H=H,alpha=alpha,folds=len(INTERNAL),n_scored_games=metrics.pop('n_games'),**metrics))
        for season,fold in scored.groupby('season'):
            fold_rows.append(dict(K=K,H=H,alpha=alpha,season=season,**evaluate(fold,'predicted_home_probability')))
    results=pd.DataFrame(rows).sort_values(['log_loss','brier_score','K','H','alpha'],ascending=[True,True,True,True,False],kind='stable').reset_index(drop=True)
    best=results.iloc[0];return Parameters(float(best.K),float(best.H),float(best.alpha)),results,pd.DataFrame(fold_rows)

def fit_constant(development):
    from .sealed_access import no_model_execution
    no_model_execution()
    require_open(development.season.unique())
    train=development[development.season.isin(TRAIN)]
    if train.empty or train.home_win.isna().any() or not train.home_win.isin([0,1]).all():raise ValueError('Invalid training outcomes')
    wins=int(train.home_win.sum());return dict(training_games=len(train),training_home_wins=wins,p_home_train=wins/len(train))
