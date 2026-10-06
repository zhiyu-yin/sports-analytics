import ast,csv,json,unittest,copy
from unittest.mock import patch
from anthropometrics_shooting.stage0c import *

def record(pid='1',year=2013,h=78,w=82):
    return dict(PLAYER_ID=pid,PLAYER_NAME='Example',SEASON=str(year),HEIGHT_WO_SHOES=h,WINGSPAN=w)
def sampled():return dict(player_id='1',combine_year=2013,archive_barefoot_height=78,archive_wingspan=82)
def observation():return dict(player_id='1',combine_year=2013,barefoot_height=78,wingspan=82,precision=.25)

class Stage0CUnitTests(unittest.TestCase):
    def test_same_player_required(self):
        with self.assertRaises(ValueError):pair_check(sampled(),dict(observation(),player_id='2'))
    def test_same_year_required(self):
        with self.assertRaises(ValueError):pair_check(sampled(),dict(observation(),combine_year=2012))
    def test_later_year_cannot_validate_earlier(self):
        with self.assertRaises(ValueError):pair_check(sampled(),dict(observation(),combine_year=2014))
    def test_shoe_height_is_not_barefoot(self):
        o=observation();o.pop('barefoot_height');o['shoe_height']=78
        self.assertEqual(pair_check(sampled(),o),('official_value_missing','exact','official_value_missing'))
    def test_unavailable_not_disagreement(self):
        self.assertEqual(pair_check(sampled(),None),('official_source_unavailable',)*3)
    def test_available_missing_not_disagreement(self):
        self.assertEqual(field_status(78,None),'official_value_missing')
    def test_rounding_boundary_inclusive(self):
        self.assertEqual(field_status(78,78.125),'rounding_consistent')
        self.assertEqual(field_status(78,77.875),'rounding_consistent')
    def test_rounding_over_boundary_rejected(self):
        self.assertEqual(field_status(78,78.12501),'conflict')
    def test_coarse_precision_not_rounded_into_agreement(self):
        self.assertEqual(field_status(78,78.1,precision=1),'conflict')
    def test_exact_pair(self):self.assertEqual(pair_check(sampled(),observation()),('exact',)*3)
    def test_conflict_preserved_without_correction(self):
        r=sampled();o=dict(observation(),wingspan=83);before=copy.deepcopy((r,o))
        self.assertEqual(pair_check(r,o)[2],'conflict');self.assertEqual((r,o),before)
    def test_quarantined_discrepancy_excluded(self):
        for pid,y in QUARANTINE:self.assertEqual(reference([record(pid,y)],cutoff=2019),[])
    def test_latest_complete_pre2014(self):
        rs=[record(year=2011),record(year=2012),record(year=2013,h=None),record(year=2014)]
        self.assertEqual(reference(rs)[0]['SEASON'],'2012')
    def test_no_post2013(self):self.assertEqual(reference([record(year=2014)]),[])
    def test_no_missing_id_placeholders(self):
        for pid in ['-1','0','',None,'NaN']:self.assertEqual(reference([record(pid)]),[])
    def test_duplicate_latest_rejected(self):
        with self.assertRaises(ValueError):reference([record(),record()])
    def test_sampling_reads_anthropometrics_only(self):
        class Guard(dict):
            def __getitem__(self,key):
                if key in ['FTM','FTA','FG3M','FG3A','FT_PCT']:raise AssertionError('Outcome accessed')
                return super().__getitem__(key)
            def get(self,key,*args):
                if key in ['FTM','FTA','FG3M','FG3A','FT_PCT']:raise AssertionError('Outcome accessed')
                return super().get(key,*args)
        rows,_=read_combine();a,b=sample([Guard(r) for r in rows]);self.assertEqual(len(a),45)
    def test_replacement_stays_in_full_stratum(self):
        rows,_=read_combine();chosen,reserve=sample(rows);original=chosen[0]
        r=replacement(original,reserve,set())
        for k in ['sampling_era_stratum','sampling_height_stratum','sampling_relative_wingspan_stratum']:self.assertEqual(r[k],original[k])
    def test_replacement_does_not_reuse_player(self):
        rows,_=read_combine();chosen,reserve=sample(rows);first=replacement(chosen[0],reserve,set())
        nxt=replacement(chosen[0],reserve,{(first['player_id'],first['combine_year'])})
        self.assertNotEqual(first['player_id'],nxt['player_id'])
    def test_no_shooting_column_requested_from_candidate(self):
        class Result:
            def to_pylist(self):return []
        def reader(path,*,columns):
            self.assertEqual(columns,['player_id','player_name_nba','season']);return Result()
        self.assertEqual(candidate_identities(reader),[])
    def test_combine_import_materializes_only_measurement_columns(self):
        import pyarrow.csv as pc
        original=pc.read_csv
        def spy(*args,**kwargs):
            columns=kwargs['convert_options'].include_columns
            self.assertTrue(columns)
            self.assertTrue(all(c.startswith(('PLAYER','SEASON','POSITION','HEIGHT','WINGSPAN','STANDING','WEIGHT')) for c in columns))
            return original(*args,**kwargs)
        with patch.object(pc,'read_csv',side_effect=spy):rows,_=read_combine()
        self.assertNotIn('SPOT_FIFTEEN_CORNER_LEFT',rows[0])
    def test_fractional_inches_without_leading_zero(self):self.assertEqual(source_inches("8' .25''"),96.25)
    def test_systematic_offset_rule(self):
        rs=[dict(height_difference_inches=.25,wingspan_difference_inches=0,sampling_era_stratum='early',sampling_height_stratum='short') for _ in range(3)]
        self.assertTrue(systematic_discrepancies(rs));self.assertFalse(systematic_discrepancies(rs[:2]))

class Stage0CEvidenceTests(unittest.TestCase):
    def test_predeclaration_precedes_successful_retrieval(self):
        stamp=json.loads((E/'release_rule_predeclared.json').read_text())['declared_at']
        sources=json.loads((E/'browser_capture_manifest.json').read_text())
        self.assertTrue(all(stamp<m['retrieval_timestamp_utc'] for m in sources))
    def test_original_sample_45_no_replacements(self):
        summary=json.loads((E/'validation_summary.json').read_text());self.assertEqual(summary['preselected_players'],45);self.assertEqual(summary['sample_replacements'],0)
    def test_cross_era_and_body_coverage(self):
        rows=list(csv.DictReader((E/'agreement_by_stratum.csv').open()))
        self.assertEqual(len(rows),9);self.assertTrue(all(int(r['complete_pairs'])>0 for r in rows))
    def test_every_primary_pair_exact(self):
        rows=list(csv.DictReader((E/'anthro_barefoot_wingspan_crosscheck.csv').open()))
        self.assertEqual(len(rows),45);self.assertTrue(all(r['pair_status']=='exact' for r in rows))
    def test_reference_membership_hash_unchanged(self):
        h=json.loads((E/'reference_population_hash.json').read_text())
        self.assertEqual(sha(ROOT/h['original_path']),h['sha256']);self.assertEqual(sha(ROOT/h['snapshot_path']),h['sha256'])
        old=json.loads((ROOT/'docs/stage0b_evidence/build_manifest.json').read_text())
        self.assertEqual(h['sha256'],old['residual_reference_sha256'])
    def test_reference_population_clean(self):
        s=json.loads((E/'reference_population_summary.json').read_text())
        self.assertEqual(s['participants'],960);self.assertEqual(s['direct_official_pairs'],960)
        for key in ['post2013_records','missing_id_placeholders','quarantined_records','repeated_eligible_ids']:self.assertEqual(s[key],0)
    def test_prior_evidence_and_candidate_unchanged(self):
        for path,h in json.loads((E/'prior_preservation_manifest.json').read_text()).items():self.assertEqual(sha(ROOT/path),h,path)
    def test_source_captures_checksums(self):
        for m in json.loads((E/'browser_capture_manifest.json').read_text()):self.assertEqual(sha(ROOT/m['raw_path']),m['raw_sha256'])
    def test_stale_capture_excluded(self):
        m=json.loads((E/'browser_capture_manifest.json').read_text())
        self.assertEqual(sum(not r['accepted'] for r in m),1);self.assertEqual(sum(r['accepted'] for r in m),15)
    def test_candidate_coverage_only_identity_and_source_fields(self):
        rows=list(csv.DictReader((E/'candidate_population_source_coverage.csv').open()))
        self.assertEqual(len(rows),311);self.assertEqual(len({r['player_id'] for r in rows}),311)
        self.assertTrue(all(r['source_coverage']=='direct_official_pair_corroboration' for r in rows))
        self.assertFalse({'ftm','fta','fg3m','fg3a','residual_wingspan'}&set(rows[0]))
    def test_no_model_or_association_calls(self):
        forbidden={'fit','corr','corrcoef','pearsonr','spearmanr','kendalltau','polyfit','lstsq','linregress','OLS','ols','GLM','Logit','ttest_ind','curve_fit'}
        forbidden_modules={'statsmodels','scipy','sklearn','numpy','pandas'}
        paths=[ROOT/'src/anthropometrics_shooting/stage0c.py']+list((ROOT/'scripts').glob('*stage0c*.py'))
        for path in paths:
            for n in ast.walk(ast.parse(path.read_text())):
                if isinstance(n,ast.Call):self.assertNotIn(getattr(n.func,'attr',getattr(n.func,'id','')),forbidden,str(path))
                if isinstance(n,(ast.Import,ast.ImportFrom)):
                    names=[a.name for a in n.names] if isinstance(n,ast.Import) else [n.module or '']
                    self.assertFalse(any(x.split('.')[0] in forbidden_modules for x in names),str(path))
    def test_no_residual_output(self):
        rows=list(csv.DictReader((ROOT/'data/interim/stage0c_reference_membership.csv').open()))
        self.assertEqual(set(rows[0]),{'player_id','combine_year','height_wo_shoes_inches','wingspan_inches'})
    def test_normalized_output_hashes(self):
        for path,h in json.loads((E/'build_manifest.json').read_text())['normalized_sha256'].items():self.assertEqual(sha(ROOT/path),h,path)
    def test_four_display_values_confirmed(self):
        rows=list(csv.DictReader((E/'measurement_discrepancy_review.csv').open()))
        self.assertEqual(len(rows),4);self.assertTrue(all(r['resolution']=='official_display_confirmed' and r['official_value']==r['archive_display_inches'] for r in rows))
if __name__=='__main__':unittest.main()
