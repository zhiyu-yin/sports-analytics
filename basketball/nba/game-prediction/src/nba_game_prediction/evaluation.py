"""Guarded local inputs, training-only selection, frozen validation evaluation."""
from pathlib import Path
from dataclasses import asdict
from importlib.metadata import version
import json,sys
import pandas as pd
from .policy import TRAIN,INTERNAL,VALIDATION,require_open
from .elo import INPUT,GRID,replay,select_parameters,fit_constant
from .metrics import evaluate,calibration,calibration_summary,EPSILON
from .multiseason import digest,write_json,save_table

FEATURE_PATH='data/processed/game_features_multiseason.parquet'
OUTCOME_PATH='data/interim/game_outcomes_multiseason.parquet'
IDENTITY=INPUT[:-1]

def verify_inputs(root):
    root=Path(root);e=root/'docs/stage2_evidence'
    # A recorded Stage 1D manifest is the input trust anchor; verify before reading data.
    for path,h in json.loads((e/'protected_before.json').read_text()).items():
        if digest(root/path)!=h:raise ValueError('Stage 1 provenance mismatch: '+path)
    m=json.loads((root/'docs/stage1d_evidence/build_manifest.json').read_text())
    for p in [FEATURE_PATH,OUTCOME_PATH]:
        if digest(root/p)!=m['output_sha256'][p]:raise ValueError('Input checksum mismatch: '+p)
    f=pd.read_parquet(root/FEATURE_PATH,columns=IDENTITY)
    keys=pd.read_parquet(root/OUTCOME_PATH,columns=['season','game_id'])
    expected=set(TRAIN+(VALIDATION,'2024-25'))
    if len(f)!=11979 or len(keys)!=11979 or set(f.season)!=expected or set(keys.season)!=expected:raise ValueError('Unexpected input coverage')
    if not f.game_id.is_unique or not keys.game_id.is_unique:raise ValueError('Duplicate input keys')
    pd.testing.assert_frame_equal(f[['season','game_id']].sort_values('game_id').reset_index(drop=True),keys.sort_values('game_id').reset_index(drop=True),check_exact=True)
    return f,m

def load_games(root,seasons):
    seasons=tuple(seasons);require_open(seasons) # guard before any file/data access
    if len(set(seasons))!=len(seasons):raise ValueError('Duplicate season request')
    root=Path(root);identity,_=verify_inputs(root)
    identity=identity[identity.season.isin(seasons)].copy()
    # Read only binary outcomes for permitted seasons. Scores and sealed labels never enter modeling.
    from .sealed_access import load_outcomes
    outcomes=load_outcomes(root,seasons,purpose='permitted modeling input',columns=['game_id','home_win'])
    joined=identity.merge(outcomes,on='game_id',how='left',validate='one_to_one')
    if len(joined)!=len(outcomes) or joined.home_win.isna().any():raise ValueError('Outcome join mismatch')
    return joined[INPUT].sort_values(['season','game_date','game_id']).reset_index(drop=True)

def plot_calibration(tables,path):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    fig,axes=plt.subplots(1,2,figsize=(10,4.4),sharex=True,sharey=True)
    for ax,(name,t) in zip(axes,tables.items()):
        t=t[t['count']>0]
        ax.plot([0,1],[0,1],linestyle='--',color='gray',linewidth=1,label='Perfect calibration')
        ax.plot(t.mean_predicted_probability,t.observed_home_win_rate,'o-',label=name)
        for row in t.itertuples():ax.annotate(str(row.count),(row.mean_predicted_probability,row.observed_home_win_rate),xytext=(4,5),textcoords='offset points',fontsize=8)
        ax.set(xlim=(0,1),ylim=(0,1),xlabel='Mean predicted home-win probability',title=name)
        ax.grid(alpha=.2);ax.legend(loc='upper left',fontsize=8)
    axes[0].set_ylabel('Observed home-win rate')
    fig.suptitle('2023–24 validation: reliability by fixed probability bin')
    fig.text(.5,.015,'Point labels show game counts; sparse bins are noisy. No calibration model fitted.',ha='center',fontsize=9)
    fig.tight_layout(rect=(0,.035,1,.94));path.parent.mkdir(parents=True,exist_ok=True)
    fig.savefig(path,dpi=160,metadata={'Software':'Stage 2 matplotlib'});plt.close(fig)

def build(root):
    from .sealed_access import no_model_execution
    no_model_execution()
    root=Path(root);e=root/'docs/stage2_evidence'
    protocol=json.loads((e/'protocol.json').read_text())
    if protocol['grid']!=GRID or protocol['internal_scored_seasons']!=list(INTERNAL):raise ValueError('Predeclared protocol mismatch')
    train=load_games(root,TRAIN)
    prior=fit_constant(train);params,grid,folds=select_parameters(train)
    selected={'parameters':asdict(params),'initial_rating':1500,'scale':400,'selection':'pooled internal-training log loss','internal_seasons':list(INTERNAL),'tie_break':protocol['tie_break'],'constant_prior':prior,'outcome_file_sha256':digest(root/OUTCOME_PATH),'selected_before_validation_outcome_load':True}
    # Freeze on disk before requesting validation labels; no model selection follows.
    write_json(e/'selected_elo_parameters.json',selected)
    grid.to_csv(e/'elo_grid_results.csv',index=False);folds.to_csv(e/'elo_internal_fold_metrics.csv',index=False)
    validation=load_games(root,[VALIDATION])
    audit=replay(pd.concat([train,validation],ignore_index=True),params)
    v=audit[audit.season.eq(VALIDATION)].copy()
    pred=v[['season','game_id','game_date','home_team_id','away_team_id','home_win']].copy()
    pred['constant_probability']=prior['p_home_train'];pred['elo_probability']=v.predicted_home_probability.to_numpy()
    pred['elo_home_rating_before']=v.home_rating_before.to_numpy();pred['elo_away_rating_before']=v.away_rating_before.to_numpy()
    pred=pred.reset_index(drop=True)
    if len(pred)!=1230:raise ValueError('Validation cardinality mismatch')
    save_table(root/'data/processed/stage2_predictions_2023_24.parquet',pred)
    save_table(root/'data/interim/stage2_elo_game_log.parquet',audit)
    rows=[];summaries={};plots={}
    for model,col,short in [('constant_home_prior','constant_probability','constant'),('elo','elo_probability','elo')]:
        rows.append(dict(model=model,split='2023-24 validation',**evaluate(pred,col)))
        fixed=calibration(pred,col);equal=calibration(pred,col,equal_frequency=True)
        fixed.to_csv(e/f'calibration_{short}.csv',index=False);equal.to_csv(e/f'calibration_{short}_equal_frequency.csv',index=False)
        summaries[model]=calibration_summary(fixed)
        summaries[model].update(mean_probability=float(pred[col].mean()),observed_home_win_rate=float(pred.home_win.mean()))
        plots[model]=fixed
    pd.DataFrame(rows).to_csv(e/'validation_metrics.csv',index=False)
    write_json(e/'calibration_summary.json',summaries)
    plot_calibration(plots,root/'reports/figures/stage2/calibration_2023_24.png')
    verify_inputs(root)
    outputs=[root/'data/processed/stage2_predictions_2023_24.parquet',root/'data/interim/stage2_elo_game_log.parquet',root/'reports/figures/stage2/calibration_2023_24.png']+[e/name for name in ['selected_elo_parameters.json','elo_grid_results.csv','elo_internal_fold_metrics.csv','validation_metrics.csv','calibration_constant.csv','calibration_elo.csv','calibration_constant_equal_frequency.csv','calibration_elo_equal_frequency.csv','calibration_summary.json']]
    codes=[root/'src/nba_game_prediction'/n for n in ['policy.py','metrics.py','elo.py','evaluation.py']]+[root/'scripts/run_stage2_baselines.py']
    manifest={'stage':'2','input_sha256':{p:digest(root/p) for p in [FEATURE_PATH,OUTCOME_PATH,'docs/stage1d_evidence/build_manifest.json']},'protocol_sha256':digest(e/'protocol.json'),'grid':GRID,'selected_parameters':asdict(params),'constant_prior':prior,'training_games':len(train),'validation_games':len(validation),'internal_scored_games':int(grid.iloc[0].n_scored_games),'sealed_2024_25':True,'holdout_2025_26_accessed':False,'log_loss_epsilon':EPSILON,'code_sha256':{str(p.relative_to(root)):digest(p) for p in codes},'output_sha256':{str(p.relative_to(root)):digest(p) for p in outputs},'requirements_sha256':digest(root/'requirements.txt'),'versions':{p:version(p) for p in ['numpy','pandas','pyarrow','matplotlib','nba_api']},'python':sys.version,'access_contract':'Full key-only metadata; projected identity; only permitted-season home_win; no scores or engineered features.'}
    write_json(e/'build_manifest.json',manifest)
    print(json.dumps({'selected':asdict(params),'constant':prior,'validation':rows,'calibration':summaries},indent=2),flush=True)
    return manifest
