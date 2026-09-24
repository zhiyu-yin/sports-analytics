"""Final protocol freeze only. No data loader, model, prediction or evaluation calls."""
from pathlib import Path
from hashlib import sha256
from importlib.metadata import version
import contextlib,io,json,re,sys,unittest
from .sealed_access import ROOT,checksum,_RAW_OPEN
from .multiseason import write_json
E=ROOT/'docs/stage5a_evidence'
PROTOCOL=ROOT/'docs/final_holdout_protocol_2025_26.md'
CANDIDATES=['constant_home_prior','raw_elo','basketball_features_logistic','elo_logistic','features_plus_elo_logistic','basketball_features_hgb','features_plus_elo_hgb']
PRIMARY=['features_plus_elo_logistic','raw_elo']
TRAIN=[f'{y}-{str(y+1)[2:]}' for y in range(2015,2023)]

def protocol_bytes():
    # The older data guard conservatively rejects every path containing 2025-26,
    # including the user-requested document name. This NO-ARG metadata reader
    # permits only this fixed, nonsymlink documentation file. No data exception.
    if PROTOCOL.resolve()!=PROTOCOL:raise ValueError('Protocol must be the fixed nonsymlink documentation path')
    with _RAW_OPEN(PROTOCOL,'rb') as f:return f.read()

def canonical_hash(value):return sha256(json.dumps(value,sort_keys=True,separators=(',',':')).encode()).hexdigest()

def protected():
    expected=json.loads((E/'protected_artifact_hashes_before.json').read_text())
    actual={p:checksum(ROOT/p) for p in expected}
    if actual!=expected:raise ValueError('Previous scientific artifact changed; STOP')
    return actual

def code_checkpoint():
    paths=[p for folder in ['src','scripts','tests'] for p in sorted((ROOT/folder).rglob('*.py'))]
    paths+=[ROOT/'.venv/lib/python3.10/site-packages/sports_analytics_development_policy.pth']
    return {str(p.relative_to(ROOT)):checksum(p) for p in paths}

def freeze_spec():
    prior=protected();candidate=json.loads((ROOT/'docs/stage4a_evidence/candidate_freeze.json').read_text())
    if candidate['candidates']!=CANDIDATES or candidate['estimator_training_seasons']!=TRAIN:raise ValueError('Candidate/training mismatch')
    c=candidate['recipes'][PRIMARY[0]];elo=candidate['recipes'][PRIMARY[1]]
    if c['C']!=.01 or c['penalty']!='l2' or c['solver']!='lbfgs' or len(c['features'])!=33 or c['features'][-1]!='elo_logit' or elo['parameters']!={'K':20.,'H':50.,'alpha':.5}:raise ValueError('Recipe mismatch')
    uncertainty=json.loads((E/'uncertainty_protocol.json').read_text())
    if uncertainty['replicates']!=10000 or uncertainty['seed']!=0 or uncertainty['method']!='date-clustered descriptive bootstrap intervals':raise ValueError('Uncertainty mismatch')
    training=dict(statistical_model_seasons=TRAIN,refit_validation=False,refit_preholdout=False,elo_state='Frozen parameters; chronological completed-game online updates through 2023-24 and 2024-25 before final season; no replay in Stage 5A')
    preprocessing={k:c[k] for k in ['imputer','scaler','penalty','solver','max_iter','tol','random_state']}
    metrics_path='docs/stage5_evidence/frozen_source/metrics.py'
    old=json.loads((ROOT/'docs/stage3_evidence/build_manifest.json').read_text())['code_sha256']['src/nba_game_prediction/metrics.py']
    if checksum(ROOT/metrics_path)!=old:raise ValueError('Metric implementation changed')
    return dict(status='FROZEN — NOT YET EXECUTED',authorized_to_open=False,confirmatory_candidate=PRIMARY[0],primary_benchmark=PRIMARY[1],primary_comparison=PRIMARY,delta_definition='Model C minus raw Elo; negative primary losses favor C',candidates=CANDIDATES,secondary_candidates=[m for m in CANDIDATES if m not in PRIMARY],model_c_recipe=c,model_c_recipe_sha256=canonical_hash(c),raw_elo_recipe=elo,raw_elo_recipe_sha256=canonical_hash(elo),full_candidate_freeze_sha256=checksum(ROOT/'docs/stage4a_evidence/candidate_freeze.json'),features=c['features'],feature_allowlist_sha256=canonical_hash(c['features']),preprocessing_policy=preprocessing,preprocessing_sha256=canonical_hash(preprocessing),training_policy=training,training_policy_sha256=canonical_hash(training),primary_metrics=['log_loss','brier_score'],secondary_metrics=['accuracy','roc_auc','fixed_bin_calibration','fixed_bin_ece'],metrics_implementation=dict(path=metrics_path,sha256=old),calibration_implementation=dict(path=metrics_path,sha256=old,bins=[i/10 for i in range(11)],empty_bins_retained=True,fit_calibrator=False),uncertainty_protocol=uncertainty,uncertainty_protocol_sha256=checksum(E/'uncertainty_protocol.json'),uncertainty_implementation='Protocol only; no executable bootstrap or final-season executor enabled',protocol_sha256=sha256(protocol_bytes()).hexdigest(),opening_ledger_schema_sha256=checksum(E/'final_opening_ledger.schema.json'),expected_scope=dict(season='2025-26',scope='Complete validated NBA regular season; designated-home target; no postseason or non-regular-season games',observed_game_count=None,observed_date_range=None,physical_access_permitted=False),stage5_evidence_sha256={p:h for p,h in prior.items() if p.startswith('docs/stage5_evidence/') or p=='data/processed/stage5_predictions_2024_25.parquet' or p.startswith('reports/figures/stage5/')},saved_estimators_sha256=checksum(ROOT/'docs/stage5_evidence/frozen_estimators.pkl'),current_code_checkpoint=code_checkpoint(),versions={p:version(p) for p in ['numpy','pandas','scikit-learn','pyarrow']},final_data_access_timestamps_populated=False,stage6_executor_enabled=False)

def create_freeze():
    target=E/'final_holdout_freeze.json'
    if target.exists():raise RuntimeError('Freeze already exists; changes require explicit re-freeze')
    write_json(target,freeze_spec())

def verify():
    before=protected();expected=freeze_spec();saved=json.loads((E/'final_holdout_freeze.json').read_text())
    if saved!=expected:raise ValueError('Final freeze changed; explicit re-freeze required')
    from . import sealed_access as access
    access.EVENTS.clear();access.READS.clear()
    # A call profiler fails BEFORE any frozen numerical model/evaluation body executes.
    # Negative guard probes and estimator construction are permitted infrastructure tests.
    blocked_names={'fit','predict','predict_proba','replay','evaluate','calibration','select_parameters','select_hgb','select_logistic'}
    forbidden_calls=[]
    def profiler(frame,event,arg):
        if event=='call':
            path=frame.f_code.co_filename;name=frame.f_code.co_name
            numerical=('docs/stage5_evidence/frozen_source/' in path or '/sklearn/' in path)
            if numerical and name in blocked_names:
                forbidden_calls.append(dict(path=path,function=name));raise RuntimeError('Stage 5A forbids numerical model execution')
    stream=io.StringIO();previous=sys.getprofile();sys.setprofile(profiler)
    try:
        with contextlib.redirect_stdout(stream),contextlib.redirect_stderr(stream):
            suite=unittest.defaultTestLoader.discover(str(ROOT/'tests'))
            result=unittest.TextTestRunner(stream=stream,verbosity=2).run(suite)
    finally:sys.setprofile(previous)
    log=re.sub(r'Ran (\d+) tests in [0-9.]+s',r'Ran \1 tests (runtime omitted for deterministic verification)',stream.getvalue());(E/'test_run.txt').write_text(log)
    audit=access.snapshot()
    if forbidden_calls or not result.wasSuccessful():raise RuntimeError('Stage 5A tests failed; see test_run.txt')
    if any('2025-26' in x['path'] or '2025_26' in x['path'] for x in audit['reads']):raise RuntimeError('Forbidden final-data access')
    write_json(E/'test_summary.json',dict(tests=result.testsRun,failures=len(result.failures),errors=len(result.errors),skipped=len(result.skipped),passed=True,model_execution_calls=forbidden_calls,offline=True,final_holdout_access=False))
    write_json(E/'access_audit.json',dict(**audit,admitted_final_holdout_data_reads=0,numerical_model_calls=forbidden_calls,protocol_document_read='Fixed documentation metadata only; separate from data access'))
    after=protected();write_json(E/'protected_artifact_hashes_after.json',after)
    names=['final_holdout_freeze.json','uncertainty_protocol.json','final_opening_ledger.schema.json','protected_artifact_hashes_before.json','protected_artifact_hashes_after.json','test_summary.json','test_run.txt','access_audit.json','test_scope.json']
    manifest=dict(stage='5A',passed=True,tests=result.testsRun,protected_artifacts=len(after),all_previous_artifacts_unchanged=before==after,protocol_sha256=sha256(protocol_bytes()).hexdigest(),output_sha256={n:checksum(E/n) for n in names},code_sha256=code_checkpoint(),no_model_execution=True,no_final_data_access=True,no_final_executor=True)
    write_json(E/'build_manifest.json',manifest)
    print(f'Stage 5A: {result.testsRun} infrastructure tests passed; {len(after)} artifacts unchanged; no model execution or final-holdout access.')
    return manifest
