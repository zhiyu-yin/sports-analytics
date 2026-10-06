# Results outline and prose-ready summaries

## Study population

The primary replication panel comprised 13 seasons, 4,117 player-seasons and 857 accounting players. Of these, 3,980 positive-FTA rows from 835 players contributed 469,099 attempts; 137 zero-FTA rows remained in accounting. The 2013-14 development season was excluded. Table 1 distinguishes accounting and likelihood denominators; Figure 1 shows the source-to-panel flow. [R01]

## Exposure distribution

Across the 857 unique accounting players, barefoot height was 77.53 inches (SD 3.24), wingspan 82.47 (SD 3.90), and residual wingspan 0.26 (SD 2.12). FTA per accounting player-season had median 75 and quartiles 25 and 160. Position counts in Table 1 describe player-seasons, not independent players. [R02]

## Primary association

The primary grouped-binomial estimate was beta=-0.03045199 per residual inch (OR=0.970007); the 95% player-cluster CR1 interval was [-0.05228116, -0.00862282] and the two-sided p-value was 0.00625365. The player-bootstrap percentile interval was [-0.05433056, -0.01047528]. Both intervals describe uncertainty around the same original primary point estimate. Each additional inch of wingspan beyond that expected for height was associated with approximately 3% lower adjusted odds of a made free throw. Odds are not percentage points. This is a between-player association and does not represent changing one player's anatomy. [R03]

## Player-bootstrap uncertainty

All 2,000 predeclared primary bootstrap fits succeeded. The bootstrap mean was -0.03175031, SD 0.01147371, and fraction of coefficients below zero 0.9995. The original estimate remains the point displayed in Table 2 and Figure 2; the bootstrap mean is not a second primary estimator. [R04]

## Robustness analyses

Secondary beta-binomial robustness retained the original full-sample estimate beta=-0.03342554 (OR=0.967127; rho=0.03028531). Its remediated player-bootstrap 95% percentile interval was [-0.05044245, -0.01701569], with 0/2000 failures. Historical Stage 3J remains EXECUTION FAIL; the separate Stage 3J-R decision is NUMERICAL REMEDIATION PASS. J2 remains secondary. [R05]

First eligible season only: beta=-0.02768679, 95% interval [-0.04911563, -0.00625796]. This is a predeclared sensitivity with a distinct sample or weighting target, not a replacement for the primary model. [R06]

Player-balanced weighting: beta=-0.02768226, 95% interval [-0.04636503, -0.00899948]. This is a predeclared sensitivity with a distinct sample or weighting target, not a replacement for the primary model. [R07]

At the frozen FTA >=50 threshold, beta=-0.03144334; at FTA >=100, beta=-0.03488195. Both estimates remained negative. Their full intervals and sample sizes are retained in Table 3. Thresholds change the secondary population and do not redefine primary eligibility. [R08]

Supplementary exposure analyses retained the negative direction. Wingspan advantage is an algebraic reparameterization of residual wingspan when height and intercept are included, so its agreement is not independent evidence. The ratio result is displayed per 0.01 increase; residual wingspan remains primary. [R09]

## Leave-one-season-out

Across all 13 chronological leave-one-season-out omissions, beta ranged from -0.03263770 to -0.02846941 (median -0.03019642); there were 0 sign reversals. No single omitted season reversed the direction; this is sensitivity evidence within the same panel, not independent replication. [R10]

## Secondary full panel

The full panel included the 2013-14 development season: 14 seasons, 4,428 player-seasons, 866 players and 511,686 attempts. Beta=-0.03082813, with 95% player-cluster interval [-0.05262950, -0.00902675]. This is secondary and is not independent replication. [R11]

## Selection coverage

Usable-measurement coverage ranged from 51.0% to 67.3% across the approved season series. Measured players are not a random sample of all NBA players. Combine participation, measurement availability and completeness, NBA survival, playing opportunity and shooting opportunity may select the sample; the model does not correct this selection. Unmeasured skill, training and current role remain possible sources of confounding. Figure 4 retains the approved season series and marks the development season. [R12]

## Model-diagnostic limitation

Existing residual diagnostics show overpredicted pooled rates in low-attempt bins and underprediction in the 300+ attempt bin. The 100-299 bin is close to the fitted rate and slightly overpredicted, so it should not be described as underpredicted. Exact observed and fitted values are in the supplementary diagnostic figure and its data. Overall and season-level near-zero pooled residuals follow the fitted score equations and do not independently establish model adequacy. Free-throw attempt volume was used as the grouped-binomial denominator rather than as a predictor. Previous model-adequacy analyses indicated that attempt volume is informative about player-level shooting and opportunity structure. Consequently, the primary model should be interpreted as a working conditional association model rather than a complete generative model of shooting opportunity. Player-clustered uncertainty does not repair conditional-mean misspecification. [R13]


Evidence identifiers in brackets resolve to evidence_map.csv. This is a frozen assembly outline, not a completed manuscript or submission.
