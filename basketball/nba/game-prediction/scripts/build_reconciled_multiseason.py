"""Build Stage 1D from cached sources and reviewed local evidence; no network mode."""
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from nba_game_prediction.stage1d import build
if __name__=='__main__':
    m=build(Path(__file__).resolve().parents[1]);print('Combined games:',m['combined_games'])
