# NBA Game Prediction V1 — release summary

| Field | Frozen release |
| --- | --- |
| Version | V1 |
| Scope | Team-level probabilistic NBA game prediction |
| Status | Frozen / completed |
| Primary model | features_plus_elo_logistic (Model C) |
| Primary benchmark | raw_elo |
| Statistical training | 2015–16 through 2022–23 |
| Development validation | 2023–24 |
| Pre-holdout | 2024–25 |
| Final holdout | 2025–26; all 1,230 games |
| Future development | V2 player-aware model; not implemented |

**Main result:** same-direction log-loss and Brier improvement versus raw Elo across all three seasons. **Caveat:** both final date-clustered descriptive bootstrap intervals include zero; this is not definitive statistical-significance evidence.

V1 freezes existing recipes, preprocessing, feature definitions, metrics and scientific artifacts. Stage 7 adds presentation and integrity evidence only. Historical failed attempts and recovery records remain intact. No new models, tuning, evaluation, or post-hoc selection are part of this release.

[README](../README.md) · [Technical report](v1_final_report.md) · [Freeze manifest](v1_freeze_manifest.json) · [Reproduction guide](v1_reproduction.md)

Scientific release frozen. Repository release and publication status are recorded separately in the [Stage 8 release audit](stage8_github_release.md).
