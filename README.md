# Sports Analytics

**Probabilistic Forecasting, Statistical Inference, and Decision-Making**

Reproducible NBA research focused on probability quality, temporal validation, uncertainty and source validation. Two completed studies demonstrate complementary skills for quantitative research, prediction-market research and data science: forecasting game outcomes and evaluating an observational player-level association.

## Projects

### 1. NBA Game Prediction — Flagship

Can we estimate well-calibrated pregame win probabilities using only information available before tip-off?

The study uses **13,209 accepted regular-season games from 2015–16 through 2025–26**, sourced from official NBA game data. Leakage-safe rolling features and a chronological Elo baseline are compared with regularized logistic regression and histogram gradient boosting under separate training, development-validation, pre-holdout and final-holdout periods.

On the 1,230-game final holdout, combined features + Elo logistic regression achieved log loss **0.601923** and Brier score **0.207053**, versus Elo's **0.604644** and **0.208328**. These were the best observed final losses among the frozen candidates, but the predeclared date-cluster bootstrap intervals for improvement included zero. **Statistically significant superiority is not established.** Calibration findings are mixed.

[Project README](basketball/nba/game-prediction/README.md) · [Frozen technical report](basketball/nba/game-prediction/docs/v1_final_report.md)

### 2. NBA Anthropometrics and Shooting — Research Study

Is wingspan relative to height associated with free-throw accuracy among NBA players with validated combine measurements?

A development-season analysis is followed by a **13-season replication panel**, using grouped-binomial inference, player-cluster robust covariance and player bootstrap. The primary estimate is **β = −0.030452 per residual-wingspan inch; OR = 0.9700**, with player-cluster 95% CI **[−0.05228, −0.00862]** and player-bootstrap 95% CI **[−0.05433, −0.01048]** on the beta scale. Beta-binomial, first-season-only, player-balanced, attempt-threshold and leave-one-season-out analyses form the robustness package.

This is a between-player association, not a causal effect. Measurement selection, unmeasured skill/role and informative shooting opportunity remain limitations. A planned shot-context extension stopped during source validation because zone/shot-type inconsistencies prevented defensible analysis. **Analysis stopped when source validation failed rather than forcing a result.**

[Project README](basketball/nba/anthropometrics-shooting/README.md) · [Manuscript analysis freeze](basketball/nba/anthropometrics-shooting/docs/stage4a_manuscript_freeze_report.md) · [Source-validation stop](basketball/nba/anthropometrics-shooting/docs/stage4x_shot_type_specificity.md)

### 3. Team Chemistry

**Paused / exploratory research direction.** No completed model or results are claimed. [Scope](basketball/nba/chemistry/README.md).

## Research Principles

- Time-aware validation with distinct development and evaluation roles.
- No target leakage: pregame features use earlier completed games.
- Probabilities over binary picks.
- Proper scoring rules and strong baseline comparisons.
- Explicit uncertainty and sensitivity analysis.
- Reproducible frozen protocols and preserved scientific history.
- Source validation before inference.
- Stopping when evidence quality is insufficient.

## Relevance to Prediction Markets

The forecasting study develops probability estimation, calibration assessment, baseline benchmarking, out-of-time validation and decision-making under uncertainty. It does not establish trading profitability or an advantage over market prices. See the [prediction-market portfolio brief](docs/PREDICTION_MARKETS_PORTFOLIO.md).

## Repository Structure

```text
basketball/nba/game-prediction/          flagship forecasting study
basketball/nba/anthropometrics-shooting/ observational research study
basketball/nba/chemistry/               paused research direction
docs/                                  portfolio brief and publication notes
shared/                                shared-code placeholder
soccer/                                future-work placeholder
```

## Reproducibility

Code, protocols, reports, compact evidence and figures are published. Raw/intermediate data, environments, fitted model binaries and sampler traces remain local and ignored. A public checkout supports documentation and published-evidence checks; exact historical reproduction additionally requires the original source snapshots and guarded environments. Re-fetching mutable sources may not reproduce historical bytes.

Run the portable, read-only portfolio check from the repository root:

```sh
python3 scripts/verify_portfolio.py
```

See the [forecasting reproduction guide](basketball/nba/game-prediction/docs/v1_reproduction.md) and [publication notes](docs/publication/README.md) for archival boundaries. Do not rerun old builders into frozen evidence directories. Historical absolute paths remain provenance records, not portable instructions.

## Status

Forecasting: **COMPLETE / FROZEN V1**. Free-throw association study: **FT ANALYSIS COMPLETE**. Shot-context extension: **BLOCKED ON SOURCE VALIDATION**. Chemistry: **PAUSED / EXPLORATORY**. Market-probability comparison: **PLANNED, NOT YET EXECUTED**.

[Project status](docs/PROJECT_STATUS.md). This repository grants no rights to redistribute NBA source data; no market-profitability or causal claim is made.
