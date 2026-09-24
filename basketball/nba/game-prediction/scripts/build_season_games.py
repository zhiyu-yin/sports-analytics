"""Build one audited season through the shared ingestion and feature pipeline."""
import argparse
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from nba_game_prediction.seasons import get_scope
from nba_game_prediction.multiseason import build_season_games,verify_protected

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--season',required=True);p.add_argument('--fetch',action='store_true')
    args=p.parse_args()
    from nba_game_prediction.sealed_access import require_seasons
    require_seasons([args.season], 'single-season build')
    get_scope(args.season);verify_protected(ROOT)
    _,quality,scope,_,_=build_season_games(ROOT,args.season,fetch=args.fetch)
    verify_protected(ROOT);print(quality)
    if scope['completeness_issues']:raise SystemExit('Season quarantined: '+str(scope['completeness_issues']))
if __name__=='__main__':main()
