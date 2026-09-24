"""Build the audited historical range. Offline by default; excludes final holdout."""
import argparse
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from nba_game_prediction.seasons import season_range
from nba_game_prediction.multiseason import build_multi

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--start-season',default='2015-16')
    parser.add_argument('--end-season',default='2024-25')
    parser.add_argument('--fetch',action='store_true')
    parser.add_argument('--allow-partial',action='store_true')
    args=parser.parse_args()
    build_multi(ROOT,season_range(args.start_season,args.end_season),fetch=args.fetch,allow_partial=args.allow_partial)
if __name__=='__main__':main()
