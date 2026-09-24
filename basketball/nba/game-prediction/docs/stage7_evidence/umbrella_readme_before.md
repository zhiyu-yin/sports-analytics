# Sports Analytics

A collection of reproducible sports analytics projects focused on probabilistic prediction, decision-making, player interaction, and team dynamics.

- **Basketball / NBA / Game Prediction — active:** Stage 1B complete for the 2023–24 regular season: validated game history and leakage-tested pregame features. No models have been trained.
- **Basketball / NBA / Chemistry — planned / paused.**
- **Soccer — future work.**

`shared/` is reserved for utilities when cross-project needs arise.

Start with the [Stage 0 data audit](basketball/nba/game-prediction/docs/stage0_data_audit.md), including access failures, recorded sample evidence, and the proposed temporal evaluation design.

See the [Stage 1A ingestion report](basketball/nba/game-prediction/docs/stage1a_ingestion.md) for provenance, validation results, and offline reproduction commands.

See the [Stage 1B feature-engine report](basketball/nba/game-prediction/docs/stage1b_feature_engine.md) for feature definitions, leakage tests, and expected warmup missingness.
