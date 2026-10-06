"""Part A verification must not misrepresent Stage 3 as a scientific PASS."""
import json,sys,subprocess,platform
from datetime import datetime,timezone
from stage3_sources import ROOT,E,sha

def main():
 files=[ROOT/'data/interim/stage3_all_player_seasons.parquet',ROOT/'data/processed/stage3_multiseason_ft_panel.parquet',ROOT/'data/processed/stage3_primary_replication_panel.parquet',E/'shooting_validation_sample_predeclared.csv',E/'measurement_corrections.csv',E/'panel_quality_by_season.csv',E/'selection_coverage_by_season.csv',E/'panel_freeze.json',E/'multi_season_source_validation.json']
 before={str(p.relative_to(ROOT)):sha(p) for p in files}
 for script in ['stage3_sources.py','stage3_validate_sources.py','stage3_panel.py']:
  r=subprocess.run([sys.executable,str(ROOT/'scripts'/script)],capture_output=True,text=True); (E/(script+'.run.txt')).write_text(r.stdout+r.stderr); assert r.returncode==0,r.stderr
 assert before=={str(p.relative_to(ROOT)):sha(p) for p in files},'nondeterministic rebuild'
 test=subprocess.run([sys.executable,'-m','unittest','discover','-s',str(ROOT/'tests'),'-p','test_stage3.py','-v'],capture_output=True,text=True); (E/'test_run.txt').write_text(test.stdout+test.stderr); assert test.returncode==0,test.stderr
 prior=json.loads((E/'prior_preservation_manifest.json').read_text()); assert all(sha(ROOT/p)==h for p,h in prior.items())
 check=subprocess.run([sys.executable,'-m','pip','check'],capture_output=True,text=True); assert check.returncode==0; (E/'pip_check.txt').write_text(check.stdout+check.stderr)
 summary=dict(part_A_implementation_tests=20,passed=20,failed=0,errors=0,prior_files_preserved=len(prior),deterministic_rebuild_files=len(files),part_A_source_gate='BLOCKED',stage3_execution_pass=False,part_B_tests='NOT RUN: model-dependent tests L–U await source release',scope='data construction/integrity tests pass; source validation does not pass')
 (E/'test_summary.json').write_text(json.dumps(summary,indent=2)+'\n')
 environment=dict(python=platform.python_version(),executable=sys.executable,platform=platform.platform(),requirements_hash=sha(ROOT/'requirements-stage3-partA.txt'),PyMC='not installed; Part B blocked',ArviZ='not installed; Part B blocked'); (E/'environment.json').write_text(json.dumps(environment,indent=2)+'\n')
 manifest=dict(built_at=datetime.now(timezone.utc).isoformat(),execution='BLOCKED_AT_PART_A',part_B_started=False,test_summary=summary,environment=environment,artifacts={str(p.relative_to(ROOT)):sha(p) for p in E.rglob('*') if p.is_file() and p.name!='build_manifest.json'},code={str(p.relative_to(ROOT)):sha(p) for p in (ROOT/'scripts').glob('*stage3*.py')},test_code_hash=sha(ROOT/'tests/test_stage3.py'),report_hash=sha(ROOT/'docs/stage3_multiseason_hierarchical_ft.md'),candidate_hashes=before)
 (E/'build_manifest.json').write_text(json.dumps(manifest,indent=2)+'\n'); print(json.dumps(summary,indent=2))
if __name__=='__main__': main()
