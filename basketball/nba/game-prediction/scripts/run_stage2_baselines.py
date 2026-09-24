"""Stage 2 local-only runner. Socket access is blocked for the entire build."""
from pathlib import Path
import os,sys
from unittest.mock import patch
os.environ.setdefault('MPLCONFIGDIR','/private/tmp/sports-analytics-matplotlib')
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from nba_game_prediction.evaluation import build
if __name__=='__main__':
    with patch('socket.socket',side_effect=AssertionError('Stage 2 network access forbidden')):
        build(Path(__file__).resolve().parents[1])
