from .normalize import number,player_id,season

def normalize(row,nba_season):
    out=dict(player_id=player_id(row.get('PLAYER_ID')),player_name=row.get('PLAYER_NAME'),nba_season=season(nba_season))
    for k in ['FTM','FTA','FG3M','FG3A','FGM','FGA','MIN','GP','AGE']:
        out[k.lower()]=number(row.get(k))
    for m,a in [('ftm','fta'),('fg3m','fg3a'),('fgm','fga')]:
        out[m+'_pct']=out[m]/out[a] if out[a] and out[m] is not None else None
    out['fg2m']=out['fgm']-out['fg3m'] if out['fgm'] is not None and out['fg3m'] is not None else None
    out['fg2a']=out['fga']-out['fg3a'] if out['fga'] is not None and out['fg3a'] is not None else None
    return out
