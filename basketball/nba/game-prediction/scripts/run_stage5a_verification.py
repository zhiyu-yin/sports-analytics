"""Protocol verification only; no final-holdout execution mode exists."""
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'))
from nba_game_prediction.stage5a import verify
if __name__=='__main__':verify()
