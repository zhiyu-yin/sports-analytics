"""Reaggregate frozen player-game archive; no exposure/outcome association."""
from pathlib import Path
import json,csv,hashlib,sys
import pandas as pd
ROOT=Path(__file__).resolve().parents[1]; E=ROOT/'docs/stage3_evidence'
sys.path.insert(0,str(ROOT/'src'))
from anthropometrics_shooting.normalize import season,player_id,name_key
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def save(name,obj): (E/name).write_text(json.dumps(obj,indent=2)+'\n')
def main():
 metas=json.loads((ROOT/'docs/stage0_evidence/shooting_archive_sources.json').read_text()); frames=[]; inventory=[]
 for meta in metas:
  p=ROOT/meta['raw_path']; assert sha(p)==meta['sha256']; df=pd.read_csv(p,dtype=str,keep_default_na=False); frames.append(df); inventory.append(dict(**meta,schema=list(df.columns),row_count=len(df)))
 raw=pd.concat(frames,ignore_index=True); assert not raw.duplicated(['gameId','personId']).any()
 raw['player_id']=raw.personId.map(player_id); raw['season']=raw.season_year.map(season)
 raw['seconds']=raw.minutes.map(lambda v:round(float(v.split(':')[0])*60+float(v.split(':')[1])) if ':' in v else round(float(v or 0)*60))
 # Verify archive game IDs are regular season (002 prefix after zero padding).
 raw['regular_season']=raw.gameId.str.zfill(10).str.startswith('002'); assert raw.regular_season.all(),raw.loc[~raw.regular_season,'gameId'].unique()
 for out,src in [('ftm','freeThrowsMade'),('fta','freeThrowsAttempted'),('fg3m','threePointersMade'),('fg3a','threePointersAttempted')]:
  raw[out]=pd.to_numeric(raw[src]); assert (raw[out]>=0).all() and (raw[out]%1==0).all()
 assert (raw.ftm<=raw.fta).all() and (raw.fg3m<=raw.fg3a).all()
 # A recorded 0:00 appearance is distinct from an empty-minute DNP.
 played=raw[raw.minutes.ne('')].copy()
 eligible_keys=set(map(tuple,raw.loc[raw.seconds>0,['player_id','season']].to_numpy()))
 positive=played[[tuple(k) in eligible_keys for k in played[['player_id','season']].to_numpy()]].copy(); positive['position_available']=positive.position.ne('').astype(int)
 aggregation=dict(player_name=('personName','last'),seconds=('seconds','sum'),games_played=('gameId','size'),position_games=('position_available','sum'),ftm=('ftm','sum'),fta=('fta','sum'),fg3m=('fg3m','sum'),fg3a=('fg3a','sum'))
 grouped=positive.groupby(['player_id','season']).agg(**aggregation).reset_index(); grouped['minutes']=grouped.seconds/60
 grouped.to_parquet(ROOT/'data/interim/stage3_all_player_seasons.parquet',index=False)
 teamcol='teamId'; assert teamcol in positive.columns
 teams=positive.groupby(['season',teamcol]).agg(ftm=('ftm','sum'),fta=('fta','sum'),fg3m=('fg3m','sum'),fg3a=('fg3a','sum'),games_played=('gameId','nunique'),seconds=('seconds','sum')).reset_index(); teams.to_csv(ROOT/'data/interim/stage3_team_totals.csv',index=False)
 seasons=sorted(grouped.season.unique()); selected=sorted(set([seasons[0],'2016-17' if '2016-17' in seasons else seasons[len(seasons)//2],seasons[-1]])); assert len(selected)==3
 samples=[]
 for s in selected:
  ids=grouped.loc[grouped.season==s,['player_id','player_name']].copy(); ids['selection_hash']=ids.player_id.map(lambda pid:hashlib.sha256(f'stage3-validation|{s}|{pid}'.encode()).hexdigest()); ids=ids.sort_values('selection_hash').head(12); ids['season']=s; samples.append(ids)
 pd.concat(samples).to_csv(E/'shooting_validation_sample_predeclared.csv',index=False)
 save('shooting_archive_provenance.json',dict(sources=inventory,seasons=seasons,regular_season_game_id_prefix='002',raw_rows=len(raw),positive_player_games=len(positive),player_seasons=len(grouped),unique_players=grouped.player_id.nunique(),validation_seasons=selected,aggregate_hash=sha(ROOT/'data/interim/stage3_all_player_seasons.parquet')))
 print(json.dumps({'seasons':seasons,'player_seasons':len(grouped),'validation_seasons':selected,'raw_columns':list(raw.columns)},indent=2))
if __name__=='__main__': main()
