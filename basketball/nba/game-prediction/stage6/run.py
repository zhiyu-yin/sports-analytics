"""Run once. Any failure after access requires an explicit documented recovery."""
import io,sys,unittest,traceback
import runtime as r

def report(status,error=None):
    headings=['Scientific hypothesis','Explicit final authorization','Frozen confirmatory model','Frozen benchmark','Frozen training policy','Pre-opening verification','Opening ledger','Final-season acquisition and validation','Final prediction protocol','All seven candidate metrics','PRIMARY Model C vs Elo result','Three-season directional replication','Paired loss differences','Date-clustered bootstrap intervals','Calibration','Tests / preflight','Reproducibility','Interpretation','Limitations','Final status of confirmatory hypothesis','What can no longer be claimed/changed','Recommended post-holdout analysis']
    text={1:'Does frozen Model C retain lower log loss and Brier score than raw Elo? Both deltas must be negative.',2:'The exact user authorization is preserved in stage6_evidence/authorization.txt.',3:'Stage 3 features_plus_elo_logistic: exactly 32 basketball features plus elo_logit; C=.01, L2, lbfgs, max_iter=5000, tol=1e-4, seed=0; saved training-fitted median imputation with indicators and StandardScaler.',4:'Raw Elo: initial1500, scale400, K20, H50, alpha.50; pregame predictions followed by binary-result updates.',5:'Saved statistical estimators trained only on 2015–16 through 2022–23. Zero refits, tuning or model changes. Frozen Elo state may evolve through completed later seasons.',6:'Exact Stage 5A freeze, recipes, feature lists, metric/calibration source, dependencies, estimator hashes, historical code and all 275 protected artifacts verified before access. See preopening_verification.json.',7:'The durable schema-compatible final_opening_ledger.json precedes the physical access call. First access and first outcome decode are separate events; null means not reached.',8:'See acquisition.json/acquisition_failure.json and validation.json where available. Full season is required; no subset is scored.',9:'Unchanged canonical ingestion requires score/WL decode before structural validation and rolling features. The first decode boundary is recorded honestly. No individual prediction errors are inspected.',16:'138 existing tests passed. See test_summary.json for new synthetic preflight coverage A–Q and baseline_test_summary.json for the unchanged development suite.',17:'Only one cached deterministic replay is allowed after a completed evaluation; it is not independent evidence.',19:'Calendar-date clustering does not remove across-date/team dependence. Calibration is bin-dependent. Historical source revision and pregame availability limitations persist.',21:'After the recorded physical access attempt this run must not be described as never accessed. No silent restart, tuning, refit, recalibration or recipe change is allowed.',22:'If execution stops, resolve the documented acquisition/integrity issue under an explicit recovery decision before further access. After a successful evaluation, use separately labeled descriptive error analysis; keep confirmatory evidence frozen.'}
    for i in [10,11,12,13,14,15,18,20]:text[i]='Not available: final evaluation did not complete. No replication or model-ranking claim can be made.'
    if status=='completed':
        for i,name in [(10,'final_holdout_metrics.csv'),(11,'primary_comparison.csv'),(12,'cross_season_confirmation.csv'),(13,'paired_loss_summary.csv'),(14,'date_cluster_bootstrap.csv'),(15,'calibration_summary.csv')]:text[i]='```csv\n'+(r.E/name).read_text()+'```'
        text[18]='Interpret the primary direction using both frozen losses. Other candidates are descriptive only. Bootstrap intervals are date-clustered descriptive intervals, not definitive statistical significance.';text[20]=(r.E/'primary_comparison.csv').read_text()
    body='# Stage 6 — Final holdout evaluation\n\nStatus: **'+status.upper()+'**\n\n'+('Stop reason: '+error+'\n\n' if error else '')
    body+='\n\n'.join('## '+str(i)+'. '+h+'\n\n'+text[i] for i,h in enumerate(headings,1))+'\n'
    (r.ROOT/'docs/stage6_final_holdout_evaluation.md').write_text(body)

def main():
    if (r.E/'final_opening_ledger.json').exists():raise RuntimeError('Ledger exists: no automatic restart')
    gate=r.verify();stream=io.StringIO();suite=unittest.defaultTestLoader.discover(str(r.ROOT/'stage6'),pattern='test_preflight.py');result=unittest.TextTestRunner(stream=stream,verbosity=2).run(suite)
    (r.E/'test_run.txt').write_text(stream.getvalue());r.durable(r.E/'test_summary.json',dict(tests=result.testsRun,passed=result.wasSuccessful(),errors=len(result.errors),failures=len(result.failures),baseline_tests=138,scope='Synthetic Stage 6 A–Q preflight; no actual final-season access'))
    if not result.wasSuccessful():print(stream.getvalue());raise RuntimeError('Preflight failed before access')
    gate=r.verify();gate['preflight_passed']=True;gate['test_summary_sha256']=r.access.checksum(r.E/'test_summary.json');r.durable(r.E/'preopening_verification.json',gate)
    s=r.Session();s.arm((r.E/'authorization.txt').read_bytes(),gate)
    try:
        body=r.acquire(s);scope,teams,games=r.validate_body(body);s.phase='validated'
        rt,pred=r.predict(s,scope,teams,games)
        hashes=r.save_results(rt,pred,r.E)
        d=r.read_json(s.ledger);d['aggregate_results_persisted_at_utc']=r.now();r.durable(s.ledger,d)
        r.protected();r.durable(r.E/'build_manifest.json',dict(passed=True,status='completed',output_sha256=hashes,code_sha256=r.checkpoint(),zero_fit_calls=True,protected_artifacts_unchanged=True,completed_at_utc=r.now()))
        s.begin_replay()
        # Same already-opened bytes, verified against durable provenance; no new network call.
        with r.access._RAW_OPEN(r.RAW,'rb') as f:cached=f.read()
        if r.sha(cached)!=r.read_json(r.E/'acquisition.json')['sha256']:raise ValueError('Cached bytes changed')
        replay=r.E/'replay';replay.mkdir();scope2,t2,g2=r.validate_body(cached,replay);rt2,p2=r.predict(s,scope2,t2,g2);h2=r.save_results(rt2,p2,replay)
        if hashes!=h2:raise ValueError('Replay mismatch: preserve and STOP')
        r.durable(r.E/'replay_verification.json',dict(passed=True,byte_identical=True,independent_confirmation=False,fit_calls=0,output_sha256=h2),True);report('completed');print('Stage 6 completed; deterministic replay identical.')
    except Exception as exc:
        error=type(exc).__name__+': '+str(exc)
        r.durable(r.E/'execution_stop.json',dict(error=error,timestamp_utc=r.now(),automatic_restart_forbidden=True,traceback=traceback.format_exc()),True)
        r.durable(r.E/'build_manifest.json',dict(passed=False,status='stopped',reason=error,code_sha256=r.checkpoint(),zero_fit_calls=True,protected_artifacts_unchanged=bool(r.protected()),aggregate_results_persisted=r.read_json(s.ledger)['aggregate_results_persisted_at_utc']))
        if not (r.E/'replay_verification.json').exists():r.durable(r.E/'replay_verification.json',dict(passed=False,status='not performed',independent_confirmation=False,reason='Initial execution did not complete cleanly'))
        report('stopped',error);print('STOP:',error)
if __name__=='__main__':main()
