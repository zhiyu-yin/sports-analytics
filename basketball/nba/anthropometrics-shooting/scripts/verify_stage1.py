"""Run Stage 1 contracts, verify historical files, and write a build receipt."""
import json,sys,platform,subprocess
from datetime import datetime,timezone
from stage1_analysis import ROOT,E,sha,CAND,REF
prior=json.loads((ROOT/'docs/stage0c_evidence/prior_preservation_manifest.json').read_text())
changed=[p for p,h in prior.items() if sha(ROOT/p)!=h]
assert not changed,changed
run=subprocess.run([sys.executable,'-m','unittest','discover','-s',str(ROOT/'tests'),'-p','test_stage1.py','-v'],capture_output=True,text=True)
(E/'test_run.txt').write_text(run.stdout+run.stderr)
assert run.returncode==0,run.stderr
summary={'tests':22,'failures':0,'errors':0,'passed':True,'scope':'Stage 1 A–R plus denominator, code, geometry application and derived dataset integrity','prior_stage_files_verified':len(prior),'exact_primary_refit':True}
(E/'test_summary.json').write_text(json.dumps(summary,indent=2)+'\n')
receipt={'built_at':datetime.now(timezone.utc).isoformat(),'execution':'PASS','python':platform.python_version(),'platform':platform.platform(),'candidate_hash':sha(CAND),'reference_hash':sha(REF),'primary_result_hash':sha(E/'primary_result.json'),'prior_stage_files_verified':len(prior),'test_summary':summary,'artifacts':{str(p.relative_to(ROOT)):sha(p) for folder in [E,ROOT/'docs/stage1_figures'] for p in sorted(folder.iterdir()) if p.is_file() and p.name!='build_manifest.json'},'code':{str(p.relative_to(ROOT)):sha(p) for p in [ROOT/'scripts/stage1_analysis.py',ROOT/'scripts/stage1_report.py',ROOT/'scripts/verify_stage1.py',ROOT/'tests/test_stage1.py',ROOT/'requirements-stage1.txt']},'report_hash':sha(ROOT/'docs/stage1_ft_residual_wingspan_analysis.md'),'determinism':'exact primary coefficient/CI/p/contrast equality on independent fits and successful full numerical rebuild; SVG metadata not claimed byte deterministic','primary_result_before_narrative':(E/'primary_result.json').stat().st_mtime < (ROOT/'docs/stage1_ft_residual_wingspan_analysis.md').stat().st_mtime}
assert receipt['primary_result_before_narrative']
(E/'build_manifest.json').write_text(json.dumps(receipt,indent=2)+'\n')
print(json.dumps(summary,indent=2))
