import sys,json,subprocess,secrets,hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'stage6'))
import runtime as old
from nba_game_prediction.stage5a import protocol_bytes
E=ROOT/'docs/stage6r_evidence';WORKER=ROOT/'stage6r/transport_worker.py'
AUTH='8337cbd0b269ad28750d1c04fbdfb9f5304a613c514fd0e840613cbc0f5e2a2c'
def hashes():return {str(p.relative_to(ROOT)):old.access.checksum(p) for p in sorted((ROOT/'stage6r').glob('*.py'))}
def verify_protected():
 expected=old.read_json(E/'protected_artifacts_before.json')
 actual={p:(old.sha(protocol_bytes()) if p=='docs/final_holdout_protocol_2025_26.md' else old.access.checksum(ROOT/p)) for p in expected}
 if actual!=expected:raise RuntimeError('Protected artifact changed')
 return actual

def launch(mode,*,request=None):
 if request is None:
  if old.access.checksum(E/'authorization.txt')!=AUTH:raise RuntimeError('Exact recovery authorization required')
  ident=secrets.token_hex(16);nonce=secrets.token_hex(32)
  cap=dict(nonce=nonce,mode=mode,authorization_sha256=AUTH,worker_sha256=old.access.checksum(WORKER),created_at_utc=old.now())
  if mode=='part_b':
   cap.update(gate_sha256=old.access.checksum(E/'part_a_exit_gate.json'),ledger_sha256=old.access.checksum(E/'recovery_opening_ledger.json'))
  old.durable(E/'capabilities'/(ident+'.json'),cap,True);request=dict(id=ident,nonce=nonce)
 proc=subprocess.run([str(ROOT/'.venv/bin/python'),'-I','-S',str(WORKER)],input=json.dumps(request),text=True,capture_output=True,timeout=55)
 try:result=json.loads(proc.stdout)
 except Exception:result=dict(passed=False,stdout=proc.stdout,stderr=proc.stderr)
 result['returncode']=proc.returncode
 return result,request
