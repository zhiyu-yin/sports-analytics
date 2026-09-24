"""Explicit game-level schedule reconciliation; never mutate raw or MATCHUP."""
import json
from pathlib import Path
import pandas as pd
from .validate import validate_and_pair
from .multiseason import digest


def load_approved(root):
    root=Path(root);e=root/'docs/stage1d_evidence'
    for path,expected in json.loads((e/'reconciliation_inputs_sha256.json').read_text()).items():
        if digest(root/path)!=expected:raise ValueError('Reconciliation input checksum mismatch: '+path)
    table=pd.read_csv(e/'home_away_reconciliation.csv',dtype={'game_id':str})
    facts={g['gameId']:g for g in json.loads((e/'source_manifest.json').read_text())['facts']}
    if set(table.game_id)!=set(facts):raise ValueError('Evidence game set mismatch')
    for row in table.itertuples():
        f=facts[row.game_id]
        for side in ['home','away']:
            if getattr(row,'reconciled_'+side+'_team_id')!=f[side+'Team']['teamId'] or getattr(row,'reconciled_'+side+'_team_abbreviation')!=f[side+'Team']['teamTricode']:raise ValueError('Mapping disagrees with authoritative evidence')
        if row.game_date!=f['gameDateEst'][:10] or row.neutral_site!=f['isNeutral'] or row.venue!=f['arenaName']:raise ValueError('Context disagrees with evidence')
    return table


def apply_reconciliation(normalized,approved):
    """Change only is_home in a copy; retain original matchup/observed payload."""
    result=normalized.copy(deep=True)
    if approved.game_id.duplicated().any():raise ValueError('Duplicate reconciliation key')
    _,_,before=validate_and_pair(normalized,season='2024-25')
    applied=[]
    for row in approved.itertuples():
        if row.confidence!='authoritative':raise ValueError('Unresolved/conflicted reconciliation')
        if row.season!='2024-25' or not row.source_url or not row.source_retrieved_at_utc:raise ValueError('Missing reconciliation provenance')
        group=result[result.game_id.eq(row.game_id)]
        reasons=set(before.loc[before.game_id.eq(row.game_id)&before.severity.eq('reject'),'reason'])
        if reasons!={'not_one_home_and_one_away'}:raise ValueError('Mapping must target only the reviewed home/away anomaly')
        if len(group)!=2 or group.team_id.nunique()!=2:raise ValueError('Expected two distinct source teams')
        if not group.game_date.eq(pd.Timestamp(row.game_date)).all():raise ValueError('Reconciliation date mismatch')
        actual=dict(zip(group.team_id,group.matchup))
        if actual!={row.raw_team_1_id:row.raw_team_1_matchup,row.raw_team_2_id:row.raw_team_2_matchup}:raise ValueError('Raw matchup evidence mismatch')
        if {row.reconciled_home_team_id,row.reconciled_away_team_id}!=set(group.team_id):raise ValueError('Reconciliation team mismatch')
        for side in ['home','away']:
            tid=getattr(row,'reconciled_'+side+'_team_id');abbr=getattr(row,'reconciled_'+side+'_team_abbreviation')
            mask=result.game_id.eq(row.game_id)&result.team_id.eq(tid)
            if not result.loc[mask,'team_abbreviation'].eq(abbr).all():raise ValueError('Reconciliation abbreviation mismatch')
            result.loc[mask,'is_home']=side=='home'
        applied.append(row.game_id)
    # No other normalized source value can change, including scores and W/L.
    pd.testing.assert_frame_equal(normalized.drop(columns='is_home'),result.drop(columns='is_home'),check_exact=True)
    return result,applied
