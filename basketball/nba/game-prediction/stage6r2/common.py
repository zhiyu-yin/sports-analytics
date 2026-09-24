import sys,json,subprocess,secrets
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'stage6'))
import runtime as r
from nba_game_prediction.stage5a import protocol_bytes
E=ROOT/'docs/stage6r2_evidence';WORKER=ROOT/'stage6r2/schedule_worker.py'
AUTH='37c3d5e554cb9fe0d246d8651497e5105dfe04320a4d3046f6de33266945a00e'
RAW=ROOT/'data/raw/stage6r/leaguegamelog_response.json'
def protected():
 expected=r.read_json(E/'protected_artifacts_before.json')
 actual={p:(r.sha(protocol_bytes()) if p=='docs/final_holdout_protocol_2025_26.md' else r.access.checksum(ROOT/p)) for p in expected}
 if actual!=expected:raise RuntimeError('Protected artifact changed')
 return actual

def checkpoint():return {str(p.relative_to(ROOT)):r.access.checksum(p) for p in sorted((ROOT/'stage6r2').glob('*.py'))}
def launch(mode,request=None):
 if request is None:
  if r.access.checksum(E/'authorization.txt')!=AUTH:raise RuntimeError('Authorization mismatch')
  ident=secrets.token_hex(16);nonce=secrets.token_hex(32);cap=dict(nonce=nonce,mode=mode,authorization_sha256=AUTH,worker_sha256=r.access.checksum(WORKER),created_at_utc=r.now())
  if mode=='schedule':cap.update(gate_sha256=r.access.checksum(E/'part_a_exit_gate.json'),ledger_sha256=r.access.checksum(E/'schedule_lookup_ledger.json'))
  r.durable(E/'capabilities'/(ident+'.json'),cap,True);request=dict(id=ident,nonce=nonce)
 proc=subprocess.run([str(ROOT/'.venv/bin/python'),'-I','-S',str(WORKER)],input=json.dumps(request),text=True,capture_output=True,timeout=55)
 try:result=json.loads(proc.stdout)
 except Exception:result=dict(passed=False,stdout=proc.stdout,stderr=proc.stderr)
 result['returncode']=proc.returncode
 return result,request

def cached_body():
 if r.access.checksum(RAW)!=r.read_json(ROOT/'docs/stage6r_evidence/acquisition.json')['sha256']:raise ValueError('Original raw response changed')
 with r.access._RAW_OPEN(RAW,'rb') as f:return f.read()
