"""Read-only Phase 2D adapter and preparation; deliberately contains no estimator."""
import argparse
import csv
import hashlib
import json
import math
import subprocess
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path

from injury_warning.pilot_io import ROOT
from phase2c.report import normalize_boston
from phase2d.report import joined
from phase2d.audit import group, lead_bin

D = ROOT / 'phase3a'
SCIENCE = '1d6fd5c9d9e52edffa96cc6488037b504c7ab95e'
CHECKPOINT = 'b5932dff33752d9f2cdffda42ebdf1da48523b6e'
PROTOCOL_COMMIT = '96d912e664f70992f54343ab42655df1e6828137'
BATCHES = {'first_six_phase2b': 'phase2b', 'second_six_phase2c': 'phase2c',
           **{f'phase2d_batch{i}': f'phase2d/batch{i}' for i in (1, 2, 3)}}
FEATURES = ('recent_evidence_28d', 'older_or_recent_history', 'past_mean_minutes',
            'workload_change_minutes_7d', 'index_back_to_back')
REVIEW_FIELDS = ('injury_attribution', 'episode_continuity', 'first_missed_game_anchor',
                 'consecutive_injury_game_count', 'competing_noninjury_reasons', 'censoring',
                 'reviewer_decision', 'reviewer_identity', 'review_date', 'reviewer_rationale')


def read(path):
    with path.open() as f:
        return list(csv.DictReader(f))


def dump(path, obj):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, sort_keys=True) + '\n')


def write(path, rows, fields=None):
    rows = list(rows)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=fields or list(dict.fromkeys(k for r in rows for k in r)) or ['id'])
        w.writeheader()
        w.writerows(rows)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def stamp(t):
    return datetime.fromisoformat(t).timestamp()


def fold(pid):
    """No label-aware stratification or redrawing; all episodes of a PID stay together."""
    return int(hashlib.sha256(('phase3a-20240221:' + pid).encode()).hexdigest(), 16) % 5


def predictors(values):
    """Exact allowlist, rejecting rather than silently dropping outcome or ID columns."""
    if set(values) != set(FEATURES):
        raise ValueError('Predictor schema must equal the frozen allowlist')
    for v in values.values():
        if v is not None and (not isinstance(v, (float, int)) or not math.isfinite(v)):
            raise ValueError('Predictors must be finite numbers or explicit missing values')
    return dict(values)


def numeric(v):
    return None if v in ('', None) else float(v)


def flag(v):
    return {'True': 1.0, 'False': 0.0}.get(v)


def features(r, f):
    complete = r.get('history_complete') == 'True'
    return predictors(dict(
        recent_evidence_28d=flag(r.get('recent_known_symptoms_28d_B')),
        older_or_recent_history=flag(r.get('ever_known_injury_history_B')),
        past_mean_minutes=numeric(f.get('past_mean_minutes_per_appearance')) if complete else None,
        workload_change_minutes_7d=numeric(f.get('workload_change_7d')) if complete else None,
        index_back_to_back=flag(f.get('index_back_to_back', f.get('index_game_back_to_back'))) if complete else None))


def config():
    return json.loads((D / 'protocol/config.json').read_text())


def validate_config(c):
    assert c['predictor_allowlist'] == list(FEATURES)
    assert c['models']['M0']['features'] == []
    assert c['models']['M1']['features'] == list(FEATURES[:3])
    assert c['models']['M2']['features'] == list(FEATURES)
    assert c['folds'] == 5 and c['models']['M2']['C'] == 0.1
    assert c['fitting_authorized'] is False
    assert c['weights'] == 'one per observed decision; no class or event weights'


def verify_snapshot():
    manifest = json.loads((D / 'snapshot_manifest.json').read_text())
    for name, h in manifest['files'].items():
        if sha(ROOT / name) != h:
            raise ValueError('Snapshot drift: ' + name)
    for name, h in manifest['preparation_code'].items():
        if sha(ROOT / name) != h:
            raise ValueError('Preparation code drift: ' + name)
    receipt_path=D/'commit_receipt.json'
    if receipt_path.exists():
        receipt=json.loads(receipt_path.read_text())
        assert receipt['protocol_commit']==PROTOCOL_COMMIT
        for name,h in receipt['protocol_hashes'].items():
            assert sha(D/name)==h, 'Protocol changed after freeze: '+name
            committed=subprocess.check_output(['git','show',PROTOCOL_COMMIT+':basketball/nba/injury-warning/phase3a/'+name],cwd=ROOT.parents[2])
            assert hashlib.sha256(committed).hexdigest()==h
    return manifest


def load_cohort():
    rr = [dict(r, batch='Boston_prior') for r in normalize_boston()]
    fmap = {'Boston_prior': {r['row_id']: r for r in read(ROOT / 'phase1c/tables/features_assumption_B.csv')}}
    for batch, name in BATCHES.items():
        rr += [dict(r, batch=batch) for r in joined(ROOT / name)]
        fmap[batch] = {r['row_id']: r for r in read(ROOT / name / 'tables/features_B.csv')}
    assert len({r['row_id'] for r in rr}) == len(rr), 'Duplicate canonical decision'
    assert len({(r['player_id'], r['decision_at'], r['extra_lag_days']) for r in rr}) == len(rr), 'Duplicate player-decision across transfers'
    return rr, fmap


def snapshot():
    """Freeze all tracked historical module inputs, without copying raw bodies."""
    if (D/'snapshot_manifest.json').exists():
        verify_snapshot()
        return
    repo = ROOT.parents[2]
    tree = subprocess.check_output(['git', 'ls-tree', '-r', CHECKPOINT,
                                    'basketball/nba/injury-warning'], cwd=repo, text=True).splitlines()
    files = {}
    for entry in tree:
        metadata,name=entry.split('\t',1)
        expected_blob=metadata.split()[2]
        p = repo / name
        b=p.read_bytes()
        assert hashlib.sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest()==expected_blob, 'Historical working-tree drift: '+name
        assert 'data/raw' not in name
        files[str(p.relative_to(ROOT))] = sha(p)
    prior = json.loads((ROOT / 'phase2d/result_hashes.json').read_text())
    for name, h in prior.items():
        assert sha(ROOT / name) == h, name
    versions = {}
    for phase in ('phase2b', 'phase2c', 'phase2d'):
        for p in (ROOT / phase / 'registration').glob('*.json'):
            versions[str(p.relative_to(ROOT))] = json.loads(p.read_text())
    dump(D / 'snapshot_manifest.json', dict(
        scientific_result_commit=SCIENCE, documentation_checkpoint=CHECKPOINT,
        files=files, preparation_code={str(p.relative_to(ROOT)): sha(p) for p in sorted(list(D.glob('*.py')) + [ROOT/'tests/test_phase3a.py'])},
        historical_registrations=versions,
        source_provenance='Historical manifests, receipts, global URL index and result_input_hashes are individually hashed in files. Raw bodies remain local and undistributed.',
        expected_root_readme_local_sha256='b9a0a38563ece5c86d466e6f1f38b5378890981cec4c0ff965c1dd373ecc6992',
        correction_ledger=[], historical_files_modified=False))


def timing_audit(rr, fmap):
    issues = []
    indexes = {}
    for batch, path in BATCHES.items():
        obs = read(ROOT / path / 'tables/status_observations.csv')
        sig = read(ROOT / path / 'tables/recap_signals_B.csv')
        indexes[batch] = {o['observation_id']: o for o in obs} | {s['signal_id']: s for s in sig}
    for r in rr:
        if r['B_state'] != 'included':
            continue
        f = fmap[r['batch']][r['row_id']]
        latest = f.get('max_input_assumed_available_at', '')
        if not latest or stamp(latest) > stamp(r['decision_at']):
            issues.append(dict(row_id=r['row_id'], kind='workload availability', value=latest))
        for sid in filter(None, r.get('signal_ids', '').split(';')):
            s = indexes[r['batch']].get(sid)
            if not s or s['player_id'] != r['player_id'] or stamp(s['B_available_at']) > stamp(r['decision_at']):
                issues.append(dict(row_id=r['row_id'], kind='signal identity or availability', value=sid))
        if r.get('prospective_uses_retrospective_outcome_evidence', 'False') != 'False':
            issues.append(dict(row_id=r['row_id'], kind='C leakage', value='True'))
    write(D / 'tables/timing_issues.csv', issues)
    assert not issues, issues[:5]


def analyze():
    verify_snapshot()
    c = config(); validate_config(c)
    rr, fmap = load_cohort()
    timing_audit(rr, fmap)
    inc = [r for r in rr if r['B_state'] == 'included']
    events = read(ROOT / 'phase2d/tables/canonical_events.csv')
    qualifying = [e for e in events if e['severity'] == 'positive' and e['candidate_broad_onset_period'] == 'True']
    assert len(qualifying) == 37 and len({e['player_id'] for e in qualifying}) == 36
    assert len({e['canonical_event_id'] for e in events})==len(events)
    for e in events:
        assert e['canonical_event_id']==e['player_id']+'_'+e['anchor_game_id']
    # Recheck underlying game-set overlap across confirmed runs of a player.
    actual={}
    for batch,path in BATCHES.items():
        gg=defaultdict(set)
        for g in read(ROOT/path/'tables/event_game_evidence.csv'):
            gg[g['event_id']].add(g['game_id'])
        actual[batch]=gg
    independence=[]
    for i,e in enumerate(qualifying):
        for f in qualifying[i+1:]:
            if e['player_id']!=f['player_id']:continue
            shared=actual[e['batch']][e['event_id']] & actual[f['batch']][f['event_id']]
            assert not shared, 'Overlapping confirmed runs require correction ledger'
            independence.append(dict(player_id=e['player_id'],run1=e['canonical_event_id'],run2=f['canonical_event_id'],shared_game_count=0,
                                     clinical_independence='not established; group all player observations together'))
    write(D/'tables/related_runs.csv',independence)
    write(D/'tables/correction_ledger.csv',[],['assertion','source_hash','locator','before','after','reason','affected_rows'])
    opp = read(ROOT / 'phase2d/tables/available_opportunities.csv')
    byid = {r['row_id']: r for r in inc}
    for o in opp:
        r = byid[o['row_id']]
        assert r['player_id'] == o['player_id'] and r['absence_run_onset_ge10'] == 'positive'
        lo = (stamp(o['onset_lower']) - stamp(r['decision_at'])) / 86400
        hi = (stamp(o['onset_upper']) - stamp(r['decision_at'])) / 86400
        assert 0 < lo <= hi <= 14 and abs(lo-float(o['lead_days_lower'])) < 1e-10
        assert lead_bin(lo, hi) == o['lead_time_bin']
    assert len({(o['row_id'], o['canonical_event_id']) for o in opp}) == len(opp)
    summary = []
    for lag, expected in [('0', (7108, 115, 6560, 433, 32)), ('1', (6862, 109, 6329, 424, 31))]:
        sub = [r for r in inc if r['extra_lag_days'] == lag]
        cnt = Counter(r['absence_run_onset_ge10'] for r in sub)
        oo = [o for o in opp if o['extra_lag_days'] == lag]
        assert (len(sub), cnt['positive'], cnt['negative'], cnt['unknown'], len({o['canonical_event_id'] for o in oo})) == expected
        assert {r['row_id'] for r in sub if r['absence_run_onset_ge10'] == 'positive'} == {o['row_id'] for o in oo}
        acute = {o['row_id'] for o in oo if o['same_acute_B'] == 'True'}
        sens = [r for r in sub if r['row_id'] not in acute]
        summary.append(dict(lag=lag, included=len(sub), **cnt, qualifying_runs=37, run_players=36,
                            eligible_events=len({o['canonical_event_id'] for o in oo}),
                            lower=cnt['positive']/len(sub), upper=(cnt['positive']+cnt['unknown'])/len(sub),
                            acute_excluded=len(acute), sensitivity_denominator=len(sens),
                            sensitivity_positive=sum(r['absence_run_onset_ge10']=='positive' for r in sens),
                            sensitivity_events=len({o['canonical_event_id'] for o in oo if o['row_id'] not in acute})))
    write(D/'tables/reconciliation.csv', summary)
    prepared = []
    for r in inc:
        x = features(r, fmap[r['batch']][r['row_id']])
        prepared.append(dict(row_id=r['row_id'], player_id=r['player_id'], team=r['team'], lag=r['extra_lag_days'],
                             decision_at=r['decision_at'], label=r['absence_run_onset_ge10'], fold=fold(r['player_id']),
                             **{k: '' if v is None else v for k,v in x.items()}))
    write(D/'tables/analysis_rows.csv', prepared)
    write(D/'tables/player_folds.csv', [dict(player_id=pid, fold=fold(pid)) for pid in sorted({r['player_id'] for r in rr})])
    folds = []
    for lag in ('0','1'):
        for sensitivity in ('all','exclude_MEM_players'):
            mem = {r['player_id'] for r in inc if r['team']=='MEM'}
            pop = [r for r in prepared if r['lag']==lag and (sensitivity=='all' or r['player_id'] not in mem)]
            for f in range(5):
                for role in ('test','train'):
                    rows = [r for r in pop if (r['fold']==f)==(role=='test')]
                    ids={r['row_id'] for r in rows}; players={r['player_id'] for r in rows}
                    oo=[o for o in opp if o['row_id'] in ids]
                    counts=Counter(r['label'] for r in rows)
                    folds.append(dict(lag=lag, sensitivity=sensitivity, fold=f, role=role, rows=len(rows),
                                      players=len(players), positive_players=len({o['player_id'] for o in oo}),
                                      positive_events=len({o['canonical_event_id'] for o in oo}),
                                      **{k:counts[k] for k in ('positive','negative','unknown')}))
                train={r['player_id'] for r in pop if r['fold']!=f};test={r['player_id'] for r in pop if r['fold']==f}
                assert not train & test
    write(D/'tables/fold_counts.csv', folds)
    missing=[]
    for lag in ('0','1'):
        sub=[r for r in prepared if r['lag']==lag]
        for k in FEATURES:
            vals=[float(r[k]) for r in sub if r[k]!='']
            missing.append(dict(lag=lag, feature=k, rows=len(sub), missing=len(sub)-len(vals),
                                min=min(vals) if vals else '', max=max(vals) if vals else '',
                                availability='B assumed; no preprocessing fitted'))
    write(D/'tables/feature_availability.csv',missing)
    selection=[]
    for dimension in ('team','player_id','exposure_band','risk_information'):
        for lag in ('0','1'):
            groups=defaultdict(list)
            for r in prepared:
                if r['lag']!=lag:continue
                key=(r[dimension] if dimension in ('team','player_id') else
                     'missing' if r['past_mean_minutes']=='' else '<20 minutes' if float(r['past_mean_minutes'])<20 else '>=20 minutes') if dimension!='risk_information' else ('missing' if r['recent_evidence_28d']=='' else 'recent' if float(r['recent_evidence_28d'])==1 else 'no recent acquired evidence')
                groups[key].append(r)
            for key, rows in sorted(groups.items()):
                cnt=Counter(r['label'] for r in rows)
                selection.append(dict(lag=lag, dimension=dimension, value=key, rows=len(rows), players=len({r['player_id'] for r in rows}),
                                      **{k:cnt[k] for k in ('positive','negative','unknown')},
                                      any_missing_predictor=sum(any(r[k]=='' for k in FEATURES) for r in rows)))
    write(D/'tables/selection_missingness.csv',selection)
    event_table=[]
    for e in qualifying:
        for lag in ('0','1'):
            oo=sorted([o for o in opp if o['canonical_event_id']==e['canonical_event_id'] and o['extra_lag_days']==lag],key=lambda o:o['decision_at'])
            event_table.append(dict(lag=lag, event=e['canonical_event_id'], player=e['player_name'], player_id=e['player_id'],
                                   team=e['anchor_team'], opportunities=len(oo), earliest=oo[0]['decision_at'] if oo else '',
                                   earliest_lead_lower=oo[0]['lead_days_lower'] if oo else '', earliest_lead_upper=oo[0]['lead_days_upper'] if oo else '',
                                   **{b:sum(o['lead_time_bin']==b for o in oo) for b in ('>0-3d','>3-7d','>7-14d','boundary_uncertain')}))
    write(D/'tables/event_opportunities.csv',event_table)
    disclosure=[]
    # Retrospective relation to same acute event is used ONLY for descriptive ordering.
    for e in qualifying:
        path=ROOT/BATCHES[e['batch']]
        signals=read(path/'tables/recap_signals_B.csv')
        linked=set(e.get('acute_event_game_ids','').split(';'))-{''}
        times=sorted(s['B_available_at'] for s in signals if s['player_id']==e['player_id'] and s['kind']=='acute' and s['event_game_id'] in linked)
        for lag in ('0','1'):
            oo=[o for o in opp if o['canonical_event_id']==e['canonical_event_id'] and o['extra_lag_days']==lag]
            before=[o for o in oo if times and stamp(o['decision_at'])<stamp(times[0])]
            disclosure.append(dict(event=e['canonical_event_id'],lag=lag,first_acquired_same_acute_B_at=times[0] if times else '',
                                   opportunities_before=len(before),supported_order=bool(before),
                                   status='B assumption only; C same-event link' if times else 'no linked acute disclosure found; ordering unverified'))
    write(D/'tables/disclosure_ordering.csv',disclosure)
    # Source flags are intentionally not reduced to the mutually exclusive groups.
    write(D/'tables/opportunities.csv',opp)
    knowledge=[]
    for lag in ('0','1'):
        for g in ('same_acute_event_disclosed','recent_symptoms_or_injury_evidence','prior_acquired_history_without_recent_evidence','no_signal_found_under_bounded_search','unresolved_timing'):
            oo=[o for o in opp if o['extra_lag_days']==lag and o['knowledge_group_B']==g]
            knowledge.append(dict(lag=lag,group=g,rows=len(oo),events=len({o['canonical_event_id'] for o in oo})))
    write(D/'tables/knowledge.csv',knowledge)
    dump(D/'dry_run.json',dict(status='prepared_only',models_fitted=0,preprocessing_fitted=0,protected_periods_accessed=False,
                               independent_human_reviews=0,review_status='pending',timing_issues=0,corrections=0,
                               folds_workable_for_descriptive_planning=all(r['positive_events']>=2 for r in folds if r['role']=='test'),
                               snapshot_verified=True,config_sha256=sha(D/'protocol/config.json')))
    return rr, qualifying, events, summary, folds, event_table, knowledge, missing, disclosure


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--prepare',action='store_true');ap.add_argument('--execute-fit',action='store_true')
    a=ap.parse_args()
    if a.execute_fit:
        raise SystemExit('Fitting refused: Phase 3A preparation only. A later authorized implementation and explicit execution flag are required.')
    if a.prepare:
        snapshot();result=analyze()
        from .review import prepare_review
        from .report import render
        review=prepare_review(*result[:3]);render(result,review)
        dump(D/'artifact_hashes.json',{str(p.relative_to(D)):sha(p) for p in sorted(D.rglob('*')) if p.is_file() and '__pycache__' not in p.parts and p.name != 'artifact_hashes.json'})
    else:
        verify_snapshot();validate_config(config())
        for name,h in json.loads((D/'artifact_hashes.json').read_text()).items():
            if sha(D/name)!=h:raise ValueError('Preparation artifact drift: '+name)
        print((D/'dry_run.json').read_text())

if __name__=='__main__':main()
