"""Release-authoring helper; writes V1 presentation only, never scientific outputs."""
from pathlib import Path
import csv,json
R=Path(__file__).resolve().parents[1]
E=R/'docs/stage6r2_evidence'
def rows(name):
 with (E/name).open() as f:return list(csv.DictReader(f))
def table(headers, values):return '| '+' | '.join(headers)+' |\n| '+' | '.join(['---']*len(headers))+' |\n'+'\n'.join('| '+' | '.join(map(str,row))+' |' for row in values)
cross=rows('cross_season_confirmation.csv'); metrics=rows('final_holdout_metrics.csv'); boots=rows('date_cluster_bootstrap.csv'); cal=rows('calibration_summary.csv')
keys=['raw_elo_log_loss','model_c_log_loss','delta_log_loss','raw_elo_brier','model_c_brier','delta_brier']
ct=table(['Season / role','Elo LL','C LL','Δ LL','Elo Brier','C Brier','Δ Brier'],[[r['split']]+[f'{float(r[k]):.5f}' for k in keys] for r in cross])
labels={'constant_home_prior':'Constant prior','raw_elo':'Raw Elo','basketball_features_logistic':'A · Features logistic','elo_logistic':'B · Elo logistic','features_plus_elo_logistic':'C · Features + Elo logistic','basketball_features_hgb':'D · Features HGB','features_plus_elo_hgb':'E · Features + Elo HGB'}
mt=table(['Frozen candidate','Games','Log loss','Brier','Accuracy','ROC-AUC'],[[labels[r['model']],r['n_games'],f"{float(r['log_loss']):.5f}",f"{float(r['brier_score']):.5f}",f"{float(r['accuracy']):.2%}",f"{float(r['roc_auc']):.3f}"] for r in metrics])
bt=table(['Paired loss (C − Elo)','Mean difference','Bootstrap SE','Descriptive 95% interval','Includes zero'],[[r['metric'],f"{float(r['observed_mean_difference']):.5f}",f"{float(r['bootstrap_standard_error']):.5f}",f"[{float(r['ci_lower_2_5']):.5f}, {float(r['ci_upper_97_5']):.5f}]",r['includes_zero']] for r in boots])
cl=table(['Model','Fixed-bin ECE','Mean predicted P(home win)','Observed home-win rate','Populated / sparse bins'],[[labels[r['model']],f"{float(r['fixed_bin_ece']):.5f}",f"{float(r['mean_predicted_probability']):.5f}",f"{float(r['observed_designated_home_win_rate']):.5f}",r['populated_bins']+' / '+r['bins_below_30']] for r in cal if r['model'] in ('raw_elo','features_plus_elo_logistic')])
with (R/'docs/stage1d_evidence/multiseason_quality_after_reconciliation.csv').open() as f: counts=list(csv.DictReader(f))
train=sum(int(x['accepted_games']) for x in counts[:8]); total=sum(int(x['accepted_games']) for x in counts)+int(metrics[0]['n_games'])
st=table(['Role','Seasons','Validated games'],[['Statistical training','2015–16 through 2022–23',f'{train:,}'],['Development validation','2023–24','1,230'],['Pre-holdout','2024–25','1,230'],['Final holdout','2025–26','1,230']])
finding='The Model C improvement over raw Elo had the same direction in three consecutive out-of-time seasons.'
caveat='The predeclared date-clustered descriptive bootstrap intervals on the final holdout included zero, so the final result is not presented as definitive statistical-significance evidence.'
readme=f'''# NBA Game Prediction V1 — Team-Level Probabilistic Modeling

A reproducible probabilistic forecasting study of NBA regular-season games, emphasizing temporal leakage control, model comparison and out-of-time validation. **V1 complete / frozen.**

## Key result

{finding}

{ct}

LL = log loss; Δ = Model C − raw Elo; lower losses are better. [Frozen full-precision source](docs/stage6r2_evidence/cross_season_confirmation.csv).

{caveat}

![Three-season probability losses](reports/figures/v1/three_season_comparison.png)

## Method and frozen model

```text
NBA historical games → leakage-safe pregame features → Elo baseline
→ regularized logistic / HGB → chronological validation
→ pre-holdout → final holdout
```

Predict P(designated home team wins). Model C (`features_plus_elo_logistic`) combines 32 team form/schedule features with frozen `elo_logit`: training-median imputation + missingness indicators → StandardScaler → L2 logistic regression (C=0.01, lbfgs, max_iter=5000, tol=1e-4, seed=0). Elo: initial 1500, scale 400, K=20, home advantage 50, offseason alpha=0.50.

## Evaluation and findings

Statistical training: **2015–16–2022–23**; development validation: **2023–24**; pre-holdout: **2024–25**; final holdout: **2025–26**. Statistical parameters stay frozen; Elo state advances after completed games.

- All 1,230 final-season games included; no warmup games dropped.
- Model C has the lowest final log loss/Brier among seven frozen candidates.
- Features alone and Elo-only logistic did not beat raw Elo on those losses; HGB did not beat C.
- Calibration is mixed: C has smaller mean bias but higher final fixed-bin ECE than Elo.

## Repository structure

```text
src/                 ingestion, features, baselines and guarded modeling
scripts/             historical build/stage entry points
tests/               ordinary safe development checks
data/                local cached and derived data
stage6*/             controlled final-evaluation and recovery code
docs/                V1 report, freeze manifest and historical evidence
reports/figures/      validated figures and V1 summary
stage7/              documentation-only integrity verifier
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
'''
report=f'''# NBA Game Prediction V1 — Team-Level Probabilistic Modeling

**Frozen research release.** This study asks whether explicit pregame team form and schedule information complements a chronological Elo baseline. All results below come from existing frozen evidence; this report introduces no new experiment.

## 1. Research question

Can a regularized model combining Elo and team-level basketball history improve the probability assigned to the designated home team winning an NBA regular-season game? Log loss and Brier score are primary because the task is probability estimation, not simply picking winners. Raw Elo is the primary benchmark; Model C is the preselected confirmatory candidate.

## 2. Why this problem is harder than it looks

A rolling statistic can silently include the game it predicts, and random splits can let future team strength inform earlier predictions. Team strength evolves, so earlier completed games may update pregame information while fitted statistical parameters stay fixed. Season openers lack rolling history; dropping them would change the evaluated population.

Designated home is also different from physical home advantage at neutral venues. Source matchup strings can be ambiguous. Finally, better classification accuracy does not necessarily mean better probability quality or calibration. Chronological evaluation, explicit missingness and a documented source-reconciliation process are therefore central to this study.

## 3. Dataset

{st}

Across these roles, {total:,} accepted games span eleven seasons. Most seasons contain 1,230 games; the historical scope includes 1,059 in 2019–20 and 1,080 in 2020–21. Counts come from [reconciled historical quality evidence](stage1d_evidence/multiseason_quality_after_reconciliation.csv) and the [final validation record](stage6r2_final_holdout_completion.md). The historical combined table ends at 2024–25; final-season artifacts remain separate.

The source is official NBA LeagueGameLog accessed through the maintained `nba_api` client. Scope is completed regular-season games, including Cup games that count toward the regular season, excluding the Cup championship and postseason. Canonical construction pairs two distinct team rows per game, checks dates, reciprocal opponents, designated sides, complementary W/L and score consistency. Scores and targets are separated from the predictor matrix; saved evaluation predictions explicitly contain targets and must not be treated as feature inputs.

Raw responses and provenance retain source parameters, retrieval timestamps and checksums. Explicit official ScheduleLeagueV2 mappings resolve five both-away pairs in each of 2024–25 and 2025–26, changing only canonical `is_home`; raw MATCHUP, scores and W/L remain intact. Neutral context is stored separately and is not a V1 feature. These are reviewed mappings, not a rule that every both-away pair must be neutral.

The final season contains all 1,230 games, 30 teams and 82 games per team, from 2025-10-21 through 2026-04-12, with zero rejected games after reconciliation. The prior 1,225-game partial set was never scored.

## 4. Feature design

The frozen 32-feature matrix contains home/away versions of 13 team-history measures plus six differences. Groups cover season-to-date games and win rate, recent five-/ten-game win form, point differential, points scored/allowed, rest days, back-to-back status and games in the preceding seven days. History resets each season. Full rolling windows are required; early missing values remain missing until training-fitted preprocessing handles them.

The [feature dictionary](stage1b_feature_dictionary.csv) and [availability contract](stage1b_availability_contract.md) define the complete V1 inputs. `elo_logit` is appended only for the frozen combined models. Identity fields, target-game scores, venue context and outcomes do not enter the feature allowlist.

## 5. Leakage controls

Shift-before-roll construction excludes the target game. Only strictly earlier calendar dates for the same team enter its history; ambiguous same-team dates fail validation. Independent prefix and target/future mutation tests verify that changing a target or future result cannot change an earlier pregame vector.

Expanding temporal folds preserve chronology. Each logistic fold fits its own median imputer, missingness indicators and scaler using training rows only; evaluation receives transformations without fitting. Outcomes are never imputed. Elo predicts before updating from the completed binary result.

The [sealed-evaluation hardening record](stage4a_sealed_evaluation_hardening.md) documents guarded loaders, explicit projections, checksums and disabled ordinary model execution. Historical structural tests had decoded 2024–25 scores before hardening; no performance from that season had selected the recipes. Those tests were replaced with synthetic fixtures. Accordingly, “sealed” means controlled performance access under the recorded protocol, not that source labels had never been processed.

The final attempt first stopped on TLS, then on five ambiguous home/away pairs. Authorized recovery reconciled those identities before first final scoring, without changing any recipe. [Stage 6](stage6_final_holdout_evaluation.md), [Stage 6R](stage6r_final_holdout_recovery.md) and [Stage 6R2](stage6r2_final_holdout_completion.md) retain the full access/stop/continuation history. This is a frozen performance evaluation completed through documented recovery, not a claim that the season remained physically untouched throughout.

## 6. Baselines

The constant prior is the original training home-win fraction, 5,437 / 9,519. It provides no game-specific discrimination. Raw Elo maintains evolving team ratings, predicts with designated-home advantage, and then updates only from completed wins/losses. Its frozen values are initial rating 1500, scale 400, K=20, H=50 and offseason alpha=0.50. There is no margin-of-victory or neutral-site adjustment.

Elo's parameters were selected within the training era; chronological state can subsequently evolve through completed evaluation games. State evolution does not retrain the statistical models. See [baseline evidence](stage2_probabilistic_baselines.md) and the [frozen recipes](stage5a_evidence/final_holdout_freeze.json).

## 7. Models

| Model | Inputs | Family |
| --- | --- | --- |
| A | 32 basketball features | L2 logistic |
| B | elo_logit | L2 logistic |
| C | 32 basketball features + elo_logit | L2 logistic |
| D | 32 basketball features | HistGradientBoosting |
| E | 32 basketball features + elo_logit | HistGradientBoosting |

All logistic models use C=0.01, L2, lbfgs, max_iter=5000, tol=1e-4, random_state=0, training-median imputation with missingness indicators and StandardScaler. HGB uses native missing-value handling with no imputer/scaler. D/E use learning_rate=0.03, max_leaf_nodes=7, max_iter=200, min_samples_leaf=30, max_bins=255, early_stopping=False and seed=0; L2 regularization is 5 for D and 1 for E.

Model C became the leading candidate on development-validation evidence and was frozen before pre-holdout and final performance openings. It was not selected after seeing the final season. The [seven-candidate freeze](stage4a_evidence/candidate_freeze.json) preserves all recipes and input allowlists; secondary candidates remain reported even when they do not improve the benchmark.

## 8. Experimental design

Statistical training is strictly 2015–16 through 2022–23 (9,519 games). Five expanding internal folds score 2018–19 through 2022–23, pooling 5,829 games with equal game weight. Selection uses training-era log loss, with predeclared tie-breaks; Elo's grid precedes logistic/HGB comparisons. Because Elo was selected across the training era, the subsequent internal stacking folds are development estimates, not an unbiased nested assessment of the whole selection procedure.

2023–24 is development validation and informed candidate choice. 2024–25 is the separately opened frozen pre-holdout. 2025–26 is the final performance evaluation under the [predeclared protocol](final_holdout_protocol_2025_26.md). These roles are not pooled or portrayed as three untouched confirmatory tests. Saved statistical estimators remain trained only through 2022–23; later seasons update completed-game history and Elo state, never coefficients or preprocessing.

## 9. Results

### Final 2025–26: all seven frozen candidates

{mt}

Source: [final-holdout metrics](stage6r2_evidence/final_holdout_metrics.csv). Every candidate covers the identical full season. C has the lowest two primary losses, descriptively; other metrics do not change its preselected role. Accuracy uses p ≥ 0.5; log loss uses natural logs, Brier uses original probabilities, and AUC handles ties.

### Three-season primary comparison

{ct}

Source: [full-precision cross-season table](stage6r2_evidence/cross_season_confirmation.csv). Δ = C − Elo; negative loss deltas favor C. The final reduction is smaller than in the earlier seasons. Rounding is presentation only.

![Frozen three-season comparison](../reports/figures/v1/three_season_comparison.png)

### Final calibration summary

{cl}

Source: [calibration summary](stage6r2_evidence/calibration_summary.csv). Sparse means a populated bin with fewer than 30 games. Section 12 explains why these diagnostics are mixed.

### Final uncertainty

{bt}

Source: [frozen date-cluster bootstrap](stage6r2_evidence/date_cluster_bootstrap.csv). The predeclared procedure uses 10,000 paired whole-date draws over 164 dates, seed 0, `default_rng`/PCG64, shared draws for both losses and game-weighted means. Standard errors use ddof=1; percentile intervals use linear quantiles. No bootstrap was rerun for this report. Minute floating-point differences between mean paired losses and differences of separately averaged losses reflect reduction order, not different results.

{caveat}

## 10. Main finding

{finding} Combining Elo with recent team-form/schedule information through regularized logistic regression improved both probability losses in the development, pre-holdout and final seasons examined. Basketball features alone did not outperform Elo on these losses. The nonlinear HGB alternatives did not outperform C. This supports a modest descriptive incremental-value finding within this protocol, not guaranteed future superiority or a causal attribution to individual features.

## 11. What did not work

Features-only A and D remained worse than raw Elo on log loss and Brier in the evaluated seasons. Elo-only logistic B did not improve raw Elo on those scores. Adding nonlinear flexibility did not make HGB outperform C. These comparisons matter: success against a constant prior alone would not establish added value beyond a strong chronological benchmark. No post-result retuning, feature selection or calibrator was introduced to rescue a weaker model.

## 12. Calibration

Probability losses and fixed-bin ECE do not measure the same property. In the final season, C has slightly higher ECE than Elo, but its mean predicted probability lies closer to the observed designated-home win rate. Thus C has smaller aggregate mean bias, not universally better calibration. ECE depends on the chosen ten bins, and sparse tail bins are noisy. Better Brier score combines calibration and discrimination effects rather than isolating calibration.

The existing pre-holdout figure illustrates the same distinction without creating a new diagnostic:

![Archived 2024–25 calibration, not final-holdout calibration](../reports/figures/stage5/calibration_2024_25.png)

Final bin-level evidence remains in [raw Elo bins](stage6r2_evidence/calibration_raw_elo.csv) and [Model C bins](stage6r2_evidence/calibration_model_c.csv). No probability recalibration was fitted.

## 13. Reproducibility and testing

Immutable raw caches, SHA-256 provenance, pinned requirements, outcome separation and explicit reconciliation layers make each dataset version traceable. Historical offline builds and deterministic replays are documented in their stage evidence. The final controlled preflight passed 178 tests: 138 ordinary development tests plus 40 synthetic final-stage tests. One cached final replay made zero fits/network calls and reproduced all 14 evaluation artifacts byte-for-byte; it is reproducibility evidence, not an independent test. See [final verification](stage6r2_evidence/final_verification.json) and [replay verification](stage6r2_evidence/replay_verification.json).

Stage 7 runs only the ordinary safe suite and documentation/hash checks. Its fresh results are in [Stage 7 verification](stage7_evidence/verification.json) and [test log](stage7_evidence/test_run.txt); archived model-execution tests are not enabled. The [reproduction guide](v1_reproduction.md) distinguishes safe current verification from historical commands that write artifacts or are disabled by today's sealed policy. Guards reduce accidental access through supported interfaces; they are not an operating-system security boundary.

The [V1 freeze manifest](v1_freeze_manifest.json) hashes the release documents, recipes, primary tables, uncertainty, figures, dependencies and current source checkpoint. Old manifests retain their historical meanings. Hashes prove byte identity, not source truth or external scientific validity.

## 14. Limitations

V1 uses aggregate team-level history only, without injuries, player availability, projected lineups or minutes. Historical neutral-site context is incomplete; designated home does not always imply home-court advantage. Dates establish earlier-game history but do not prove exact publication-time availability. Retrospective NBA corrections and schedule lookups can differ from what was available on the original game day.

There is only one final holdout season. The descriptive bootstrap intervals include zero, and date clustering leaves across-date and team/game dependence. Development-validation evidence informed candidate choice. Replays add no independent observations, and fixed-bin calibration has sparse-tail uncertainty. These constraints rule out definitive significance or broad generalization claims.

## 15. V2 roadmap — future work only

V2 may investigate player-aware modeling: injuries/availability, projected starters, expected minutes, player impact, roster changes/trades and lineup strength. Context extensions may include consistently audited neutral-site status, travel, altitude, richer rest/fatigue and matchup/style effects. Each needs a pregame availability contract, new versioned features, temporal validation and new future evaluation data. V1's opened seasons cannot become unseen again. None of these extensions is implemented or claimed here.

## 16. Conclusion

Frozen Model C improves log loss and Brier over raw Elo in the same direction across three consecutive out-of-time seasons, including all final-season games. The gain is modest and the final descriptive intervals include zero. V1 is complete as a reproducible team-level probability study; future modeling belongs to V2 or later.
'''
release=f'''# NBA Game Prediction V1 — release summary

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

Ready for review before a Git commit/push; no commit or push has been performed. The current local project directory has no Git metadata.
'''
repro='''# V1 reproduction and verification

Run commands from `basketball/nba/game-prediction/`. Keep the frozen tree intact.

## Safe current checks

```sh
.venv/bin/python -m unittest discover -s tests -v
python3 stage7/verify_v1.py
```

The existing project virtualenv activates the development policy through `sports_analytics_development_policy.pth`. Ordinary discovery uses synthetic/safe fixtures and does not enable archived model-execution tests. The standalone verifier uses Python's standard library solely to hash files, inspect release Markdown links and compare presentation tables with already-published aggregate CSVs. It does not import project model code, decode raw/Parquet outcomes, load estimators, fit, predict or score. Using a standard interpreter for opaque checksums is an integrity operation, not a holdout-execution escape hatch.

Dependencies are pinned in [requirements.txt](../requirements.txt). A recreated environment also needs the documented [startup policy](stage4a_sealed_evaluation_hardening.md); installing requirements alone does not install that policy. Preserve its source checkpoint in the V1 manifest. Raw caches and derived data are excluded by the umbrella `.gitignore`; they may be absent from a published checkout. Exact source snapshots may need reacquisition, and revised responses will not necessarily match historical hashes. The verifier reports missing files rather than claiming a complete reproduction.

## Cached builds: historical reference only

The original open-season commands were:

```sh
.venv/bin/python scripts/build_2023_24_games.py
.venv/bin/python scripts/build_2023_24_features.py
```

The first defaults to cache-only, but writes Stage 1A outputs/manifests. The second is offline and enforces the historical Stage 1B provenance/requirements gate, which does not match later dependency/code checkpoints automatically. **Do not run either against this frozen release.** Reconstructing a historical build requires a disposable copy, the exact period-specific environment/code/input snapshot and explicit handling of these historical gates; do not weaken them to make current code pass. No cache rebuild is necessary for release verification.

The reconciled multiseason build `scripts/build_reconciled_multiseason.py` additionally includes protected 2024–25 data and is disabled under ordinary development policy. Older Stage 1C builds represent a superseded quarantine state. Their audit documents remain historical evidence, not current runnable instructions.

## Open historical development stages: archived entry points

For traceability, these were the original 2023–24 development commands:

```sh
.venv/bin/python scripts/run_stage2_baselines.py
.venv/bin/python scripts/run_stage3_logistic.py
.venv/bin/python scripts/run_stage4_boosting.py
```

They performed fitting/searches and wrote scientific artifacts at the time. They are intentionally disabled under the current execution boundary, even though 2015–16–2023–24 is open historical data. They are **not supported rerun commands for frozen V1**. A future independently authorized development environment must version its provenance and preserve V1; there is no recommended force flag or policy bypass. This restriction is a reproducibility limitation, not evidence that those runs were reproduced during finalization.

## Final-stage evidence

The one-time pre-holdout/final openings used authorization ledgers, exact recipe/data hashes and controlled infrastructure. Their preparation/opening capabilities are consumed. Keep [Stage 5](stage5_preholdout_evaluation.md) and [Stage 6R2](stage6r2_final_holdout_completion.md) outputs archived; do not rerun their executors or old verification scripts into existing evidence directories. The saved byte-identical replay is already the deterministic reproduction record. No final-stage or archived model tests are enabled by the commands above.
'''
(R/'README.md').write_text(readme)
for name,content in [('v1_final_report.md',report),('v1_release_summary.md',release),('v1_reproduction.md',repro)]: (R/'docs'/name).write_text(content)
(R/'../../../README.md').write_text('''# Sports Analytics

A collection of reproducible sports analytics research projects, emphasizing data quality, temporal validation and evidence-based model comparison.

```text
Basketball
└── NBA
    ├── Game Prediction — V1 complete
    └── Chemistry — planned / paused
Soccer — future work
```

## NBA Game Prediction

[**NBA Game Prediction V1 — Team-Level Probabilistic Modeling**](basketball/nba/game-prediction/README.md) is complete and frozen: probabilistic regular-season prediction using Elo plus leakage-safe pregame team features. The study compares regularized logistic and boosting models across chronological development, pre-holdout and final evaluation seasons.

[Technical report](basketball/nba/game-prediction/docs/v1_final_report.md) · [Release summary](basketball/nba/game-prediction/docs/v1_release_summary.md)

Future player-aware modeling belongs to V2. NBA Chemistry remains planned/paused; soccer is future work. Historical audit records remain alongside each project's current documentation. Local raw/derived data and environments are excluded from Git.
''')
(R/'docs/stage7_evidence/table_sources.json').write_text(json.dumps({'three_season':{'source':'docs/stage6r2_evidence/cross_season_confirmation.csv','markdown':ct},'final_metrics':{'source':'docs/stage6r2_evidence/final_holdout_metrics.csv','markdown':mt},'uncertainty':{'source':'docs/stage6r2_evidence/date_cluster_bootstrap.csv','markdown':bt},'calibration':{'source':'docs/stage6r2_evidence/calibration_summary.csv','markdown':cl}},indent=2)+'\n')
print('Created V1 documents and updated umbrella README')
