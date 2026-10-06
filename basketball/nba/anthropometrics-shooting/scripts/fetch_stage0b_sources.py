"""Bounded retrieval of explicit official sources; adds only Stage 0B raw files."""
import sys,json,concurrent.futures
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from anthropometrics_shooting.stage0b_io import *
SOURCES=[
('warriors_2016_17_guide','https://ak-static-int.nba.com/wp-content/uploads/sites/3/2016/10/2016-17-Media-Guide-Warriors.pdf'),
('combine_2013_original','https://mediacentral.nba.com/media/mediacentral/051713-2013-NBA-Draft-Combine-Anthropometric-Results.pdf'),
('combine_2013_stats','https://stats.nba.com/stats/draftcombineplayeranthro?LeagueID=00&SeasonYear=2013'),
('durant_career_stats','https://stats.nba.com/stats/playercareerstats?LeagueID=00&PerMode=Totals&PlayerID=201142'),
('durant_mvp','https://pr.nba.com/kevin-durant-2013-14-kia-nba-mvp/'),
('largest_wingspans','https://www.nba.com/news/nba-draft-combine-largest-wingspans')]
def main():
    def f(pair):
        label,url=pair; b,m=fetch(url,label,40); print(label,m['http_status'],len(b),flush=True); return m
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool: out=list(pool.map(f,SOURCES))
    dump(E/'official_retrievals.json',out)
if __name__=='__main__':main()
