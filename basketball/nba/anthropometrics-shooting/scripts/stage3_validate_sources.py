"""Official factual comparisons; never calculate an exposure-outcome association."""
import json,re,csv
import pandas as pd
from stage3_sources import ROOT,E,sha,save,name_key
from anthropometrics_shooting.normalize import inches,number
RAW=ROOT/'data/raw/stage3'
def official_stats(path,kind):
 s=json.loads(path.read_text()); assert s['filters'][1:3]==['Regular Season','Totals']; t=s['tables'][0]; rows=[]
 for row in t['rows']:
  links=[a['href'] for a in row['links'] if re.match(f'/stats/{kind}/[0-9]+/',a['href'])]; assert len(links)==1
  pid=re.search(r'/([0-9]+)/',links[0])[1]; r=dict(zip(t['headers'],row['cells'])); r['id']=pid; rows.append(r)
 return rows,s

def main():
 source=[]
 for p in sorted(RAW.glob('*.json')):
  s=json.loads(p.read_text()); source.append(dict(path=str(p.relative_to(ROOT)),sha256=sha(p),url=s['url'],retrieved_at=s['retrieved_at'],accepted=p.name!='players_2016-17.json',note='partial pagination capture superseded by complete capture' if p.name=='players_2016-17.json' else 'official rendered DOM factual table'))
 save('official_capture_manifest.json',source)
 d=pd.read_parquet(ROOT/'data/interim/stage3_all_player_seasons.parquet'); teams=pd.read_csv(ROOT/'data/interim/stage3_team_totals.csv',dtype={'teamId':str}); sample=pd.read_csv(E/'shooting_validation_sample_predeclared.csv',dtype={'player_id':str}); checks=[]; aggregates=[]; census=[]
 mapping={'ftm':'FTM','fta':'FTA','fg3m':'3PM','fg3a':'3PA','games_played':'GP','minutes':'MIN'}
 for season in sorted(sample.season.unique()):
  path=RAW/f'players_{season}{"_complete" if season=="2016-17" else ""}.json'; records,meta=official_stats(path,'player'); lookup={r['id']:r for r in records}; assert len(records)==len(lookup)
  for a in d[d.season==season].itertuples():
   o=lookup.get(a.player_id)
   for field,col in mapping.items():
    observed=float(o[col]) if o else None; value=getattr(a,field); tol=.050001 if field=='minutes' else 0
    rec=dict(season=season,player_id=a.player_id,player_name=a.player_name,field=field,archive=value,official=observed,difference=value-observed if observed is not None else None,tolerance=tol,match=observed is not None and abs(value-observed)<=tol,source=meta['url'],raw_sha256=sha(path))
    census.append(rec)
    if a.player_id in set(sample.loc[sample.season==season,'player_id']): checks.append(rec)
  path=RAW/f'teams_{season}.json'; records,meta=official_stats(path,'team'); assert len(records)==30
  official={r['id']:r for r in records}; sub=teams[teams.season==season]; assert len(sub)==30
  for a in sub.itertuples():
   for field,col in list(mapping.items())[:5]:
    v=float(official[a.teamId][col]); av=getattr(a,field); aggregates.append(dict(season=season,team_id=a.teamId,field=field,archive=av,official=v,difference=av-v,match=av==v,source=meta['url'],raw_sha256=sha(path)))
 pd.DataFrame(checks).to_csv(E/'shooting_player_crosscheck.csv',index=False); pd.DataFrame(census).to_csv(E/'shooting_census_crosscheck.csv',index=False); pd.DataFrame(aggregates).to_csv(E/'shooting_team_reconciliation.csv',index=False)
 # Later-year census, same-year normalized exact unique name only.
 archive=json.loads((ROOT/'docs/stage0_evidence/archive_sources.json').read_text())[0]; p=ROOT/archive['raw_path']; assert sha(p)==archive['sha256']; combine=list(csv.DictReader(p.open())); corrected=[]; corrections=[]; comparisons=[]; years=[]
 for year in sorted({int(r['SEASON']) for r in combine if int(r['SEASON'])>2013}):
  path=RAW/f'combine_{year}.json'; meta=json.loads(path.read_text()); assert int(meta['season'][:4])==year; t=meta['tables'][0]
  heads=[v.replace('\xa0',' ') for v in t['headers']]; assert heads[5]=='HEIGHT W/O SHOES' and heads[9]=='WINGSPAN'
  official={}; duplicates=set()
  for cells in t['rows']:
   key=name_key(cells[0]); duplicates.update([key] if key in official else []); official[key]=cells
  rows=[r for r in combine if int(r['SEASON'])==year]; stats=dict(year=year,archive_rows=len(rows),official_rows=len(t['rows']),complete_pairs=0,exact_pairs=0,rounding_pairs=0,corrected_pairs=0,conflicts=0,missing_official_pairs=0,unmatched_names=0,quarantined=0)
  for r in rows:
   key=name_key(r['PLAYER_NAME']); cells=official.get(key); values={}; status='exact'; reason=''
   if cells is None or key in duplicates: status='quarantined'; reason='unmatched or ambiguous exact normalized name'; stats['unmatched_names']+=1
   else:
    for field,i in [('HEIGHT_WO_SHOES',5),('WINGSPAN',9)]:
     raw=number(r[field]); value=inches(cells[i]); values[field]=value
     if value is None: status='quarantined'; reason='missing official core pair'
     elif raw!=value:
      if raw is not None and abs(raw-value)<=.125:
       if status=='exact': status='rounding_consistent'
       values[field]=raw
      else:
       if status!='quarantined': status='official_corrected'
       corrections.append(dict(player_id=r['PLAYER_ID'],player_name=r['PLAYER_NAME'],combine_year=year,field=field,raw_numeric_value=raw,raw_display_value=r[field+'_FT_IN'],official_value=value,source=meta['url'],resolution='official_value_applied',reason='same-year exact normalized unique name; official core measurement supersedes secondary numeric value',raw_sha256=sha(path)))
    if any(v is None for v in values.values()): stats['missing_official_pairs']+=1
    else: stats['complete_pairs']+=1
   if status=='quarantined': stats['quarantined']+=1
   elif status=='exact': stats['exact_pairs']+=1
   elif status=='rounding_consistent': stats['rounding_pairs']+=1
   else: stats['corrected_pairs']+=1; stats['conflicts']+=1
   comparisons.append(dict(player_id=r['PLAYER_ID'],player_name=r['PLAYER_NAME'],combine_year=year,status=status,reason=reason,archive_height=number(r['HEIGHT_WO_SHOES']),official_height=values.get('HEIGHT_WO_SHOES'),archive_wingspan=number(r['WINGSPAN']),official_wingspan=values.get('WINGSPAN'),source=meta['url'],raw_sha256=sha(path)))
   if status!='quarantined': corrected.append(dict(player_id=r['PLAYER_ID'],player_name_combine=r['PLAYER_NAME'],combine_year=year,combine_position=r['POSITION'],height_wo_shoes_inches=values['HEIGHT_WO_SHOES'],wingspan_inches=values['WINGSPAN'],measurement_source_status='official_same_year_pair',measurement_correction_status=status))
  years.append(stats)
 cols=['player_id','player_name','combine_year','field','raw_numeric_value','raw_display_value','official_value','source','resolution','reason','raw_sha256']; correction=pd.DataFrame(corrections,columns=cols); correction.to_csv(E/'measurement_corrections.csv',index=False); correction.to_csv(ROOT/'data/interim/stage3_measurement_corrections.csv',index=False)
 pd.DataFrame(comparisons).to_csv(E/'later_combine_comparison.csv',index=False); pd.DataFrame(years).to_csv(E/'later_combine_validation_by_year.csv',index=False)
 # Retain only complete Stage 0C validated pre-2014 vectors; no reference refit.
 older=pd.read_csv(ROOT/'data/interim/stage0c_official_measurements.csv',dtype={'player_id':str}); old_lookup={(r.player_id,int(r.combine_year)):r for r in older.itertuples() if r.combine_year<=2013}
 for r in combine:
  y=int(r['SEASON'])
  if y>2013 or int(r['PLAYER_ID'])<=0: continue
  o=old_lookup[(r['PLAYER_ID'],y)]; h=number(r['HEIGHT_WO_SHOES']); w=number(r['WINGSPAN'])
  if h is None or w is None: continue
  assert h==o.barefoot_height and w==o.wingspan
  corrected.append(dict(player_id=r['PLAYER_ID'],player_name_combine=r['PLAYER_NAME'],combine_year=y,combine_position=r['POSITION'],height_wo_shoes_inches=h,wingspan_inches=w,measurement_source_status='Stage0C_official_pair',measurement_correction_status='unchanged'))
 valid=pd.DataFrame(corrected); valid=valid[(valid.player_id.astype(int)>0)&valid.height_wo_shoes_inches.between(60,96)&valid.wingspan_inches.between(60,108)]; valid.to_csv(ROOT/'data/interim/stage3_validated_measurements.csv',index=False)
 shooting_pass=len(checks)==216 and all(r['match'] for r in checks) and len(aggregates)==450 and all(r['match'] for r in aggregates)
 # Unexpected census conflicts also block release, even beyond the preselected sample.
 census_pass=all(r['match'] for r in census)
 summary=dict(part_A_source_gate='PASS' if shooting_pass and census_pass else 'BLOCKED',shooting_sample_players=36,shooting_sample_fields=len(checks),sample_mismatches=[r for r in checks if not r['match']],team_mismatches=[r for r in aggregates if not r['match']],census_mismatches=[r for r in census if not r['match']],shooting_sample_pass=shooting_pass,census_pass=census_pass,anthropometric_years=years,correction_fields=len(corrections),validated_measurement_rows=len(valid),inference_authorized=False,note='Panel freeze and tests additionally required before Part B')
 save('multi_season_source_validation.json',summary)
 print(json.dumps(summary,indent=2))
if __name__=='__main__': main()
