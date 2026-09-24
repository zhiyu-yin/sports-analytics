from pathlib import Path
import sys,unittest,math
import numpy as np
import pandas as pd
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from nba_game_prediction.metrics import evaluate,calibration,EPSILON

def frame(y,p):return pd.DataFrame({'season':['2023-24']*len(y),'home_win':y,'p':p})
class MetricTests(unittest.TestCase):
    def test_log_loss_hand(self):self.assertAlmostEqual(evaluate(frame([0,1],[.25,.75]),'p')['log_loss'],-math.log(.75))
    def test_brier_hand(self):self.assertEqual(evaluate(frame([0,1],[.25,.75]),'p')['brier_score'],.0625)
    def test_accuracy_threshold(self):self.assertEqual(evaluate(frame([0,1,0,1],[.5,.5,.49,.49]),'p')['accuracy'],.5)
    def test_auc_hand(self):self.assertEqual(evaluate(frame([0,0,1,1],[.1,.4,.35,.8]),'p')['roc_auc'],.75)
    def test_auc_ties_constant(self):self.assertEqual(evaluate(frame([0,1,0,1],[.6]*4),'p')['roc_auc'],.5)
    def test_auc_ties_pairwise(self):
        y=np.array([0,1,1,0,1,0]);p=np.array([.1,.3,.3,.3,.9,.9]);pairs=[float(a>b)+.5*float(a==b) for a in p[y==1] for b in p[y==0]]
        self.assertAlmostEqual(evaluate(frame(y,p),'p')['roc_auc'],np.mean(pairs))
    def test_single_class_auc_explicit(self):
        m=evaluate(frame([1,1],[.1,.9]),'p');self.assertIsNone(m['roc_auc']);self.assertFalse(m['roc_auc_defined'])
    def test_exact_and_near_probability_extremes(self):
        m=evaluate(frame([1,0,1,0],[0,1,1e-300,1-1e-12]),'p');self.assertTrue(math.isfinite(m['log_loss']))
        self.assertEqual(evaluate(frame([0,1],[0,1]),'p')['brier_score'],0)
        self.assertAlmostEqual(evaluate(frame([1],[0]),'p')['log_loss'],-math.log(EPSILON))
    def test_bin_boundaries_and_empty_bins(self):
        t=calibration(frame([0]*11,[i/10 for i in range(11)]),'p')
        self.assertEqual(t['count'].tolist(),[1]*9+[2]);self.assertEqual(t.iloc[3].mean_predicted_probability,.3)
        t=calibration(frame([1],[.5]),'p');self.assertEqual(t.iloc[5]['count'],1);self.assertEqual(int(t['count'].sum()),1)
        self.assertTrue(t[t['count'].eq(0)].mean_predicted_probability.isna().all())
    def test_equal_frequency_constant(self):
        t=calibration(frame([0,1],[.6,.6]),'p',True);self.assertEqual(len(t),1);self.assertEqual(t.iloc[0]['count'],2)
    def test_equal_frequency_conservation(self):
        t=calibration(frame([0,1]*10,np.arange(20)/20),'p',True);self.assertEqual(int(t['count'].sum()),20)
    def test_no_silent_nan(self):
        for f in [frame([0,np.nan],[.2,.8]),frame([0,1],[.2,np.nan]),frame([0,1],[.2,np.inf])]:
            for fn in [evaluate,calibration]:
                with self.assertRaises(ValueError):fn(f,'p')
    def test_invalid_probability_or_outcome(self):
        for f in [frame([0],[1.01]),frame([0],[-.1]),frame([2],[.5])]:
            with self.assertRaises(ValueError):evaluate(f,'p')
    def test_empty_evaluation_rejected(self):
        with self.assertRaises(ValueError):evaluate(frame([],[]),'p')
    def test_mixed_sealed_season_rejected(self):
        f=frame([0,1],[.2,.8]);f.loc[1,'season']='2024-25'
        with self.assertRaisesRegex(ValueError,'sealed'):evaluate(f,'p')
if __name__=='__main__':unittest.main()
