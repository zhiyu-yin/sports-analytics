"""Run the predeclared Stage 4 build with network sockets blocked."""
from pathlib import Path
import os,sys
from unittest.mock import patch
os.environ.setdefault('MPLCONFIGDIR','/private/tmp/sports-analytics-matplotlib')
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from nba_game_prediction.stage4 import build
if __name__=='__main__':
    with patch('socket.socket',side_effect=AssertionError('Stage 4 network forbidden')):
        build(Path(__file__).resolve().parents[1])
