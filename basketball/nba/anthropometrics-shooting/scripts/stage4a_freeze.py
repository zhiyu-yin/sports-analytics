"""Freeze manuscript scope and protect historical bytes; no analytical data decoded."""
from pathlib import Path
import hashlib, json
from datetime import datetime, timezone
ROOT=Path(__file__).resolve().parents[1]
D=ROOT/'docs/manuscript'
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1024*1024),b''): h.update(b)
 return h.hexdigest()
def read(p): return json.loads((ROOT/p).read_text())
def save(p,x): (D/p).write_text(json.dumps(x,indent=2,ensure_ascii=False)+'\n')
def main():
 assert not (D/'manuscript_freeze.json').exists(), 'Immutable freeze already exists'
 old=read('docs/stage3jr_evidence/prior_preservation_manifest.json')
 manifest=read('docs/stage3jr_evidence/build_manifest.json')
 old.update({p:v['sha256'] for p,v in manifest['files'].items()})
 for folder in ['docs','reports','scripts','tests','data','models']:
  for p in (ROOT/folder).rglob('*'):
   rel=p.relative_to(ROOT).as_posix()
   if p.is_file() and '__pycache__' not in rel and '/manuscript/' not in rel and 'stage4a' not in rel:
    if rel not in old: old[rel]=sha(p)
 bad=[p for p,h in old.items() if not (ROOT/p).exists() or sha(ROOT/p)!=h]
 assert not bad,bad
 save('prior_preservation_manifest.json',old)
 inventory=[]
 for d in sorted((ROOT/'docs').glob('*_evidence')):
  files=sorted(str(p.relative_to(ROOT)) for p in d.rglob('*') if p.is_file())
  inventory.append(dict(directory=str(d.relative_to(ROOT)),file_count=len(files),files=files))
 save('audit_chain_inventory.json',inventory)
 protocol=read('docs/stage3j_evidence/analysis_protocol.json')
 core='Greater residual wingspan was associated with lower free-throw accuracy in NBA players with available combine measurements. The negative association was observed in the 2013-14 development analysis and persisted in a 13-season replication panel excluding that season, with similar estimates across player-clustered, beta-binomial, first-season-only, player-balanced, attempt-threshold and leave-one-season-out analyses.'
 limitations=[
 'Measurement coverage is approximately 51%-67%. Combine participation, measurement availability/completeness, NBA survival, playing and shooting opportunity select the sample; the model does not correct this selection.',
 'Free-throw attempt volume is the grouped-binomial denominator rather than a predictor. Low-FTA rates are overpredicted and rates in the 300+ FTA bin are underpredicted. The primary model is a working conditional association model, not a complete generative model of shooting opportunity.',
 'Residual wingspan is time invariant and identified between players. Player-clustered uncertainty accounts for dependence, not unmeasured skill, training or role. Repeated outcomes do not provide within-player exposure identification or establish a causal mechanism.',
 'Original combine position is an imperfect historical role proxy. Inference conditions on the frozen geometric reference; measurement and reference-fit uncertainty are not propagated.']
 inputs=['docs/stage3j_evidence/primary_result.json','docs/stage3jr_evidence/full_bootstrap_summary.json','docs/stage3jr_evidence/stage3jr_decision.json','docs/stage3j_evidence/analysis_protocol.json']
 freeze=dict(stage='4A',frozen_at=datetime.now(timezone.utc).isoformat(),primary_analysis='Stage 3J J1',secondary_analysis='J2 beta-binomial with Stage 3J-R remediated player bootstrap',primary_estimand=protocol['estimand'],primary_panel_hash=protocol['primary_panel_sha256'],full_panel_hash=protocol['full_panel_sha256'],primary_model=protocol['formula'],response=protocol['response'],exposure_definition=protocol['residualization'],primary_result_artifact_hash=sha(ROOT/inputs[0]),J2_remediation_artifact_hash=sha(ROOT/inputs[1]),J2_remediation_decision_hash=sha(ROOT/inputs[2]),inputs={p:sha(ROOT/p) for p in inputs},primary_uncertainty=['player-cluster CR1','2000-replicate player percentile bootstrap'],primary_seasons=protocol['seasons'],main_robustness_set=['J2 beta-binomial','first eligible replication season','player-balanced','FTA >=50','FTA >=100','leave-one-season-out','full secondary panel including development'],supplementary_exposures=['wingspan advantage','wingspan ratio'],development_replication_distinction='2013-14 is development and excluded from primary; players may overlap. Out-of-season replication, not independent-player replication.',approved_core_conclusion=core,prohibited_causal_wording=['effect of wingspan','Long arms hurt shooting','causes worse free-throw shooting','mechanically reduces shooting accuracy','proves'],main_limitations=limitations,planned_tables=['main_table1_sample','main_table2_primary','main_table3_robustness','supp_leave_one_season_out','supp_alternate_exposures'],planned_figures=['figure1_study_flow','figure2_robustness_forest','figure3_leave_one_season_out','figure4_selection_coverage','supp_figure1_attempt_volume_diagnostic'],descriptive_exposure_figure={'status':'REQUIRES FUTURE ANALYSIS','placement':'SUPPLEMENT if separately authorized','reason':'Only development-season exposure bins exist; replication bins or new player summaries would be new analysis. No new bins, raw unweighted FT-percent scatter, or fitted line is generated.'},table1_position_policy='Use accounting player-season counts recovered arithmetically as frozen observed position FTA total / frozen observed position mean FTA from Stage3DR joint_PPC_metrics. No fitted or predictive fields used; round only after checking near-integer, require total 4117. Unique-player position distribution is not available as a frozen summary and is not invented.',table1_fta_policy='Use frozen observed overall FTA mean, SD and quartiles only; all accounting rows including zeros. No posterior predictions from failed models enter Table 1.',flow_policy='Use frozen approved 14-season coverage sum, full and primary panel counts. Combine eligibility and exact-ID linkage share one observed intersection count; do not invent sequential attrition counts.',historical_decisions={'Stage3':'BLOCKED under original source gate','Stage3A':'UNRESOLVED — INSUFFICIENT PRECISION EVIDENCE','Stage3B':'PASS UNDER AMENDED PROTOCOL','Stage3C':'FAIL — PPC inadequacy despite sampler pass','Stage3D':'Prior prerequisite failed; posterior unassessed','Stage3DR':'ADEQUACY UNRESOLVED — D3 FAILS','Stage3F':'STRUCTURAL ADEQUACY UNRESOLVED','Stage3FR':'IDENTIFICATION UNRESOLVED — NO EQUIVALENT F2 PARAMETERIZATION PASSES SAMPLER','Stage3H':'SHARED-FACTOR ADEQUACY UNRESOLVED','Stage3I':'RESIDUAL ADEQUACY UNRESOLVED','Stage3J':'EXECUTION FAIL','Stage3JR':'NUMERICAL REMEDIATION PASS'},allowed_operations=['read frozen JSON/CSV/report evidence','hash historical files without decoding traces or panels','copy published values','format and label','exp coefficient interval endpoints for OR display if needed','arithmetic recovery of existing denominators','sum approved coverage counts for flow','matplotlib rendering','verification'],forbidden_operations=['statistical fitting','bootstrap or RNG','panel decoding or filtering','new threshold/exposure/outcome/subgroup/interaction','decoding failed scientific traces','Stage4B','commit','push','submission'],preserved_artifacts=len(old),preservation_manifest_hash=sha(D/'prior_preservation_manifest.json'))
 save('manuscript_freeze.json',freeze)
 save('freeze_receipt.json',dict(frozen_at=freeze['frozen_at'],sha256=sha(D/'manuscript_freeze.json'),before_manuscript_prose=True))
 print('Frozen manuscript scope; protected',len(old),'historical artifacts; no historical differences.')
if __name__=='__main__': main()
