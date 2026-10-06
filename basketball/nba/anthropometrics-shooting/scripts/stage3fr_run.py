"""Run each authorized fit at most twice; stop before any later equivalent candidate."""
import subprocess,sys
from stage3fr_common import *
def run(candidate):
 if candidate in ['R2','R3']:
  previous='r1' if candidate=='R2' else 'r2'
  prior=read(E/(previous+'_diagnostics.json'))
  assert prior.get('sampler_pass') is False and prior.get('recovery_exhausted'), 'Earlier eligible candidate must exhaust its recovery first'
 for attempt in [1,2]:
  for action in ['fit','diagnostics']:
   record=E/f'{candidate.lower()}_attempt{attempt}_{"sampling" if action=="fit" else "diagnostics"}.json'
   if record.exists():
    existing=read(record)
    if action=='diagnostics':continue
    if existing.get('status')=='COMPLETE':
     assert sha(M/f'{candidate.lower()}_attempt{attempt}_trace.nc')==existing['trace_sha256']
     continue
    raise RuntimeError('Incomplete prior launch: inspect process and preserve interruption evidence before restarting')
   with (E/f'{candidate.lower()}_attempt{attempt}_{action}_run.txt').open('w') as log:r=subprocess.run([sys.executable,str(ROOT/'scripts/stage3fr_sampling.py'),action,candidate,'--attempt',str(attempt)],stdout=log,stderr=subprocess.STDOUT)
   if r.returncode:raise RuntimeError(candidate+' '+action+' failed; inspect log without changing target model')
   print(candidate,attempt,action,'complete',flush=True)
  d=read(E/f'{candidate.lower()}_attempt{attempt}_diagnostics.json')
  if d['numeric_gate_pass']:break
 return d
if __name__=='__main__':
 for c in (['DIAG-A','DIAG-B','DIAG-C'] if sys.argv[1]=='diagnostics' else [sys.argv[1]]):run(c)
