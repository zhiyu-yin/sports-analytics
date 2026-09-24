"""Activate policy before ordinary local unittest discovery."""
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent/'src'))
from nba_game_prediction.sealed_access import install
install()
