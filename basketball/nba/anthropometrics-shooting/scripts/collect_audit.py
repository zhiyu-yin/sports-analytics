"""Bounded public-source probes. Run from any directory; standard library + curl."""
import sys, re, json, concurrent.futures
from pathlib import Path
from urllib.parse import urlsplit, parse_qsl, urlencode
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from anthropometrics_shooting.provenance import retrieve,tables,EVIDENCE
ENDPOINTS=['draftcombineplayeranthro','draftcombinestats','leaguedashplayerstats','leaguedashptstats','playerdashptshots','leaguedashplayershotlocations','shotchartdetail','commonallplayers']

def getdoc(ep):
    b,m=retrieve('https://raw.githubusercontent.com/swar/nba_api/master/docs/nba_api/stats/endpoints/'+ep+'.md','nba_api endpoint documentation')
    text=b.decode(errors='replace')
    urls=re.findall(r'https://stats\.nba\.com/stats/[^\s)\]>]+',text)
    valid=next((u for u in urls if '?' in u),None)
    return ep,dict(provenance=m,valid_url=valid,documented_schemas=re.findall(r"\['[^\n]+",text))

def probe(job):
    ep,p=job
    url='https://stats.nba.com/stats/'+ep+'?'+urlencode(p)
    b,m=retrieve(url,ep,p,18)
    try:
        t=tables(b); m.update(status='ok' if m['transport_exit']==0 else 'transport_error',tables={k:{'schema':v['schema'],'row_count':v['row_count']} for k,v in t.items()})
    except Exception as e: m.update(status='unavailable',parse_error=str(e),tables=None)
    print(ep,p.get('Season',p.get('SeasonYear')),p.get('PtMeasureType',''),m['status'],flush=True)
    return m

def main():
    EVIDENCE.mkdir(parents=True,exist_ok=True)
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool: docs=dict(pool.map(getdoc,ENDPOINTS))
    (EVIDENCE/'endpoint_documentation.json').write_text(json.dumps(docs,indent=2))
    jobs=[]
    for ep,d in docs.items():
        if not d['valid_url']: continue
        base=dict(parse_qsl(urlsplit(d['valid_url']).query,keep_blank_values=True))
        if ep.startswith('draftcombine'):
            years=[1999,2000,2003,2009,2013,2019,2022,2025,2026] if ep=='draftcombineplayeranthro' else [2000,2022]
            for y in years: jobs.append((ep,dict(base,SeasonYear=str(y),LeagueID='00')))
        elif ep=='commonallplayers': jobs.append((ep,dict(base,Season='2025-26',IsOnlyCurrentSeason='0',LeagueID='00')))
        else:
            for y in ([2000,2012,2013,2022,2025] if ep in ['leaguedashplayerstats','leaguedashptstats'] else [2012,2013,2025]):
                p=dict(base,Season=f'{y}-{(y+1)%100:02d}',LeagueID='00',SeasonType='Regular Season')
                if 'PerMode' in p: p['PerMode']='Totals'
                if ep=='leaguedashptstats':
                    for kind in ['CatchShoot','PullUpShot']: jobs.append((ep,dict(p,PlayerOrTeam='Player',PtMeasureType=kind)))
                else:
                    if ep in ['playerdashptshots','shotchartdetail']: p.update(PlayerID='201939',TeamID='0')
                    if ep=='shotchartdetail': p.update(ContextMeasure='FGA')
                    jobs.append((ep,p))
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool: results=list(pool.map(probe,jobs))
    (EVIDENCE/'endpoint_probes.json').write_text(json.dumps(results,indent=2))
    # Secondary, explicitly labeled archive; never confused with live NBA validation.
    b,m=retrieve('https://api.github.com/repos/ianstack/NBA-Draft-Combine-Analysis/commits/main','GitHub archive revision')
    try: ref=json.loads(b)['sha']
    except Exception: ref='main'
    archives=[]
    for name in ['nba_draft_data.csv']:
        _,m=retrieve(f'https://raw.githubusercontent.com/ianstack/NBA-Draft-Combine-Analysis/{ref}/data/{name}','Secondary NBA-derived archive: ianstack',{'revision':ref,'file':name}); archives.append(m)
    (EVIDENCE/'archive_sources.json').write_text(json.dumps(archives,indent=2))
    b,m=retrieve('https://api.github.com/repos/NocturneBear/NBA-Data-2010-2024/commits/main','GitHub archive revision')
    ref=json.loads(b)['sha']
    archives=[]
    for n in [1,2,3]:
        name=f'regular_season_box_scores_2010_2024_part_{n}.csv'
        _,m=retrieve(f'https://raw.githubusercontent.com/NocturneBear/NBA-Data-2010-2024/{ref}/{name}','Secondary NBA-shaped box-score archive: NocturneBear',{'revision':ref,'file':name},60)
        archives.append(m)
    (EVIDENCE/'shooting_archive_sources.json').write_text(json.dumps(archives,indent=2))
if __name__=='__main__': main()
