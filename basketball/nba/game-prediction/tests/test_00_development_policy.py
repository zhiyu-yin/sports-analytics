"""Discovery installs policy before any test fixture is loaded."""
from pathlib import Path
import sys,unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from nba_game_prediction import sealed_access as access
access.install()
class StartupPolicyTests(unittest.TestCase):
    def test_policy_active(self):self.assertTrue(access.INSTALLED)
