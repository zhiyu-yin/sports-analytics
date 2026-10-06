"""Final file inventory; all numerical/scientific freezes stay untouched."""
from stage3jr_solver import *
p=protocol();assert read(E/'test_summary.json')['passed'];assert read(E/'artifact_verification.json')['passed']
files=[f for f in E.rglob('*') if f.is_file() and f.name!='build_manifest.json']+[f for f in M.rglob('*') if f.is_file()]+list((ROOT/'scripts').glob('stage3jr_*.py'))+[ROOT/'tests/test_stage3jr.py',ROOT/'docs/stage3jr_beta_binomial_numerical_remediation.md']
manifest={str(f.relative_to(ROOT)):dict(sha256=sha(f),bytes=f.stat().st_size) for f in files}
save('build_manifest.json',dict(built_at=now(),classification=read(E/'stage3jr_decision.json')['classification'],historical_Stage3J='EXECUTION FAIL unchanged',primary_result_sha256=sha(J/'primary_result.json'),numerical_protocol_sha256=sha(E/'numerical_protocol.json'),decision_sha256=sha(E/'stage3jr_decision.json'),historical_artifacts=len(read(E/'prior_preservation_manifest.json')),files=manifest,no_commit=True,no_push=True,no_stage4=True),immutable=False)
print('Build manifest:',len(manifest),'artifacts',flush=True)
