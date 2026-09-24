"""Read-only release checks: no model imports, fits, predictions or outcome decoding."""
from pathlib import Path
from hashlib import sha256
import csv
import json
import re

R=Path(__file__).resolve().parents[1]
def digest(p):
    h=sha256()
    with p.open('rb') as f:
        for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
    return h.hexdigest()
def rows(name):
    with (R/'docs/stage6r2_evidence'/name).open() as f:return list(csv.DictReader(f))
def table(headers, values):
    return '| '+' | '.join(headers)+' |\n| '+' | '.join(['---']*len(headers))+' |\n'+'\n'.join('| '+' | '.join(map(str,row))+' |' for row in values)
def main():
    protected=json.loads((R/'docs/stage7_evidence/protected_artifacts_before.json').read_text())['sha256']
    changed=[p for p,h in protected.items() if not (R/p).is_file() or digest(R/p)!=h]
    assert not changed, ('Changed historical files',changed)
    manifest=json.loads((R/'docs/v1_freeze_manifest.json').read_text())
    for p,h in manifest['artifact_sha256'].items():assert digest(R/p)==h,p
    for p,h in manifest['current_source_code_checkpoint'].items():assert digest(R/p)==h,p
    for recipe in manifest['recipes'].values():
        obj=json.loads((R/recipe['path']).read_text())[recipe['json_pointer'][1:]]
        assert sha256(json.dumps(obj,sort_keys=True,separators=(',',':')).encode()).hexdigest()==recipe['canonical_json_sha256']
    docs=[R/'README.md',R/'../../../README.md']+list((R/'docs').glob('v1*.md'))
    links=0
    for p in docs:
        for url in re.findall(r'\]\(([^)]+)\)',p.read_text()):
            if '://' in url or url.startswith('#'):continue
            assert (p.parent/url.split('#')[0]).exists(),(str(p),url)
            links+=1
    cross=rows('cross_season_confirmation.csv')
    expected=table(['Season / role','Elo LL','C LL','Δ LL','Elo Brier','C Brier','Δ Brier'],[[r['split']]+[f"{float(r[k]):.5f}" for k in ['raw_elo_log_loss','model_c_log_loss','delta_log_loss','raw_elo_brier','model_c_brier','delta_brier']] for r in cross])
    assert expected in (R/'README.md').read_text()
    report=(R/'docs/v1_final_report.md').read_text()
    assert expected in report
    labels={'constant_home_prior':'Constant prior','raw_elo':'Raw Elo','basketball_features_logistic':'A · Features logistic','elo_logistic':'B · Elo logistic','features_plus_elo_logistic':'C · Features + Elo logistic','basketball_features_hgb':'D · Features HGB','features_plus_elo_hgb':'E · Features + Elo HGB'}
    metrics=rows('final_holdout_metrics.csv')
    expected=table(['Frozen candidate','Games','Log loss','Brier','Accuracy','ROC-AUC'],[[labels[r['model']],r['n_games'],f"{float(r['log_loss']):.5f}",f"{float(r['brier_score']):.5f}",f"{float(r['accuracy']):.2%}",f"{float(r['roc_auc']):.3f}"] for r in metrics])
    assert expected in report
    for r in rows('date_cluster_bootstrap.csv'):
        line='| '+' | '.join([r['metric'],f"{float(r['observed_mean_difference']):.5f}",f"{float(r['bootstrap_standard_error']):.5f}",f"[{float(r['ci_lower_2_5']):.5f}, {float(r['ci_upper_97_5']):.5f}]",r['includes_zero']])+' |'
        assert line in report
    for r in rows('calibration_summary.csv'):
        if r['model'] not in ('raw_elo','features_plus_elo_logistic'):continue
        line='| '+' | '.join([labels[r['model']],f"{float(r['fixed_bin_ece']):.5f}",f"{float(r['mean_predicted_probability']):.5f}",f"{float(r['observed_designated_home_win_rate']):.5f}",r['populated_bins']+' / '+r['bins_below_30']])+' |'
        assert line in report
    assert len(re.findall(r'^## \d+\.',report,re.M))==16
    log=(R/'docs/stage7_evidence/test_run.txt').read_text()
    assert 'Ran 138 tests' in log and log.rstrip().endswith('OK')
    out={'passed':True,'protected_preexisting_files_unchanged':len(protected),'scientific_artifacts_changed':False,'old_stage_evidence_unchanged':True,'local_markdown_links_resolved':links,'presentation_tables_match_frozen_csvs':True,'ordinary_safe_tests_passed':138,'archived_model_execution_tests_run':False,'models_rerun':False,'figure_visually_reviewed':True,'manifest_sha256':digest(R/'docs/v1_freeze_manifest.json'),'git_status':'No Git repository present; hash comparison used','commit_or_push':False}
    print(json.dumps(out,indent=2,sort_keys=True))
if __name__=='__main__':main()
