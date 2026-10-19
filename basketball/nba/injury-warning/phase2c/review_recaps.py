"""Same-agent source-locator adjudication of medical recap candidates; no C input."""
import json
from .pipeline import D,ROOT,write,rows,manifest
# Explicit player/paragraph assertions, reviewed against complete original recap.
# Empty candidates are reviewed rejections: opponent, ambiguous surname, figurative
# injury language, missed shots, contract/rest/suspension, or no player attribution.
H={2:'202681',3:'1629027 1630552',10:'203992',12:'1630552 1629631',14:'1629011',15:'1630193',17:'202681 203501',23:'1629684 202681 1627884',24:'1630182 1628467',25:'1629029',26:'1629631 1630552',27:'1630217',29:'202681',30:'1629631 1630552',34:'203991',35:'1629631',36:'203992',39:'203991',40:'1630552',41:'203992',44:'203935 201565',46:'202681 1630182 1628467 1641726',48:'202693',50:'1629011',55:'1629011 1630579',57:'202681',59:'202681 1641726 1630182',63:'202681 1629029',64:'202681 1629029',66:'203957',67:'1629631',71:'202681 1629029',73:'1641726 202681',76:'1630552',79:'203935',81:'1630581',82:'202681',84:'1630182',85:'202681 1629029',86:'1629630',88:'1629631',90:'1629011',92:'1629029',93:'203552 202681',96:'1628379',98:'202681',99:'202681',101:'202681',102:'202681',109:'1629029',110:'1629029',111:'1641726 1629684',112:'202681',117:'203957 1628467 1641726',118:'1629630',119:'1629630',127:'1629630',129:'1628991 203935',131:'203991 1629631',134:'1629029 1641726 203957',137:'1629630',138:'203935 1630217',139:'1627749',140:'1629630 203935 1630217',141:'1628991',142:'1628973',143:'1628973',145:'1631096',146:'1629029 203957 1641726',148:'1628467',150:'1629029',151:'1629029',152:'1641726',153:'1628973',155:'1628991 1630583',156:'1628983',159:'1628973',160:'1628973',161:'1629029',162:'1628973',163:'1628404',166:'1629630 203935 1630217 203500 1629634 201565 1631222',168:'1629027',171:'1629027',173:'1628392 1629011',175:'1629630 203935 1630217',176:'1630583',177:'1629630 203935 1630217',180:'1629027',186:'1629630 203500',188:'202681',191:'1629027',193:'202681',195:'1629630 203935 201565',200:'1628392',203:'202681',206:'1628379',207:'1627749',208:'203944',209:'203944',210:'1628384 1629011',214:'202681 1627884 203957',215:'1629631',218:'203944 1628384',219:'1629011',221:'1629029 202681',222:'1629029 202681',223:'1641726 203957 1627884',224:'1629029 202681',225:'1631114 1630198',231:'203944 1628384',232:'203944 1628384 1629656',236:'1629631',237:'1631114 1630198',241:'1629029 202681',242:'203935',246:'1631114 1630198',247:'202681',248:'1629029 202681',250:'203991',251:'1629029',252:'202681',257:'203944 1628384',260:'203991',262:'1628973 203944 1628384 1629011',263:'1628392',264:'203944 1628384 1629011',266:'1628991',268:'1641726',269:'202681',273:'1629631 203991',274:'1628973',276:'203991',279:'1641726 203957',280:'203991 1630168',281:'203991 1630168',282:'203944 1628978 202711 1628392',283:'1641726'}
A={5:'202681',6:'202681',8:'1628973',18:'1627884',24:'203552',32:'201565',50:'1630579',62:'1630581',103:'1641726 1629684',115:'1629726',124:'1629029',128:'203935',136:'1630217',170:'1629027',179:'202681',194:'1627884',197:'203944',228:'1628973',255:'1628973',278:'1629029'}
# Sources use only completed-game B publication assumption; later independent
# continuity reviews never enter this file. Same-event linkage is C-only elsewhere.
def review():
    raw=json.loads((ROOT/'data/raw/phase2c/recap_review.json').read_text());cards=[];seen_cards=set();people={r['player_id']:r['player_name'] for r in rows('players')}
    for r in raw:
        if not r['player_ids'] or r['game_date']>'2024-02-17':continue
        key=(r['game_id'],r['paragraph'],tuple(r['player_ids']))
        if key in seen_cards:continue
        seen_cards.add(key);cards.append(dict(r,card_id=len(cards),players={pid:people.get(pid) for pid in r['player_ids']}))
    assert len(cards)==285,'Medical review proposal inventory changed; re-review before rebuilding'
    (ROOT/'data/raw/phase2c/recap_cards.json').write_text(json.dumps(cards,indent=2)+'\n')
    out=[];signals=[];seen=set()
    for c in cards:
        selected=[]
        for kind,mapping in [('history',H),('acute',A)]:
            for pid in mapping.get(c['card_id'],'').split():
                selected.append(pid);key=(pid,c['game_id'],c['paragraph'],kind)
                if key in seen:continue
                seen.add(key);signals.append(dict(player_id=pid,source_game_id=c['game_id'],event_game_id=c['game_id'],paragraph=c['paragraph'],kind=kind,locator=f"story.content[{c['paragraph']}]",review_note='Explicit source-attributed medical history/symptom or new indexed-game injury; other named players not assumed injured. Same-agent original paragraph review.'))
        out.append(dict(card_id=c['card_id'],source_id='page_'+c['game_id'],game_date=c['game_date'],locator=f"story.content[{c['paragraph']}]",candidate_player_ids=';'.join(c['player_ids']),accepted_player_ids=';'.join(sorted(set(selected))),decision='accept_specific_medical_assertions' if selected else 'reject_no_explicit_medical_assertion_for_sampled_player',reviewer='Codex same agent, not independent human',evidence_role='B end-upper+6h; A historical original timing unresolved',reason='Read original paragraph; exact player attribution, including surname/suffix disambiguation. No inference from missed shots, opponent injuries, rest, suspension or ambiguous pronouns.'))
    # Suffix matching in the proposal inventory is deliberately not authoritative.
    # The full paragraph says Hardaway, whereas roster uses Hardaway Jr.
    signals.append(dict(player_id='203501',source_game_id='0022300556',event_game_id='0022300556',paragraph=4,kind='acute',locator='story.content[4]',review_note='Explicit mild ankle sprain with brief exit; full paragraph subject resolves missing surname suffix.'))
    # The back announcement was in the Feb15 recap and lacked a family-name
    # proposal due to Jr. formatting; it is a historical symptom, not an indexed
    # injury in a game Pippen did not play.
    signals.append(dict(player_id='1630590',source_game_id='0022300790',event_game_id='0022300783',paragraph=14,kind='history',locator='story.content[14]',review_note='Team announced ongoing back condition, not an injury in the nonappearance game.'))
    # Explicit prior-team medical assertions from the eight reviewed December cards.
    for pid,gid,para,kind in [('1629023','0022300312',11,'acute'),('1629023','0022300326',7,'history'),('202330','0022300354',4,'history'),('202330','0022300428',10,'history'),('202330','0022300436',9,'history')]:
        signals.append(dict(player_id=pid,source_game_id=gid,event_game_id=gid,paragraph=para,kind=kind,locator=f'story.content[{para}]',review_note='Reviewed full prior-team December paragraph; direct medical attribution. Other three candidates were opponent injuries or missed shots.'))
    (D/'recap_adjudications.json').write_text(json.dumps(signals,indent=2)+'\n');write('recap_candidate_adjudication',out);print('Reviewed cards',len(cards),'accepted source/player assertions',len(signals))
if __name__=='__main__':review()
