"""Frozen one-time pre-holdout execution; preparation never reads 2024-25 labels."""
from pathlib import Path
from importlib.metadata import version
import json,pickle,sys
import numpy as np
import pandas as pd
from .sealed_access import checksum,load_outcomes,OPEN
from .features import GAME_FEATURES
from .multiseason import write_json,save_table
from .stage5_access import Session,frozen_runtime,verify_artifacts,verify_recipes,IDENTITY,NAMES,PRIMARY,SEASON,now,sha_bytes

def code_hashes(root):
    paths=[root/'src/nba_game_prediction'/n for n in ['stage5.py','stage5_access.py','sealed_access.py']]+[root/'scripts/run_stage5_preholdout.py']+sorted((root/'docs/stage5_evidence/frozen_source').glob('*.py'))
    return {str(p.relative_to(root)):checksum(p) for p in paths}

def load_open(root,seasons):
    from .sealed_access import require_seasons
    require_seasons(seasons,'Stage 5 frozen training/validation')
    f=pd.read_parquet(root/'data/processed/game_features_multiseason.parquet',columns=IDENTITY+GAME_FEATURES,filters=[('season','in',list(seasons))])
    y=load_outcomes(root,seasons,'Stage 5 frozen training/validation')
    d=f.merge(y,on='game_id',validate='one_to_one')
    if len(d)!=len(f) or len(d)!=len(y) or d.home_win.isna().any():raise ValueError('Open input join mismatch')
    return d.sort_values(['season','game_date','game_id']).reset_index(drop=True)

def prediction_frame(rt,fits,data,prior):
    rt.policy.require_open(data.season.unique())
    pred=data[IDENTITY+['home_win']].copy();pred['constant_probability']=prior;pred['raw_elo_probability']=data.raw_elo_probability
    for m,f in fits.items():pred[NAMES[m]]=(rt.boosting.predict if m.endswith('_hgb') else rt.logistic.predict)(f,data)
    if list(pred)!=IDENTITY+['home_win']+list(NAMES.values()) or not pred.game_id.is_unique or not np.isfinite(pred[list(NAMES.values())]).all().all():raise ValueError('Prediction contract mismatch')
    return pred

def fit_frozen(rt,session,train,s3,s4):
    if set(train.season)!=set(OPEN[:-1]) or len(train)!=9519:raise ValueError('Only original training permitted')
    fits={}
    for m in list(NAMES)[2:]:
        session.training_model=m
        fits[m]=rt.boosting.fit_model(train,m,s4['parameters_by_model'][m]) if m.endswith('_hgb') else rt.logistic.fit_model(train,m,s3['C_by_model'][m])
    session.training_model=None
    return fits

def prepare(root):
    root=Path(root);e=root/'docs/stage5_evidence'
    if (e/'preopening_verification.json').exists():raise RuntimeError('Preparation already frozen; do not repeat')
    session=Session(root,'open');rt=frozen_runtime(root,session);freeze,s2,s3,s4=verify_recipes(root)
    checkpoint=json.loads((e/'stage4a_code_checkpoint.json').read_text())
    for p,h in checkpoint.items():
        if p!='src/nba_game_prediction/sealed_access.py' and checksum(root/p)!=h:raise ValueError('Unexpected Stage 4A code change: '+p)
    old=json.loads((root/'docs/stage4_evidence/build_manifest.json').read_text())
    versions={p:version(p) for p in old['versions']}
    if versions!=old['versions'] or checksum(root/'requirements.txt')!=old['requirements_sha256']:raise ValueError('Frozen dependency mismatch')
    with session.activate():
        train=rt.modeling_data.add_frozen_elo(load_open(root,OPEN[:-1]))
        fits=fit_frozen(rt,session,train,s3,s4)
        validation=load_open(root,['2023-24'])
        history=pd.concat([train.drop(columns=['raw_elo_probability','elo_logit']),validation],ignore_index=True)
        augmented=rt.modeling_data.add_frozen_elo(history)
        val=augmented[augmented.season.eq('2023-24')].reset_index(drop=True)
        pred=prediction_frame(rt,fits,val,s2['constant_prior']['p_home_train'])
        reference=pd.read_parquet(root/'data/processed/stage4_predictions_2023_24.parquet')
        for c in pred:
            if not np.array_equal(pred[c],reference[c]):raise ValueError('Frozen 2023-24 prediction mismatch: '+c)
        metrics=pd.read_csv(root/'docs/stage4_evidence/validation_metrics.csv',float_precision='round_trip').set_index('model')
        for m,col in NAMES.items():
            if any(v!=metrics.loc[m,k] for k,v in rt.metrics.evaluate(pred,col).items()):raise ValueError('Frozen 2023-24 metric mismatch: '+m)
        states={m:rt.logistic.fitted_state(f) for m,f in fits.items() if not m.endswith('_hgb')}
        if states!=json.loads((root/'docs/stage3_evidence/fitted_pipeline_state.json').read_text()):raise ValueError('Frozen logistic state mismatch')
    # Persist the actual frozen fitted objects; neither opening nor replay ever refits.
    bundle=dict(fits=fits,history=history,prior=s2['constant_prior']['p_home_train'])
    target=e/'frozen_estimators.pkl';target.write_bytes(pickle.dumps(bundle,protocol=5))
    gate=dict(passed=True,candidates=list(NAMES),candidate_freeze_sha256=checksum(root/'docs/stage4a_evidence/candidate_freeze.json'),protocol_sha256=checksum(e/'protocol.json'),code_sha256=code_hashes(root),frozen_artifact_sha256=verify_artifacts(root),selected_stage2=s2,selected_stage3=s3,selected_stage4=s4,feature_allowlists={m:freeze['recipes'][m].get('features',[]) for m in NAMES},versions=versions,requirements_sha256=checksum(root/'requirements.txt'),validation_prediction_arrays_exact=True,validation_metrics_exact=True,logistic_fitted_states_exact=True,training_games=9519,training_seasons=list(OPEN[:-1]),fit_calls=session.fit_calls,fitted_bundle_sha256=checksum(target),authorization_source_sha256=checksum(e/'authorization.txt'),sealed_outcomes_decoded=0,primary_comparison=list(PRIMARY))
    write_json(e/'preopening_verification.json',gate)
    print('Pre-opening gate PASSED: five original-training fits, seven exact validation arrays/metrics, no 2024-25 outcome access.',flush=True)
    return gate

def verify_gate(root):
    e=root/'docs/stage5_evidence';gate=json.loads((e/'preopening_verification.json').read_text())
    if not gate['passed'] or gate['code_sha256']!=code_hashes(root) or gate['protocol_sha256']!=checksum(e/'protocol.json') or gate['fitted_bundle_sha256']!=checksum(e/'frozen_estimators.pkl'):raise ValueError('Pre-opening gate or bundle mismatch')
    if gate['candidate_freeze_sha256']!=checksum(root/'docs/stage4a_evidence/candidate_freeze.json'):raise ValueError('Candidate freeze changed')
    gate['gate_file_sha256']=checksum(e/'preopening_verification.json')
    return gate

def assert_coverage(pred):
    if len(pred)!=1230 or set(pred.season)!={SEASON} or not pred.game_id.is_unique or set(pred)&{'home_pts','away_pts','pts','wl'}:raise ValueError('Fatal pre-holdout coverage/schema mismatch')
    if pred[list(NAMES.values())].isna().any().any() or not ((pred[list(NAMES.values())]>=0)&(pred[list(NAMES.values())]<=1)).all().all():raise ValueError('Invalid probability coverage')

def figure(tables,path):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    fig,axes=plt.subplots(1,2,figsize=(9,4.7),sharex=True,sharey=True)
    for ax,m,title in zip(axes,['raw_elo',PRIMARY[0]],['Frozen raw Elo','Frozen features + Elo logistic (C)']):
        t=tables[m];t=t[t['count']>0];ax.plot([0,1],[0,1],'--',color='gray',lw=1);ax.plot(t.mean_predicted_probability,t.observed_home_win_rate,'o-')
        for row in t.itertuples():ax.annotate(str(row.count),(row.mean_predicted_probability,row.observed_home_win_rate),xytext=(3,5),textcoords='offset points',fontsize=8)
        ax.set(xlim=(0,1),ylim=(0,1),title=title,xlabel='Mean predicted probability');ax.grid(alpha=.2)
    axes[0].set_ylabel('Observed designated-home win rate');fig.suptitle('2024–25 pre-holdout: fixed-bin calibration')
    fig.text(.5,.02,'Diagonal = perfect calibration. Labels = game counts; sparse bins are noisy.',ha='center',fontsize=9)
    fig.tight_layout(rect=(0,.05,1,.94));path.parent.mkdir(parents=True,exist_ok=True);fig.savefig(path,dpi=160,metadata={'Software':'Stage 5 matplotlib'});plt.close(fig)

def results(rt,root,out,pred,figure_path,prediction_path):
    out.mkdir(parents=True,exist_ok=True)
    assert_coverage(pred);save_table(prediction_path,pred)
    metrics=pd.DataFrame([dict(model=m,split='2024-25 pre-holdout',**rt.metrics.evaluate(pred,col)) for m,col in NAMES.items()]);metrics.to_csv(out/'preholdout_metrics.csv',index=False)
    ix=metrics.set_index('model');comparisons=[PRIMARY,('basketball_features_logistic','raw_elo'),('features_plus_elo_hgb','raw_elo'),('features_plus_elo_hgb',PRIMARY[0])]
    deltas=pd.DataFrame([dict(comparison=a+' vs '+b,**{'delta_'+dest:float(ix.loc[a,src]-ix.loc[b,src]) for src,dest in [('log_loss','log_loss'),('brier_score','brier'),('accuracy','accuracy'),('roc_auc','roc_auc')]}) for a,b in comparisons]);deltas.to_csv(out/'primary_comparison.csv',index=False)
    old=pd.read_csv(root/'docs/stage4_evidence/validation_metrics.csv',float_precision='round_trip').set_index('model');rows=[]
    for label,table in [('2023-24 validation',old),('2024-25 pre-holdout',ix)]:
        row=dict(split=label)
        for src,dest in [('log_loss','log_loss'),('brier_score','brier'),('accuracy','accuracy'),('roc_auc','auc')]:
            row['raw_elo_'+dest]=float(table.loc['raw_elo',src]);row['model_c_'+dest]=float(table.loc[PRIMARY[0],src])
            if dest in ('log_loss','brier'):row['delta_'+dest]=row['model_c_'+dest]-row['raw_elo_'+dest]
        rows.append(row)
    pd.DataFrame(rows).to_csv(out/'cross_season_replication.csv',index=False)
    tables={m:rt.metrics.calibration(pred,col) for m,col in NAMES.items()};summaries={}
    for m,t in tables.items():
        t.to_csv(out/f'calibration_{m}.csv',index=False)
        summaries[m]=dict(**rt.metrics.calibration_summary(t),mean_predicted_probability=float(pred[NAMES[m]].mean()),observed_designated_home_win_rate=float(pred.home_win.mean()))
    write_json(out/'calibration_summary.json',summaries)
    pd.concat([t.assign(model=m) for m,t in tables.items() if m in PRIMARY],ignore_index=True).to_csv(out/'calibration_figure_data.csv',index=False)
    figure(tables,figure_path)
    return metrics,deltas

def evaluate_opening(root,mode):
    root=Path(root);e=root/'docs/stage5_evidence';gate=verify_gate(root);session=Session(root,mode);rt=frozen_runtime(root,session)
    bundle=pickle.loads((e/'frozen_estimators.pkl').read_bytes());fits=bundle['fits']
    if list(fits)!=list(NAMES)[2:]:raise ValueError('Fitted candidates mismatch')
    state_before=sha_bytes(pickle.dumps(fits,protocol=5))
    if mode=='open':
        session.fit_calls=list(gate['fit_calls']);session.arm(gate,gate['protocol_sha256'],gate['code_sha256'])
    else:
        ledger=json.loads(session.ledger_path.read_text())
        if ledger['preopening_gate_sha256']!=gate['gate_file_sha256'] or ledger['code_sha256']!=gate['code_sha256']:raise ValueError('Opened recipe/code changed; replay forbidden')
    try:
        with session.activate():
            # First authorized target decode starts at admit_read; ledger persisted first.
            y=pd.read_parquet(root/'data/interim/reconciled/game_outcomes_2024_25.parquet',columns=['game_id','home_win'])
            if mode=='open':
                ledger=json.loads(session.ledger_path.read_text());ledger['first_outcome_decode_completed_at_utc']=now();write_json(session.ledger_path,ledger)
            features=pd.read_parquet(root/'data/processed/seasons/game_features_2024_25.parquet',columns=IDENTITY+GAME_FEATURES)
            data=features.merge(y,on='game_id',validate='one_to_one')
            if len(data)!=1230 or len(y)!=1230 or data.home_win.isna().any():raise ValueError('Stage 1D input coverage failure')
            augmented=rt.modeling_data.add_frozen_elo(pd.concat([bundle['history'],data],ignore_index=True))
            data=augmented[augmented.season.eq(SEASON)].reset_index(drop=True)
            pred=prediction_frame(rt,fits,data,bundle['prior']);assert_coverage(pred)
            if state_before!=sha_bytes(pickle.dumps(fits,protocol=5)):raise ValueError('Frozen estimator state mutated')
            if mode=='open':out=e;prediction_path=root/'data/processed/stage5_predictions_2024_25.parquet';figpath=root/'reports/figures/stage5/calibration_2024_25.png'
            else:out=e/'replay';prediction_path=out/'stage5_predictions_2024_25.parquet';figpath=out/'calibration_2024_25.png'
            metrics,deltas=results(rt,root,out,pred,figpath,prediction_path)
        verify_artifacts(root)
        files=[out/n for n in ['preholdout_metrics.csv','primary_comparison.csv','cross_season_replication.csv','calibration_summary.json','calibration_figure_data.csv']]+[out/f'calibration_{m}.csv' for m in NAMES]+[prediction_path,figpath]
        hashes={p.name:checksum(p) for p in files}
        if mode=='open':
            manifest=dict(stage=5,output_sha256=hashes,code_sha256=gate['code_sha256'],preopening_gate_sha256=gate['gate_file_sha256'],fitted_bundle_sha256=gate['fitted_bundle_sha256'],candidate_freeze_sha256=gate['candidate_freeze_sha256'],n_games=1230,candidates=list(NAMES),fit_calls_before_opening=gate['fit_calls'],fit_calls_after_opening=0,outcome_decodes=1,individual_error_analysis=False,holdout_accessed=False,versions=gate['versions'])
            write_json(e/'build_manifest.json',manifest)
            ledger=json.loads(session.ledger_path.read_text());ledger.update(status='completed',aggregate_results_persisted_at_utc=now(),build_manifest_sha256=checksum(e/'build_manifest.json'));write_json(session.ledger_path,ledger)
        else:
            expected=json.loads((e/'build_manifest.json').read_text())['output_sha256']
            if hashes!=expected:raise ValueError('Deterministic replay mismatch; STOP')
            write_json(e/'replay_verification.json',dict(passed=True,identical_output_sha256=hashes,predictions_metrics_calibration_comparisons_exact=True,fit_calls=0,evaluation_runs=2,independent_tests=1,statement='Replay reproduces the already-opened frozen evaluation; it is not independent evidence.',holdout_accessed=False))
        print(metrics.to_string(index=False),flush=True);print(deltas.to_string(index=False),flush=True)
    except Exception as exc:
        if mode=='open' and session.ledger_path.exists():
            ledger=json.loads(session.ledger_path.read_text());ledger.update(status='failed_stop',failure_type=type(exc).__name__,failure=str(exc));write_json(session.ledger_path,ledger)
        raise
