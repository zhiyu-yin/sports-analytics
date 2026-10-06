"""Fixed sequential candidate schedule; one diagnostic recovery per candidate."""
import subprocess,sys
from stage3f_common import *
def main():
 authorize()
 for candidate in ['F1','F2']:
  for attempt in [1,2]:
   for action in ['fit','diagnostics']:
    with (E/f'{candidate.lower()}_attempt{attempt}_{action}_run.txt').open('w') as log:
     result=subprocess.run([sys.executable,str(ROOT/'scripts/stage3f_sampling.py'),action,candidate,'--attempt',str(attempt)],stdout=log,stderr=subprocess.STDOUT)
    if result.returncode:raise RuntimeError(f'{candidate} {action} failed; no simplification permitted')
    print(candidate,attempt,action,'complete',flush=True)
   diag=read(E/f'{candidate.lower()}_attempt{attempt}_diagnostics.json')
   if diag['numeric_gate_pass']:break
   if not diag['finite_covariance']:raise RuntimeError('Nonfinite 3D covariance; stop without structural simplification')
if __name__=='__main__':main()
