# Prediction-Market Research Portfolio

## 1. Why this repository is relevant to prediction markets

Prediction-market research requires credible probabilities, appropriate benchmarks and honest uncertainty. This repository demonstrates those skills through NBA win-probability forecasting and a separate observational inference study. It provides research infrastructure and evaluation discipline; it does not claim a profitable trading strategy or measured market edge.

## 2. NBA win-probability forecasting

The flagship study estimates pregame home-win probabilities using official NBA game data: 13,209 accepted regular-season games spanning 2015–16 through 2025–26. Team form, scoring history, rest and schedule features use only earlier completed games. Elo provides a strong chronological baseline; regularized logistic regression and histogram gradient boosting test whether additional information helps.

The frozen combined logistic candidate had final-holdout log loss 0.601923 and Brier score 0.207053, compared with Elo's 0.604644 and 0.208328. Accuracy was 0.676423 versus 0.674797, and AUC 0.731559 versus 0.730759. These are modest observed differences across 1,230 games, not evidence of a tradeable advantage.

## 3. Probability calibration and scoring

Log loss and Brier score evaluate probability quality rather than only the winning label. Accuracy and AUC provide complementary classification and ranking views. Calibration diagnostics check whether predicted frequencies match outcomes. The combined model had smaller aggregate mean bias but higher fixed-bin calibration error than Elo on the final season: calibration was mixed, not uniformly improved. No post-holdout recalibration was fitted.

## 4. Baseline discipline

Raw Elo, a constant prior and five logistic/boosting candidates were reported. The combined logistic model was selected before final performance access and achieved the best observed final log loss and Brier score among the frozen candidates. Models that did not improve the benchmark remain in the report. Small gains over a credible baseline warrant more scrutiny than large gains over an artificially weak one.

## 5. Out-of-time validation

Statistical training covers 2015–16 through 2022–23; 2023–24 is development validation; 2024–25 is a pre-holdout; 2025–26 is the final holdout. These roles are distinct: development validation informed candidate selection. Features shift before rolling, preprocessing fits on training data, and Elo predicts before updating. Statistical coefficients remain frozen while completed-game history evolves. Source recovery and controlled holdout access are documented in the audit trail.

## 6. Uncertainty and robustness

A predeclared paired date-cluster bootstrap used 10,000 draws for final loss comparisons. Its intervals included zero, so statistically significant superiority over Elo is not established. Shared dates are resampled together, but remaining dependence and a single final season limit generalization. The separate shooting study demonstrates player-cluster covariance, player bootstrap, beta-binomial numerical validation and sensitivity analyses appropriate to repeated player observations.

## 7. Research/data-quality judgment

The free-throw study found a negative residual-wingspan association in a 13-season replication panel; it makes no causal claim. A planned shot-context extension stopped at source validation after zone/shot-type inconsistencies appeared in every candidate season. Analysis stopped when source validation failed rather than forcing a result. Failed models, numerical remediation, limitations and source disagreements remain preserved alongside approved results.

## 8. Next planned extension: model probabilities vs market-implied probabilities

The next natural extension is to compare model probabilities with validated historical market-implied probabilities, evaluate calibration and disagreement, and test whether the model contains incremental information beyond market consensus.

This work is **planned, not yet executed**. It would require timestamped pregame prices, event/contract matching, appropriate treatment of bookmaker margin where relevant, and a new frozen temporal evaluation protocol. Profitability would require additional execution-cost, liquidity and settlement analysis; none is claimed here.

[Forecasting project](../basketball/nba/game-prediction/README.md) · [Frozen report](../basketball/nba/game-prediction/docs/v1_final_report.md) · [Shooting study](../basketball/nba/anthropometrics-shooting/README.md)
