"""Seal final reporting artifacts without altering frozen scientific results."""
from stage3j_core import *
p=authorize(True)
assert read(E/'artifact_verification.json')['passed']
assert read(E/'supplementary_checks.json')['passed']
assert read(E/'execution_decision.json')['execution']=='FAIL'
assert read(E/'test_summary.json')['passed']==24
report=ROOT/'docs/stage3j_simplified_multiseason_inference.md';assert '**FAIL**' in report.read_text()
files=list(E.glob('*'))+list(F.glob('*'))+list((ROOT/'scripts').glob('stage3j_*.py'))+[ROOT/'tests/test_stage3j.py',report]
manifest={str(f.relative_to(ROOT)):dict(sha256=sha(f),bytes=f.stat().st_size) for f in files if f.is_file() and f.name!='build_manifest.json'}
save('build_manifest.json',dict(built_at=now(),protocol_sha256=sha(E/'analysis_protocol.json'),primary_result_sha256=sha(E/'primary_result.json'),historical_artifacts=len(read(E/'prior_preservation_manifest.json')),execution='FAIL',primary_J1='PASS',reason='J2 bootstrap numerical failure cap exceeded; interval withheld without tuning',files=manifest,no_commit=True,no_push=True,no_stage4=True))
print('Final build manifest:',len(manifest),'artifacts',flush=True)
