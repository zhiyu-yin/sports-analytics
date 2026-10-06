# Methods outline and prose-ready summaries

## Study design

Observational multiseason study of the adjusted association between residual wingspan and free-throw accuracy. The simplified analysis protocol was prospective to its own fitting, after earlier source audits and model-development analyses; it was not registration before all historical data inspection. Residual wingspan is time invariant, so its coefficient is identified between players. Repeated seasons provide additional outcome information and dependence-aware uncertainty, but not within-player exposure identification. Player clustering is not adjustment for player fixed effects or unmeasured player ability. [M01]

## Data sources

Pinned combine and player-game archives supplied measurements and regular-season shooting counts. Official NBA historical tables and selected official player/team records supported source validation. Source snapshots, retrieval metadata and checksums remain archived; no live-source refresh was performed for manuscript assembly. [M02]

## Anthropometric measurements

One fixed measurement vector per player was selected: the latest complete, plausible, officially supported, non-quarantined record on or before the start year of the first observed positive-minute NBA season in the archive. The first observed season may be left-truncated and is not necessarily the player's NBA debut. Barefoot height and wingspan use inches from the same record; no shoe-height substitution or outcome-guided measurement selection was used. [M03]

## Exposure definition

Residual wingspan = wingspan - (4.574910520685837 + 1.0013410045156863 x barefoot height), in inches. The outcome-independent geometric reference fit was frozen in the development stage and reused unchanged. The reference included 960 usable positive-ID combine participants through 2013, regardless of NBA survival or FT attempts. Inference conditions on this fitted transformation and does not propagate its estimation uncertainty. [M04]

## Free-throw outcome

The grouped response was [FTM, FTA-FTM]. Makes and attempts were summed across recorded appearances; percentages were not averaged. Positive total season minutes defined eligibility. Recorded zero-minute appearances remained distinct from DNP/empty-minute records and contributed recorded counts. [M05]

## Study population

The primary replication panel comprised 13 seasons, 4,117 player-seasons and 857 accounting players. Of these, 3,980 positive-FTA rows from 835 players contributed 469,099 attempts; 137 zero-FTA rows remained in accounting. The 2013-14 development season was excluded. [M06]

## Source validation

Anthropometric records came from a pinned secondary archive and were corroborated against official NBA historical combine tables. In the predeclared validation sample, all 45/45 same-player, same-year barefoot-height and wingspan pairs agreed exactly. A broader historical census included 970 rows and 965 complete pairs with exact core agreement; the frozen geometric reference comprised 960 positive-ID participants. Later official combine validation covered 582 records, including 543 complete pairs and four versioned corrections. Analytical linkage used exact positive NBA IDs; source-table name corroboration did not authorize fuzzy analytical joins. [M07]

## Development vs replication split

The 2013-14 season supplied development evidence. Primary replication used 2010-11, 2011-12, 2012-13 and 2014-15 through 2023-24. Players may overlap development data; the appropriate description is out-of-season replication or replication across additional seasons. The secondary full panel includes the development season and is not independent replication. [M08]

## Primary statistical model

logit(p_it) = intercept + beta_RW residual_wingspan_i + beta_H barefoot_height_i + original_combine_position_i + season_t. Barefoot height remains in raw inches. Original hybrid categories remain distinct; missing position is unknown. C and 2010-11 are reference levels. The primary model has no player random intercept, player fixed effects, opportunity component, FTA predictor or MIN predictor. With mean misspecification, the coefficient is a working-logit projection dependent on the observed attempt and covariate distribution. [M09]

## Player-cluster covariance

Player scores are sums of grouped-row scores X_it(FTM_it-FTA_it*p_it). Sandwich covariance uses the inverse grouped-binomial information and player-summed outer products, with CR1 correction G/(G-1) x (N-1)/(N-K). Here G=835 contributing players, N=3,980 positive-FTA rows and K=28 estimable columns. Normal-Wald intervals and two-sided normal p-values were predeclared. Zero-only players supply no score clusters. [M10]

## Player bootstrap

The primary bootstrap used exactly 2,000 draws of 857 accounting players with replacement, carrying all seasons for each selected player and assigning duplicate copies distinct cluster identities. Zero-FTA rows remained in resampling accounting. No residualization was refitted. Percentile intervals used linear interpolation at the 2.5th and 97.5th percentiles. Bootstrap means are descriptive summaries; manuscript points remain the original fitted coefficients. Empirical fractions below zero are not posterior probabilities. [M11]

## Robustness analyses

The predeclared package retained beta-binomial regression with the same mean formula; earliest eligible replication season per player with HC1; player-balanced 1/T_i likelihood weights; FTA >=50 and >=100 subsets; each season omitted once; and a full secondary panel including 2013-14 development. T_i includes accounting seasons with zero attempts. Equal aggregate season weights do not equalize player information because attempt counts still differ. Alternate advantage and ratio exposures remain supplementary, with residual wingspan primary. [M12]

The secondary beta-binomial player bootstrap required numerical remediation. A prospectively amended numerical ladder was applied uniformly to the exact original scheduled samples with the same likelihood, data and numerical acceptance gates. The original failed execution and the separate numerical-remediation pass are both disclosed. No failed-only percentile interval is used. [M13]

## Missing / zero-attempt handling

Incomplete or unsupported measurement pairs and unresolved name-only identity links were not admitted under frozen eligibility. Missing combine position is retained as unknown. No FT accuracy is imputed for zero attempts. Zero-FTA rows remain in accounting and bootstrap membership, while only positive-FTA rows inform the accuracy likelihood. In first-season sensitivity, an earliest eligible zero-attempt season is not replaced by a later positive season. [M14]

## Model-development history

More elaborate hierarchical joint models of free-throw opportunity and accuracy were investigated during model development. These models showed posterior predictive misspecification or weak identification among opportunity and player-level latent effects, with predictive checks withheld when sampling failed. They were therefore not used for primary scientific inference. Their adequacy failures remain part of the scientific history. [M15]

## Selection / generalizability

Usable-measurement coverage ranged from 51.0% to 67.3% across the approved season series. Measured players are not a random sample of all NBA players. Combine participation, measurement availability and completeness, NBA survival, playing opportunity and shooting opportunity may select the sample; the model does not correct this selection. Unmeasured skill, training and current role remain possible sources of confounding. Free-throw attempt volume was used as the grouped-binomial denominator rather than as a predictor. Previous model-adequacy analyses indicated that attempt volume is informative about player-level shooting and opportunity structure. Consequently, the primary model should be interpreted as a working conditional association model rather than a complete generative model of shooting opportunity. Player-clustered uncertainty does not repair conditional-mean misspecification. [M16]

## Software / reproducibility

Frozen analyses used Python 3.10.8, statsmodels 0.14.5, NumPy 2.2.6, SciPy 1.15.3, pandas 2.2.3 and pyarrow 21.0.0. The isolated environment and archived source, data, code, protocols and results support reproduction. Stage 4A only reads frozen summaries, formats evidence and renders matplotlib figures; it does not rerun fitting or bootstrap procedures. Manuscript freeze and build manifests link every displayed result to its source. [M17]


Evidence identifiers in brackets resolve to evidence_map.csv. This is a frozen assembly outline, not a completed manuscript or submission.
