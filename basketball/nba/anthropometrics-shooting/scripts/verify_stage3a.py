"""Offline verification; never rerun or rewrite the failed Stage 3 gate."""
import json,subprocess,sys,platform,re
from datetime import datetime,timezone
from stage3a_prepare import ROOT,E,sha,save

def main():
    stable=['official_game_minute_crosscheck.csv','minute_reconstruction_by_player_season.csv','minute_difference_distribution.csv','minute_quantization_summary.json','zero_minute_appearance_audit.csv','minute_parser_validation.json','game_level_reconciliation_summary.json','candidate_rounding_explanations.csv','official_game_count_sum_crosscheck.csv','minute_parser_sample.csv','season_eligibility_crosscheck.csv','official_boxscore_classification_crosscheck.csv']
    before={p:sha(E/p) for p in stable}
    rebuild=subprocess.run([sys.executable,str(ROOT/'scripts/stage3a_audit.py')],capture_output=True,text=True)
    (E/'rebuild_run.txt').write_text(rebuild.stdout+rebuild.stderr);assert rebuild.returncode==0,rebuild.stderr
    assert before=={p:sha(E/p) for p in stable},'numeric/source reconstruction changed'
    test=subprocess.run([sys.executable,'-m','unittest','discover','-s',str(ROOT/'tests'),'-p','test_stage3a.py','-v'],capture_output=True,text=True)
    output=test.stdout+test.stderr;(E/'test_run.txt').write_text(output)
    n=int(re.search(r'Ran (\d+) tests',output)[1]);passed=test.returncode==0
    prior=json.loads((E/'prior_artifact_hashes.json').read_text());preserved=all(sha(ROOT/p)==h for p,h in prior.items())
    summary=dict(tests_run=n,tests_passed=n if passed else None,execution_success=passed,prior_files_preserved=len(prior) if preserved else False,deterministic_rebuild_files=len(stable),stage3a_classification='UNRESOLVED — INSUFFICIENT PRECISION EVIDENCE',source_gate_pass=False,part_B_started=False,scope='provenance and software checks only; passing tests do not resolve the precision mechanism')
    save('test_summary.json',summary)
    environment=dict(python=platform.python_version(),executable=sys.executable,requirements='requirements-stage3-partA.txt',requirements_sha256=sha(ROOT/'requirements-stage3-partA.txt'),new_packages_installed=False)
    save('environment.json',environment)
    paths=list(E.rglob('*'))+list((ROOT/'data/raw/stage3a').glob('*'))+list((ROOT/'scripts').glob('*stage3a*.py'))+[ROOT/'tests/test_stage3a.py',ROOT/'docs/stage3a_minute_precision_resolution.md']
    save('build_manifest.json',dict(built_at=datetime.now(timezone.utc).isoformat(),test_summary=summary,environment=environment,artifacts={str(p.relative_to(ROOT)):sha(p) for p in sorted(paths) if p.is_file() and p.name!='build_manifest.json'},prior_hash_manifest_sha256=sha(E/'prior_artifact_hashes.json'),sample_sha256=sha(E/'minute_audit_sample_predeclared.csv'),part_B_started=False))
    print(json.dumps(summary,indent=2));assert passed and preserved,output
if __name__=='__main__':main()
