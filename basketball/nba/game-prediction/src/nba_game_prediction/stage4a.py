"""Infrastructure verification only: hashes, guarded structural tests and access audit."""
from pathlib import Path
import contextlib,io,json,re,sys,unittest
from importlib.metadata import version
from .sealed_access import ROOT,checksum,snapshot,EVENTS,READS,SAFE
from .multiseason import write_json

def protected(root):
    expected=json.loads((root/'docs/stage4a_evidence/protected_artifact_hashes_before.json').read_text())
    actual={p:checksum(root/p) for p in expected}
    if actual!=expected:raise ValueError('Frozen artifact changed; STOP')
    return actual

def build(root=ROOT):
    root=Path(root);e=root/'docs/stage4a_evidence'
    before=protected(root)
    freeze=json.loads((e/'candidate_freeze.json').read_text())
    if len(freeze['candidates'])!=7 or freeze['leading_candidate']!='features_plus_elo_logistic':raise ValueError('Candidate freeze mismatch')
    if any(before.get(p)!=h for p,h in freeze['artifact_sha256'].items()):raise ValueError('Candidate artifact mismatch')
    EVENTS.clear();READS.clear()
    stream=io.StringIO()
    with contextlib.redirect_stdout(stream),contextlib.redirect_stderr(stream):
        suite=unittest.defaultTestLoader.discover(str(root/'tests'))
        result=unittest.TextTestRunner(stream=stream,verbosity=2).run(suite)
    # Runtime is deliberately excluded from deterministic evidence; test identities/results remain.
    log=re.sub(r'Ran (\d+) tests in [0-9.]+s',r'Ran \1 tests (runtime omitted for deterministic evidence)',stream.getvalue())
    (e/'test_run.txt').write_text(log)
    audit=snapshot()
    # Every recorded read is an admitted request; negative probes increment blocked events only.
    sealed=[r for r in audit['reads'] if ('2024_25' in r['path'] or '2024-25' in r['path'] or 'multiseason' in r['path'] and 'stage1c_' not in r['path'])]
    violations=[r for r in sealed if not set(r['columns']).issubset(SAFE)]
    if violations:raise ValueError('Nonmetadata read of sealed/mixed container: STOP')
    audit.update(admitted_sealed_outcome_reads=len(violations),admitted_2025_26_reads=sum('2025' in r['path'] and ('2025_26' in r['path'] or '2025-26' in r['path']) for r in audit['reads']),model_execution_policy='All fitting/replay/prediction/evaluation boundaries fail before body execution; negative probes expected',network_policy='Socket construction blocked from virtualenv startup',expected_denials='Adversarial tests intentionally request prohibited reads/execution; these are denied before decoder/cache access',passed=result.wasSuccessful() and not violations)
    write_json(e/'access_spy_results.json',audit)
    summary=dict(tests=result.testsRun,failures=len(result.failures),errors=len(result.errors),skipped=len(result.skipped),passed=result.wasSuccessful(),network_blocked=True,sealed_outcome_guard_active=True,model_fits=0,model_performance_evaluations=0,archived_model_execution_test_modules=5,archived_real_data_test_modules=1)
    write_json(e/'test_summary.json',summary)
    if not result.wasSuccessful():raise RuntimeError('Development tests failed; see test_run.txt')
    after=protected(root);write_json(e/'protected_artifact_hashes_after.json',after)
    files=['sealed_access_audit.csv','sealed_data_policy.json','candidate_freeze.json','protected_artifact_hashes_before.json','protected_artifact_hashes_after.json','test_run.txt','test_summary.json','access_spy_results.json']
    paths=[e/n for n in files]+[root/'docs/preholdout_protocol_2024_25_draft.md']
    codes=[p for folder in ['src','scripts','tests','tests_archived'] for p in sorted((root/folder).rglob('*.py'))]+[root/'sitecustomize.py',root/'.venv/lib/python3.10/site-packages/sports_analytics_development_policy.pth']
    manifest=dict(stage='4A',protected_artifacts=len(after),all_protected_artifacts_unchanged=before==after,tests=result.testsRun,output_sha256={str(p.relative_to(root)):checksum(p) for p in paths},code_sha256={str(p.relative_to(root)):checksum(p) for p in codes},versions={p:version(p) for p in ['numpy','pandas','pyarrow','scikit-learn']},python=sys.version,models_executed=False,sealed_labels_read=False,preholdout_performance_computed=False,holdout_accessed=False)
    write_json(e/'build_manifest.json',manifest)
    print(f'Stage 4A: {result.testsRun} tests passed; {len(after)} frozen artifacts unchanged; no admitted sealed label reads or model execution.')
    return manifest
