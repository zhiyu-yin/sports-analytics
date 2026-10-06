# Stage 4X — Shot-type specificity extension

**SHOT-TYPE EXTENSION BLOCKED**

## 1. Scientific motivation

Assess whether the relative-wingspan association varies across shooting contexts while preserving FT as the sole manuscript primary.

## 2. Data source

Stage 4X-A: **SHOT DATA FEASIBILITY BLOCKED**. Overall: **SHOT-TYPE EXTENSION BLOCKED**.

Audited 2,852,950 candidate shot records across 14 seasons (2010–11 through 2023–24). All 14 have zone/shot-type inconsistencies: 905 records total. SHOT_TYPE-derived totals disagree with validated season totals in 133 player-seasons for 3PM and 336 for 3PA. Zone-derived totals including Backcourt disagree in 404 and 988 player-seasons, respectively. These are separate counts, not a union.

For 2023–24, SHOT_TYPE-derived counts agree exactly, but ten Above the Break 3 records are marked 2PT and eleven Mid-Range records are marked 3PT. Agreement of aggregate totals cannot validate these zone assignments. No candidate season is approved. No scientific panel exists; analysis players, player-seasons and attempts are unavailable, not zero. Candidate counts are retained separately in candidate_outcome_counts.csv.

There are 89 identical-record excess rows (175 rows in groups), without event IDs. These may include genuine repeated tip attempts; none were deleted. Player-game differences and all conflicting records are exported for independent resolution.

Exact-ID candidate linkage: 1696 unique shot players; 863 matched (50.88%); 833 unmatched; zero ambiguous IDs or fuzzy links. A matched ID does not imply inclusion in an approved analysis population.

The proposed, unvalidated mapping is Restricted Area → rim finishing; Mid-Range → mid-range; Left Corner 3, Right Corner 3 and Above the Break 3 → ordinary three-point. Paint Non-RA and Backcourt remain separate. No post-result mapping exists because no coefficients were fitted. No Stage4X-B protocol was frozen.


## 3. Source validation

BLOCKED. Full checks A–J and exact counts are in stage4x_evidence/shot_source_validation.json. No repair was applied. The historical official census and secondary player-game reconciliation have different validation scopes; see source provenance.

## 4. Eligible seasons

None approved. The candidate period is 2010–11 through 2023–24. A shorter contiguous period cannot bypass conflicts present in every season.

## 5. Player linkage

Deterministic ID linkage only; per-season records and matched/unmatched statuses are in shot_player_linkage.csv. No unvalidated fuzzy match entered a panel.

## 6. Shot-zone definitions

Candidate mapping only, documented in shot_zone_mapping_protocol.json. Restricted Area; Mid-Range; three ordinary 3PT zones. Paint Non-RA and Backcourt excluded. Labels are unresolved and not approved.

## 7. Frozen protocol

NOT_RUN. Phase B is barred by the Phase A gate. The exposure remains wingspan − (4.574910520685837 + 1.0013410045156863 × barefoot height), in inches. No residualization was refitted.

## 8. Restricted-area result

NOT_RUN; beta, OR, CI, players, player-seasons and analysis attempts unavailable.

## 9. Mid-range result

NOT_RUN; beta, OR, CI, players, player-seasons and analysis attempts unavailable.

## 10. Three-point result

NOT_RUN; beta, OR, CI, players, player-seasons and analysis attempts unavailable. Aggregate 3P totals cannot substitute for the requested zone-defined outcome.

## 11. Player bootstrap

NOT_RUN for all three outcomes. No bootstrap draws or replacement replicates.

## 12. Multiplicity-adjusted inference

NOT_RUN. Future approved protocol must apply Holm to exactly the three secondary residual-wingspan tests, excluding primary FT.

## 13. First-season robustness

NOT_RUN. No eligible chronological season set established.

## 14. Leave-one-season-out

NOT_RUN. No sign or stability claims.

## 15. Attempt-threshold sensitivity

NOT_RUN. No thresholds or volume bins selected from results.

## 16. Common-support comparison

NOT_RUN. No common-support FT result produced.

## 17. Formal heterogeneity test

FORMAL HETEROGENEITY TEST NOT RUN. Explicit JSON record retained.

## 18. Cross-shot-type comparison

NOT_RUN. A forest plot would falsely imply fitted secondary results; no figure produced.

## 19. Shot-volume diagnostics

NOT_RUN. Candidate counts are source-audit quantities only; no fitted rates or exposure-bin figure.

## 20. Selection / role limitations

Even after source validation, shot selection, offensive role, defensive pressure, shot creation, catch-and-shoot versus off-dribble mix, within-zone distance, team system, playing time and player skill can confound or select the observations. Rim finishing includes dunks, layups, tips, athleticism and contact; it is not pure shooting touch. Mid-range likewise mixes distance and creation contexts.

## 21. Relationship to frozen FT result

Frozen primary J1 beta = −0.030451990605906667 per inch; OR = 0.9700070003976983; nominal player-CR1 beta CI [−0.05228115912326727, −0.008622822088546062]. Its 2,000-player-bootstrap percentile CI is [−0.054330558012167116, −0.010475281001090258]. These are historical reference values, not new Stage4X fits. FT retains its 13-season primary population. Original 2013–14 FT development status remains; it is not automatically development for unexamined secondary shot outcomes.

## 22. Manuscript implications

No cross-context pattern classification can be made. Consistency, specificity and mixed/uncertain empirical patterns all require results. No manuscript draft, tables, figures, evidence map or freeze changed.

## 23. What is NOT established

No secondary effect, coefficient difference, distance gradient, biomechanical mechanism or causal effect is established. Blockage does not mean null associations or absence of available data elsewhere.

## 24. Reproducibility

Run scripts/stage4x_feasibility.py and scripts/stage4x_finish_audit.py with the existing .venv after retaining source ZIPs. Source hashes, exact disagreements, candidate coverage, linkage and preservation hashes are in stage4x_evidence. Run scripts/test_stage4x.py for stopping-rule and immutability checks. Verification completed: 12/12 executable audit tests passed, with zero failures or errors; all 19,993 protected historical artifacts matched their hashes. Scientific prerequisites are reported separately: source gate F is BLOCKED and analysis-dependent requirements remain NOT_RUN.

## 25. Stage 4X decision

SHOT-TYPE EXTENSION BLOCKED. Stop at 4X-A. Phases B–D, all three outcomes and all dependent sensitivities remain NOT_RUN. No commit or push.
