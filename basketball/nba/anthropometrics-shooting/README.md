# NBA Anthropometrics and Shooting

Is wingspan relative to height associated with NBA free-throw accuracy?

**Completed FT association study / shot-context extension blocked on source validation.** The manuscript analysis package is frozen; a full manuscript draft has not been started.

## Main result

The 13-season replication panel excludes the 2013–14 development season and retains 4,117 player-season accounting rows from 857 players. Positive-attempt inference uses 3,980 rows from 835 players and 469,099 free-throw attempts.

The grouped-binomial model estimates **β = −0.030452 per residual-wingspan inch**, or **OR = 0.9700**. The 95% player-cluster interval is **[−0.05228, −0.00862]**; the 2,000-replicate player-bootstrap interval is **[−0.05433, −0.01048]**, both on the beta scale. This corresponds to approximately 3% lower adjusted odds per inch, not a three-percentage-point change in accuracy.

The frozen exposure is wingspan minus `(4.574910520685837 + 1.0013410045156863 × barefoot height)`, measured in inches. Adjustment uses barefoot height, original combine position and season. Repeated seasons are clustered by player. The robustness package includes beta-binomial, chronological first-season-only, player-balanced, attempt-threshold and leave-one-season-out analyses. The beta-binomial bootstrap required a documented numerical remedy; its historical failure and subsequent successful remediation remain separate records.

## Interpretation and limits

This is an observational, between-player association among players with validated combine measurements. It does not identify a causal anatomical effect or a within-player change. Measured-player selection, unmeasured ability/role, measurement error and informative free-throw opportunity remain limitations. Player-cluster uncertainty does not fix conditional-mean misspecification. Development and replication seasons can contain the same players.

## Source-validation stop

The planned restricted-area finishing, mid-range and three-point extension stopped before protocol freeze or model fitting. Its audit found 905 zone/shot-type conflicts across all 14 candidate seasons. No secondary coefficients were estimated. **Analysis stopped when source validation failed rather than forcing a result.**

[Stage 4A manuscript freeze](docs/stage4a_manuscript_freeze_report.md) · [Stage 4X source-validation report](docs/stage4x_shot_type_specificity.md)

## What this project demonstrates

- Data provenance and deterministic identity validation.
- Prospective protocol discipline and preserved failed analyses.
- Grouped count models and clustered inference.
- Player bootstrap and numerical validation.
- Willingness to stop when source validity fails.

## Evidence and reproducibility

[Primary inference](docs/stage3j_simplified_multiseason_inference.md) · [Numerical remediation](docs/stage3jr_beta_binomial_numerical_remediation.md) · [Frozen manuscript package](docs/manuscript/README.md)

Stage-specific dependency files and scripts are retained for traceability. Raw data, derived panels, environments and sampler traces are excluded from Git. Full historical hash checks require the original local archive; they are not fresh-checkout tests. Do not regenerate frozen analyses or overwrite their outputs. The repository-root `python3 scripts/verify_portfolio.py` checks published links and evidence integrity without fitting models.

The previous Stage 0B README is retained byte-for-byte in the [publication archive](../../../docs/publication/shooting_README_before.md). Its dated blocked status and commands describe that historical stage, not the completed study. See [publication notes](../../../docs/publication/README.md) for the explicit presentation-only hash exception; frozen scientific manifests are unchanged.
