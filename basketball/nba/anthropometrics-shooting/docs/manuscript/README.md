# Manuscript assembly package

This package freezes analysis and assembles outlines. It does not start Stage 4B.

- `manuscript_freeze.json` and `freeze_receipt.json`: immutable scope and chronology.
- `evidence_map.csv`: approved statements and numeric source fields.
- `numeric_lineage.json`: exact source-value and output-cell bindings; display arithmetic is explicit.
- `content_disposition.csv`: major outputs and manuscript roles.
- `historical_artifact_disposition.csv`: exhaustive preservation inventory placements.
- `figure_manifest.json`: figure names and frozen display-data sources.
- `visual_review.json`: review of rendered final PDFs.
- `test_run.txt`, `test_summary.json`, `build_manifest.json`: final checks and hashes.

Read the Stage 4A report first. Markdown tables round for readability; CSV values retain frozen precision. Anthropometric summaries use unique players. Position and FTA summaries use accounting player-seasons including zeros. The position denominator is an arithmetic recovery of existing observed total/mean summaries, checked to be integer-valued and sum correctly. No failed-model predictive estimates are imported for those sample descriptions.

Reproduction from the subproject directory, with the existing `.venv`:

```sh
PYTHONDONTWRITEBYTECODE=1 MPLCONFIGDIR=/private/tmp/stage4a-mpl .venv/bin/python scripts/stage4a_build.py
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python scripts/stage4a_prose.py
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python scripts/stage4a_verify.py
```

The freeze script is one-time and refuses overwrite. Do not rerun historical builders. Rebuilt PDFs must be rendered and visually reviewed before release; the verifier requires a matching visual-review receipt. Running the prose builder resets the Stage 4A report decision to pending until checks finish. Builders write only Stage 4A paths. Publication timestamps in PDF metadata can change on rendering; numeric sources are deterministic and protected. No package installation, statistical fitting, sample filtering or bootstrap is required.

The descriptive replication exposure-outcome figure is REQUIRES FUTURE ANALYSIS. Do not derive new bins or a fitted line within manuscript assembly.
