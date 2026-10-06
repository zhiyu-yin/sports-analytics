"""Isolated Stage 3F-R paths and immutable-input guards."""
from pathlib import Path
from stage3f_common import ROOT,PANEL,EXPECTED,BINS,now,sha,read,original,decomposition,summary,ztnb_random
import json,numpy as np
E=ROOT/'docs/stage3fr_evidence';M=ROOT/'models/stage3fr';F=ROOT/'docs/stage3fr_figures'
def save(name,v):(E/name).write_text(json.dumps(v,indent=2,allow_nan=False)+'\n')
def protocol():
 p=read(E/'reparameterization_protocol.json');assert sha(E/'reparameterization_protocol.json')==read(E/'freeze_receipt.json')['protocol_sha256'];return p
def authorize():
 p=protocol();assert sha(PANEL)==EXPECTED
 for n,h in p['frozen_code'].items():assert sha(ROOT/n)==h,n
 assert sha(ROOT/'docs/stage3f_evidence/opportunity_decomposition.csv')==p['decomposition_csv_sha256']
def gate(r,b,t):return bool(np.isfinite([r,b,t]).all() and r<=1.01 and b>=400 and t>=400)
