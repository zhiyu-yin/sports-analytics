# Stage 8 — GitHub release / repository polish

## 1. Objective
Prepare the umbrella Sports Analytics repository for release with NBA Game Prediction V1 complete and frozen. No scientific execution or result changes are permitted.

## 2. Initial Git state
No Git repository or parent repository existed; branch/remotes/tracked files were absent. The initial filesystem contained approximately 453 MB, mostly the local virtualenv. See [inventory](stage8_evidence/initial_inventory.json) for files above 1 MB and 10 MB, environment and symlink details.

## 3. Repository boundary
The only intended Git root is `sports-analytics/`, with `basketball/nba/game-prediction/` as a subproject. No nested Git metadata was found. All three discovered symlinks belong to the excluded virtualenv. No directory restructuring or audit-history deletion was needed.

## 4. README polish
The key finding now explicitly distinguishes development validation, pre-holdout and final holdout. The result table and bootstrap-zero caveat stay near the top. The folder summary emphasizes source, tests, docs, figures and local data. The umbrella introduction covers the broader research collection. The release summary delegates publication status to this audit.

## 5. .gitignore audit
Umbrella-wide rules exclude virtualenvs, bytecode, credentials/key files, OS/editor artifacts, local cache/temp/log directories, raw/interim/processed data, serialized models and Parquet datasets, including replay datasets outside `data/`. Exact Stage 0 payload patterns exclude recorded/live NBA responses while retaining their manifests and summaries. Source, tests, requirements, Markdown, small evidence CSV/JSON and validated figures remain candidates. Scientific evidence logs are retained; no blanket log exclusion hides the audit trail.

## 6. Secret scan
Pattern scanning checks private keys, GitHub/API/AWS credentials, credential assignments, authorization/cookie values and credential-bearing database URLs without printing values. No secret candidates were found. This is a heuristic scan, not a guarantee. Retained personal-path occurrences are historical execution context; no email/contact content was found in the initial project text scan. See [candidate scan](stage8_evidence/candidate_scan.json).

## 7. Large-file scan
No intended release candidate exceeds 1 MB or 10 MB. The 3,827,748-byte fitted estimator pickle is local-only. Large environment binaries, raw responses and derived datasets are excluded. The largest retained pre-release evidence file is the 229,493-byte team-history lineage JSON; it contains provenance identities rather than raw box-score responses. The candidate scan lists the largest 20 files. Small validated PNGs remain included.

## 8. Local-path audit
Current public READMEs, report, reproduction instructions and reusable entry points contain no hard-coded user-home paths. Historical Stage 0 probe code, stage reports, authorization records and failure ledgers retain original paths as historical audit context. These files are preserved byte-for-byte, not silently rewritten. No license exists; none was invented. Public documentation distinguishes original code from NBA source-data rights.

## 9. Link verification
The five release Markdown documents and umbrella README are checked through the V1 verifier. Referenced figures and relative documentation links must resolve. No external network check or new research is required. Excluded source/model artifacts remain named in historical manifests, with their local-only status explained in the reproduction guide.

## 10. V1 integrity verification
Only the umbrella README, subproject README, V1 release summary and reproduction guide have refreshed presentation hashes. The [original V1 manifest](stage8_evidence/v1_freeze_manifest_before.json) is archived. All scientific artifact hashes, recipes, figures, source checkpoints and final tables are unchanged. Stage 7 records remain historical and are not overwritten. Fresh Stage 8 results: **138 safe tests passed; the V1 verifier passed; 45 local links resolve; all 537 protected historical files are byte-identical.** Outputs are stored separately in `stage8_evidence/test_run.txt` and `stage8_evidence/v1_verification.json`. No archived model tests, training, predictions, scoring or holdout replay were executed.

## 11. Files intentionally excluded
Local virtualenv/cache/OS/editor files; all raw/interim/processed data; all Parquet evaluation datasets; fitted pickle/joblib binaries; original Stage 0 response payloads; credential/key patterns; the post-commit local receipt. Nothing was deleted. A plain Git checkout intentionally lacks artifacts required by the complete local integrity suite. Historical hashes and provenance remain published.

## 12. Files staged
The exact reviewed staging inventory is saved in `stage8_evidence/staged_files.txt`: **446 files, approximately 3.1 MB**. Every staged blob was checked for size, type, raw-response JSON structure, secret patterns and exact equality with the reviewed working file. All 48 release/audit Markdown links resolve to included files. Intended scope is umbrella/project documentation, source, guarded historical entry points, current and explicitly archived tests, compact scientific evidence, validated figures and shared lightweight placeholders. No blind `git add .` is used.

## 13. Commit
Release commit message: `Initialize sports analytics repository with NBA Game Prediction V1`. The release commit is identified by `git log -1 --format='%H %s'`. Its exact hash and observed post-commit status are recorded in the ignored local `stage8_evidence/local_release_receipt.json` and the delivery summary, avoiding a self-referential commit hash in its own tree.

## 14. Remote status
Remote remains absent. After the initial local commit, a read-only `gh api user` call verified the authenticated account **liyingerya**. A read-only lookup of `liyingerya/sports-analytics` returned HTTP 404 (not present or not accessible). No repository was created. Visibility is not established.

## 15. Push status
Not published. No remote creation or push is authorized without established visibility. No tag is created.

## 16. Remaining GitHub actions
The single remaining user decision is **public or private** for the proposed `liyingerya/sports-analytics` repository. After that decision, remote creation/push may proceed without force-push. No settings, topics, Pages or license changes are part of this stage.

## 17. Stage 8 exit status
**Locally complete; not published.** All safety gates passed and the release commit is on `main` at the umbrella root. The initial commit had a clean working tree; this audit was then amended into the same single release commit to record the observed GitHub account and remaining visibility decision. The ignored post-commit receipt records the final commit hash and clean-tree check. No scientific file, source checkpoint or final result changed; no remote, push or tag was created.
