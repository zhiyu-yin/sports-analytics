import unittest
from anthropometrics_shooting.normalize import inches,season
from anthropometrics_shooting.combine import normalize as normalize_combine
from anthropometrics_shooting.provenance import tables
from anthropometrics_shooting.identities import classify
from anthropometrics_shooting.validate import anthropometrics,shooting
from anthropometrics_shooting.shooting import normalize
class AuditTests(unittest.TestCase):
    def test_units(self):
        self.assertEqual(inches('6\' 7.5"'),79.5)
        self.assertAlmostEqual(inches(203.2,'cm'),80)
        with self.assertRaises(ValueError): inches('6\' 12"')
        with self.assertRaises(ValueError): season('2022-24')
    def test_no_false_name_links(self):
        players=[dict(player_id='1',player_name='José Smith Jr.'),dict(player_id='2',player_name='Alex Smith'),dict(player_id='3',player_name='Alex Smith')]
        rows=[dict(player_id=None,player_name='Jose Smith Jr'),dict(player_id='9',player_name='Jose Smith Jr'),dict(player_id=None,player_name='Alex Smith'),dict(player_id=None,player_name='Jose Smith')]
        self.assertEqual([r['join_status'] for r in classify(rows,players)],['exact normalized name','manually reviewable','ambiguous','unmatched'])
    def test_placeholder_and_nba_display(self):
        self.assertIsNone(normalize_combine({'PLAYER_ID':'-1'})['player_id'])
        self.assertEqual(inches("6' 8.25''"),80.25)
        self.assertIsNone(inches('NaN'))
    def test_empty_is_not_failure(self):
        import json
        result=tables(json.dumps({'resultSets':[{'name':'sample','headers':['ID'],'rowSet':[]}]}))
        self.assertEqual(result['sample']['row_count'],0)
        with self.assertRaises(ValueError): tables('{}')
        with self.assertRaises(ValueError): tables(json.dumps({'resultSets':[{'name':'sample','headers':['ID'],'rowSet':[[1,2]]}]}))
    def test_duplicate_id_ambiguous(self):
        p=dict(player_id='1',player_name='Example')
        self.assertEqual(classify([p],[p,p])[0]['join_status'],'ambiguous')
    def test_counts(self):
        self.assertIn('FTM:invalid_counts',shooting({'FTM':6,'FTA':5}))
        self.assertIn('FT_PCT:disagreement',shooting({'FTM':4,'FTA':5,'FT_PCT':.7}))
        self.assertIsNone(normalize({'PLAYER_ID':1,'FTM':0,'FTA':0},'2022-23')['ftm_pct'])
    def test_short_wingspan_retained(self):
        self.assertEqual(anthropometrics(dict(height_inches=80,wingspan_inches=79)),[])
if __name__=='__main__': unittest.main()
