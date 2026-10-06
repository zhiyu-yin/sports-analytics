# NBA Anthropometrics × Shooting

Independent research subproject. Stage 0 audits data availability, coverage, identity and research design. The question is associational: is relative wingspan associated with shooting performance after accounting for body size, role and shot context?

**Status: Stage 0B candidate frozen; inferential release blocked by incomplete historical anthropometric validation.** No correlations, regressions, hypothesis tests or effect-direction conclusions have been run.

Read [the Stage 0 report](docs/stage0_data_audit.md) and [compact evidence](docs/stage0_evidence/). The existing NBA Game Prediction V1 is untouched.

## Reproduce

For Stage 0: Python 3.9+ and `curl`; no external Python dependencies. Run from this subproject:

```sh
# Public network retrieval, bounded timeouts; may take several minutes.
python3 scripts/collect_audit.py
# Offline: verifies raw checksums, rebuilds coverage and a 12-row join prototype.
python3 scripts/audit_joinability.py
python3 scripts/summarize_sources.py
PYTHONPATH=src python3 -m unittest discover -s tests -v
```

The current report is a dated narrative snapshot; inspect regenerated evidence and revise it after new retrievals. `combine_corrected_probes.json` preserves the initial audit's corrected four-digit combine-year probes; initial exploratory season-label attempts remain separately identifiable in `endpoint_probes.json`. A fresh collector uses four-digit combine years.

Raw bytes and timestamped manifests are immutable under `data/raw/`; local identity review and the prototype are under `data/interim/`. `data/processed/` now contains the Git-ignored Stage 0B candidate freeze. All three data directories are already Git-ignored by the umbrella repository. Scripts recreate the required data and evidence directories after a fresh checkout. No source datasets are redistributed in docs. No commit or push is part of this stage.

Modules separate units, measurement normalization, shooting counts, identity classification, data validation and provenance. The Stage 0B candidate is for review; no statistical model is fitted.

## Stage 0B

Read [source validation and freeze report](docs/stage0b_source_validation.md), [predeclared protocol](docs/stage0b_protocol.md), and [evidence](docs/stage0b_evidence/). The candidate has 311 players, but remains **not cleared for inference**. Stage 0 files and the NBA Game Prediction project remain preserved.

Use a separate Python environment with `requirements-stage0b.txt` (pypdf for PDF text and pyarrow for Parquet). No dependencies were added to NBA Game Prediction. From this subproject, with the original local raw/interim bundle present:

```sh
python3 scripts/prepare_stage0b.py
python3 scripts/extract_stage0b_pdfs.py
python3 scripts/crosscheck_stage0b.py
python3 scripts/crosscheck_stage0b_mirror.py
python3 scripts/build_stage0b.py
python3 scripts/test_stage0b.py
```

These steps run offline and verify raw hashes. Preparation preserves the original sample declaration timestamp and refuses changed sample membership. The build verifies all source checksums and refuses a changed existing Parquet. Tests preserve a full log and JSON summary. The initial PDF extraction was also checked against rendered source pages; rerunning text extraction is not a substitute for that visual source inspection.

Full data/raw page bodies are not distributed with Git. A fresh checkout needs the original local bundle, including Stage 0 identity audit inputs and historical raw records whose hashes are protected. URLs and checksums are recorded in source manifests, but refetching a mutable official page may not recover identical historical bytes. `fetch_stage0b_sources.py` and `fetch_stage0b_profiles.py` document the principal initial retrievals; supplemental URLs/attempts are recorded separately. New retrievals are a new audit amendment, not an automatic replacement of this frozen evidence.

No scientific effect estimate, residual fit, commit or push was performed. The exact frozen file is `data/processed/ft_2013_14_stage1_dataset.parquet`; metadata and every row flag its pending source validation.
