"""Invoke the exact frozen Stage 3F F2 PPC on equivalent coordinates in isolated paths."""
import sys
from stage3fr_common import *
from stage3fr_model import build
import stage3f_ppc as frozen

def run(candidate,attempt):
 authorize();d=read(E/f'{candidate.lower()}_diagnostics.json');assert d['sampler_pass'];assert read(E/f'{candidate.lower()}_equivalence_validation.json')['passed']
 # Existing code is reused verbatim; all output and input paths are redirected to this stage.
 local=M/f'f2_attempt{attempt}_trace.nc';source=M/f'{candidate.lower()}_attempt{attempt}_trace.nc'
 if not local.exists():local.symlink_to(source.name)
 assert local.resolve()==source.resolve()
 save(f'f2_attempt{attempt}_diagnostics.json',read(E/f'{candidate.lower()}_attempt{attempt}_diagnostics.json'));save(f'f2_attempt{attempt}_visual_review.json',d['visual_review'])
 frozen.E=E;frozen.M=M;frozen.save=save;frozen.authorize=authorize;frozen.protocol=protocol;frozen.build=lambda _:build(candidate)
 frozen.run('F2',attempt)
 save('ppc_implementation_receipt.json',dict(frozen_stage3f_code_sha256=sha(ROOT/'scripts/stage3f_ppc.py'),selected=candidate,attempt=attempt,replicates=2000,seed=20260929,only_changes='Stage-local paths and mathematically equivalent model builder',scientific_parameter_summary_exported=False))
if __name__=='__main__':run(sys.argv[1],int(sys.argv[2]))
