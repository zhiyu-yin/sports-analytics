"""Tiny synthetic 2023-24 fixtures only. These tests never query the network."""
import copy
from hashlib import sha256
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from nba_game_prediction.ingest import PARAMETERS, extract_table, retrieve
from nba_game_prediction.normalize import normalize, parse_matchup
from nba_game_prediction.validate import validate_and_pair


def fixture():
    common = dict(SEASON_ID='22023',GAME_ID='0022300001',GAME_DATE='2023-11-01',
                  FGA=90,FG3A=30,FTA=20,OREB=10,DREB=30,REB=40,AST=20,STL=5,BLK=3,TOV=10,PF=15)
    home = dict(common,TEAM_ID=1610612747,TEAM_NAME='Los Angeles Lakers',TEAM_ABBREVIATION='LAL',MATCHUP='LAL vs. BOS',WL='W',PTS=110,FGM=40,FG3M=10,FTM=20,PLUS_MINUS=10)
    away = dict(common,TEAM_ID=1610612738,TEAM_NAME='Boston Celtics',TEAM_ABBREVIATION='BOS',MATCHUP='BOS @ LAL',WL='L',PTS=100,FGM=35,FG3M=10,FTM=20,PLUS_MINUS=-10)
    return [home,away]


def body(rows):
    columns=list(rows[0])
    return json.dumps({'resultSets':[{'name':'LeagueGameLog','headers':columns,'rowSet':[[r.get(c) for c in columns] for r in rows]}]}).encode()


def run(rows):
    return validate_and_pair(normalize(body(rows)))


class NormalizationTests(unittest.TestCase):
    def test_home_and_away(self):
        self.assertEqual(parse_matchup('LAL vs. BOS','LAL'),(True,'BOS'))
        self.assertEqual(parse_matchup('BOS @ LAL','BOS'),(False,'LAL'))

    def test_malformed_matchups(self):
        for value,abbr in [('LAL-BOS','LAL'),('LAL vs. LAL','LAL'),('LAL vs. BOS','BOS'),(None,'LAL')]:
            with self.subTest(value=value),self.assertRaises(ValueError): parse_matchup(value,abbr)

    def test_pairing_independent_of_row_order(self):
        teams,games,anomalies=run(list(reversed(fixture())))
        self.assertEqual(len(teams),2);self.assertTrue(anomalies.empty)
        self.assertEqual(games.iloc[0]['home_team_id'],1610612747)
        self.assertEqual(games.iloc[0]['game_id'],'0022300001')
        self.assertTrue(games.iloc[0]['home_win'])

    def test_away_win(self):
        rows=fixture()
        for r in rows: r['WL']='L' if r['WL']=='W' else 'W';r['PLUS_MINUS']=-r['PLUS_MINUS']
        rows[0]['PTS'],rows[0]['FGM']=100,35
        rows[1]['PTS'],rows[1]['FGM']=110,40
        self.assertFalse(run(rows)[1].iloc[0]['home_win'])

    def rejected(self,rows,reason):
        teams,games,anomalies=run(rows)
        self.assertTrue(teams.empty);self.assertTrue(games.empty)
        self.assertIn(reason,set(anomalies.loc[anomalies['severity']=='reject','reason']))
        self.assertTrue(all(json.loads(v) for v in anomalies['observed_values_json']))

    def test_duplicate_detection(self):
        rows=fixture();rows.append(copy.deepcopy(rows[0]))
        self.rejected(rows,'duplicate_team_game')

    def test_missing_opponent_row(self): self.rejected(fixture()[:1],'not_exactly_two_rows')

    def test_reciprocal_team_validation(self):
        rows=fixture();rows[1]['MATCHUP']='BOS @ NYK'
        self.rejected(rows,'nonreciprocal_opponents')

    def test_two_home_rows(self):
        rows=fixture();rows[1]['MATCHUP']='BOS vs. LAL'
        self.rejected(rows,'not_one_home_and_one_away')

    def test_same_team_id(self):
        rows=fixture();rows[1]['TEAM_ID']=rows[0]['TEAM_ID']
        self.rejected(rows,'not_two_distinct_teams')

    def test_different_dates(self):
        rows=fixture();rows[1]['GAME_DATE']='2023-11-02'
        self.rejected(rows,'game_date_mismatch_or_missing')

    def test_bad_date_not_silently_coerced(self):
        rows=fixture();rows[0]['GAME_DATE']='11/01/2023'
        self.rejected(rows,'invalid_game_date')

    def test_missing_result(self):
        rows=fixture();rows[0]['WL']=None
        self.rejected(rows,'not_completed_or_invalid_wl')

    def test_noncomplementary_wl(self):
        rows=fixture();rows[1]['WL']='W'
        self.rejected(rows,'noncomplementary_wl')

    def test_tie_is_not_a_completed_binary_outcome(self):
        rows=fixture();rows[0]['PTS']=100;rows[0]['FGM']=35
        self.rejected(rows,'tied_final_score')

    def test_score_wl_disagree(self):
        rows=fixture();rows[0]['WL']='L';rows[1]['WL']='W'
        self.rejected(rows,'score_wl_mismatch')

    def test_scoring_components(self):
        rows=fixture();rows[0]['PTS']=111
        self.rejected(rows,'points_do_not_match_scoring_components')

    def test_optional_plus_minus_is_not_authoritative(self):
        rows=fixture();rows[0]['PLUS_MINUS']=999
        teams,games,anomalies=run(rows)
        self.assertEqual(len(games),1)
        self.assertEqual(anomalies.iloc[0]['severity'],'warning')
        self.assertEqual(anomalies.iloc[0]['reason'],'plus_minus_score_mismatch')
        self.assertEqual(teams.loc[teams['is_home'],'plus_minus'].iloc[0],999)

    def test_optional_missing_fields_remain_null_and_flagged(self):
        rows=fixture();rows[0]['AST']=None
        teams,games,anomalies=run(rows)
        self.assertEqual(len(games),1)
        self.assertEqual(int(teams['ast'].isna().sum()),1)
        self.assertIn('missing_optional_ast',set(anomalies['reason']))

    def test_bad_score_type(self):
        for value in [None,True,-1,1.5,'110']:
            with self.subTest(value=value):
                rows=fixture();rows[0]['PTS']=value
                self.rejected(rows,'invalid_pts')

    def test_wrong_season_and_postseason(self):
        rows=fixture();rows[0]['SEASON_ID']='42023'
        self.rejected(rows,'out_of_scope_season_id')
        rows=fixture()
        for r in rows:r['GAME_ID']='0042300001'
        self.rejected(rows,'out_of_scope_game_type_or_season')

    def test_cup_championship(self):
        rows=fixture()
        for r in rows:r['GAME_DATE']='2023-12-09'
        self.rejected(rows,'cup_championship_date_requires_reconciliation')

    def test_invalid_game_id_is_not_padded(self):
        rows=fixture();rows[0]['GAME_ID']=22300001
        self.rejected(rows,'invalid_game_id')

    def test_malformed_response_schema(self):
        with self.assertRaises(ValueError):
            extract_table(b'{"resultSets":[{"name":"LeagueGameLog","headers":["PTS"],"rowSet":[[1]]}]}')


class CacheTests(unittest.TestCase):
    def cache(self,directory):
        raw=body(fixture());p=Path(directory)
        (p/'raw.json').write_bytes(raw)
        cols,rows=extract_table(raw)
        meta=dict(parameters=PARAMETERS,endpoint='LeagueGameLog',http_status=200,raw_file='raw.json',sha256=sha256(raw).hexdigest(),row_count=len(rows),columns=cols)
        (p/'leaguegamelog_full_fixture.manifest.json').write_text(json.dumps(meta))
        return raw

    def test_cache_avoids_network_even_with_fetch_allowed(self):
        with tempfile.TemporaryDirectory() as d:
            expected=self.cache(d)
            with patch('requests.sessions.Session.request',side_effect=AssertionError('Network forbidden')):
                raw,_,cached=retrieve(d,allow_network=True)
            self.assertTrue(cached);self.assertEqual(raw,expected)

    def test_corrupt_cache_fails_without_network_repair(self):
        with tempfile.TemporaryDirectory() as d:
            self.cache(d);(Path(d)/'raw.json').write_bytes(b'corrupt')
            with patch('requests.sessions.Session.request',side_effect=AssertionError('Network forbidden')):
                with self.assertRaisesRegex(ValueError,'checksum'):retrieve(d,allow_network=True)

    def test_empty_cache_defaults_to_no_network(self):
        with tempfile.TemporaryDirectory() as d,self.assertRaises(FileNotFoundError):retrieve(d)

    def test_cache_scope_mismatch_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            self.cache(d);p=Path(d)/'leaguegamelog_full_fixture.manifest.json'
            meta=json.loads(p.read_text());meta['parameters']['SeasonType']='Playoffs';p.write_text(json.dumps(meta))
            with self.assertRaisesRegex(ValueError,'parameters'):retrieve(d)


if __name__=='__main__':unittest.main()
