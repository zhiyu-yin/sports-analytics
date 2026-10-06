"""Minute provenance only. No model, exposure, correlation, or revised gate."""
import csv, hashlib, json, re, statistics
from datetime import datetime, timezone
from decimal import Decimal, ROUND_HALF_UP, ROUND_FLOOR
from pathlib import Path
import pandas as pd
from stage3a_prepare import ROOT,E,sha,save
RAW=ROOT/'data/raw/stage3a'
ORIGINAL={('2010-11','201942'),('2010-11','202083'),('2010-11','2772'),('2016-17','203552')}

def seconds(raw):
    """Preserve missingness and decimal seconds; never interpret MM:SS as MM.SS."""
    if raw is None or str(raw).strip()=='': return None
    raw=str(raw).strip()
    if raw.startswith(('DNP','DND','NWT')): return None
    if ':' in raw:
        m,s=raw.split(':'); assert int(m)>=0 and Decimal(0)<=Decimal(s)<=60
        return Decimal(m)*60+Decimal(s)
    value=Decimal(raw)*60
    assert value>=0
    return value

def status(raw, present=True):
    if not present:return 'missing'
    n=seconds(raw)
    return 'empty / DNP' if n is None else 'recorded 0:00 appearance' if n==0 else 'played with positive time'

def f(value): return None if value is None else float(value)
def write_csv(name,rows):
    assert rows
    with (E/name).open('w',newline='') as h:
        w=csv.DictWriter(h,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
def round_min(sec,places='0.1'):return (sec/60).quantize(Decimal(places),rounding=ROUND_HALF_UP)

def official_seasons():
    result={}
    for s in ['2010-11','2016-17','2023-24']:
        p=ROOT/f'data/raw/stage3/players_{s}{"_complete" if s=="2016-17" else ""}.json'
        meta=json.loads(p.read_text());t=meta['tables'][0]
        for row in t['rows']:
            pid=[re.search(r'/stats/player/(\d+)/',a['href'])[1] for a in row['links'] if re.match(r'/stats/player/\d+/',a['href'])]
            assert len(pid)==1
            result[s,pid[0]]=dict(zip(t['headers'],row['cells']))|{'source':meta['url'],'sha256':sha(p)}
    return result

def load_games(path,s,pid):
    data=json.loads(path.read_text()); assert data['filters'][:2]==[s,'Regular Season']
    assert f'/player/{pid}/' in data['url']
    assert len(data['tables'])==1
    table=data['tables'][0]; result={}
    for row in table['rows']:
        links=[x['href'] for x in row['links'] if re.fullmatch(r'/game/\d{10}/',x['href'])]
        assert len(links)==1
        gid=links[0].split('/')[2];assert gid.startswith('002') and gid not in result
        for link in row['links']:
            if 'PlayerID=' in link['href']:assert f'PlayerID={pid}&' in link['href'] and f'Season={s}&' in link['href']
        item=dict(zip(table['headers'],row['cells'])); item['date']=datetime.strptime(item['MATCH UP'].split(' - ')[0],'%b %d, %Y').date().isoformat()
        assert int(s[:4]) <= int(item['date'][:4]) <= int(s[:4])+1
        result[gid]=item
    return data,result

def main():
    frozen=json.loads((E/'sample_freeze.json').read_text());assert sha(E/'minute_audit_sample_predeclared.csv')==frozen['sha256']
    sample=pd.read_csv(E/'minute_audit_sample_predeclared.csv',dtype=str);sample_keys=set(zip(sample.season,sample.player_id))
    a=pd.read_csv(E/'archive_minute_projection.csv',dtype=str,keep_default_na=False)
    assert not a.duplicated(['season_year','personId','gameId']).any()
    seasons=official_seasons(); checks=[]; recon=[]; hypotheses=[]; captures=[]; official_zero=[]; countchecks=[]
    for path in sorted(RAW.glob('games_*.json')):
        s,pid=path.stem.split('_')[1:];meta,official=load_games(path,s,pid)
        assert meta['retrieved_at']>frozen['frozen_at']
        captures.append(dict(path=str(path.relative_to(ROOT)),sha256=sha(path),url=meta['url'],retrieved_at=meta['retrieved_at'],rows=len(official),precision='MM:SS, whole displayed seconds'))
        sub=a[(a.season_year==s)&(a.personId==pid)]; archive={r.gameId:r for r in sub.itertuples()};so=seasons[s,pid]
        b=sum((seconds(r.minutes) or Decimal(0) for r in archive.values()),Decimal(0));d=sum((seconds(r['MIN']) or Decimal(0) for r in official.values()),Decimal(0));c=seconds(so['MIN'])
        ap={g for g,r in archive.items() if seconds(r.minutes) is not None};op={g for g,r in official.items() if seconds(r['MIN']) is not None}
        local=[]
        for gid in sorted(set(archive)|set(official)):
            ar=archive.get(gid);o=official.get(gid);av=seconds(ar.minutes) if ar else None;ov=seconds(o['MIN']) if o else None
            rec=dict(player_id=pid,player_name=so['PLAYER'],season=s,game_id=gid,game_date=o['date'] if o else ar.game_date,official_game_MIN_raw=o['MIN'] if o else '',official_game_MIN_parsed_seconds=f(ov),archive_game_MIN_raw=ar.minutes if ar else '',archive_game_MIN_parsed_seconds=f(av),game_level_difference_seconds=f(av-ov) if av is not None and ov is not None else None,appearance_status=status(ar.minutes,ar is not None),official_appearance_status=status(o['MIN'] if o else None,o is not None),archive_appearance_status=status(ar.minutes,ar is not None),match_status='matched_recorded_appearance' if gid in ap&op else 'archive_DNP_not_in_official_appearance_log' if ar and av is None and not o else 'unmatched_requires_review',date_match=(ar.game_date==o['date']) if ar and o else None,official_source=meta['url'],official_sha256=sha(path),official_precision='whole displayed seconds; underlying subsecond precision unavailable',sample_role='frozen_stratified_sample' if (s,pid) in sample_keys else 'zero_minute_supplement')
            checks.append(rec);local.append(rec)
            if ov==0:
                official_zero.append(dict(season=s,player_id=pid,player_name=so['PLAYER'],game_id=gid,game_date=o['date'],official_MIN_raw=o['MIN'],archive_MIN_raw=ar.minutes if ar else '',official_FTM=o['FTM'],official_FTA=o['FTA'],archive_FTM=ar.freeThrowsMade if ar else '',archive_FTA=ar.freeThrowsAttempted if ar else '',official_GP=so['GP'],archive_recorded_GP=len(ap),archive_positive_game_GP=sum(seconds(r.minutes) is not None and seconds(r.minutes)>0 for r in archive.values()),season_positive_eligible=b>0 and c>0,official_source=meta['url'],status='official_recorded_zero_confirmed' if ar and av==0 else 'review'))
        for field in ['FTM','FTA','3PM','3PA']:
            countchecks.append(dict(season=s,player_id=pid,field=field,official_game_sum=sum(int(o[field]) for o in official.values()),official_season_total=int(so[field]),match=sum(int(o[field]) for o in official.values())==int(so[field])))
        n=len(op);row=dict(season=s,player_id=pid,player_name=so['PLAYER'],sample_role='frozen_stratified_sample' if (s,pid) in sample_keys else 'zero_minute_supplement',original_failed_case=(s,pid) in ORIGINAL,A_archive_raw_season_MIN=None,A_status='not available: archive is game-level only',B_archive_sum_seconds=f(b),B_archive_sum_minutes=f(b/60),C_official_season_MIN_raw=so['MIN'],C_official_display_seconds=f(c),D_official_game_sum_seconds=f(d),D_official_game_sum_minutes=f(d/60),D_precision='sum of official whole-second MM:SS display; not unrounded clock truth',E_official_season_GP=int(so['GP']),F_reconstructed_official_GP=n,archive_recorded_GP=len(ap),archive_positive_game_GP=sum(seconds(r.minutes) is not None and seconds(r.minutes)>0 for r in archive.values()),archive_DNP_rows=len(archive)-len(ap),official_missing_recorded_games=len(ap-op),archive_missing_recorded_games=len(op-ap),all_recorded_games_match=ap==op,game_time_mismatches=sum(r['game_level_difference_seconds']!=0 for r in local if r['match_status']=='matched_recorded_appearance'),B_minus_D_seconds=f(b-d),B_minus_C_seconds=f(b-c),D_minus_C_seconds=f(d-c),archive_positive_season=b>0,official_positive_season=c>0,eligibility_changed=(b>0)!=(c>0),official_season_source=so['source'],official_game_source=meta['url'])
        recon.append(row)
        observed_round_game_tenth=sum((round_min(seconds(o['MIN'])) for o in official.values()),Decimal(0))
        observed_round_game_whole=sum((round_min(seconds(o['MIN']),'1') for o in official.values()),Decimal(0))
        # Intersect possible unobserved nearest-second intervals with a one-decimal season display interval.
        latent_compatible=max(d-Decimal(n)/2,c-3)<=min(d+Decimal(n)/2,c+3)
        hypotheses.append(dict(season=s,player_id=pid,player_name=so['PLAYER'],season_MIN_raw=so['MIN'],sum_game_seconds=f(d),whole_minute_season_round_result=str(round_min(d,'1')),whole_minute_season_round_compatible=round_min(d,'1')==Decimal(so['MIN']),one_decimal_season_round_result=str(round_min(d)),one_decimal_season_round_compatible=round_min(d)==Decimal(so['MIN']),one_decimal_season_truncation_result=str((d/60).quantize(Decimal('.1'),rounding=ROUND_FLOOR)),one_decimal_season_truncation_compatible=(d/60).quantize(Decimal('.1'),rounding=ROUND_FLOOR)==Decimal(so['MIN']),sum_per_game_rounded_tenths=str(observed_round_game_tenth),per_game_tenth_rounding_compatible=observed_round_game_tenth==Decimal(so['MIN']),sum_per_game_rounded_whole=str(observed_round_game_whole),per_game_whole_rounding_compatible=observed_round_game_whole==Decimal(so['MIN']),unobserved_fractional_seconds_then_rounding_compatible=latent_compatible,unobserved_fractional_seconds_mechanism_demonstrated=False,archive_MM_dot_SS_error_supported=False,source_revision_evidence='none; matched public game records do not exclude an internal revision between products',genuine_material_source_conflict='not observed at available game precision',mechanism='not established'))
    write_csv('official_game_count_sum_crosscheck.csv',countchecks);write_csv('official_game_minute_crosscheck.csv',checks);write_csv('minute_reconstruction_by_player_season.csv',recon);write_csv('candidate_rounding_explanations.csv',hypotheses);write_csv('zero_minute_appearance_audit.csv',official_zero);save('official_capture_manifest.json',captures)
    # Independent whole-game classification evidence, including explicit DNP/DND rows.
    box=json.loads((RAW/'box_0021601203.json').read_text());boxchecks=[]
    for table in box['tables']:
        for row in table['rows']:
            ids=[re.search(r'/player/(\d+)/',l['href'])[1] for l in row['links'] if re.match(r'/player/\d+/',l['href'])]
            if not ids:continue
            assert len(ids)==1
            pid=ids[0];o=dict(zip(table['headers'],row['cells'])); ar=a[(a.gameId=='0021601203')&(a.personId==pid)];assert len(ar)==1;ar=ar.iloc[0]
            boxchecks.append(dict(game_id='0021601203',player_id=pid,player_name=o['PLAYER'],official_MIN_raw=o['MIN'],archive_MIN_raw=ar.minutes,archive_comment=ar.comment,official_status=status(o['MIN']),archive_status=status(ar.minutes),classification_match=status(o['MIN'])==status(ar.minutes),official_FTM=o.get('FTM',''),official_FTA=o.get('FTA',''),archive_FTM=ar.freeThrowsMade,archive_FTA=ar.freeThrowsAttempted,source=box['url']))
    write_csv('official_boxscore_classification_crosscheck.csv',boxchecks)
    # Preserve original counts, and compute the quantization from independent integer seconds plus raw official season display.
    census=pd.read_csv(ROOT/'docs/stage3_evidence/shooting_census_crosscheck.csv',dtype={'player_id':str})
    mism=census[(census.field=='minutes')&~census.match];differences=[];eligibility=[]
    for r in census[census.field=='minutes'].itertuples():
        ar=a[(a.season_year==r.season)&(a.personId==r.player_id)];total=sum((seconds(v) or Decimal(0) for v in ar.minutes),Decimal(0));off=seconds(seasons[r.season,r.player_id]['MIN']); delta=total-off
        assert abs(float(delta)-r.difference*60)<1e-7
        eligibility.append(dict(season=r.season,player_id=r.player_id,archive_sum_seconds=f(total),official_display_seconds=f(off),eligibility_changed=(total>0)!=(off>0)))
        if not r.match: differences.append(delta)
    vals=[float(x) for x in differences];freq=[dict(difference_seconds=i,frequency=sum(x==i for x in differences)) for i in range(-8,9)];write_csv('minute_difference_distribution.csv',freq);write_csv('season_eligibility_crosscheck.csv',eligibility)
    quant=dict(n=len(vals),sign='archive exact game-second sum minus official displayed season MIN converted to seconds',mean=statistics.mean(vals),median=statistics.median(vals),sample_SD=statistics.stdev(vals),population_SD=statistics.pstdev(vals),min=min(vals),max=max(vals),absolute_median=statistics.median(map(abs,vals)),absolute_max=max(map(abs,vals)),all_on_integer_second_grid=all(v==v.to_integral_value() for v in differences),negative=sum(v<0 for v in vals),positive=sum(v>0 for v in vals),zero=sum(v==0 for v in vals),symmetric=False,interpretation='Discrete but strongly positive-skewed; not a symmetric error distribution. Conditioned on failed original gate, not an unbiased rounding-error sample.',new_acceptance_threshold=None)
    save('minute_quantization_summary.json',quant)
    # Deterministic independent parser sample of 100 nonempty archive rows; no statistics used in selection.
    candidates=a[a.minutes.ne('')].copy();candidates['key']=[hashlib.sha256(f'stage3a-parser-v1|{s}|{g}|{p}'.encode()).hexdigest() for s,g,p in zip(candidates.season_year,candidates.gameId,candidates.personId)];chosen=candidates.sort_values('key').head(100);parserrows=[]
    for r in chosen.itertuples():
        m,ss=r.minutes.split(':');expected=int(m)*60+int(ss);got=seconds(r.minutes);old=round(float(m)*60+float(ss));assert got==expected==old
        parserrows.append(dict(season=r.season_year,game_id=r.gameId,player_id=r.personId,raw=r.minutes,expected_seconds=expected,parsed_seconds=str(got),stage3_parser_seconds=old,decimal_minutes=str(got/60),roundtrip_seconds=str((got/60*60).quantize(Decimal('.000000001'))),exact_seconds_preserved=True))
    write_csv('minute_parser_sample.csv',parserrows)
    save('minute_parser_validation.json',dict(noncanonical_MM_60_archive_rows=int(a.minutes.str.endswith(':60').sum()),noncanonical_MM_60_official_audit_rows=sum(str(r['official_game_MIN_raw']).endswith(':60') for r in checks),MM_60_policy='Preserve raw string; normalize M:60 to (M+1)*60 seconds; no loss or silent exclusion. Both sources display these values.',rows_checked=len(parserrows),selection='100 lowest SHA256 stage3a-parser-v1|season|game_id|player_id among nonempty game rows in validation seasons',all_exact_seconds_preserved=True,examples=[dict(raw='12:04',seconds=724,decimal_minutes=str(Decimal(12)+Decimal(4)/60),incorrect_MM_dot_SS='12.04'),dict(raw='12:28',seconds=748,decimal_minutes=str(Decimal(12)+Decimal(28)/60),incorrect_MM_dot_SS='12.28')],existing_stage3_parser_matches=True,archive_MM_dot_SS_bug=False,decimal_minutes_unit_test='12.4 minutes = 744 seconds, distinct from 12:04 = 724 seconds',missing_is_not_zero=True))
    integer=census[census.field.isin(['ftm','fta','fg3m','fg3a','games_played'])];teams=pd.read_csv(ROOT/'docs/stage3_evidence/shooting_team_reconciliation.csv')
    summary=dict(frozen_sample_player_seasons=len(sample),frozen_within_tolerance=int((sample.case_type=='within_original_tolerance').sum()),frozen_mismatch=int((sample.case_type=='census_mismatch').sum()),additional_census_mismatch=int((sample.case_type=='census_mismatch').sum())-4,total_audited_player_seasons=len(recon),official_recorded_game_rows=sum(r['F_reconstructed_official_GP'] for r in recon),frozen_sample_recorded_game_rows=sum(r['F_reconstructed_official_GP'] for r in recon if r['sample_role']=='frozen_stratified_sample'),crosscheck_union_rows=len(checks),archive_DNP_not_in_logs=sum(r['match_status']=='archive_DNP_not_in_official_appearance_log' for r in checks),unmatched_recorded_games=sum(r['official_missing_recorded_games']+r['archive_missing_recorded_games'] for r in recon),game_time_mismatches=sum(r['game_time_mismatches'] for r in recon),official_game_count_comparisons=len(countchecks),official_game_count_mismatches=sum(not r['match'] for r in countchecks),GP_mismatches=sum(r['E_official_season_GP']!=r['F_reconstructed_official_GP'] or r['E_official_season_GP']!=r['archive_recorded_GP'] for r in recon),official_zero_appearances=len(official_zero),zero_appearance_by_season={s:sum(r['season']==s for r in official_zero) for s in ['2010-11','2016-17','2023-24']},official_boxscore_classified_rows=len(boxchecks),official_boxscore_classification_mismatches=sum(not r['classification_match'] for r in boxchecks),season_eligibility_comparisons=len(eligibility),eligibility_changes=sum(r['eligibility_changed'] for r in eligibility),primary_integer_comparisons=len(integer),primary_integer_mismatches=int((~integer.match).sum()),team_count_comparisons=len(teams),team_count_mismatches=int((~teams.match).sum()),finer_than_season_display_reconciles=True,finer_than_whole_second_data_obtained=False,season_display_mechanism_demonstrated=False,part_B_started=False,scientific_association_inspected=False)
    save('game_level_reconciliation_summary.json',summary)
    decision=dict(stage3a_classification='UNRESOLVED — INSUFFICIENT PRECISION EVIDENCE',dated_at=datetime.now(timezone.utc).isoformat(),reason='All available official game MM:SS records match the archive exactly, but the mechanism connecting those game displays to official season decimals is not established. The failed-census distribution is strongly asymmetric.',criteria=dict(A='supported: all primary integer comparisons exact',B='partial: all audited games/time match; precision mechanism not demonstrated',C='supported at recorded display/appearance precision; all 15 zero appearances and explicit box DNP/DND classifications retained',D='supported: zero eligibility changes in 1510 season comparisons',E='partial: small and discrete, but asymmetric; no missing audited games; systematic rounding/aggregation cause remains unproved',F='supported: no Stage 3 scientific model fitted'),amendment_recommended=False,amendment_applied=False,new_numeric_tolerance=None,stage3_part_A='BLOCKED; prior failure preserved',stage3_part_B='DISABLED',scientific_models_run=False,rerun_may_be_diagnostic_only=True,rerun_can_release_part_B=False)
    save('stage3a_decision.json',decision)
    print(json.dumps(summary,indent=2)); print(json.dumps(quant,indent=2))
if __name__=='__main__':main()
