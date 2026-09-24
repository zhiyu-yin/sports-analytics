# Stage 1B feature availability contract — v1.0.0

Established before feature implementation. Scope: the checksum-verified Stage 1A 2023-24 regular-season snapshot only.

For a target game with source game_date T, eligible history is that team's completed regular-season games with game_date strictly less than T. No exact tip-off timestamps exist. Never infer intraday ordering from GAME_ID. A repeated team/date is a fatal validation error; no feature output is published for that build.

Sort within team and season by date, then shift all historical outcome series by one row **before** expanding/rolling. Since duplicate team/dates are forbidden, previous rows are strictly earlier dates. Current-game scores/WL/box scores are internal historical observations only and never exported as target-game predictors. Derive historical point differential from paired scores, never PLUS_MINUS.

- games_played_before: count of prior games in this season, zero at opener.
- season_win_pct_before: prior wins / prior games; missing at opener.
- Last-5/last-10 win percentage, mean point differential, mean points for and mean points against: exactly the previous 5/10 games, min_periods equal to window; otherwise missing.
- rest_days: calendar date difference from previous game minus one; missing at opener.
- is_back_to_back: 1 if rest_days=0; otherwise 0, including opener. Opener 0 means no observed prior game in this season, not known offseason rest.
- games_last_7_days: count prior games with dates in [T-7 calendar days,T), inclusive left and exclusive right; zero at opener.
- Six difference features: home minus away season win percentage, last-5/10 win percentage, last-5/10 mean point differential, and rest days. Missing on either side propagates.

No imputation, backfill, early-game removal, cross-season carryover, model fitting, external data or new NBA requests. Outcomes stay in the Stage 1A outcome table. Identity columns are join metadata, not automatically model inputs.

Historical final values may contain later corrections; a date cutoff cannot establish original publication-time availability. This contract is a date-based backtest rule, not an exact timestamp/publication archive guarantee. Feature builders must fail on provenance discrepancies before writing outputs. Keep Stage 1A inputs and evidence unchanged.
