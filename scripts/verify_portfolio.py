"""Read-only public-checkout verification; stdlib only; no fits or source retrieval."""
from pathlib import Path
import hashlib,json,re,csv
R=Path(__file__).resolve().parents[1]
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 manifest=json.loads((R/'docs/publication/published_evidence_manifest.json').read_text())
 for p,h in manifest.items():assert (R/p).is_file() and digest(R/p)==h,('Missing/changed published evidence',p)
 pages=['README.md','docs/PREDICTION_MARKETS_PORTFOLIO.md','docs/PROJECT_STATUS.md','docs/publication/README.md','basketball/nba/game-prediction/README.md','basketball/nba/anthropometrics-shooting/README.md'];links=0
 for p in pages:
  text=(R/p).read_text();assert '/Users/' not in text and '/private/tmp/' not in text,p
  for u in re.findall(r'\]\(([^)]+)\)',text):
   if '://' in u or u.startswith('#'):continue
   assert (R/p).parent.joinpath(u.split('#')[0]).is_file(),(p,u);links+=1
 metrics={r['model']:r for r in csv.DictReader((R/'basketball/nba/game-prediction/docs/stage6r2_evidence/final_holdout_metrics.csv').open())}
 readme=(R/'basketball/nba/game-prediction/README.md').read_text()
 for model in ['raw_elo','features_plus_elo_logistic']:
  for key in ['log_loss','brier_score','accuracy','roc_auc']:assert f"{float(metrics[model][key]):.6f}" in readme,(model,key)
 a=R/'basketball/nba/anthropometrics-shooting';assert digest(a/'docs/stage3j_evidence/primary_result.json')=='79b8f461efcc61e0a6e3ff33728fa0d0019839aae03b9809d530f8c9b6906e02'
 assert digest(a/'docs/manuscript/manuscript_freeze.json')=='66a07aa5c826ac34f7aa8a09ee9565312e350e676d0965bb7f2040b02f7c6def'
 assert json.loads((a/'docs/stage4x_evidence/shot_source_validation.json').read_text())['classification']=='SHOT DATA FEASIBILITY BLOCKED'
 print(json.dumps({'passed':True,'published_evidence_hashes_verified':len(manifest),'presentation_links_verified':links,'final_metrics_match_frozen_evidence':True,'models_run':False},indent=2))
if __name__=='__main__':main()
