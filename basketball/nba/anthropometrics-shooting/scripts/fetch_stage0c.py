import sys,json,concurrent.futures
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from anthropometrics_shooting.stage0c import *
def main():
    jobs=[('https://www.nba.com/stats/draft/combine-anthro?SeasonYear=2013-14','NBA stats historical table','official_table',[2013]),('https://stats.nba.com/stats/draftcombineplayeranthro?LeagueID=00&SeasonYear=2004','NBA API 2004','official_api',[2004]),('https://stats.nba.com/stats/draftcombineplayeranthro?LeagueID=00&SeasonYear=2007','NBA API 2007','official_api',[2007]),('https://stats.nba.com/stats/draftcombineplayeranthro?LeagueID=00&SeasonYear=2013','NBA API 2013','official_api',[2013]),('https://www.nba.com/bulls/news/predraft_vitals_04.html','Bulls 2004 pre-draft table','official_table',[2004])]
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as pool:ms=list(pool.map(lambda args:fetch(*args),jobs))
    dump(E/'initial_retrievals.json',ms);print([(m['source_name'],m['http_status'],m['bytes']) for m in ms])
if __name__=='__main__':main()
