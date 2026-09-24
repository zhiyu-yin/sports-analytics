"""Verify infrastructure only; no model fit, replay, prediction or evaluation."""
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from nba_game_prediction.stage4a import build
if __name__=='__main__':build(ROOT)
