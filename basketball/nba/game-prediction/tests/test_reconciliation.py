"""Structural reconciliation on invented games/teams/results only."""
from pathlib import Path
import sys,unittest,json
from unittest.mock import patch
import pandas as pd
from pandas.testing import assert_frame_equal
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from test_ingestion import body
from nba_game_prediction.normalize import normalize
from nba_game_prediction.validate import validate_and_pair
from nba_game_prediction.reconciliation import apply_reconciliation,load_approved
from nba_game_prediction.features import build_features
from nba_game_prediction.sealed_access import checksum
ROOT=Path(__file__).resolve().parents[1]
REGISTRY=[dict(id=9000001,abbreviation='AAA'),dict(id=9000002,abbreviation='BBB')]

def synthetic_history():
    rows=[];maps=[]
    for i,date in enumerate(pd.date_range('2024-11-01',periods=12)):
        gid=f'002249{i:04d}'
        for tid,abbr,other,home in [(9000001,'AAA','BBB',False),(9000002,'BBB','AAA',True)]:
            won=(i%2==0)==home
            rows.append(dict(SEASON_ID='22024',GAME_ID=gid,GAME_DATE=str(date.date()),TEAM_ID=tid,TEAM_NAME='Synthetic '+abbr,TEAM_ABBREVIATION=abbr,MATCHUP=f'{abbr} '+('vs.' if home and i!=2 else '@')+f' {other}',WL='W' if won else 'L',PTS=110 if won else 100,FGM=40 if won else 35,FG3M=10,FTM=20,FGA=90,FG3A=30,FTA=20,OREB=10,DREB=30,REB=40,AST=20,STL=5,BLK=3,TOV=10,PF=15,PLUS_MINUS=10 if won else -10))
        if i==2:maps.append(dict(season='2024-25',game_id=gid,game_date=str(date.date()),confidence='authoritative',source_url='https://synthetic.invalid/schedule',source_retrieved_at_utc='synthetic fixture',raw_team_1_id=9000001,raw_team_1_matchup='AAA @ BBB',raw_team_2_id=9000002,raw_team_2_matchup='BBB @ AAA',reconciled_home_team_id=9000002,reconciled_home_team_abbreviation='BBB',reconciled_away_team_id=9000001,reconciled_away_team_abbreviation='AAA',neutral_site=True))
    return normalize(body(rows),season='2024-25'),pd.DataFrame(maps)

class ReconciliationTests(unittest.TestCase):
    def setUp(self):
        self.registry=patch('nba_game_prediction.validate.get_teams',return_value=REGISTRY);self.registry.start();self.addCleanup(self.registry.stop)
        self.norm,self.approved=synthetic_history();self.fixed,self.applied=apply_reconciliation(self.norm,self.approved)
        self.teams,self.games,self.anomalies=validate_and_pair(self.fixed,season='2024-25')
    def test_input_immutable(self):
        baseline=self.norm.copy(deep=True);apply_reconciliation(self.norm,self.approved);assert_frame_equal(baseline,self.norm,check_exact=True)
    def test_explicit_only(self):
        x,a=apply_reconciliation(self.norm,self.approved.iloc[:0]);_,g,errors=validate_and_pair(x,season='2024-25');self.assertEqual(len(g),11);self.assertEqual(a,[]);self.assertEqual(errors.game_id.nunique(),1)
    def test_approved_mapping(self):
        g=self.games.set_index('game_id').loc[self.applied[0]];self.assertEqual(g.home_team_id,9000002);self.assertEqual(g.away_team_id,9000001)
    def test_reciprocal_pairing(self):
        self.assertEqual(len(self.games),12);self.assertTrue(self.anomalies.empty);self.assertTrue(self.teams.groupby('game_id').is_home.sum().eq(1).all())
    def test_only_is_home_changes(self):assert_frame_equal(self.norm.drop(columns='is_home'),self.fixed.drop(columns='is_home'),check_exact=True)
    def test_complete_downstream_history(self):
        tf,_=build_features(self.teams,self.games,self.games[['game_id','home_pts','away_pts','home_win']].copy())
        for tid,t in self.teams.groupby('team_id'):
            t=t.sort_values('game_date');f=tf[tf.team_id.eq(tid)].sort_values('game_date');self.assertEqual(f.games_played_before.tolist(),list(range(12)))
            self.assertEqual(f.iloc[5].pts_for_avg_last_5,float(t.iloc[:5].pts.mean()));self.assertEqual(f.iloc[5].win_pct_last_5,float(t.iloc[:5].wl.eq('W').mean()))
    def test_future_reconciliation_invariance(self):
        cut=self.norm.game_date.min()+pd.Timedelta(days=2);before=self.norm[self.norm.game_date.lt(cut)]
        fixed,_=apply_reconciliation(before,self.approved.iloc[:0]);assert_frame_equal(fixed,self.fixed[self.fixed.game_date.lt(cut)],check_exact=True)
    def test_conflicted_mapping(self):
        for status in ['unresolved','conflicted']:
            a=self.approved.assign(confidence=status)
            with self.assertRaises(ValueError):apply_reconciliation(self.norm,a)
    def test_neutral_flag_and_matchup_preserved(self):
        a=self.approved.copy();apply_reconciliation(self.norm,a);assert_frame_equal(a,self.approved);self.assertTrue(a.neutral_site.all());self.assertEqual(set(self.fixed[self.fixed.game_id.eq(self.applied[0])].matchup),{'AAA @ BBB','BBB @ AAA'})
    def test_wrong_date(self):
        with self.assertRaises(ValueError):apply_reconciliation(self.norm,self.approved.assign(game_date='2024-11-04'))
    def test_wrong_raw_label(self):
        with self.assertRaises(ValueError):apply_reconciliation(self.norm,self.approved.assign(raw_team_1_matchup='AAA vs. BBB'))
    def test_duplicate_evidence(self):
        with self.assertRaises(ValueError):apply_reconciliation(self.norm,pd.concat([self.approved,self.approved]))
    def test_other_anomaly_not_repaired(self):
        n=self.norm.copy();n.loc[n.game_id.eq(self.applied[0]),'pts']=999
        with self.assertRaises(ValueError):apply_reconciliation(n,self.approved)
    def test_historical_evidence_hashes_unchanged(self):
        hashes=json.loads((ROOT/'docs/stage4a_evidence/protected_artifact_hashes_before.json').read_text())
        for p,h in hashes.items():
            if p.startswith('docs/stage1d'):self.assertEqual(checksum(ROOT/p),h)
