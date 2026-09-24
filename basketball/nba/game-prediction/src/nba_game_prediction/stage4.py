"""Offline Stage 4 orchestration; freeze precedes external outcome access."""
from pathlib import Path
from importlib.metadata import version
import json,pickle,hashlib,sys
import numpy as np
import pandas as pd
from .boosting import GRID,FIXED,MODELS,D,E,select_hgb,fit_final,predict
from .modeling_data import verify_frozen,load_modeling_data,add_frozen_elo,FROZEN
from .policy import TRAIN,VALIDATION
from .evaluation import IDENTITY
from .metrics import evaluate,calibration,calibration_summary
from .multiseason import digest,write_json,save_table
from .stage3 import NAMES as BASELINES,compare_baselines
NAMES={**BASELINES,D:D+'_probability',E:E+'_probability'}

def verify_protected(root):
    verify_frozen(root)
    for p,h in json.loads((root/'docs/stage4_evidence/protected_before.json').read_text()).items():
        if digest(root/p)!=h:raise ValueError('Protected Stage 3 artifact mismatch: '+p)

def baseline_regression(root,pred):
    old=pd.read_parquet(root/'data/processed/stage3_predictions_2023_24.parquet')
    for col in IDENTITY+['home_win']:
        if not np.array_equal(pred[col],old[col]):raise ValueError('Stage 3 identity/target mismatch: '+col)
    metrics=pd.read_csv(root/'docs/stage3_evidence/validation_metrics.csv',float_precision='round_trip').set_index('model')
    checks=[]
    for m,col in BASELINES.items():
        if not np.array_equal(pred[col],old[col]):raise ValueError('Stage 3 prediction mismatch: '+m)
        if any(value!=metrics.loc[m,k] for k,value in evaluate(pred,col).items()):raise ValueError('Stage 3 metric mismatch: '+m)
        checks.append(dict(model=m,probabilities_exact=True,metrics_exact=True))
    return dict(passed=True,stage3=checks,stage2=compare_baselines(root,pred))

def figure(tables,path):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    fig,axes=plt.subplots(1,3,figsize=(12,4.5),sharex=True,sharey=True)
    for ax,m,title in zip(axes,['raw_elo','features_plus_elo_logistic',E],['Frozen raw Elo','Frozen features + Elo logistic','Features + Elo HGB']):
        t=tables[m];t=t[t['count']>0]
        ax.plot([0,1],[0,1],'--',color='gray',lw=1)
        ax.plot(t.mean_predicted_probability,t.observed_home_win_rate,'o-',lw=1.5)
        for row in t.itertuples():ax.annotate(str(row.count),(row.mean_predicted_probability,row.observed_home_win_rate),xytext=(3,5),textcoords='offset points',fontsize=7)
        ax.set(xlim=(0,1),ylim=(0,1),title=title,xlabel='Mean predicted probability');ax.grid(alpha=.2)
    axes[0].set_ylabel('Observed home-win rate');fig.suptitle('2023–24 validation: fixed-bin reliability')
    fig.text(.5,.02,'Diagonal = perfect calibration. Labels = game counts; sparse bins are noisy.',ha='center',fontsize=9)
    fig.tight_layout(rect=(0,.05,1,.94));path.parent.mkdir(parents=True,exist_ok=True);fig.savefig(path,dpi=160,metadata={'Software':'Stage 4 matplotlib'});plt.close(fig)

def build(root):
    from .sealed_access import no_model_execution
    no_model_execution()
    root=Path(root);e=root/'docs/stage4_evidence';verify_protected(root)
    protocol=json.loads((e/'protocol.json').read_text())
    if protocol['grid']!=list(GRID) or protocol['fixed']!=FIXED or protocol['models']!={k:list(v) for k,v in MODELS.items()} or protocol['frozen_elo']!=FROZEN:raise ValueError('Predeclared protocol mismatch')
    train=add_frozen_elo(load_modeling_data(root,TRAIN))
    choices,grid,folds=select_hgb(train)
    if len(train)!=9519 or len(grid)!=54 or len(folds)!=270 or not grid.n_scored_games.eq(5829).all():raise ValueError('Unexpected development coverage')
    write_json(e/'selected_hgb_parameters.json',dict(parameters_by_model=choices,fixed=FIXED,frozen_elo=FROZEN,selected_before_validation_label_load=True,selection=protocol['selection']))
    grid.to_csv(e/'hgb_grid_results.csv',index=False);folds.to_csv(e/'hgb_fold_results.csv',index=False)
    final=fit_final(train,choices)
    state=lambda:{m:hashlib.sha256(pickle.dumps(f)).hexdigest() for m,f in final.items()}
    before=state()
    write_json(e/'final_fit_audit.json',{m:dict(training_seasons=list(f.training_seasons),training_games=f.training_games,input_features=list(MODELS[m]),iterations=int(f.estimator.n_iter_),native_nan_cells=int(train[list(MODELS[m])].isna().sum().sum()),early_stopping=f.estimator.early_stopping) for m,f in final.items()})
    # First external-label read; both recipes saved and final estimators already fitted.
    val=load_modeling_data(root,[VALIDATION])
    combined=add_frozen_elo(pd.concat([train.drop(columns=['raw_elo_probability','elo_logit']),val],ignore_index=True))
    val=combined[combined.season.eq(VALIDATION)].reset_index(drop=True)
    old=pd.read_parquet(root/'data/processed/stage3_predictions_2023_24.parquet')
    pred=val[IDENTITY+['home_win']].copy()
    if not np.array_equal(pred.game_id,old.game_id):raise ValueError('Frozen baseline key order differs')
    for col in BASELINES.values():pred[col]=old[col].to_numpy()
    if not np.array_equal(pred.raw_elo_probability,val.raw_elo_probability):raise ValueError('Frozen Elo replay differs')
    write_json(e/'baseline_regression.json',baseline_regression(root,pred))
    for m,f in final.items():pred[NAMES[m]]=predict(f,val)
    if before!=state():raise ValueError('External prediction mutated final model')
    if len(pred)!=1230 or not pred.game_id.is_unique or set(pred.season)!={VALIDATION}:raise ValueError('Unexpected validation coverage')
    save_table(root/'data/processed/stage4_predictions_2023_24.parquet',pred)
    metrics=pd.DataFrame([dict(model=m,split='2023-24 validation',**evaluate(pred,col)) for m,col in NAMES.items()]);metrics.to_csv(e/'validation_metrics.csv',index=False)
    ix=metrics.set_index('model');comparisons=[(D,'raw_elo'),(D,'basketball_features_logistic'),(E,'raw_elo'),(E,'features_plus_elo_logistic'),(E,D)]
    deltas=[dict(comparison=a+' vs '+b,**{'delta_'+dest:float(ix.loc[a,src]-ix.loc[b,src]) for src,dest in [('log_loss','log_loss'),('brier_score','brier'),('accuracy','accuracy'),('roc_auc','roc_auc')]}) for a,b in comparisons]
    pd.DataFrame(deltas).to_csv(e/'incremental_value.csv',index=False)
    tables={m:calibration(pred,NAMES[m]) for m in ['raw_elo','features_plus_elo_logistic',D,E]}
    for m,name in [('raw_elo','raw_elo'),('features_plus_elo_logistic','stage3_features_plus_elo'),(D,'hgb_features'),(E,'hgb_features_plus_elo')]:tables[m].to_csv(e/f'calibration_{name}.csv',index=False)
    pd.concat([t.assign(model=m) for m,t in tables.items()],ignore_index=True).to_csv(e/'calibration_figure_data.csv',index=False)
    write_json(e/'calibration_summary.json',{m:calibration_summary(t) for m,t in tables.items()})
    figure(tables,root/'reports/figures/stage4/calibration_2023_24.png');verify_protected(root)
    outputs=['selected_hgb_parameters.json','hgb_grid_results.csv','hgb_fold_results.csv','final_fit_audit.json','baseline_regression.json','validation_metrics.csv','incremental_value.csv','calibration_raw_elo.csv','calibration_stage3_features_plus_elo.csv','calibration_hgb_features.csv','calibration_hgb_features_plus_elo.csv','calibration_figure_data.csv','calibration_summary.json']
    paths=[e/n for n in outputs]+[root/'data/processed/stage4_predictions_2023_24.parquet',root/'reports/figures/stage4/calibration_2023_24.png']
    codes=['src/nba_game_prediction/boosting.py','src/nba_game_prediction/stage4.py','scripts/run_stage4_boosting.py','tests/test_boosting.py']
    manifest=dict(stage=4,parameters_by_model=choices,training_games=9519,internal_scored_games=5829,validation_games=1230,grid_candidates=54,fold_fits=270,final_fits=2,output_sha256={str(p.relative_to(root)):digest(p) for p in paths},code_sha256={p:digest(root/p) for p in codes},protected_sha256=digest(e/'protected_before.json'),protocol_sha256=digest(e/'protocol.json'),requirements_sha256=digest(root/'requirements.txt'),versions={p:version(p) for p in ['scikit-learn','scipy','numpy','pandas','pyarrow','matplotlib','threadpoolctl','joblib']},python=sys.version,sockets_blocked=True,sealed_2024_25=True,holdout_accessed=False,baseline_metrics_exact=True)
    write_json(e/'build_manifest.json',manifest);print(metrics.to_string(index=False),flush=True)
    return manifest
