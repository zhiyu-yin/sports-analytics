"""Explicit Stage 5 frozen preparation/opening/replay; final holdout always blocked."""
from pathlib import Path
import argparse,os,sys
os.environ.setdefault('MPLCONFIGDIR','/private/tmp/sports-analytics-matplotlib')
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'))
from nba_game_prediction.stage5 import prepare,evaluate_opening
if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('mode',choices=['prepare','open','replay']);args=p.parse_args()
    prepare(ROOT) if args.mode=='prepare' else evaluate_opening(ROOT,args.mode)
