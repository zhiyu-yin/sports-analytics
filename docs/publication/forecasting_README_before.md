# NBA Game Prediction V1 — Team-Level Probabilistic Modeling

A reproducible probabilistic forecasting study of NBA regular-season games, emphasizing temporal leakage control, model comparison and out-of-time validation. **V1 complete / frozen.**

## Key result

The Model C improvement over raw Elo had the same direction across three consecutive temporally held-out seasons, including development validation, a pre-holdout and a final holdout.

| Season / role | Elo LL | C LL | Δ LL | Elo Brier | C Brier | Δ Brier |
| --- | --- | --- | --- | --- | --- | --- |
| 2023-24 development validation | 0.61558 | 0.61011 | -0.00546 | 0.21411 | 0.21136 | -0.00274 |
| 2024-25 pre-holdout | 0.61450 | 0.60600 | -0.00850 | 0.21332 | 0.20939 | -0.00393 |
| 2025-26 final holdout | 0.60464 | 0.60192 | -0.00272 | 0.20833 | 0.20705 | -0.00127 |

LL = log loss; Δ = Model C − raw Elo; lower losses are better. [Frozen full-precision source](docs/stage6r2_evidence/cross_season_confirmation.csv).

The predeclared date-clustered descriptive bootstrap intervals on the final holdout included zero, so the final result is not presented as definitive statistical-significance evidence.

![Three-season probability losses](reports/figures/v1/three_season_comparison.png)

## Method and frozen model

```text
NBA historical games → leakage-safe pregame features → Elo baseline
→ regularized logistic / HGB → chronological validation
→ pre-holdout → final holdout
```

Predict P(designated home team wins). Model C (`features_plus_elo_logistic`) combines 32 team form/schedule features with frozen `elo_logit`: training-median imputation + missingness indicators → StandardScaler → L2 logistic regression (C=0.01, lbfgs, max_iter=5000, tol=1e-4, seed=0). Elo: initial 1500, scale 400, K=20, home advantage 50, offseason alpha=0.50.

## Evaluation and findings

Statistical training: **2015–16 through 2022–23**; development validation: **2023–24**; pre-holdout: **2024–25**; final holdout: **2025–26**. Statistical parameters stay frozen; Elo state advances after completed games.

- All 1,230 final-season games included; no warmup games dropped.
- Model C has the lowest final log loss/Brier among seven frozen candidates.
- Features alone and Elo-only logistic did not beat raw Elo on those losses; HGB did not beat C.
- Calibration is mixed: C has smaller mean bias but higher final fixed-bin ECE than Elo.

## Repository structure

```text
src/                 reusable data and modeling code
tests/               leakage, validation and reproducibility tests
docs/                methodology, V1 report and audit trail
reports/figures/      validated research figures
data/                local caches and derived artifacts, not tracked
```

## Reproduce / verify

From this subproject, with the existing pinned environment:

```sh
.venv/bin/python -m unittest discover -s tests -v
python3 stage7/verify_v1.py
```

The verifier hashes archived files without decoding outcomes or running models. Raw caches are local and excluded from Git; exact source data may need reacquisition, and later source revisions may differ. [Reproduction guide](docs/v1_reproduction.md) lists cached-build and open historical development commands with their archival restrictions. Final-stage execution required controlled, explicitly authorized infrastructure; keep its results archived rather than casually rerunning the holdout.

## Limitations and V2

Team aggregates omit injuries, player availability and lineups. Historical venue coverage is incomplete; availability is date-based, not verified at exact publication time. One final season and remaining game/team dependence limit inference. **Future V2:** player-aware inputs and richer context; no V2 changes are part of this release.

## Documentation

[Final technical report](docs/v1_final_report.md) · [V1 release summary](docs/v1_release_summary.md) · [Freeze manifest](docs/v1_freeze_manifest.json) · [Feature dictionary](docs/stage1b_feature_dictionary.csv)

Raw NBA data are not distributed here. Data were retrieved from NBA sources through `nba_api`; historical responses may change. This repository does not claim ownership of NBA data. Review source terms before redistributing data.
