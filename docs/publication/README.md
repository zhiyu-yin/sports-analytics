# Publication and Reproducibility Notes

This portfolio publication packages completed scientific work and updates presentation only. No models, MCMC, bootstraps or source-data analyses were rerun. Historical scientific reports, manifests, evidence and figures retain their original bytes, including dated failures and execution restrictions.

## Presentation-only exceptions

The root README, both project READMEs and root ignore rules were updated with explicit publication authorization. The prior [root README](root_README_before.md), [forecasting README](forecasting_README_before.md) and [shooting README](shooting_README_before.md) are preserved byte-for-byte. Relative links inside these snapshots refer to their original project directories; the snapshots are historical evidence, not navigation pages.

Frozen historical manifests still reference the original README paths and hashes. Their full historical verifiers therefore intentionally do not pass against the new presentation at those paths. No scientific manifest or historical test was altered to hide this difference. The publication integrity audit checks the archived README bytes against those original hashes and verifies the other protected artifacts unchanged. A separate portable verifier checks the published evidence subset and current presentation.

## Verification

From the repository root:

```sh
python3 scripts/verify_portfolio.py
```

This standard-library-only check resolves current presentation links, verifies published scientific evidence hashes and matches the forecasting results table to frozen metrics. It does not fit, predict, score, decode sampler traces or retrieve data. Its successful completion is an integrity check, not independent scientific reproduction.

The [verification record](verification.json) reports the original local archive preservation checks and safe test result. The [published evidence manifest](published_evidence_manifest.json) covers existing published files other than the explicitly revised presentation files. The local archive includes additional ignored data and environment files; it is not bundled into this public Git repository.

## What remains local

Raw/interim/processed source data, virtual environments, model binaries, NumPy/NetCDF sampler outputs, caches and temporary local files remain ignored and retained on disk. Compact audit tables, scientific logs, failed-model diagnostic figures, source checksums and decisions are retained in Git. No scientific evidence was deleted. The largest published evidence file is approximately 6 MB; no individual publication artifact approaches GitHub's 100 MB file limit.

Historical absolute filesystem paths in logs, receipts and older scripts are retained as provenance rather than rewritten inside frozen files. Current portfolio commands use repository-relative paths. Those older source records may require the original local directory layout and are not promoted as portable commands. Credentials and machine-local environment files are excluded; publication checks also scan the staged text for common credential formats.

Raw source ownership and redistribution rights are not granted by this repository. Some compact validation tables necessarily contain NBA-derived observations; they serve as audit evidence, not a redistributed raw-data bundle. No license or new source-data rights are asserted by this cleanup.
