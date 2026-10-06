"""Offline candidate freeze. No scientific model or exposure/outcome statistic."""
import sys,json,csv,collections,statistics,datetime,hashlib
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from anthropometrics_shooting.stage0b_io import *
from anthropometrics_shooting.stage0b import eligibility,select_measurement,complete,positive_id,validate_frozen
from anthropometrics_shooting.normalize import name_key,number

def main():
    import pyarrow as pa
    import pyarrow.parquet as pq
    cm=json.loads((E0/'archive_sources.json').read_text())[0]; combine=archive(cm)
    sm=json.loads((E0/'shooting_archive_sources.json').read_text())
    nba=list(csv.DictReader((ROOT/'data/interim/stage0b_nba_2013_14_totals.csv').open()))
    for r in nba:
        for k in ['FTM','FTA','FG3M','FG3A','GP','seconds','position_rows']:r[k]=int(r[k])
    identities=list(csv.DictReader((ROOT/'data/interim/stage0b_nba_identities.csv').open()))
    byname=collections.defaultdict(list)
    for r in identities:byname[name_key(r['player_name'])].append(r)
    crosswalk=[]
    for r in csv.DictReader((ROOT/'data/interim/identity_audit.csv').open()):
        if r['join_status']!='manually reviewable':continue
        candidates=byname[name_key(r['player_name'])]
        assert len(candidates)==1
        p=candidates[0]
        crosswalk.append(dict(combine_source_id=r['player_id'],combine_name=r['player_name'],shooting_source_id=p['player_id'],shooting_name=p['player_name'],normalized_name=name_key(r['player_name']),resolution_status='unresolved',resolved_nba_id='',evidence_source=cm['url']+' | '+sm[0]['url'],notes='Reviewed source records: conflicting positive IDs; no independent ID bridge. Normalized name alone is insufficient. Not auto-merged; primary freeze allows exact IDs only.'))
    assert len(crosswalk)==21
    for c in crosswalk:
        exact=[r for r in combine if r['PLAYER_ID']==c['shooting_source_id']]
        eligible,_=select_measurement(exact)
        c['independent_exact_prior_record_available']=eligible is not None
        if eligible:
            c['notes']+=' Separate exact-ID prior combine record exists for shooting ID; that record may qualify without using this unresolved name link.'
    csvwrite(ROOT/'data/interim/identity_crosswalk_review.csv',crosswalk);csvwrite(E/'identity_crosswalk_review.csv',crosswalk)
    conflict_ids={r['shooting_source_id'] for r in crosswalk}
    aliases=list(csv.DictReader((ROOT/'data/interim/id_name_differences.csv').open()))
    csvwrite(E/'exact_id_alias_audit.csv',[dict(r,resolution_status='retained_exact_id',notes='Names preserved; exact positive ID takes priority') for r in aliases])
    byid=collections.defaultdict(list)
    for r in combine:
        pid=positive_id(r['PLAYER_ID'])
        if pid:byid[pid].append(r)
    repeated=[]
    for pid,rows in byid.items():
        complete_rows=sorted([r for r in rows if complete(r)],key=lambda r:int(r['SEASON']))
        if len(complete_rows)<2:continue
        a,b=complete_rows[0],complete_rows[-1];dh=float(b['HEIGHT_WO_SHOES'])-float(a['HEIGHT_WO_SHOES']);dw=float(b['WINGSPAN'])-float(a['WINGSPAN'])
        repeated.append(dict(player_id=pid,player_name=b['PLAYER_NAME'],years=';'.join(r['SEASON'] for r in complete_rows),height_difference_inches=dh,wingspan_difference_inches=dw,status='identical' if dh==0 and dw==0 else 'near-identical' if max(abs(dh),abs(dw))<=.25 else 'materially different',pre_2013_record_count=sum(int(r['SEASON'])<=2013 for r in complete_rows),notes='Latest minus earliest complete numeric values; differences flagged, not corrected.'))
    csvwrite(E/'repeated_measurements.csv',repeated)
    frozen=[];excluded=[];exact_prior=0
    for n in sorted(nba,key=lambda r:int(r['player_id'])):
        rows=byid.get(n['player_id'],[])
        if any(int(r['SEASON'])<=2013 for r in rows) and n['seconds']>0:exact_prior+=1
        m,reasons=eligibility(n,rows,n['player_id'] in conflict_ids)
        if reasons:
            excluded.append(dict(player_id=n['player_id'],player_name_nba=n['player_name'],positive_minutes=n['seconds']>0,combine_source_ids=';'.join(sorted({r['PLAYER_ID'] for r in rows})),reason_codes=';'.join(reasons)))
            continue
        h=float(m['HEIGHT_WO_SHOES']);w=float(m['WINGSPAN'])
        frozen.append(dict(player_id=n['player_id'],player_name_nba=n['player_name'],player_name_combine=m['PLAYER_NAME'],combine_year=int(m['SEASON']),combine_position=m['POSITION'],height_wo_shoes_inches=h,wingspan_inches=w,wingspan_advantage=w-h,wingspan_ratio=w/h,measurement_resolution_status='archive_plausible_source_validation_pending',season='2013-14',ftm=n['FTM'],fta=n['FTA'],fg3m=n['FG3M'],fg3a=n['FG3A'],minutes=n['seconds']/60,playing_seconds=n['seconds'],games_played=n['GP'],join_status='exact ID',source_flags='secondary_archives;pinned;exact_id;latest_complete_prior;source_gate_pending;standing_reach_not_used',binomial_likelihood_eligible=n['FTA']>0))
    validate_frozen(frozen)
    # Independently re-sum raw player-games, including zero-minute rows, with keys audited.
    reconstructed=collections.defaultdict(lambda:collections.Counter());seen=set();teams=collections.defaultdict(lambda:collections.Counter());games=set();zero_min_nonzero_counts=0
    for meta in sm:
        for r in archive(meta):
            if r['season_year']!='2013-14':continue
            key=(r['gameId'],r['personId'])
            if key in seen:raise ValueError('Duplicate player-game')
            seen.add(key);games.add(r['gameId']);pid=r['personId']
            vals={k:int(r[v]) for k,v in [('FTM','freeThrowsMade'),('FTA','freeThrowsAttempted'),('FG3M','threePointersMade'),('FG3A','threePointersAttempted')]}
            assert 0<=vals['FTM']<=vals['FTA'] and 0<=vals['FG3M']<=vals['FG3A']
            pieces=r['minutes'].split(':') if r['minutes'] else [];seconds=int(pieces[0])*60+int(pieces[1]) if len(pieces)==2 else 0
            if seconds==0 and any(vals.values()):zero_min_nonzero_counts+=1
            reconstructed[pid].update(vals);reconstructed[pid]['seconds']+=seconds;reconstructed[pid]['GP']+=seconds>0
            teams[r['teamId']].update(vals)
    for n in nba:
        assert all(n[k]==reconstructed[n['player_id']][k] for k in ['FTM','FTA','FG3M','FG3A','seconds','GP'])
    assert zero_min_nonzero_counts==0
    # Official GSW yearly team totals, PDF page 137; independent of candidate exposure.
    official_gsw={'FTM':1303,'FTA':1731,'FG3M':774,'FG3A':2037}
    assert all(teams['1610612744'][k]==v for k,v in official_gsw.items())
    dump(E/'shooting_internal_reconstruction.json',dict(season='2013-14',player_game_keys=len(seen),games=len(games),roster_players=len(nba),all_player_totals_reconstruct_exactly=True,zero_minute_nonzero_count_rows=0,official_aggregate_scope='Golden State only; league-wide official total unavailable',GSW_official_totals=official_gsw,GSW_archive_totals=dict(teams['1610612744']),GSW_exact_match=True,official_source='https://ak-static-int.nba.com/wp-content/uploads/sites/3/2016/10/2016-17-Media-Guide-Warriors.pdf#page=137'))
    table=pa.Table.from_pylist(frozen);out=ROOT/'data/processed/ft_2013_14_stage1_dataset.parquet'
    metadata={b'status':b'candidate frozen for review; NOT cleared for inference',b'protocol':b'docs/stage0b_protocol.md',b'no_effect_estimated':b'true'}
    table=table.replace_schema_metadata(metadata)
    # Never silently replace a different frozen dataset.
    if out.exists():
        if pq.read_table(out).to_pylist()!=frozen:raise ValueError('Existing freeze differs; explicit versioned amendment required')
    else:pq.write_table(table,out,compression='zstd')
    assert pq.read_table(out).to_pylist()==frozen
    csvwrite(ROOT/'data/interim/ft_2013_14_exclusions.csv',excluded)
    counts=collections.Counter(reason for r in excluded for reason in r['reason_codes'].split(';'))
    csvwrite(E/'ft_2013_14_exclusion_summary.csv',[dict(reason_code=k,players=v,denominator='487 roster players; multi-reason counts may overlap') for k,v in sorted(counts.items())])
    positions=collections.Counter(r['combine_position'] or '(missing)' for r in frozen)
    csvwrite(E/'position_coverage.csv',[dict(combine_position=k,players=v,share=v/len(frozen)) for k,v in sorted(positions.items())])
    reference=[]
    for pid,rows in sorted(byid.items(),key=lambda pair:int(pair[0])):
        m,_=select_measurement(rows)
        if m:reference.append(dict(player_id=pid,combine_year=int(m['SEASON']),height_wo_shoes_inches=float(m['HEIGHT_WO_SHOES']),wingspan_inches=float(m['WINGSPAN'])))
    csvwrite(ROOT/'data/interim/residual_reference_pre2013.csv',reference)
    fta=[r['fta'] for r in frozen]
    def quantile(xs,p):
        vals=sorted(xs);i=(len(vals)-1)*p;lo=int(i);hi=min(lo+1,len(vals)-1);return vals[lo]+(vals[hi]-vals[lo])*(i-lo)
    ids={r['player_id'] for r in frozen}
    groups={}
    for name,pop in [('measured',[r for r in nba if r['seconds']>0 and r['player_id'] in ids]),('unmeasured',[r for r in nba if r['seconds']>0 and r['player_id'] not in ids])]:
        groups[name]=dict(players=len(pop),median_minutes=statistics.median(r['seconds']/60 for r in pop),mean_minutes=statistics.mean(r['seconds']/60 for r in pop),median_games=statistics.median(r['GP'] for r in pop),mean_games=statistics.mean(r['GP'] for r in pop),players_with_any_box_position=sum(r['position_rows']>0 for r in pop),box_position_labeled_game_fraction=sum(r['position_rows'] for r in pop)/sum(r['GP'] for r in pop))
    summary=dict(status='candidate_frozen_not_cleared_for_inference',roster_players=len(nba),NBA_players_positive_minutes=sum(r['seconds']>0 for r in nba),exact_id_prior_measurement_matches=exact_prior,eligible_prior_measurement_players=len(frozen),excluded_roster_players=len(excluded),excluded_positive_minute_players=sum(r['positive_minutes'] for r in excluded),final_players=len(frozen),total_FTA=sum(fta),median_FTA=statistics.median(fta),FTA_quantiles={str(p):quantile(fta,p) for p in [0,.10,.25,.50,.75,.90,1]},FTA_zero=sum(v==0 for v in fta),FTA_ge_50=sum(v>=50 for v in fta),FTA_ge_100=sum(v>=100 for v in fta),anthropometric_ranges={k:[min(r[k] for r in frozen),max(r[k] for r in frozen)] for k in ['height_wo_shoes_inches','wingspan_inches','wingspan_advantage','wingspan_ratio']},selection_coverage=groups,reference_population_players=len(reference),repeated_measurements=len(repeated),repeated_statuses=dict(collections.Counter(r['status'] for r in repeated)),repeated_with_multiple_pre2013=sum(r['pre_2013_record_count']>1 for r in repeated),identity_conflicts_unresolved=len(crosswalk),primary_exposure='residual_wingspan (not yet calculated)',primary_outcome='2013-14 regular-season FTM out of FTA',no_effect_estimate_calculated=True)
    dump(E/'ft_2013_14_dataset_summary.json',summary)
    source_list=[dict(role='combine_archive',**cm)]+[dict(role='shooting_archive',**m) for m in sm]
    source_list += [json.loads(p.read_text()) for p in sorted(RAW.glob('*.manifest.json'))]
    for source in source_list:
        path=source.get('raw_path'); expected=source.get('raw_sha256',source.get('sha256'))
        if path and expected: assert sha(ROOT/path)==expected, 'Raw source changed: '+path
    normalized=list(E.glob('*crosscheck.csv'))+[E/'measurement_discrepancy_review.csv',E/'repeated_measurements.csv',E/'exact_id_alias_audit.csv',ROOT/'data/interim/stage0b_nba_2013_14_totals.csv',out,ROOT/'data/interim/ft_2013_14_exclusions.csv',ROOT/'data/interim/identity_crosswalk_review.csv',ROOT/'data/interim/residual_reference_pre2013.csv']
    dump(E/'source_manifest.json',dict(sources=source_list,normalized_outputs={str(p.relative_to(ROOT)):sha(p) for p in normalized},interpretation='Official pages are factual spot-checks, not complete proof of archive lineage; all full payloads stay local.'))
    protected=json.loads((E/'stage0_preservation_manifest.json').read_text())
    assert all(sha(ROOT/p)==h for p,h in protected.items())
    dump(E/'build_manifest.json',dict(built_at=datetime.datetime.now(datetime.timezone.utc).isoformat(),status=summary['status'],dataset=str(out.relative_to(ROOT)),dataset_sha256=sha(out),dataset_rows=len(frozen),schema=str(table.schema),protocol_sha256=sha(ROOT/'docs/stage0b_protocol.md'),residual_reference_sha256=sha(ROOT/'data/interim/residual_reference_pre2013.csv'),source_manifest_sha256=sha(E/'source_manifest.json'),stage0_preserved=True,stage0_protected_files=len(protected),pyarrow_version=pa.__version__,scientific_model_executed=False,code_sha256={str(p.relative_to(ROOT)):sha(p) for p in list((ROOT/'src/anthropometrics_shooting').glob('*.py'))+list((ROOT/'scripts').glob('*stage0b*.py'))}))
    print(json.dumps(summary,indent=2))
if __name__=='__main__':main()
