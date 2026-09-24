"""Frozen Stage 3 experiment; local inputs and deterministic output artifacts."""
from pathlib import Path
from importlib.metadata import version
import json,sys
import numpy as np
import pandas as pd
from threadpoolctl import threadpool_limits
from .policy import TRAIN,VALIDATION
from .modeling_data import verify_frozen,load_modeling_data,add_frozen_elo,MODELS,FROZEN
from .logistic import C_GRID,fit_final,predict,coefficients,fitted_state
from .model_selection import select_logistic
from .metrics import evaluate,calibration,calibration_summary
from .multiseason import digest,write_json,save_table
NAMES={'constant_home_prior':'constant_probability','raw_elo':'raw_elo_probability','basketball_features_logistic':'basketball_features_logistic_probability','elo_logistic':'elo_logistic_probability','features_plus_elo_logistic':'features_plus_elo_logistic_probability'}
SHORT={'constant_home_prior':'constant','raw_elo':'raw_elo','basketball_features_logistic':'basketball_features','elo_logistic':'elo_logistic','features_plus_elo_logistic':'features_plus_elo'}

def compare_baselines(root,pred):
    old=pd.read_parquet(root/'data/processed/stage2_predictions_2023_24.parquet')
    if not np.array_equal(old.game_id,pred.game_id):raise ValueError('Stage 2 baseline keys differ')
    checks=[];oldmetrics=pd.read_csv(root/'docs/stage2_evidence/validation_metrics.csv',float_precision='round_trip').set_index('model')
    for model,previous,col,oldcol in [('constant_home_prior','constant_home_prior','constant_probability','constant_probability'),('raw_elo','elo','raw_elo_probability','elo_probability')]:
        if not np.array_equal(pred[col],old[oldcol]):raise ValueError('Stage 2 baseline prediction mismatch')
        now=evaluate(pred,col)
        for metric,value in now.items():
            if value!=oldmetrics.loc[previous,metric]:raise ValueError('Stage 2 baseline metric mismatch: '+metric)
        checks.append({'model':model,'probabilities_exact':True,'metrics_exact':True})
    return checks

def figure(tables,path):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    chosen=['raw_elo','basketball_features_logistic','features_plus_elo_logistic'];titles=['Raw frozen Elo','Basketball features logistic','Features + Elo logistic']
    fig,axes=plt.subplots(1,3,figsize=(12,4.3),sharex=True,sharey=True)
    for ax,key,title in zip(axes,chosen,titles):
        t=tables[key];t=t[t['count']>0]
        ax.plot([0,1],[0,1],'--',color='gray',linewidth=1)
        ax.plot(t.mean_predicted_probability,t.observed_home_win_rate,'o-',linewidth=1.5)
        for row in t.itertuples():ax.annotate(str(row.count),(row.mean_predicted_probability,row.observed_home_win_rate),xytext=(3,5),textcoords='offset points',fontsize=7)
        ax.set(xlim=(0,1),ylim=(0,1),title=title,xlabel='Mean predicted probability');ax.grid(alpha=.2)
    axes[0].set_ylabel('Observed home-win rate');fig.suptitle('2023–24 validation: fixed-bin reliability')
    fig.text(.5,.015,'Diagonal = perfect calibration. Point labels = game counts; sparse bins are noisy.',ha='center',fontsize=9)
    fig.tight_layout(rect=(0,.04,1,.94));path.parent.mkdir(parents=True,exist_ok=True);fig.savefig(path,dpi=160,metadata={'Software':'Stage 3 matplotlib'});plt.close(fig)

def build(root):
    from .sealed_access import no_model_execution
    no_model_execution()
    root=Path(root);e=root/'docs/stage3_evidence';spec=verify_frozen(root)
    protocol=json.loads((e/'protocol.json').read_text())
    if protocol['C_grid']!=list(C_GRID) or protocol['models']!={k:list(v) for k,v in MODELS.items()} or protocol['frozen_elo']!=FROZEN:raise ValueError('Predeclared protocol mismatch')
    train=add_frozen_elo(load_modeling_data(root,TRAIN))
    with threadpool_limits(limits=1):
        choices,grid,folds,audit=select_logistic(train)
        selected={'C_by_model':choices,'frozen_elo':FROZEN,'selected_before_validation_label_load':True,'selection':protocol['selection'],'training_games':len(train),'internal_scored_games':int(grid.iloc[0].n_scored_games)}
        write_json(e/'selected_logistic_parameters.json',selected)
        grid.to_csv(e/'logistic_grid_results.csv',index=False);folds.to_csv(e/'logistic_fold_results.csv',index=False);write_json(e/'fold_fit_audit.json',audit)
        final=fit_final(train,choices)
        state={m:fitted_state(f) for m,f in final.items()};write_json(e/'fitted_pipeline_state.json',state)
        # No validation labels have been requested before choices and final fits are fixed.
        val=load_modeling_data(root,[VALIDATION])
        combined=add_frozen_elo(pd.concat([train.drop(columns=['raw_elo_probability','elo_logit']),val],ignore_index=True))
        val=combined[combined.season.eq(VALIDATION)].reset_index(drop=True)
        pred=val[['season','game_id','game_date','home_team_id','away_team_id','home_win']].copy()
        pred['constant_probability']=spec['constant_prior']['p_home_train'];pred['raw_elo_probability']=val.raw_elo_probability
        write_json(e/'baseline_regression.json',{'passed':True,'checks':compare_baselines(root,pred)})
        for model,fit in final.items():pred[NAMES[model]]=predict(fit,val)
        if state!={m:fitted_state(f) for m,f in final.items()}:raise ValueError('Validation mutated fitted pipeline')
    if len(pred)!=1230 or set(pred.season)!={VALIDATION}:raise ValueError('Unexpected validation coverage')
    save_table(root/'data/processed/stage3_predictions_2023_24.parquet',pred)
    rows=[];tables={};summaries={}
    for model,col in NAMES.items():
        rows.append(dict(model=model,split='2023-24 validation',**evaluate(pred,col)))
        table=calibration(pred,col);tables[model]=table;table.to_csv(e/f'calibration_{SHORT[model]}.csv',index=False)
        if model in MODELS:calibration(pred,col,equal_frequency=True).to_csv(e/f'calibration_{SHORT[model]}_equal_frequency.csv',index=False)
        summaries[model]=dict(**calibration_summary(table),mean_probability=float(pred[col].mean()),observed_home_win_rate=float(pred.home_win.mean()))
    metrics=pd.DataFrame(rows);metrics.to_csv(e/'validation_metrics.csv',index=False);indexed=metrics.set_index('model');deltas=[]
    comparisons=[(m,'raw_elo') for m in MODELS]+[('features_plus_elo_logistic','basketball_features_logistic')]
    for new,reference in comparisons:
        deltas.append(dict(comparison=new+' vs '+reference,**{'delta_'+dest:float(indexed.loc[new,source]-indexed.loc[reference,source]) for source,dest in [('log_loss','log_loss'),('brier_score','brier'),('accuracy','accuracy'),('roc_auc','roc_auc')]}))
    pd.DataFrame(deltas).to_csv(e/'incremental_value.csv',index=False);write_json(e/'calibration_summary.json',summaries)
    for model,name in [('basketball_features_logistic','features_only'),('elo_logistic','elo_logistic'),('features_plus_elo_logistic','features_plus_elo')]:coefficients(final[model]).to_csv(e/f'coefficients_{name}.csv',index=False)
    figure(tables,root/'reports/figures/stage3/calibration_2023_24.png')
    verify_frozen(root)
    output_names=['selected_logistic_parameters.json','logistic_grid_results.csv','logistic_fold_results.csv','fold_fit_audit.json','fitted_pipeline_state.json','baseline_regression.json','validation_metrics.csv','incremental_value.csv','calibration_summary.json']
    output_names += [f'calibration_{SHORT[m]}.csv' for m in NAMES]+[f'calibration_{SHORT[m]}_equal_frequency.csv' for m in MODELS]+[f'coefficients_{n}.csv' for n in ['features_only','elo_logistic','features_plus_elo']]
    paths=[e/n for n in output_names]+[root/'data/processed/stage3_predictions_2023_24.parquet',root/'reports/figures/stage3/calibration_2023_24.png']
    code=[root/'src/nba_game_prediction'/n for n in ['modeling_data.py','logistic.py','model_selection.py','stage3.py','metrics.py','elo.py','evaluation.py','features.py','policy.py']]+[root/'scripts/run_stage3_logistic.py']
    manifest={'stage':3,'C_by_model':choices,'frozen_elo':FROZEN,'protocol_sha256':digest(e/'protocol.json'),'training_games':len(train),'validation_games':len(pred),'internal_scored_games':int(grid.iloc[0].n_scored_games),'input_sha256':{p:digest(root/p) for p in ['data/processed/game_features_multiseason.parquet','data/interim/game_outcomes_multiseason.parquet','docs/stage2_evidence/selected_elo_parameters.json']},'code_sha256':{str(p.relative_to(root)):digest(p) for p in code},'output_sha256':{str(p.relative_to(root)):digest(p) for p in paths},'requirements_sha256':digest(root/'requirements.txt'),'versions':{p:version(p) for p in ['scikit-learn','scipy','numpy','pandas','pyarrow','matplotlib','threadpoolctl','joblib']},'python':sys.version,'sealed_2024_25':True,'holdout_accessed':False,'baseline_metrics_exact':True}
    write_json(e/'build_manifest.json',manifest)
    print(json.dumps({'selected':choices,'metrics':rows,'incremental':deltas,'calibration':summaries},indent=2),flush=True)
    return manifest
