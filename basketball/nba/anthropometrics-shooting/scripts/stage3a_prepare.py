"""Freeze provenance-only sample before any official game reconstruction."""
import hashlib,json
from pathlib import Path
from datetime import datetime,timezone
import pandas as pd
ROOT=Path(__file__).resolve().parents[1]
E=ROOT/'docs/stage3a_evidence'
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def save(name,obj): (E/name).write_text(json.dumps(obj,indent=2)+'\n')
def main():
 E.mkdir(exist_ok=True)
 assert not (E/'minute_audit_sample_predeclared.csv').exists(),'Frozen sample already exists'
 protected={str(p.relative_to(ROOT)):sha(p) for p in ROOT.rglob('*') if p.is_file() and not any(x.startswith('.venv') or x=='__pycache__' for x in p.parts) and 'stage3a' not in str(p.relative_to(ROOT))}
 save('prior_artifact_hashes.json',protected)
 cols=['season','player_id','player_name','field','archive','official','match']
 c=pd.read_csv(ROOT/'docs/stage3_evidence/shooting_census_crosscheck.csv',usecols=cols,dtype={'player_id':str}); c=c[c.field=='minutes'].drop(columns='field').copy()
 c['minute_band']=c.groupby('season').archive.transform(lambda v:pd.qcut(v.rank(method='first'),3,labels=['low','medium','high']))
 c['selection_hash']=[hashlib.sha256(f'stage3a-minute-only-v1|{s}|{p}'.encode()).hexdigest() for s,p in zip(c.season,c.player_id)]
 c['case_type']=c.match.map({True:'within_original_tolerance',False:'census_mismatch'})
 selected=c.sort_values('selection_hash').groupby(['season','minute_band','case_type'],observed=True).head(2).copy(); selected['selection_reason']='two lowest SHA256 per season / minute tertile / original gate status'
 originals={('2010-11','201942'),('2010-11','202083'),('2010-11','2772'),('2016-17','203552')}
 for s,p in originals:
  r=c[(c.season==s)&(c.player_id==p)].copy();r['selection_reason']='original predeclared failed case';selected=pd.concat([selected[~((selected.season==s)&(selected.player_id==p))],r])
 selected=selected.sort_values(['season','player_id']);selected.to_csv(E/'minute_audit_sample_predeclared.csv',index=False)
 save('sample_freeze.json',dict(frozen_at=datetime.now(timezone.utc).isoformat(),sha256=sha(E/'minute_audit_sample_predeclared.csv'),rows=len(selected),selection_columns=cols,prohibited_selection_variables_used=False,algorithm='SHA256 stage3a-minute-only-v1|season|player_id; two smallest per season, within-season minute tertile, original MIN gate status; add four originals',new_numeric_tolerance=None,part_B_authorized=False))
 print(selected[['season','player_id','player_name','minute_band','case_type']].to_string(index=False))
if __name__=='__main__': main()
