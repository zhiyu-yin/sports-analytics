# Predeclared robustness analyses

| Analysis | Beta / inch | OR / inch | 95% beta CI | Uncertainty | Player-seasons | Players | FTA |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Primary grouped-binomial model | -0.030452 | 0.970007 | [-0.052281, -0.008623] | Player-cluster CR1 | 4117 | 857 | 469099 |
| Beta-binomial robustness | -0.033426 | 0.967127 | [-0.050442, -0.017016] | Remediated player bootstrap percentile | 4117 | 857 | 469099 |
| First eligible season only | -0.027687 | 0.972693 | [-0.049116, -0.006258] | HC1 | 857 | 857 | 68480 |
| Player-balanced weighting | -0.027682 | 0.972697 | [-0.046365, -0.008999] | Player-cluster CR1 | 4117 | 857 | 469099 |
| FTA >=50 sensitivity | -0.031443 | 0.969046 | [-0.053900, -0.008986] | Player-cluster CR1 | 2535 | 545 | 438530 |
| FTA >=100 sensitivity | -0.034882 | 0.965719 | [-0.058966, -0.010798] | Player-cluster CR1 | 1688 | 398 | 377105 |
| Full panel including development | -0.030828 | 0.969642 | [-0.052630, -0.009027] | Player-cluster CR1 | 4428 | 866 | 511686 |

Beta and its 95% CI are log odds per residual inch. Player-seasons and players are accounting counts; contributing-player counts are retained in CSV. FTA totals are unweighted. Beta-binomial is secondary: original full-sample point estimate with the separately remediated bootstrap interval. Historical Stage 3J remains EXECUTION FAIL; Stage 3J-R is NUMERICAL REMEDIATION PASS. The full panel includes the 2013-14 development season and is not independent replication. First-season analysis uses 803 contributing players; player-balanced weights do not equalize total player information.

Source: evidence_map.csv, numeric claim IDs robust_*. Exact values are retained in CSV.
