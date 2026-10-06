"""Official anthropometric comparisons and membership audit; no scientific analysis."""
import sys,json,csv,collections,statistics,shutil
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from anthropometrics_shooting.stage0c import *

def load_official(combine):
    observations={};manifests=[];unmatched=[]
    expected=['PLAYER','POS','BODY FAT %','HAND LENGTH (INCHES)','HAND WIDTH (INCHES)','HEIGHT W/O SHOES','HEIGHT W/ SHOES','STANDING REACH','WEIGHT (LBS)','WINGSPAN']
    files=sorted(RAW.glob('browser*.json'))
    for p in files:
        m=json.loads(p.read_text());year=int(m['season'][:4]);stale=p.name=='browser_2001-02.json'
        manifests.append(dict(source_name='NBA Stats rendered combine table',publisher='NBA',source_type='official_NBA_factual_record',url=m['url'],url_pattern='https://www.nba.com/stats/draft/combine-anthro?SeasonYear={YYYY}-{YY}',years=[year],fields_available=['barefoot_height','shoe_height','wingspan','standing_reach','weight'],measurement_precision='quarter-inch increments in feet/inches; missing explicitly blank or dash',retrieval_method='browser: season dropdown, rendered DOM table extraction; no hidden state or API response fabricated',retrieval_timestamp_utc=m['retrieved_at'],raw_path=str(p.relative_to(ROOT)),raw_sha256=sha(p),accepted=not stale,notes='Rejected stale capture: selected season changed before preceding year table refreshed. Retained for audit; verified 2001 capture supersedes.' if stale else 'Official page season + same-year unique normalized name mapping; archive ID is audit label, not independent ID certification.'))
        if stale:continue
        assert len(m['tables'])==1
        t=m['tables'][0];assert [h.replace('\xa0',' ') for h in t['headers']]==expected
        for cells in t['rows']:
            assert len(cells)==10
            rs=[r for r in combine if int(r['SEASON'])==year and name_key(r['PLAYER_NAME'])==name_key(cells[0])]
            if len(rs)!=1:unmatched.append(dict(year=year,official_name=cells[0]));continue
            r=rs[0];key=(r['PLAYER_ID'],year)
            # -1 placeholders stay keyed by name for source-wide audit only, never reference members.
            if key[0]=='-1':key=(r['PLAYER_ID']+':'+r['PLAYER_NAME'],year)
            if key in observations:raise ValueError('Duplicate official name/year mapping')
            observations[key]=dict(player_id=r['PLAYER_ID'],player_name=r['PLAYER_NAME'],official_name=cells[0],combine_year=year,barefoot_height=source_inches(cells[5]),shoe_height=source_inches(cells[6]),wingspan=source_inches(cells[9]),standing_reach=source_inches(cells[7]),weight=number(cells[8]),precision=.25,source_type='official_NBA_factual_record',source_url=m['url'],retrieval_timestamp_utc=m['retrieved_at'],raw_sha256=sha(p))
    assert not unmatched,unmatched
    dump(E/'browser_capture_manifest.json',manifests)
    csvwrite(ROOT/'data/interim/stage0c_official_measurements.csv',list(observations.values()))
    return observations,manifests

def agreement(rows):
    pairs=[r for r in rows if r['official_barefoot_height'] is not None and r['official_wingspan'] is not None]
    exact=sum(r['pair_status']=='exact' for r in pairs);rounded=sum(r['pair_status']=='rounding_consistent' for r in pairs)
    return dict(preselected_players=len(rows),successful_official_source_retrievals=sum(bool(r['official_source_url']) for r in rows),direct_barefoot_observations=sum(r['official_barefoot_height'] is not None for r in rows),direct_wingspan_observations=sum(r['official_wingspan'] is not None for r in rows),complete_pairs=len(pairs),exact_pairs=exact,rounding_consistent_pairs=rounded,conflict_pairs=sum(r['pair_status']=='conflict' for r in pairs),official_source_unavailable=sum(r['pair_status']=='official_source_unavailable' for r in rows),agreement_rate=(exact+rounded)/len(pairs) if pairs else None)

def main():
    combine,archive_meta=read_combine();ref=reference(combine)
    selected=list(csv.DictReader((E/'validation_sample_predeclared.csv').open()))
    assert sample(combine)[0]==[{**r,'combine_year':int(r['combine_year']),'archive_barefoot_height':float(r['archive_barefoot_height']),'archive_wingspan':float(r['archive_wingspan']),'within_cell_advantage_rank':float(r['within_cell_advantage_rank'])} for r in selected]
    official,manifests=load_official(combine)
    checks=[]
    for r in selected:
        o=official.get((r['player_id'],int(r['combine_year'])));h,w,pair=pair_check(r,o)
        found='official_source_unavailable' if o is None else 'official_pair_found' if o['barefoot_height'] is not None and o['wingspan'] is not None else 'official_source_found_but_barefoot_missing' if o['barefoot_height'] is None else 'official_partial_only'
        checks.append(dict(r,official_barefoot_height=o['barefoot_height'] if o else None,height_difference_inches=float(r['archive_barefoot_height'])-o['barefoot_height'] if o and o['barefoot_height'] is not None else None,official_wingspan=o['wingspan'] if o else None,wingspan_difference_inches=float(r['archive_wingspan'])-o['wingspan'] if o and o['wingspan'] is not None else None,archive_source=archive_meta['url'],official_source_type=o['source_type'] if o else None,official_source_url=o['source_url'] if o else '',retrieval_timestamp_utc=o['retrieval_timestamp_utc'] if o else '',official_raw_sha256=o['raw_sha256'] if o else '',height_status=h,wingspan_status=w,pair_status=pair,availability_status=found,notes='Exact normalized unique name within exact combine year; no shoe-height substitution; official values retained without correction.'))
    csvwrite(E/'anthro_barefoot_wingspan_crosscheck.csv',checks)
    strat=[]
    for field in ['sampling_era_stratum','sampling_height_stratum','sampling_relative_wingspan_stratum']:
        for label in sorted({r[field] for r in checks}):strat.append(dict(dimension=field,stratum=label,**agreement([r for r in checks if r[field]==label])))
    csvwrite(E/'agreement_by_stratum.csv',strat)
    # Census corroboration is separate from the predeclared primary sample.
    census=[];internal=[];missing=[];keys=collections.Counter()
    for r in combine:
        year=int(r['SEASON'])
        if year>2013:continue
        key=(r['PLAYER_ID'],year);keys[key if key[0]!='-1' else (key[0]+':'+r['PLAYER_NAME'],year)]+=1
        o=official[(r['PLAYER_ID']+':'+r['PLAYER_NAME'] if r['PLAYER_ID']=='-1' else r['PLAYER_ID'],year)]
        for field,src in [('HEIGHT_WO_SHOES','barefoot_height'),('WINGSPAN','wingspan'),('STANDING_REACH','standing_reach')]:
            a=number(r[field]);display=source_inches(r[field+'_FT_IN']);v=o[src]
            internal.append(dict(player_id=r['PLAYER_ID'],player_name=r['PLAYER_NAME'],year=year,field=field,numeric=a,display_inches=display,difference=a-display if a is not None and display is not None else None,status='missing' if a is None or display is None else 'exact' if a==display else 'conflict'))
        ah=number(r['HEIGHT_WO_SHOES']);aw=number(r['WINGSPAN'])
        census.append(dict(player_id=r['PLAYER_ID'],player_name=r['PLAYER_NAME'],year=year,height_agrees=ah==o['barefoot_height'],wingspan_agrees=aw==o['wingspan'],complete_pair=ah is not None and aw is not None,standing_reach_agrees=number(r['STANDING_REACH'])==o['standing_reach']))
    csvwrite(ROOT/'data/interim/stage0c_internal_measurement_checks.csv',internal)
    csvwrite(ROOT/'data/interim/stage0c_sourcewide_comparisons.csv',census)
    for year in range(2000,2014):
        rs=[r for r in combine if int(r['SEASON'])==year]
        missing.append(dict(combine_year=year,records=len(rs),missing_barefoot_height=sum(number(r['HEIGHT_WO_SHOES']) is None for r in rs),missing_wingspan=sum(number(r['WINGSPAN']) is None for r in rs),missing_standing_reach=sum(number(r['STANDING_REACH']) is None for r in rs),complete_core_pairs=sum(number(r['HEIGHT_WO_SHOES']) is not None and number(r['WINGSPAN']) is not None for r in rs)))
    csvwrite(E/'measurement_missingness_by_year.csv',missing)
    refkeys={(r['PLAYER_ID'],int(r['SEASON'])) for r in ref}
    ref_internal=[r for r in internal if (r['player_id'],r['year']) in refkeys]
    consistency=dict(pre2014_rows=len(census),complete_pairs=sum(r['complete_pair'] for r in census),core_conflicts=[r for r in census if not r['height_agrees'] or not r['wingspan_agrees']],standing_reach_official_conflicts=[r for r in census if not r['standing_reach_agrees']],duplicate_player_year_keys=[str(k) for k,v in keys.items() if v>1],reference_numeric_display={field:dict(collections.Counter(r['status'] for r in ref_internal if r['field']==field)) for field in ['HEIGHT_WO_SHOES','WINGSPAN','STANDING_REACH']},reference_implausible_core=sum(not usable(r) for r in ref),reference_reach_not_above_height=sum(number(r['STANDING_REACH']) is not None and number(r['STANDING_REACH'])<=number(r['HEIGHT_WO_SHOES']) for r in ref),reference_reach_outside_80_132=sum(number(r['STANDING_REACH']) is not None and not 80<=number(r['STANDING_REACH'])<=132 for r in ref))
    dump(E/'internal_consistency_summary.json',consistency)
    reach_review=[]
    for r in ref:
        a=number(r['STANDING_REACH']);display=source_inches(r['STANDING_REACH_FT_IN'])
        if a is not None and display is not None and a!=display:
            o=official[(r['PLAYER_ID'],int(r['SEASON']))];v=o['standing_reach']
            reach_review.append(dict(player_id=r['PLAYER_ID'],player_name=r['PLAYER_NAME'],combine_year=int(r['SEASON']),field='STANDING_REACH',archive_numeric=a,archive_display_inches=display,official_value=v,difference_inches=round(a-v,8),status=field_status(a,v),source_url=o['source_url'],explanation='0.05-inch difference consistent with one-decimal numeric representation versus quarter-inch display; display matches official. Standing reach is outside the frozen exposure and reference fields. No correction applied.'))
    csvwrite(E/'standing_reach_difference_review.csv',reach_review)

    # Repeat review restricted to eligibility years, with later repeats supplied separately.
    groups=collections.defaultdict(list)
    for r in combine:
        if valid_id(r['PLAYER_ID']) and number(r['HEIGHT_WO_SHOES']) is not None and number(r['WINGSPAN']) is not None:groups[r['PLAYER_ID']].append(r)
    repeated=[]
    for pid,rs in groups.items():
        if len(rs)<2:continue
        rs=sorted(rs,key=lambda r:int(r['SEASON']));a,b=rs[0],rs[-1];dh=float(b['HEIGHT_WO_SHOES'])-float(a['HEIGHT_WO_SHOES']);dw=float(b['WINGSPAN'])-float(a['WINGSPAN'])
        repeated.append(dict(player_id=pid,player_name=b['PLAYER_NAME'],earliest_year=int(a['SEASON']),latest_year=int(b['SEASON']),height_change_inches=dh,wingspan_change_inches=dw,classification='identical' if dh==dw==0 else 'near-identical' if max(abs(dh),abs(dw))<=.25 else 'materially different',eligible_pre2014_records=sum(int(r['SEASON'])<=2013 and usable(r) for r in rs),review_scope='Full-archive supplementary audit; no repeated eligible pre-2014 records',review_flag=max(abs(dh),abs(dw))>.25))
    csvwrite(E/'repeated_measurement_review.csv',repeated)
    # Verify unchanged membership against the existing frozen reference, without fitting anything.
    existing=ROOT/'data/interim/residual_reference_pre2013.csv'
    old=list(csv.DictReader(existing.open()))
    derived=[dict(player_id=r['PLAYER_ID'],combine_year=str(r['SEASON']),height_wo_shoes_inches=str(float(r['HEIGHT_WO_SHOES'])),wingspan_inches=str(float(r['WINGSPAN']))) for r in ref]
    assert old==derived,'Reference membership or measurements changed'
    snapshot=ROOT/'data/interim/stage0c_reference_membership.csv'
    if snapshot.exists():assert sha(snapshot)==sha(existing)
    else:shutil.copyfile(existing,snapshot)
    prior_build=json.loads((ROOT/'docs/stage0b_evidence/build_manifest.json').read_text())
    assert sha(existing)==prior_build['residual_reference_sha256']
    dump(E/'reference_population_hash.json',dict(original_path=str(existing.relative_to(ROOT)),snapshot_path=str(snapshot.relative_to(ROOT)),sha256=sha(existing),matches_stage0b=True,canonical_membership_sha256=hashlib.sha256(json.dumps(derived,sort_keys=True,separators=(',',':')).encode()).hexdigest()))
    refsummary=dict(participants=len(ref),year_min=min(int(r['SEASON']) for r in ref),year_max=max(int(r['SEASON']) for r in ref),unique_positive_ids=len({r['PLAYER_ID'] for r in ref}),missing_id_placeholders=sum(not valid_id(r['PLAYER_ID']) for r in ref),quarantined_records=sum((r['PLAYER_ID'],int(r['SEASON'])) in QUARANTINE for r in ref),post2013_records=sum(int(r['SEASON'])>2013 for r in ref),repeated_eligible_ids=sum(r['eligible_pre2014_records']>1 for r in repeated),membership_matches_stage0b=True,direct_official_pairs=sum(official[(r['PLAYER_ID'],int(r['SEASON']))]['barefoot_height'] is not None and official[(r['PLAYER_ID'],int(r['SEASON']))]['wingspan'] is not None for r in ref),reference_rule='latest complete plausible non-quarantined record <=2013 per positive archive ID',residual_fit_performed=False)
    dump(E/'reference_population_summary.json',refsummary)
    discrepancies=[]
    for pid,year in sorted(QUARANTINE):
        r=next(r for r in combine if r['PLAYER_ID']==pid and int(r['SEASON'])==year);o=official[(pid,year)]
        field='HEIGHT_WO_SHOES' if pid=='1629675' else 'WINGSPAN';v=o['barefoot_height' if field=='HEIGHT_WO_SHOES' else 'wingspan'];a=number(r[field]);display=source_inches(r[field+'_FT_IN'])
        status='unresolved_quarantine' if v is None else 'official_numeric_confirmed' if a==v else 'official_display_confirmed' if display==v else 'official_third_value_confirmed'
        discrepancies.append(dict(player_id=pid,player_name=r['PLAYER_NAME'],combine_year=year,field=field,archive_numeric_value=a,archive_display_value=r[field+'_FT_IN'],archive_display_inches=display,official_value=v,official_source=o['source_url'],retrieval_timestamp_utc=o['retrieval_timestamp_utc'],raw_sha256=o['raw_sha256'],resolution=status,action='Evidence resolves value; no archive or prior quarantine file edited. Outside <=2013 population and reference. Future inclusion requires versioned corrected record.'))
    csvwrite(E/'measurement_discrepancy_review.csv',discrepancies)
    # Only after primary anthropometric work, project candidate identities. No outcome columns.
    identities=candidate_identities();assert len(identities)==311
    coverage=[];ref_byid={r['PLAYER_ID']:r for r in ref}
    for n in identities:
        r=ref_byid[n['player_id']];o=official.get((r['PLAYER_ID'],int(r['SEASON'])))
        complete=o and o['barefoot_height'] is not None and o['wingspan'] is not None
        status='quarantined_measurement' if (r['PLAYER_ID'],int(r['SEASON'])) in QUARANTINE else 'direct_official_pair_corroboration' if complete and float(r['HEIGHT_WO_SHOES'])==o['barefoot_height'] and float(r['WINGSPAN'])==o['wingspan'] else 'official_partial_corroboration' if o and (o['barefoot_height'] is not None or o['wingspan'] is not None) else 'archive_only'
        coverage.append(dict(player_id=n['player_id'],player_name=n['player_name_nba'],season=n['season'],combine_year=int(r['SEASON']),source_coverage=status,official_source_url=o['source_url'] if o else '',notes='Combine year from independently reconstructed unchanged reference; candidate projection contains identity/season only. No eligibility changes.'))
    csvwrite(E/'candidate_population_source_coverage.csv',coverage)
    summary=agreement(checks)
    systematic=bool(systematic_discrepancies(checks))
    dump(E/'systematic_discrepancy_screen.json',dict(flags=systematic_discrepancies(checks),all_sourcewide_core_differences_zero=not consistency['core_conflicts'],method='Predeclared same-sign descriptive offset screen; no inference'))
    clean=not consistency['core_conflicts'] and not consistency['duplicate_player_year_keys'] and refsummary['participants']==960 and not refsummary['quarantined_records']
    criteria=dict(minimum_30_pairs=summary['complete_pairs']>=30,agreement_at_least_95_percent=summary['agreement_rate'] is not None and summary['agreement_rate']>=.95,all_era_height_relative_strata=all(len([r for r in strat if r['dimension']==dim and r['complete_pairs']>0])==3 for dim in ['sampling_era_stratum','sampling_height_stratum','sampling_relative_wingspan_stratum']),no_unresolved_systematic_discrepancy=not systematic,substantive_conflicts_reconciled_or_quarantined=not consistency['core_conflicts'],reference_population_clean=clean)
    decision='PASS' if all(criteria.values()) else 'FAIL — MATERIAL SOURCE CONFLICT' if consistency['core_conflicts'] else 'PARTIAL — INSUFFICIENT DIRECT VALIDATION'
    summary.update(decision_pending_tests=decision,gate_criteria=criteria,sample_replacements=0,successful_unique_official_historical_tables=14,sourcewide_complete_pairs=consistency['complete_pairs'],sourcewide_rows=consistency['pre2014_rows'],systematic_discrepancy=systematic,candidate_coverage=dict(collections.Counter(r['source_coverage'] for r in coverage)),reference_population=refsummary['participants'],four_discrepancy_resolutions=dict(collections.Counter(r['resolution'] for r in discrepancies)),scientific_outcomes_loaded=False,candidate_columns_loaded=IDENTITY_COLUMNS,no_residual_fit=True,no_effect_estimate=True)
    dump(E/'validation_summary.json',summary)
    raw_sources=[json.loads(p.read_text()) for p in sorted(RAW.glob('*.manifest.json'))]
    for m in raw_sources:
        if m['raw_path']:assert sha(ROOT/m['raw_path'])==m['raw_sha256']
    archive_source=dict(source_name='Pinned ianstack combine archive',publisher='ianstack',source_type='pinned_secondary_archive',retrieval_timestamp_utc=archive_meta['retrieved_at'],raw_sha256=archive_meta['sha256'],raw_path=archive_meta['raw_path'],url_pattern='https://raw.githubusercontent.com/ianstack/NBA-Draft-Combine-Analysis/{revision}/data/nba_draft_data.csv',url=archive_meta['url'],years=list(range(2000,2023)),fields_available=['barefoot_height','wingspan','shoe_height','standing_reach','weight'],measurement_precision='numeric inches and feet/inches display; quarter-inch increments',retrieval_method='Stage 0 pinned CSV; column-projected read in Stage 0C',original_metadata=archive_meta)
    for m in raw_sources:
        m['fields_available']=[] if m['transport_exit'] or m['http_status']!=200 or 'PDF' in m['source_name'] or 'sheet' in m['source_name'] or 'Bulls' in m['source_name'] else ['page retrieved; not used as factual pair evidence']
        m['measurement_precision']='unverified; no accepted measurements from this attempt'
        m['url_pattern']=m['url']
    dump(E/'source_provenance_map.json',dict(sources=[archive_source]+manifests+raw_sources,distinctions='Browser-rendered NBA tables are direct official factual records. curl HTML shells, timeouts, stale browser capture and failed historical archives are not validation. Prior secondary 2013 PDF was not needed or reclassified.',accepted_historical_coverage=list(range(2000,2014)),supplemental_resolution_year=2019))
    protected=json.loads((E/'prior_preservation_manifest.json').read_text())
    assert all(sha(ROOT/p)==h for p,h in protected.items()),'Prior artifact changed'
    normalized=[p for p in E.iterdir() if p.suffix in ['.json','.csv'] and p.name not in ['build_manifest.json','test_summary.json']]+[ROOT/'data/interim/stage0c_official_measurements.csv',snapshot,ROOT/'data/interim/stage0c_internal_measurement_checks.csv',ROOT/'data/interim/stage0c_sourcewide_comparisons.csv',ROOT/'data/interim/stage0c_replacement_pool_predeclared.csv']
    dump(E/'build_manifest.json',dict(built_at=now(),decision_pending_tests=decision,prior_files_preserved=len(protected),prior_preservation_manifest_sha256=sha(E/'prior_preservation_manifest.json'),candidate_dataset_sha256=sha(ROOT/'data/processed/ft_2013_14_stage1_dataset.parquet'),reference_sha256=sha(existing),sampling_rule_sha256=sha(E/'release_rule_predeclared.json'),sample_sha256=sha(E/'validation_sample_predeclared.csv'),normalized_sha256={str(p.relative_to(ROOT)):sha(p) for p in normalized},code_sha256={str(p.relative_to(ROOT)):sha(p) for p in [ROOT/'src/anthropometrics_shooting/stage0c.py']+list((ROOT/'scripts').glob('*stage0c*.py'))+list((ROOT/'tests').glob('test_stage0c.py'))},candidate_columns_loaded=IDENTITY_COLUMNS,scientific_outcomes_loaded=False,residual_fit_performed=False,exposure_outcome_model_called=False))
    print(json.dumps(summary,indent=2))
if __name__=='__main__':main()
