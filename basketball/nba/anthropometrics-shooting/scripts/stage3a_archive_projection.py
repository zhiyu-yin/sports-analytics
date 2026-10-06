import sys,json
from stage3a_prepare import *
s=pd.read_csv(E/'minute_audit_sample_predeclared.csv',dtype=str)
sources=json.loads((ROOT/'docs/stage0_evidence/shooting_archive_sources.json').read_text())
assert all(sha(ROOT/x['raw_path'])==x['sha256'] for x in sources)
cols=['season_year','game_date','gameId','personId','personName','minutes','comment','freeThrowsMade','freeThrowsAttempted']
a=pd.concat([pd.read_csv(ROOT/x['raw_path'],usecols=cols,dtype=str,keep_default_na=False) for x in sources]);a=a[a.season_year.isin(['2010-11','2016-17','2023-24'])];a.gameId=a.gameId.str.zfill(10)
a.to_csv(E/'archive_minute_projection.csv',index=False)
z=a[a.minutes.eq('0:00')];z.to_csv(E/'zero_minute_archive_predeclared.csv',index=False)
t=s[['season','player_id']].to_dict('records')
for r in z.itertuples():
 row={'season':r.season_year,'player_id':r.personId}
 if row not in t:t.append(row)
save('retrieval_targets.json',t)
print('targets',len(t),'zero rows',len(z))
