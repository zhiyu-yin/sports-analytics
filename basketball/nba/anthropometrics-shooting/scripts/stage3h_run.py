"""One initial fit and at most one unchanged-model recovery."""
import sys,subprocess
from stage3h_common import *
def run(candidate):
 authorize(candidate)
 for attempt in [1,2]:
  for action in ['fit','diagnostics']:
   target=E/f'{candidate.lower()}_attempt{attempt}_{"sampling" if action=="fit" else "diagnostics"}.json'
   if target.exists():
    record=read(target)
    if action=='diagnostics':continue
    assert record['status']=='COMPLETE','Inspect running/incomplete launch; do not duplicate'
    assert sha(M/f'{candidate.lower()}_attempt{attempt}_trace.nc')==record['trace_sha256'];continue
   with (E/f'{candidate.lower()}_attempt{attempt}_{action}_run.txt').open('w') as log:r=subprocess.run([sys.executable,str(ROOT/'scripts/stage3h_sampling.py'),action,candidate,'--attempt',str(attempt)],stdout=log,stderr=subprocess.STDOUT)
   assert r.returncode==0,'Inspect infrastructure log; no scientific change allowed'
   print(candidate,attempt,action,'complete',flush=True)
  if read(E/f'{candidate.lower()}_attempt{attempt}_diagnostics.json')['numeric_gate_pass']:break
if __name__=='__main__':run(sys.argv[1])
