from .normalize import inches, player_id

def normalize(row):
    h=inches(row.get('HEIGHT_WO_SHOES')); w=inches(row.get('WINGSPAN'))
    return dict(player_id=player_id(row.get('PLAYER_ID')) if row.get('PLAYER_ID') not in ('-1','0',-1,0) else None,player_name=row.get('PLAYER_NAME'),
        combine_year=row.get('SEASON'),height_inches=h,wingspan_inches=w,
        wingspan_advantage=w-h if h and w else None,wingspan_ratio=w/h if h and w else None,
        position=row.get('POSITION'))
