"""Stage 3H immutable inputs, with no posterior scientific-effect exports."""
from stage3f_common import ROOT,PANEL,EXPECTED,BINS,now,sha,read,original,decomposition,summary,ztnb_random,fixed_data
import json,numpy as np
E=ROOT/'docs/stage3h_evidence';M=ROOT/'models/stage3h';F=ROOT/'docs/stage3h_figures'
def save(name,value):(E/name).write_text(json.dumps(value,indent=2,allow_nan=False)+'\n')
def protocol():
 p=read(E/'model_protocol.json');assert sha(E/'model_protocol.json')==read(E/'freeze_receipt.json')['model_protocol_sha256'];return p
def authorize(candidate=None):
 p=protocol();assert sha(PANEL)==EXPECTED
 for path,h in p['frozen_code'].items():assert sha(ROOT/path)==h,path
 assert sha(E/'prior_protocol.json')==p['prior_protocol_sha256']
 assert sha(ROOT/'docs/stage3f_evidence/opportunity_decomposition.csv')==p['decomposition_csv_sha256']
 if candidate:
  assert read(E/(candidate.lower()+'_prior_predictive.json'))['passed'],'Prior prerequisite failed'
  if candidate=='H2':
   assert read(E/'h1_diagnostics.json')['sampler_pass']
   assert not (read(E/'h1_conditional_accuracy_ppc.json')['gate_pass'] and read(E/'h1_joint_opportunity_ppc.json')['gate_pass'])
def gate(r,b,t):return bool(np.isfinite([r,b,t]).all() and r<=1.01 and b>=400 and t>=400)
def observed_within(d):
 import pandas as pd
 f=pd.read_csv(ROOT/'docs/stage3f_evidence/opportunity_decomposition.csv',dtype={'player_id':str,'season':str},float_precision='round_trip')
 assert np.array_equal(f.player_id.astype(str),d.player_id.astype(str)) and np.array_equal(f.season,d.season)
 assert np.array_equal(f.FTA,d.fta) and np.array_equal(f.GP,d.games_played)
 return f.within.to_numpy()
