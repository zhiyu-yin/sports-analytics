"""Rebuild compact evidence from checksum-verified local archives; no network or models."""
import sys,csv,json,hashlib,collections
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from anthropometrics_shooting.provenance import ROOT,EVIDENCE
from anthropometrics_shooting.combine import normalize
from anthropometrics_shooting.normalize import number,player_id,season,inches,name_key
from anthropometrics_shooting.identities import classify
from anthropometrics_shooting.validate import anthropometrics,shooting,duplicate_keys

def dump(name,obj): (EVIDENCE/name).write_text(json.dumps(obj,indent=2,ensure_ascii=False)+'\n')
def writecsv(path,rows,fields=None):
    with path.open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=fields or list(rows[0])); w.writeheader(); w.writerows(rows)
def read(meta):
    path=ROOT/meta['raw_path']; b=path.read_bytes()
    if hashlib.sha256(b).hexdigest()!=meta['sha256']: raise ValueError('Checksum mismatch')
    return csv.DictReader(b.decode('utf-8-sig').splitlines())

def main():
    (ROOT/'data/interim').mkdir(parents=True,exist_ok=True)
    (ROOT/'data/processed').mkdir(parents=True,exist_ok=True)
    cm=json.loads((EVIDENCE/'archive_sources.json').read_text())[0]
    cr=list(read(cm)); norm=[normalize(r) for r in cr]
    valid=[r for r in norm if not anthropometrics(r)]
    byid=collections.defaultdict(list)
    for r in valid: byid[r['player_id'] or 'missing_id:'+name_key(r['player_name'])].append(r)
    # Preserve repeated combines in audit, use earliest for the schema-only prototype.
    unique=[sorted(v,key=lambda r:int(r['combine_year']))[0] for v in byid.values()]
    missing={k:sum(number(r[k]) is None for r in cr) for k in ['HEIGHT_WO_SHOES','HEIGHT_W_SHOES','WINGSPAN','WEIGHT','STANDING_REACH','HAND_LENGTH','HAND_WIDTH']}
    fields=list(cr[0]); dump('combine_schema.json',dict(evidence_type='observed_secondary_archive',fields=fields,row_count=len(cr),numeric_units={'linear':'inches','weight':'pounds'},numeric_storage='CSV strings parse as numbers; parallel feet/inches display strings',missing=missing))
    sm=json.loads((EVIDENCE/'shooting_archive_sources.json').read_text())
    mapping={'FTM':'freeThrowsMade','FTA':'freeThrowsAttempted','FT_PCT':'freeThrowsPercentage','FG3M':'threePointersMade','FG3A':'threePointersAttempted','FG3_PCT':'threePointersPercentage','FGM':'fieldGoalsMade','FGA':'fieldGoalsAttempted','FG_PCT':'fieldGoalsPercentage'}
    counters=collections.Counter(); players={}; seasons=collections.defaultdict(set); games=collections.defaultdict(set); agg={}; seen={}; conflicts=[]; min_dates={}; max_dates={}; pos=collections.Counter()
    for meta in sm:
        reader=read(meta); shooting_fields=reader.fieldnames
        for r in reader:
            counters['raw_rows']+=1
            s=season(r['season_year']); pid=player_id(r['personId']); key=(r['gameId'],pid)
            fingerprint=tuple(r.values())
            if key in seen:
                counters['duplicate_game_player_rows']+=1
                if seen[key]!=fingerprint: conflicts.append(key)
                continue
            seen[key]=fingerprint; games[s].add(r['gameId'])
            min_dates[s]=min(min_dates.get(s,r['game_date']),r['game_date']); max_dates[s]=max(max_dates.get(s,r['game_date']),r['game_date'])
            raw={k:r[v] for k,v in mapping.items()}
            for issue in shooting(raw): counters[issue]+=1
            parts=r['minutes'].split(':') if r['minutes'] else []
            minutes=(float(parts[0])+float(parts[1])/60) if len(parts)==2 else (float(parts[0]) if len(parts)==1 else 0)
            if minutes<=0: counters['rows_without_positive_minutes']+=1; continue
            players[pid]=dict(player_id=pid,player_name=r['personName']); seasons[s].add(pid); pos[r['position'] or '(missing)']+=1
            k=(pid,s)
            if k not in agg: agg[k]=dict(player_id=pid,player_name=r['personName'],nba_season=s,ftm=0,fta=0,fg3m=0,fg3a=0,fgm=0,fga=0,gp=0,minutes=0)
            a=agg[k]; a['gp']+=1; a['minutes']+=minutes
            for field in ['FTM','FTA','FG3M','FG3A','FGM','FGA']: a[field.lower()]+=int(raw[field])
    if conflicts: raise ValueError(f'Conflicting duplicate player-games: {len(conflicts)}')
    joins=classify(unique,list(players.values()))
    id_name_differences=[dict(player_id=r['player_id'],combine_name=r['player_name'],shooting_name=players[r['player_id']]['player_name']) for r in joins if r['join_status']=='exact ID' and name_key(r['player_name'])!=name_key(players[r['player_id']]['player_name'])]
    writecsv(ROOT/'data/interim/id_name_differences.csv',id_name_differences)
    statuses=collections.Counter(r['join_status'] for r in joins)
    matched={r['matched_player_id'] for r in joins if r['join_status'] in ['exact ID','exact normalized name']}
    measured_lookup={r['matched_player_id']:r for r in joins if r['matched_player_id']}
    # No pre-measurement performance in feasibility sample.
    matched_agg=[r for (pid,s),r in agg.items() if pid in matched and int(s[:4])>=int(measured_lookup[pid]['combine_year'])]
    after_ids={r['player_id'] for r in matched_agg}
    cov=[]
    for y in sorted({r['SEASON'] for r in cr}):
        rows=[r for r in cr if r['SEASON']==y]; vr=[r for r in valid if r['combine_year']==y]
        ids={r['player_id'] or 'missing_id:'+name_key(r['player_name']) for r in vr}
        later={pid for pid in ids if any(pid in seasons[s] and int(s[:4])>=int(y) for s in seasons)}
        cov.append(dict(combine_year=y,records=len(rows),height_wingspan_complete_rows=len(vr),unique_measured_entities=len(ids),height_wingspan_missing_rows=len(rows)-len(vr),missing_rate=(len(rows)-len(vr))/len(rows),observed_NBA_after_measurement_2010_2023=len(later),lifetime_NBA_count='',NBA_missing_measurement_rate=''))
    writecsv(EVIDENCE/'coverage_by_year.csv',cov)
    seasonrows=[]
    for s in sorted(seasons):
        nba=seasons[s]; mids={pid for pid in nba & matched if int(measured_lookup[pid]['combine_year'])<=int(s[:4])}
        ar=[r for r in matched_agg if r['nba_season']==s]
        seasonrows.append(dict(nba_season=s,nba_players=len(nba),measured_players=len(mids),reverse_coverage=len(mids)/len(nba),missing_measurement_rate=1-len(mids)/len(nba),matched_fta=sum(r['fta'] for r in ar),matched_player_seasons=len(ar),players_FTA_ge_50=sum(r['fta']>=50 for r in ar),players_FTA_ge_100=sum(r['fta']>=100 for r in ar),games=len(games[s]),first_date=min_dates[s],last_date=max_dates[s]))
    writecsv(EVIDENCE/'match_rate_summary.csv',seasonrows)
    cohort=[r for r in unique if r['combine_year']=='2013']; cohort_matches=[r for r in joins if r['combine_year']=='2013' and r['matched_player_id']]
    summary=dict(evidence_type='observed_secondary_archives_only',combine_rows=len(cr),unique_record_ids=len({r['PLAYER_ID'] for r in cr if float(r['PLAYER_ID'])>0}),missing_id_records=sum(float(r['PLAYER_ID'])<=0 for r in cr),complete_measurement_rows=len(valid),unique_measured_players=len(unique),NBA_players_in_archive=len(players),join_status_counts={s:statuses.get(s,0) for s in ['exact ID','exact normalized name','manually reviewable','ambiguous','unmatched']},matched_measured_players=len(matched),measured_to_observed_NBA_fraction=len(matched)/len(unique),expected_NBA_denominator=None,expected_NBA_match_rate=None,reason='No independent complete NBA-ever roster; unmatched includes non-NBA prospects and careers outside 2010-11 through 2023-24.',matched_after_measurement_players=len(after_ids),matched_player_seasons=len(matched_agg),total_fta=sum(r['fta'] for r in matched_agg),player_seasons_FTA_ge_50=sum(r['fta']>=50 for r in matched_agg),player_seasons_FTA_ge_100=sum(r['fta']>=100 for r in matched_agg),cohort_2013=dict(unique_measured=len(cohort),matched=len(cohort_matches)),prototype_rule='First 12 alphabetically sorted matched players in 2013-14, earliest complete combine on/before season; audit only.')
    dump('join_audit.json',summary)
    issues=collections.Counter(i for r in norm for i in anthropometrics(r))
    diff=[]
    for r in cr:
        for numeric,formatted in [('HEIGHT_WO_SHOES','HEIGHT_WO_SHOES_FT_IN'),('WINGSPAN','WINGSPAN_FT_IN')]:
            if r[formatted] and r[numeric]:
                try:
                    if abs(inches(r[formatted])-float(r[numeric]))>0.01: diff.append((r['PLAYER_ID'],numeric,'mismatch'))
                except ValueError: diff.append((r['PLAYER_ID'],numeric,'malformed'))
    dump('data_quality_summary.json',dict(combine_issues=issues,missing=missing,duplicate_player_year=duplicate_keys(norm,['player_id','combine_year']),repeated_player_ids={k:len(v) for k,v in byid.items() if len(v)>1},wingspan_below_height=sum(r['wingspan_inches']<r['height_inches'] for r in valid),formatted_numeric_issues=diff,shooting=counters,shooting_conflicting_duplicates=len(conflicts),box_position_distribution=pos,id_name_difference_count=len(id_name_differences),final_player_season_duplicate_count=0,notes=['Zero-attempt percentages normalized to missing, never 0 accuracy.','Range flags are review prompts, not corrections.','Complete measurement means positive plausible numeric height and wingspan.']))
    dump('shooting_schema.json',dict(evidence_type='observed_secondary_archive',fields=shooting_fields,raw_rows=counters['raw_rows'],grain='player-game (includes inactive/DNP rows)',normalized_grain='player-season audit aggregates in memory only',seasons=sorted(seasons),source_field_mapping=mapping))
    sample=[]
    for s in sorted([r for r in matched_agg if r['nba_season']=='2013-14'],key=lambda r:r['player_name'])[:12]:
        m=measured_lookup[s['player_id']]
        sample.append({**{k:m[k] for k in ['player_id','player_name','combine_year','height_inches','wingspan_inches','wingspan_advantage','wingspan_ratio','position']},**{k:s[k] for k in ['nba_season','ftm','fta','fg3m','fg3a']},'join_status':m['join_status']})
    writecsv(ROOT/'data/interim/join_prototype.csv',sample)
    writecsv(ROOT/'data/interim/identity_audit.csv',joins)
    # Only compact aggregates in docs; player-level table remains ignored local data.
    print(json.dumps(summary,indent=2)); print('Quality:',dict(issues),dict(counters)); print('Prototype:',sample[:2])
if __name__=='__main__': main()
