import ast,csv,json,math,unittest
from pathlib import Path
from anthropometrics_shooting.stage0b import eligibility,select_measurement,valid_counts,validate_frozen,QUARANTINE
from anthropometrics_shooting.normalize import inches
from anthropometrics_shooting.stage0b_io import ROOT,E,sha

def measurement(pid='1',year=2013,h=78,w=82):
    return dict(PLAYER_ID=pid,PLAYER_NAME='Combine alias',SEASON=str(year),HEIGHT_WO_SHOES=h,WINGSPAN=w)
def nba(pid='1',fta=1,ftm=1):
    return dict(player_id=pid,player_name='NBA alias',seconds=60,FTM=ftm,FTA=fta,FG3M=0,FG3A=0)

class EligibilityTests(unittest.TestCase):
    def test_exact_id_priority_over_name_conflict(self):
        row,reasons=eligibility(nba(),[measurement(),measurement('2')],True)
        self.assertEqual(row['PLAYER_ID'],'1');self.assertEqual(reasons,[])
    def test_unresolved_identity_excluded(self):
        row,reasons=eligibility(nba(),[measurement('2')],True)
        self.assertIsNone(row);self.assertIn('unresolved_identity_conflict',reasons)
    def test_no_name_or_fuzzy_auto_match(self):
        n=nba();n['player_name']='Combine alias'
        self.assertIsNone(eligibility(n,[measurement('2')])[0])
        n['player_name']='Combine aliaz'
        self.assertIsNone(eligibility(n,[measurement('2')])[0])
    def test_latest_complete_prior(self):
        row,reasons=select_measurement([measurement(year=2011),measurement(year=2013),measurement(year=2014)])
        self.assertEqual(row['SEASON'],'2013');self.assertEqual(reasons,[])
    def test_latest_incomplete_uses_earlier_complete(self):
        row,_=select_measurement([measurement(year=2011),measurement(year=2013,h=None)])
        self.assertEqual(row['SEASON'],'2011')
    def test_only_future_measurement_excluded(self):
        self.assertEqual(select_measurement([measurement(year=2014)])[1],['post-season-only measurement'])
    def test_duplicate_same_year_rejected(self):
        self.assertEqual(select_measurement([measurement(),measurement()])[1],['duplicate_measurement_record'])
    def test_units(self):
        self.assertEqual(inches("6' 8.25''"),80.25);self.assertAlmostEqual(inches(203.2,'cm'),80)
        with self.assertRaises(ValueError):inches('6\' 12"')
    def test_all_four_discrepancies_quarantined(self):
        for pid,year in QUARANTINE:
            row,reasons=select_measurement([measurement(pid,year)],cutoff=2019)
            self.assertIsNone(row);self.assertIn('unresolved_measurement_conflict',reasons)
    def test_counts_makes_cannot_exceed_attempts(self):
        self.assertFalse(valid_counts(2,1));self.assertTrue(valid_counts(1,1))
    def test_counts_nonnegative_integer_finite(self):
        for m,a in [(-1,2),(1,1.5),(None,1),(1,float('inf')),(float('nan'),1)]:self.assertFalse(valid_counts(m,a))
    def test_zero_attempts_retained_for_accounting(self):
        self.assertEqual(eligibility(nba(fta=0,ftm=0),[measurement()])[1],[])
    def test_reason_logging_multiple_failures(self):
        n=nba(ftm=2,fta=1);n['seconds']=0
        self.assertEqual(eligibility(n,[measurement(h=None,w=None)])[1],['invalid_ft_counts','missing_height','missing_wingspan','no_positive_minutes'])
    def test_shorter_wingspan_allowed(self):
        self.assertEqual(eligibility(nba(),[measurement(h=80,w=79)])[1],[])
    def test_invalid_id_not_joined(self):
        self.assertIn('invalid_player_id',eligibility(nba('-1'),[measurement('-1')])[1])

class FrozenEvidenceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        import pyarrow.parquet as pq
        cls.rows=pq.read_table(ROOT/'data/processed/ft_2013_14_stage1_dataset.parquet').to_pylist()
    def test_unique_one_row_per_player(self):
        self.assertTrue(validate_frozen(self.rows));self.assertEqual(len(self.rows),311)
        with self.assertRaises(ValueError):validate_frozen(self.rows+[self.rows[0]])
    def test_no_future_measurement(self):
        self.assertTrue(all(r['combine_year']<=2013 for r in self.rows))
        with self.assertRaises(ValueError):validate_frozen([dict(self.rows[0],combine_year=2014)])
    def test_zero_attempt_likelihood_flag(self):
        zero=[r for r in self.rows if r['fta']==0];self.assertEqual(len(zero),12)
        self.assertTrue(all(not r['binomial_likelihood_eligible'] and r['ftm']==0 for r in zero))
    def test_every_roster_candidate_accounted_once(self):
        excluded=list(csv.DictReader((ROOT/'data/interim/ft_2013_14_exclusions.csv').open()))
        roster=list(csv.DictReader((ROOT/'data/interim/stage0b_nba_2013_14_totals.csv').open()))
        ids=[r['player_id'] for r in self.rows+excluded]
        self.assertEqual(len(ids),len(set(ids)));self.assertEqual(set(ids),{r['player_id'] for r in roster})
        self.assertTrue(all(r['reason_codes'] for r in excluded))
    def test_unresolved_crosswalk_links_not_used(self):
        conflicts=list(csv.DictReader((E/'identity_crosswalk_review.csv').open()))
        self.assertEqual(len(conflicts),21)
        from anthropometrics_shooting.stage0b_io import archive,E0
        combine=archive(json.loads((E0/'archive_sources.json').read_text())[0])
        for c in conflicts:
            retained=[r for r in self.rows if r['player_id']==c['shooting_source_id']]
            for r in retained:
                exact=[m for m in combine if m['PLAYER_ID']==r['player_id'] and int(m['SEASON'])==r['combine_year']]
                self.assertEqual(len(exact),1)
                self.assertNotEqual(exact[0]['PLAYER_ID'],c['combine_source_id'])
                self.assertEqual(r['player_name_combine'],exact[0]['PLAYER_NAME'])
    def test_original_names_and_no_residual(self):
        self.assertTrue(all(r['player_name_nba'] and r['player_name_combine'] for r in self.rows))
        self.assertTrue(all('residual_wingspan' not in r for r in self.rows))
    def test_frozen_hash_and_source_checksums(self):
        build=json.loads((E/'build_manifest.json').read_text())
        self.assertEqual(sha(ROOT/build['dataset']),build['dataset_sha256'])
        sources=json.loads((E/'source_manifest.json').read_text())
        for path,h in sources['normalized_outputs'].items():self.assertEqual(sha(ROOT/path),h,path)
        for m in sources['sources']:
            if m.get('raw_path'):self.assertEqual(sha(ROOT/m['raw_path']),m.get('raw_sha256',m.get('sha256')))
    def test_stage0_preserved(self):
        for path,h in json.loads((E/'stage0_preservation_manifest.json').read_text()).items():self.assertEqual(sha(ROOT/path),h,path)
    def test_reference_temporally_frozen_unique(self):
        rows=list(csv.DictReader((ROOT/'data/interim/residual_reference_pre2013.csv').open()))
        self.assertEqual(len(rows),960);self.assertEqual(len({r['player_id'] for r in rows}),960)
        self.assertTrue(all(int(r['combine_year'])<=2013 for r in rows))
    def test_shooting_official_and_internal_checks(self):
        rows=list(csv.DictReader((E/'shooting_official_crosscheck.csv').open()))
        self.assertEqual(len(rows),72);self.assertFalse(any(r['match_status']=='conflict' for r in rows))
        m=json.loads((E/'shooting_internal_reconstruction.json').read_text())
        self.assertTrue(m['all_player_totals_reconstruct_exactly']);self.assertTrue(m['GSW_exact_match'])
    def test_no_scientific_association_calls_in_pipeline(self):
        # Static guard over all project modules and Stage 0B scripts; descriptive sums allowed.
        forbidden={'corr','corrcoef','correlate','pearsonr','spearmanr','kendalltau','linregress','polyfit','lstsq','ols','OLS','GLM','Logit','fit','ttest_ind','pearson','spearman'}
        libraries={'scipy','statsmodels','sklearn'}
        paths=list((ROOT/'src/anthropometrics_shooting').glob('*.py'))+list((ROOT/'scripts').glob('*stage0b*.py'))
        for path in paths:
            tree=ast.parse(path.read_text())
            for node in ast.walk(tree):
                if isinstance(node,ast.Call):self.assertNotIn(getattr(node.func,'attr',getattr(node.func,'id','')),forbidden,str(path))
                if isinstance(node,(ast.Import,ast.ImportFrom)):
                    names=[a.name for a in node.names] if isinstance(node,ast.Import) else [node.module or '']
                    self.assertFalse(any(n.split('.')[0] in libraries for n in names),str(path))
if __name__=='__main__':unittest.main()
