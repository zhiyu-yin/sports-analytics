"""Stage 3I immutable inputs, with no posterior scientific-effect exports."""
from stage3f_common import ROOT,PANEL,EXPECTED,BINS,now,sha,read,original,decomposition,summary,ztnb_random,fixed_data
import json,numpy as np
E=ROOT/'docs/stage3i_evidence';M=ROOT/'models/stage3i';F=ROOT/'docs/stage3i_figures'
def save(name,value):(E/name).write_text(json.dumps(value,indent=2,allow_nan=False)+'\n')
def protocol():
 p=read(E/'model_protocol.json');assert sha(E/'model_protocol.json')==read(E/'freeze_receipt.json')['model_protocol_sha256'];return p
def authorize(candidate=None):
 p=protocol();assert sha(PANEL)==EXPECTED
 for path,h in p['frozen_code'].items():assert sha(ROOT/path)==h,path
 assert sha(E/'prior_protocol.json')==p['prior_protocol_sha256']
 assert sha(E/'within_quadratic_basis.json')==p['basis_sha256']
 assert sha(ROOT/'docs/stage3f_evidence/opportunity_decomposition.csv')==p['decomposition_csv_sha256']
 if candidate:
  assert read(E/(candidate.lower()+'_prior_predictive.json'))['passed'],'Prior prerequisite failed'
  assert candidate in ['I1','I2','I3']
  assert read(E/'prior_predictive_summary.json')['I3']['passed']
  for prev in ['I1','I2','I3'][:['I1','I2','I3'].index(candidate)]:
   assert (E/(prev.lower()+'_diagnostics.json')).exists()

def gate(r,b,t):return bool(np.isfinite([r,b,t]).all() and r<=1.01 and b>=400 and t>=400)
def observed_within(d):
 import pandas as pd
 f=pd.read_csv(ROOT/'docs/stage3f_evidence/opportunity_decomposition.csv',dtype={'player_id':str,'season':str},float_precision='round_trip')
 assert np.array_equal(f.player_id.astype(str),d.player_id.astype(str)) and np.array_equal(f.season,d.season)
 assert np.array_equal(f.FTA,d.fta) and np.array_equal(f.GP,d.games_played)
 return f.within.to_numpy()

def quadratic_basis(w):
 b=read(E/'within_quadratic_basis.json');z=np.asarray(w)/b['s_W'];return z,z*z-b['quadratic_center']
