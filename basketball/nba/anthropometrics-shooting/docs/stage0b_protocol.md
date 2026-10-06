# Stage 0B / Stage 1 protocol freeze

Declared 2026-09-28 before any scientific association calculation. Source validation may block release of the candidate dataset; this protocol does not waive that gate.

## Population and identities

Target: NBA 2013-14 regular-season players with positive minutes, a positive exact-ID join to the combine archive, and complete plausible barefoot height and wingspan measured by calendar year 2013. Treat 2013 combine records as pre-season; no record dated 2014 or later qualifies. Select the latest complete, non-quarantined record through 2013. Never choose by FT accuracy. Retain exact-ID name differences. A reviewed name crosswalk does not change the primary exact-ID eligibility rule. Unresolved identity or measurement conflicts are excluded with reasons; source-wide validation is distinct from individual row plausibility.

No minimum FTA. All integer counts must be nonnegative and makes cannot exceed attempts. Keep FTA=0 players in population accounting; Stage 1's binomial accuracy likelihood uses FTA>0 only. Do not impute accuracy for zero attempts. Do not average game percentages. Store exact summed playing seconds and minutes=seconds/60; official whole-minute season totals are rounding comparisons (tolerance 0.5 minute), not reasons to change the raw sums.

Screen every player appearing in the 2013-14 archive including DNP/zero-minute records; document all failed criteria. Players absent from every 2013-14 archive row are outside this screening population, not silently filtered members of it. Preserve raw archives and all Stage 0 evidence.

## Measurements and repeated records

NBA linear measurements are inches; explicit centimeters require division by 2.54. Numeric/display disagreement is quarantined unless official same-year evidence resolves it. Generic roster heights and rounded narrative wingspans cannot resolve a quarter-inch combine disagreement. Treat <=0.25 inch changes as near-identical and >0.25 inch as materially different for audit purposes, not a scientific threshold. For repeated records report signed latest-minus-earliest differences. A material difference is not automatically an error; investigate affected pre-2013 records before release.

## Primary exposure

Preselect **residual wingspan** for Stage 1, on geometric grounds: wingspan-minus-height imposes a slope of one, and a ratio imposes proportional scaling. Preserve advantage and ratio as alternate exposures. Do not calculate residuals in Stage 0B.

Reference population: option A, **all usable complete NBA combine participants in the pinned archive with positive IDs and measurement year <=2013**, regardless of NBA survival or FT attempts. One latest complete, non-quarantined record per person, same plausibility and conflict checks as the analytical population. Thus the reference is outcome-independent and strictly pre-season; freeze its membership/hash separately. The archive must pass the source validation gate before this reference is called trusted. Do not silently restrict it to eventual NBA players (option B), which would add NBA selection, or extend it with later years. Do not use missing-ID placeholders as one person. Current data contain only NBA draft-combine men's records, so no additional sex/league mixture is intentionally introduced.

Stage 1 may fit linear OLS wingspan ~ intercept + barefoot height **in this reference population**, without FT information, then apply the estimated geometric transformation to the 2013-14 panel. Linear form is predeclared; nonlinear residualization is a labeled later sensitivity requiring a protocol amendment. No residualization or outcome model is fitted in Stage 0B. Full-archive reference use could increase precision, but later cohorts and repeated measurements complicate temporal interpretation, so it is not selected here.

## Primary outcome and first model ladder

Primary outcome: 2013-14 regular-season FTM out of FTA; future likelihood `FTM_i ~ Binomial(FTA_i, p_i)`. FT% is not the modeled response.

- Model 0: primary relative-wingspan exposure.
- Model 1: add barefoot height.
- Model 2: add original combine position, categorical, with missing recorded as unknown and each hybrid label retained separately. Any pooling change must be declared before fitting; do not infer grouping from outcomes.
- Model 3: add season-age/experience only if independently validated before fitting.

No season fixed effect in this single-season panel. No primary FTA predictor merely because denominator sizes differ. Minutes, attempt thresholds, alternate exposures and alternative position mappings are later sensitivities. A proposed, unapplied grouping is PG/SG -> guards; SF/PF -> forwards/wings; C -> bigs; hybrids remain their own categories pending a declared policy.

## Frozen interpretation

“This analysis estimates associations within NBA players with available combine measurements. It does not identify a causal effect of arm length on shooting, because combine participation, NBA selection, role assignment and other factors may jointly affect the observed sample.”

## Source-validation release gate

Official factual cross-checks must meaningfully support both anthropometrics and shooting counts. HTTP 200 without factual fields is not validation; timeouts are not empty data. Report unavailable strata without replacing them. All four flagged discrepancies must be resolved or quarantined. Shooting sample count conflicts must be explained or quarantined before inference. Candidate parquet and protocol may be frozen for review even when the gate is closed; manifests and final report must explicitly say inference is not approved.
