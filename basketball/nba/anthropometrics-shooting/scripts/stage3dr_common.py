"""New continuation paths; immutable historical protocol and panel."""
from stage3d_protocol import ROOT,EXPECTED,PANEL,BINS,now,sha,read,fixed_data
import json,numpy as np
E=ROOT/'docs/stage3dr_evidence';M=ROOT/'models/stage3dr';F=ROOT/'docs/stage3dr_figures'
def save(name,value): (E/name).write_text(json.dumps(value,indent=2,allow_nan=False)+'\n')
def protocol():
 original=ROOT/'docs/stage3d_evidence/model_adequacy_protocol.json'
 assert sha(original)==read(ROOT/'docs/stage3d_evidence/protocol_freeze_receipt.json')['sha256']
 return read(original)
def amendment():
 path=E/'opportunity_prior_amendment.json';assert sha(path)==read(E/'amendment_freeze_receipt.json')['sha256'];return read(path)
def summary(x):
 x=np.asarray(x).ravel();return dict(mean=float(x.mean()),median=float(np.median(x)),SD=float(x.std(ddof=1)),CI95=np.quantile(x,[.025,.975]).tolist())
