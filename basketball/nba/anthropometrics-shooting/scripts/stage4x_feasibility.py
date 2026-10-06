"""Stage 4X-A source audit only. No scientific fitting or record repairs."""
from pathlib import Path
import json, hashlib, zipfile, datetime, os, csv
import pandas as pd
ROOT=Path(__file__).resolve().parents[1]; os.chdir(ROOT)
E=Path('docs/stage4x_evidence'); E.mkdir(exist_ok=True)
def js(name,obj): (E/name).write_text(json.dumps(obj,indent=2,default=str)+'\n')
def sha(p):
 h=hashlib.sha256()
 with open(p,'rb') as f:
  for b in iter(lambda:f.read(1048576),b''): h.update(b)
 return h.hexdigest()
# Local inventory excludes software environments; source tables and payloads included.
inventory=[]
for base,dirs,files in os.walk(ROOT.parents[2]):
 dirs[:]=[x for x in dirs if x not in {'.git','node_modules','__pycache__','site-packages','models'} and not x.startswith('.venv')]
 for n in files:
  p=Path(base)/n
  if p.suffix not in {'.csv','.parquet','.payload'} or 'stage4x' in str(p): continue
  rec={'path':str(p.relative_to(ROOT.parents[2])),'bytes':p.stat().st_size}
  try:
   if p.suffix=='.parquet':
    import pyarrow.parquet as pq
    cols=pq.read_schema(p).names
   else:
    with p.open(errors='strict') as f: cols=next(csv.reader(f))
    if len(cols)>100 or any(len(x)>200 for x in cols): continue
   rec['columns']=cols;rec['has_zone_field']=any(x.upper() in {'SHOT_ZONE_BASIC','BASIC_ZONE'} for x in cols)
   inventory.append(rec)
  except Exception: pass
js('shot_data_inventory.json',{'scope':'Repository table schemas before downloaded Stage4X sources; software environments excluded','local_tables':inventory,'preexisting_zone_tables':[r for r in inventory if r['has_zone_field']]})
sources=json.load(open('docs/stage3_evidence/shooting_archive_provenance.json'))['sources']
b=pd.concat([pd.read_csv(s['raw_path'],usecols=['season_year','gameId','personId','fieldGoalsMade','fieldGoalsAttempted','threePointersMade','threePointersAttempted']) for s in sources],ignore_index=True)
b=b.rename(columns={'season_year':'season','gameId':'GAME_ID','personId':'PLAYER_ID','fieldGoalsMade':'fgm','fieldGoalsAttempted':'fga','threePointersMade':'fg3m','threePointersAttempted':'fg3a'})
b=b.groupby(['season','GAME_ID','PLAYER_ID'])[['fgm','fga','fg3m','fg3a']].sum()
s=pd.read_parquet('data/interim/stage3_all_player_seasons.parquet');s.player_id=s.player_id.astype(int)
a=pd.read_csv('data/interim/stage3_frozen_player_vectors.csv');a.player_id=a.player_id.astype(int)
coverage=[];links=[];mismatches=[];duplicates=[];metadata=[];zone_counts=[]
for year in range(2011,2025):
 season=f'{year-1}-{str(year)[2:]}';p=Path(f'data/raw/stage4x/NBA_{year}_Shots.csv.zip')
 z=zipfile.ZipFile(p); member=[x for x in z.namelist() if x.endswith('.csv') and not x.startswith('__')][0];d=pd.read_csv(z.open(member))
 metadata.append({'season':season,'path':str(p),'sha256':sha(p),'git_blob_sha1':hashlib.sha1(b'blob '+str(p.stat().st_size).encode()+b'\0'+p.read_bytes()).hexdigest(),'columns':d.columns.tolist(),'rows':len(d),'shot_event_id_present':False})
 for pid,n in d.groupby('PLAYER_ID').size().items(): links.append({'season':season,'player_id':pid,'shot_records':n,'linkage':'MATCHED_ID' if pid in set(a.player_id) else 'UNMATCHED_ID','ambiguous':False})
 dup=d[d.duplicated(keep=False)].copy();dup['audit_season']=season;duplicates.append(dup)
 d['three']=d.SHOT_TYPE.eq('3PT Field Goal');d['three_made']=d.three & d.SHOT_MADE
 g=d.groupby(['GAME_ID','PLAYER_ID']).agg(fgm=('SHOT_MADE','sum'),fga=('SHOT_MADE','size'),fg3m=('three_made','sum'),fg3a=('three','sum'))
 ref=b.loc[season];v=ref.join(g,how='outer',lsuffix='_target',rsuffix='_shot').fillna(0)
 bad=pd.Series(False,index=v.index)
 counts={}
 for field in ['fgm','fga','fg3m','fg3a']:
  q=v[field+'_target']!=v[field+'_shot'];counts[field+'_game_disagreements']=int(q.sum());bad|=q
 vv=v[bad].reset_index();vv['season']=season;mismatches.append(vv)
 t=d.groupby('PLAYER_ID').agg(fg3m=('three_made','sum'),fg3a=('three','sum'))
 r=s[s.season==season].set_index('player_id')[['fg3m','fg3a']];u=r.join(t,how='outer',lsuffix='_target',rsuffix='_shot').fillna(0)
 counts['fg3m_season_disagreements']=int((u.fg3m_target!=u.fg3m_shot).sum());counts['fg3a_season_disagreements']=int((u.fg3a_target!=u.fg3a_shot).sum())
 known={'Restricted Area','In The Paint (Non-RA)','Mid-Range','Left Corner 3','Right Corner 3','Above the Break 3','Backcourt'}
 threezones={'Left Corner 3','Right Corner 3','Above the Break 3','Backcourt'}
 for zone,q in d.groupby('BASIC_ZONE'):zone_counts.append({'season':season,'zone':zone,'attempts':len(q),'makes':int(q.SHOT_MADE.sum())})
 row={'season':season,'shot_records':len(d),'players':d.PLAYER_ID.nunique(),'games':d.GAME_ID.nunique(),'matched_players':d.loc[d.PLAYER_ID.isin(a.player_id),'PLAYER_ID'].nunique(),'exact_duplicate_excess':int(d.duplicated().sum()),'duplicate_group_rows':len(dup),'unknown_zone':int((~d.BASIC_ZONE.isin(known)).sum()),'zone_type_conflict':int((d.three!=d.BASIC_ZONE.isin(threezones)).sum()),'season_label_conflict':int((d.SEASON_2!=season).sum()),'missing_required':int(d[['PLAYER_ID','GAME_ID','SHOT_MADE','BASIC_ZONE','SHOT_TYPE','LOC_X','LOC_Y','SHOT_DISTANCE']].isna().any(axis=1).sum()),'invalid_made':int((~d.SHOT_MADE.isin([True,False])).sum()),'event_outcome_conflict':int((d.SHOT_MADE!=d.EVENT_TYPE.eq('Made Shot')).sum()),'gross_location_outside_court':int(((d.LOC_X.abs()>25.1)|(d.LOC_Y<0)|(d.LOC_Y>94)|(d.SHOT_DISTANCE<0)|(d.SHOT_DISTANCE>94)).sum()),**counts}
 coverage.append(row)
 print(season,row,flush=True)
pd.DataFrame(coverage).to_csv(E/'shot_season_coverage.csv',index=False)
pd.DataFrame(links).to_csv(E/'shot_player_linkage.csv',index=False)
pd.concat(mismatches).to_csv(E/'player_game_disagreements.csv',index=False)
pd.concat(duplicates).to_csv(E/'duplicate_record_groups.csv',index=False)
pd.DataFrame(zone_counts).to_csv(E/'zone_counts.csv',index=False)
js('downloaded_sources.json',metadata)
js('audit_counts.json',coverage)
