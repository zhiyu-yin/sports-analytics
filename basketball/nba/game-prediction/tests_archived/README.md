# Historical tests — NOT part of normal development discovery

`model_execution/` preserves the original Stage 2–4 model-fit/replay/evaluation tests byte-for-byte. They are not run during infrastructure-only Stage 4A, including synthetic model fits and benchmark metric recalculation. Current model execution guards intentionally reject them. They require a separately authorized modeling stage and an explicit policy revision before reuse.

`historical_real_data/test_reconciliation.py` preserves the original Stage 1D real-data tests byte-for-byte. Do not execute them under the sealed development policy. Normal reconciliation tests use invented teams, game IDs and results. Historical Stage 1D evidence has not been rewritten.

Normal command: `.venv/bin/python -m unittest discover -s tests -v`.
No force flag or historical reproduction escape hatch is provided.
