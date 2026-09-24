# Stage 1C policy (established before new-season acquisition)

Only the ten audited seasons 2015-16 through 2024-25 may be used; 2025-26 is forbidden at the cache/network boundary. Preserve all 2023-24 original artifacts/evidence. Compare generalized 2023-24 values, dtypes and serialization before retrieving additional seasons.

Sequential maintained-client retrieval: use any valid cache first, one request at a time, at least three seconds between new requests. At most two attempts for a retrieval failure, with a ten-second retry delay. No overrides/bypasses or substitute datasets. A cache-integrity error stops the whole build; do not overwrite or repair it by downloading.

Default CLI policy is strict. An explicit --allow-partial permits continuing after an external retrieval failure or quarantining an incomplete season, records the exact failure and coverage, and excludes it from combined outputs. In Stage 1C use this explicit option to audit all requested seasons, never to conceal gaps.

Keep all structural rejection rules and plus-minus warnings. Preserve accepted/rejected season-level records, but publish season features only if there are no rejected games and completeness checks pass: do not silently make a shortened team history by dropping rejected games. Errors in leakage assertions or 2023-24 regression stop the full build regardless of --allow-partial.

Feature definitions remain v1.0.0. Group history by (season, season_type, team_id). Each season starts empty; all 13 team features and six home-minus-away differences are unchanged. No models or metrics.
