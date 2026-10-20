"""Conclusion-blinded factual packet; no final conclusions in first_pass/."""
import hashlib
from collections import defaultdict
import json
import re
from .study import ROOT,D,BATCHES,REVIEW_FIELDS,read,write,dump,stamp


def narrative_locator(source, name):
    """Exact cached JSON leaf locators; no new requests, no copied article body."""
    raw=source.get('raw_file','')
    if not raw or not (ROOT/raw).is_file():return ''
    path=ROOT/raw
    from .study import sha
    if sha(path)!=source.get('sha256'):return ''
    if path.suffix=='.pdf':
        return ('PDF injury-report player row ' if 'Injury-Report' in source.get('url','') else 'PDF FINAL BOX active/inactive player entry ') + name
    text=path.read_text(errors='replace')
    match=re.search(r'<script id="__NEXT_DATA__"[^>]*>(.*?)</script>',text,re.S)
    try:obj=json.loads(match.group(1) if match else text)
    except (ValueError,AttributeError):
        from html.parser import HTMLParser
        found=[]
        class Locator(HTMLParser):
            def __init__(self):super().__init__();self.stack=[]
            def handle_starttag(self,tag,attrs):self.stack.append(tag)
            def handle_endtag(self,tag):
                if tag in self.stack:self.stack=self.stack[:len(self.stack)-1-self.stack[::-1].index(tag)]
            def handle_data(self,data):
                if name.split()[-1].lower() in data.lower() and len(data.split())>5 and not any(t in self.stack for t in ('script','style')):
                    found.append('cached HTML text node line/column '+str(self.getpos())+' tag '+('/'.join(self.stack[-3:])))
        parser=Locator();parser.feed(text)
        return '; '.join(found[:10])
    tokens=[t for t in name.split() if t.lower().strip('.') not in ('jr','ii','iii','iv')]
    surname=tokens[-1] if tokens else name
    paths=[]
    def walk(v,loc):
        if isinstance(v,dict):
            for k,a in v.items():walk(a,loc+'.'+k)
        elif isinstance(v,list):
            for i,a in enumerate(v):walk(a,loc+f'[{i}]')
        elif isinstance(v,str) and surname.lower() in v.lower() and len(v.split())>8:
            if any(t in loc.lower() for t in ('story','content','body')):paths.append(loc)
    walk(obj,'__NEXT_DATA__' if match else '$')
    if not paths:
        def names(v,loc):
            if isinstance(v,dict):
                for k,a in v.items():names(a,loc+'.'+k)
            elif isinstance(v,list):
                for i,a in enumerate(v):names(a,loc+f'[{i}]')
            elif isinstance(v,str) and v.lower()==surname.lower():paths.append(loc)
        names(obj,'__NEXT_DATA__' if match else '$')
    return '; '.join(paths[:20])


def prepare_review(cohort, qualifying, events):
    from phase2d.runtime import manifest
    global_sources=manifest()
    from phase2a.acquire import manifest as first_manifest
    from phase2c.pipeline import manifest as second_manifest
    from phase1c.sources import manifest as boston_manifest
    historical_first=first_manifest()
    for rec in json.loads((ROOT/'phase2b/source_manifest.json').read_text()):historical_first[rec['source_id']]=rec
    source_versions={'Boston_prior':boston_manifest(),'first_six_phase2b':historical_first,'second_six_phase2c':second_manifest(),
                     **{f'phase2d_batch{i}':global_sources for i in (1,2,3)}}
    version_audit=[]
    included={r['row_id']:r for r in cohort if r['B_state']=='included'}
    bycanonical={e['canonical_event_id']:e for e in events}
    mapping={e['event_id']:e['canonical_event_id'] for e in events}
    consequential=defaultdict(set)
    for batch,path in BATCHES.items():
        for link in read(ROOT/path/'tables/row_event_links.csv'):
            r=included.get(link['row_id'])
            if r and r['absence_run_onset_ge10']=='unknown' and link['severity']=='unknown' and link['window_membership']!='False':
                key=mapping.get(link['event_id'])
                if key:consequential[key].add(r['row_id'])
    unknown=[bycanonical[k] for k in sorted(consequential) if bycanonical[k]['severity']=='unknown']
    negatives=[]
    teams=sorted({r['team'] for r in included.values()})
    for team in teams:
        candidates=[r for r in included.values() if r['team']==team and r['extra_lag_days']=='0' and r['absence_run_onset_ge10']=='negative']
        assert candidates,team
        negatives.append(min(candidates,key=lambda r:hashlib.sha256(('phase3a-negative-20240221:'+r['row_id']).encode()).hexdigest()))
    assert len(negatives)==30
    cases=[dict(key=e['canonical_event_id'],e=e,role='currently_qualifying') for e in qualifying]
    cases += [dict(key=e['canonical_event_id'],e=e,role='consequential_unknown') for e in unknown]
    cases += [dict(key=r['row_id'],r=r,role='sampled_negative') for r in negatives]
    cases.sort(key=lambda c:hashlib.sha256(('phase3a-case-order:'+c['key']).encode()).hexdigest())
    games={b:read(ROOT/p/'tables/player_games.csv') for b,p in BATCHES.items()}
    games['Boston_prior']=[dict(g,team='BOS',reason=g['nonappearance_reason'],page_source=g['source_id'],reason_source=g['reason_source_id'],reason_locator=g['evidence_locator'],roster_observed='True',coverage='pilot_page_and_book') for g in read(ROOT/'pilot/tables/player_games.csv')]
    packet=[];key=[];timeline=[];refs=[];source_words=defaultdict(int)
    for i,c in enumerate(cases,1):
        cid=f'R{i:03d}';e=c.get('e');r=c.get('r')
        batch=e['batch'] if e else r['batch']
        sources=source_versions[batch]
        pid=e['player_id'] if e else r['player_id']
        name=e['player_name'] if e else r['player_name']
        # Same factual schema for all case types; selection remains imperfect blindness.
        start=e['anchor_date'] if e else r['decision_at'][:10]
        stop=(e.get('return_date') or '2024-04-14') if e else r['window_end'][:10]
        packet.append(dict(case_id=cid,player_id=pid,player_name=name,reference_date=start,
                           **{f:'' for f in REVIEW_FIELDS},review_status='pending'))
        key.append(dict(case_id=cid,selection_role=c['role'],historical_key=c['key'],batch=batch,
                        original_severity=e['severity'] if e else 'negative',
                        original_continuity=e.get('continuity_supported','') if e else '',
                        original_reason=e.get('reason','') if e else r.get('outcome_reason',''),
                        original_continuity_assertion=e.get('continuity_review_note','') if e else '',
                        original_anchor_lower=e.get('run_lower','') if e else '',
                        original_anchor_upper=e.get('run_upper','') if e else '',
                        original_count=e.get('confirmed_same_episode_games','') if e else '',
                        original_censoring=e.get('censoring','') if e else '',
                        consequential_decisions=len(consequential.get(c['key'],set()))))
        # Use actual roster/appearance rows, retaining noninjury records and return game.
        gs=[g for g in games[batch] if g['player_id']==pid and start<=g['game_date']<=stop]
        prior=[g for g in games[batch] if g['player_id']==pid and g['game_date']<start]
        if prior:gs += [max(prior,key=lambda g:(g['game_date'],g['game_id']))]
        if not gs and e:
            gs=[g for g in read(ROOT/BATCHES[batch]/'tables/event_game_evidence.csv') if g['event_id']==e['event_id']]
        seen=set()
        for g in sorted(gs,key=lambda g:(g['game_date'],g['game_id'],g['team'])):
            ident=(g['game_id'],g['team'])
            if ident in seen:continue
            seen.add(ident)
            timeline.append(dict(case_id=cid,game_date=g['game_date'],team=g['team'],game_id=g['game_id'],
                                 appeared=g.get('appeared',''),minutes=g.get('minutes',''),
                                 recorded_reason=g.get('reason',''),roster_observed=g.get('roster_observed',''),
                                 coverage=g.get('coverage',''),
                                 page_url=sources.get(g.get('page_source',''),{}).get('url',''),
                                 reason_url=sources.get(g.get('reason_source',''),{}).get('url',''),
                                 locator=g.get('reason_locator') or 'FINAL BOX: player active/inactive entry; match player ID/name and game ID'))
            for field in ('page_source','reason_source'):
                sid=g.get(field,'');s=sources.get(sid,{})
                if not s.get('url'):continue
                words=g.get('reason','').split();excerpt=''
                # Global source-level budget, even if shared across many cases.
                budget=max(0,25-source_words[s['url']]);take=min(10,budget,len(words))
                if field=='reason_source' and take:
                    excerpt=' '.join(words[:take]);source_words[s['url']]+=take
                refs.append(dict(case_id=cid,source_id=sid,url=s['url'],sha256=s.get('sha256',''),
                                 locator=g.get('reason_locator') or 'FINAL BOX player entry; game '+g['game_id'],
                                 short_excerpt=excerpt,evidence_kind='recorded box-score fact'))
        if e:
            # Only locators and source links, never prior continuity conclusions.
            for sid in filter(None,e.get('continuity_source_ids','').split(';')):
                sid=sid.strip();s=sources.get(sid,global_sources.get(sid,{}))
                refs.append(dict(case_id=cid,source_id=sid,url=s.get('url',''),sha256=s.get('sha256',''),
                                 locator=narrative_locator(s,name),short_excerpt='',evidence_kind='narrative source for reviewer inspection'))
        else:
            for sid in filter(None,r.get('source_ids','').split(';')):
                s=sources.get(sid,{})
                refs.append(dict(case_id=cid,source_id=sid,url=s.get('url',''),sha256=s.get('sha256',''),locator='Decision source record; player entry',short_excerpt='',evidence_kind='decision source'))
    case_batches={f'R{i:03d}':(c['e']['batch'] if 'e' in c else c['r']['batch']) for i,c in enumerate(cases,1)}
    referenced_by_batch=defaultdict(set)
    for ref in refs:referenced_by_batch[case_batches[ref['case_id']]].add(ref['source_id'])
    for batch in sorted({c['e']['batch'] if 'e' in c else c['r']['batch'] for c in cases}):
        for sid,source in source_versions[batch].items():
            if sid in referenced_by_batch[batch]:
                other=global_sources.get(sid,{})
                version_audit.append(dict(batch=batch,source_id=sid,historical_sha256=source.get('sha256',''),global_sha256=other.get('sha256',''),different=source.get('sha256')!=other.get('sha256'),selection='historical batch manifest for case facts; global only for otherwise unavailable C supplements'))
    version_audit=list({(r['batch'],r['source_id']):r for r in version_audit}.values())
    write(D/'review/source_version_audit.csv',version_audit)
    write(D/'review/first_pass/cases.csv',packet)
    write(D/'review/first_pass/factual_timeline.csv',timeline)
    # Some historical locators embed conclusions; replace all narrative locators with neutral exact paragraph tokens only.
    import re
    for r in refs:
        if r['evidence_kind'].startswith('narrative'):
            r['locator']=r['locator'] or 'Full recap/story body: locate named player; exact cached paragraph locator unavailable'
    write(D/'review/first_pass/sources.csv',refs)
    write(D/'review/answer_key.csv',key)
    assert all(any(t['case_id']==p['case_id'] for t in timeline) for p in packet), 'Case lacks factual timeline'
    missing_urls=sum(not r['url'] for r in refs)
    dump(D/'review/summary.json',dict(qualifying=len(qualifying),consequential_unknown=len(unknown),negative=30,
                                     cases=len(cases),teams_in_negative_sample=teams,seed=20240221,
                                     independent_human_reviews=0,status='pending',missing_source_urls=missing_urls,
                                     narrative_without_exact_paragraph=sum(r['locator'].startswith('Full recap') for r in refs)))
    (D/'review/first_pass/README.md').write_text('''# Conclusion-blinded first-pass review

Distribute only this directory. Do not distribute the separate answer key, analysis report or historical tables before first-pass decisions. Case selection may reveal case type; this packet is conclusion-blinded, not perfectly blinded. Public sources may themselves state diagnoses or missed counts: these are evidence to assess, not hidden adjudication answers. Blank structured fields are for a separate human reviewer. No independent human review has occurred.

Use cases.csv, factual_timeline.csv and sources.csv together. Record attribution, common-episode support, first-miss anchor, consecutive injury-game count, competing reasons, censoring, decision, identity and rationale. Count actual applicable-team games; keep transfer/contract gaps uncertain. A return closes a run, not recovery. Distinct runs in one person need not be independent medical injuries. Retain ambiguous original anchors. Do not add nonmedical misses to ten. Reasons are recorded source facts, not adjudicated injury labels. Narrative sources without an exact paragraph locator are explicitly marked and require direct source inspection; do not infer continuity from this packet alone.

Source excerpts are capped at 25 words per URL across the packet; structured reason fields are factual transcriptions. Raw PDFs/full bodies remain in local ignored caches. An unavailable URL or changed historical page requires the matching checksummed local source; do not invent evidence. After first pass, a coordinator may compare the separately held answer key and log each proposed correction before changing any dataset. No prior labels have been changed by preparing this packet.
''')
    return json_summary(D/'review/summary.json')


def json_summary(path):
    import json
    return json.loads(path.read_text())
