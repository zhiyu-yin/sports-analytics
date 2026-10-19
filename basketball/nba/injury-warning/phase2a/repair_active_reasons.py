"""Prefer full named final-box reasons to truncated structured-page medical comments."""
from io import BytesIO
from pathlib import Path
import re
from .prepare import rows,write
from .acquire import D,manifest,read
from injury_warning.longitudinal import canonical,absence_category

def repair():
    from pypdf import PdfReader
    sm=manifest();pg=rows('player_games');texts={};changes=[]
    for r in pg:
        if r['appeared']=='True' or r['reason'] not in {'DND - Injury/Illness','DNP - Injury/Illness','NWT - Injury/Illness'}:continue
        sid='book_'+r['game_id']
        if sm.get(sid,{}).get('status')!='obtained':continue
        if sid not in texts:texts[sid]=PdfReader(BytesIO(read(sid,sm))).pages[0].extract_text(extraction_mode='layout')
        matches=[l for l in texts[sid].splitlines() if canonical(r['player_name']) in canonical(l) and re.search(r'(?:DND|DNP|NWT) -',l)]
        if len(matches)==1:
            value=re.search(r'(?:DND|DNP|NWT) -.*',matches[0])[0].strip()
            if value!=r['reason']:
                changes.append(dict(player_id=r['player_id'],game_id=r['game_id'],old_reason=r['reason'],new_reason=value,old_category=r['category'],new_category=absence_category(value),source_id=sid,evidence_locator='FINAL BOX page 1 full named active-box DND/DNP/NWT row'))
                r.update(reason=value,category=absence_category(value),reason_source=sid,reason_locator='FINAL BOX page 1 full named active-box row; structured generic comment was truncated')
    old=rows('reason_extraction_corrections') if (Path(D/'tables/reason_extraction_corrections.csv')).exists() else []
    history=list({(r['player_id'],r['game_id']):r for r in old+changes}.values())
    write('player_games',pg);write('reason_extraction_corrections',history);print('full named PDF reason corrections',len(changes))
if __name__=='__main__':repair()
