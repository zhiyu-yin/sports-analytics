# Stage 4A — Manuscript Freeze & Main Tables/Figures

## 1. Objective

Freeze the scientific story and assemble tables, figures, evidence mapping and outlines from existing evidence. No new scientific analysis is performed.

## 2. Why model development stops here

More elaborate hierarchical joint models of free-throw opportunity and accuracy were investigated during model development. These models showed posterior predictive misspecification or weak identification among opportunity and player-level latent effects, with predictive checks withheld when sampling failed. They were therefore not used for primary scientific inference. Their adequacy failures remain part of the scientific history. The requested primary target is a transparent working association, not a claim that the joint opportunity process has been solved.

## 3. Frozen primary scientific result

The primary replication panel comprised 13 seasons, 4,117 player-seasons and 857 accounting players. Of these, 3,980 positive-FTA rows from 835 players contributed 469,099 attempts; 137 zero-FTA rows remained in accounting. The 2013-14 development season was excluded.

The primary grouped-binomial estimate was beta=-0.03045199 per residual inch (OR=0.970007); the 95% player-cluster CR1 interval was [-0.05228116, -0.00862282] and the two-sided p-value was 0.00625365. The player-bootstrap percentile interval was [-0.05433056, -0.01047528]. Both intervals describe uncertainty around the same original primary point estimate.

Each additional inch of wingspan beyond that expected for height was associated with approximately 3% lower adjusted odds of a made free throw. Odds are not percentage points. This is a between-player association and does not represent changing one player's anatomy.

## 4. Frozen robustness package

Secondary beta-binomial robustness retained the original full-sample estimate beta=-0.03342554 (OR=0.967127; rho=0.03028531). Its remediated player-bootstrap 95% percentile interval was [-0.05044245, -0.01701569], with 0/2000 failures. Historical Stage 3J remains EXECUTION FAIL; the separate Stage 3J-R decision is NUMERICAL REMEDIATION PASS. J2 remains secondary.

All first-season, player-balanced, attempt-threshold, full-panel and alternate-exposure results retain their frozen definitions and units. Across all 13 chronological leave-one-season-out omissions, beta ranged from -0.03263770 to -0.02846941 (median -0.03019642); there were 0 sign reversals. No single omitted season reversed the direction; this is sensitivity evidence within the same panel, not independent replication.

## 5. Development vs replication distinction

2013-14 is development and excluded from primary; players may overlap. Out-of-season replication, not independent-player replication. The primary seasons are 2010-11, 2011-12, 2012-13, 2014-15, 2015-16, 2016-17, 2017-18, 2018-19, 2019-20, 2020-21, 2021-22, 2022-23, 2023-24.

## 6. Main scientific claim

Greater residual wingspan was associated with lower free-throw accuracy in NBA players with available combine measurements. The negative association was observed in the 2013-14 development analysis and persisted in a 13-season replication panel excluding that season, with similar estimates across player-clustered, beta-binomial, first-season-only, player-balanced, attempt-threshold and leave-one-season-out analyses.

## 7. Main limitations

Usable-measurement coverage ranged from 51.0% to 67.3% across the approved season series. Measured players are not a random sample of all NBA players. Combine participation, measurement availability and completeness, NBA survival, playing opportunity and shooting opportunity may select the sample; the model does not correct this selection. Unmeasured skill, training and current role remain possible sources of confounding.

Free-throw attempt volume was used as the grouped-binomial denominator rather than as a predictor. Previous model-adequacy analyses indicated that attempt volume is informative about player-level shooting and opportunity structure. Consequently, the primary model should be interpreted as a working conditional association model rather than a complete generative model of shooting opportunity. Player-clustered uncertainty does not repair conditional-mean misspecification.

Residual wingspan is time invariant, so its coefficient is identified between players. Repeated seasons provide additional outcome information and dependence-aware uncertainty, but not within-player exposure identification. Player clustering is not adjustment for player fixed effects or unmeasured player ability. Frozen geometry uncertainty and measurement error also remain.

## 8. Main manuscript content

Three tables, four figures, source-validation summary, primary model and both uncertainty methods, predeclared robustness, and prominent limitations. Main inclusion does not make a sensitivity a primary analysis. See manuscript/content_disposition.csv.

## 9. Supplement content

Detailed source reconciliation and combine validation; development model ladder and robust/influence results; minute-display amendment; alternate exposures; complete leave-one-season-out results; beta-binomial numerical-remediation details; selected complex-model adequacy evidence; attempt-volume diagnostic. See manuscript/supplement_plan.md.

## 10. Audit-only content

Execution logs, usage interruptions, failed raw traces, implementation debugging, temporary checker failures and detailed computational reparameterization mechanics. Failed/sealed scientific coefficients and the old invalid successful-only J2 interval are NOT_USE. All historical artifacts remain preserved.

## 11. Table inventory

Main Table 1: sample characteristics. Main Table 2: original primary estimate with CR1 and bootstrap intervals. Main Table 3: predeclared robustness with remediated secondary beta-binomial interval. Supplement: complete leave-one-season-out table and alternate exposures. Exact CSVs and readable Markdown tables are in manuscript/. Table 1 anthropometrics use unique players; its position distribution uses accounting player-seasons. Position denominators are recovered from frozen observed totals/means, not new data aggregation.

## 12. Figure inventory

Figure 1: observational study flow. Figure 2: primary/robustness forest on beta scale. Figure 3: chronological leave-one-season-out estimates and cluster intervals. Figure 4: approved selection coverage, development labeled. Supplement Figure 1: existing observed/fitted pooled rates by FTA bin. Each has vector PDF and high-resolution PNG in reports/manuscript/. The requested replication exposure-outcome descriptive figure is REQUIRES FUTURE ANALYSIS: no frozen replication bins exist; development bins are not substituted.

## 13. Abstract skeleton

See manuscript/abstract_skeleton.md: Background, Methods, Results and Conclusions. Not journal-specific and not a completed manuscript.

## 14. Methods structure

See manuscript/methods_outline.md: study design; data sources; measurements; exposure; outcome; population; validation; development/replication split; primary model; cluster covariance; player bootstrap; robustness; missing/zero handling; model history; selection/generalizability; software/reproducibility.

## 15. Results structure

See manuscript/results_outline.md: population; exposure distribution; primary association; bootstrap; robustness; leave-one-season-out; full secondary panel; coverage; diagnostic limitation.

## 16. Discussion structure

See manuscript/discussion_outline.md: principal finding; development/replication comparison; untested hypotheses; selection/role confounding; informative opportunity; causal limits; strengths; limitations; future research.

## 17. Evidence map

manuscript/evidence_map.csv links quantitative fields and approved statements to artifacts, locations and SHA-256 values. numeric_lineage.json binds every numeric main table and figure-data cell to a source field and declared display operation. prose_lineage.json records approved paragraphs and their sources. main/supplement/audit categories are recorded separately from manuscript roles; historical_artifact_disposition.csv covers the complete protected inventory.

## 18. Manuscript freeze

manuscript/manuscript_freeze.json was persisted before drafting these prose-ready outlines. Its receipt records 66a07aa5c826ac34f7aa8a09ee9565312e350e676d0965bb7f2040b02f7c6def. Primary result hash: 79b8f461efcc61e0a6e3ff33728fa0d0019839aae03b9809d530f8c9b6906e02. Remediated J2 summary hash: 6933e3ec7bc9bef8b6ec56f141c2bfb44411ba4cfb6865fad10d387827464882. Historical decisions and both panel hashes are separately retained.

## 19. Reproducibility

Run only the Stage 4A builders/verifier documented in manuscript/README.md. No historical builder or analytical fit was executed. Existing environments were reused. Frozen summaries are decoded; analytical panels and raw traces are hashed only. All 19939 protected historical files passed the pre-freeze check. Final tests, figure visual QA and build hashes are recorded in manuscript/.

## 20. Stage 4A decision

PASS — MANUSCRIPT ANALYSIS FROZEN. Checks: 20/20 passed, 0 failures, 0 errors, 0 skips. All historical evidence is preserved when check A passes. The descriptive exposure-outcome figure remains explicitly deferred, not fabricated.

## 21. Recommended Stage 4B

Draft the full academic manuscript strictly from this frozen package, retaining development/replication distinctions, numerical-remediation disclosure and limitations. Journal targeting and submission would require separate authorization. Stage 4B has not started. No commit, push or submission occurred.

