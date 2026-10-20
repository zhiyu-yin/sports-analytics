# Phase 3A preparation and post-inspection baseline protocol

All30 teams remain the bounded 2023–24 development cohort. No new data collection, retrieval, fitting, preprocessing fitting, threshold tuning or protected-period access occurred. Independent human review is pending. Original files and registrations remain unchanged; no assertion correction was made and the before/after correction ledger is empty. The README documentation checkpoint is explicitly versioned separately from the scientific-result snapshot.

## Snapshot and count reconciliation

`../phase3a/snapshot_manifest.json` hashes every tracked historical module artifact, code, source receipt/provenance, historical batch registration and the preparation adapter. Scientific result commit: `1d6fd5c9d9e52edffa96cc6488037b504c7ab95e`; documentation checkpoint: `b5932dff33752d9f2cdffda42ebdf1da48523b6e`. The union is read through existing adapters without re-running historical builds. Canonical decisions are unique by row ID and by player/time/timing rule, including transfers. Stable player+first-miss game keys reconcile canonical runs; historical actual-game overlap tables and115 duplicate event-record ledger entries remain hashed. No different-anchor overlapping confirmed positives were found in the frozen audit.37 qualifying runs involve36 players. Rose has two separated absence runs; this does **not** establish clinically independent injuries. Both stay in the same player fold.

| lag | included | positive | negative | unknown | qualifying_runs | run_players | eligible_events | lower | upper |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 0 | 7108 | 115 | 6560 | 433 | 37 | 36 | 32 | 0.016178953292065278 | 0.07709622960045019 |
| 1 | 6862 | 109 | 6329 | 424 | 37 | 36 | 31 | 0.0158845817545905 | 0.07767414747886914 |

Ranges are worst-case positive-label frequency identification ranges among included decisions, not confidence intervals, annual incidence, PR-AUC bounds or calibration bounds. The population includes repeated correlated decisions; unknown labels are not negatives.

## Actual observation opportunities

These are eligible observation opportunities, not model detections or successful warnings. Full anchor interval must lie in (decision,decision+14 elapsed days]. Earliest is the earliest included positive decision, not biological injury onset. A blank earliest means no eligible opportunity. All37 events and both timing rules follow; per-event counts also give player counts because IDs are canonical across transfers. Different runs for the same player are separate rows but not independent persons.

| lag | event | player | team | opportunities | earliest | earliest_lead_lower | earliest_lead_upper | >0-3d | >3-7d | >7-14d | boundary_uncertain |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 0 | 203914_0022300488 | Gary Harris | ORL | 1 | 2024-01-03T12:00:00-05:00 | 2.3826388888888888 | 2.3833333333333333 | 1 | 0 | 0 | 0 |
| 1 | 203914_0022300488 | Gary Harris | ORL | 1 | 2024-01-04T12:00:00-05:00 | 1.382638888888889 | 1.3833333333333333 | 1 | 0 | 0 | 0 |
| 0 | 1630587_0022300620 | Isaiah Livers | WAS | 2 | 2024-01-11T12:00:00-05:00 | 13.299305555555556 | 13.3 | 0 | 0 | 2 | 0 |
| 1 | 1630587_0022300620 | Isaiah Livers | WAS | 3 | 2024-01-11T12:00:00-05:00 | 13.299305555555556 | 13.3 | 0 | 0 | 3 | 0 |
| 0 | 203954_0022300686 | Joel Embiid | PHI | 4 | 2024-01-20T12:00:00-05:00 | 12.427777777777777 | 12.428472222222222 | 0 | 1 | 3 | 0 |
| 1 | 203954_0022300686 | Joel Embiid | PHI | 4 | 2024-01-21T12:00:00-05:00 | 11.427777777777777 | 11.428472222222222 | 0 | 1 | 3 | 0 |
| 0 | 1629001_0022300555 | De'Anthony Melton | PHI | 2 | 2024-01-11T12:00:00-05:00 | 4.049305555555556 | 4.05 | 1 | 1 | 0 | 0 |
| 1 | 1629001_0022300555 | De'Anthony Melton | PHI | 2 | 2024-01-12T12:00:00-05:00 | 3.0493055555555557 | 3.05 | 1 | 1 | 0 | 0 |
| 0 | 1631321_0022300519 | Sidy Cissoko | SAS | 0 |  |  |  | 0 | 0 | 0 | 0 |
| 1 | 1631321_0022300519 | Sidy Cissoko | SAS | 0 |  |  |  | 0 | 0 | 0 | 0 |
| 0 | 1631124_0022300488 | Julian Strawther | DEN | 2 | 2024-01-02T12:00:00-05:00 | 3.3826388888888888 | 3.3833333333333333 | 1 | 1 | 0 | 0 |
| 1 | 1631124_0022300488 | Julian Strawther | DEN | 1 | 2024-01-03T12:00:00-05:00 | 2.3826388888888888 | 2.3833333333333333 | 1 | 0 | 0 | 0 |
| 0 | 1628426_0022300760 | Sasha Vezenkov | SAC | 2 | 2024-02-08T12:00:00-05:00 | 3.1326388888888888 | 3.1333333333333333 | 1 | 1 | 0 | 0 |
| 1 | 1628426_0022300760 | Sasha Vezenkov | SAC | 1 | 2024-02-09T12:00:00-05:00 | 2.1326388888888888 | 2.1333333333333333 | 1 | 0 | 0 | 0 |
| 0 | 203944_0022300657 | Julius Randle | NYK | 6 | 2024-01-16T12:00:00-05:00 | 13.299305555555556 | 13.3 | 0 | 2 | 4 | 0 |
| 1 | 203944_0022300657 | Julius Randle | NYK | 6 | 2024-01-17T12:00:00-05:00 | 12.299305555555556 | 12.3 | 1 | 1 | 4 | 0 |
| 0 | 201565_0022300470 | Derrick Rose | MEM | 1 | 2024-01-03T12:00:00-05:00 | 0.34097222222222223 | 0.3416666666666667 | 1 | 0 | 0 | 0 |
| 1 | 201565_0022300470 | Derrick Rose | MEM | 0 |  |  |  | 0 | 0 | 0 | 0 |
| 0 | 201565_0022300861 | Derrick Rose | MEM | 0 |  |  |  | 0 | 0 | 0 | 0 |
| 1 | 201565_0022300861 | Derrick Rose | MEM | 0 |  |  |  | 0 | 0 | 0 | 0 |
| 0 | 1630217_0022300544 | Desmond Bane | MEM | 5 | 2024-01-03T12:00:00-05:00 | 10.340972222222222 | 10.341666666666667 | 0 | 2 | 3 | 0 |
| 1 | 1630217_0022300544 | Desmond Bane | MEM | 5 | 2024-01-04T12:00:00-05:00 | 9.340972222222222 | 9.341666666666667 | 1 | 2 | 2 | 0 |
| 0 | 203935_0022300537 | Marcus Smart | MEM | 4 | 2024-01-03T12:00:00-05:00 | 9.340972222222222 | 9.341666666666667 | 0 | 2 | 2 | 0 |
| 1 | 203935_0022300537 | Marcus Smart | MEM | 4 | 2024-01-04T12:00:00-05:00 | 8.340972222222222 | 8.341666666666667 | 0 | 2 | 2 | 0 |
| 0 | 1629630_0022300503 | Ja Morant | MEM | 3 | 2024-01-03T12:00:00-05:00 | 4.340972222222222 | 4.341666666666667 | 1 | 2 | 0 | 0 |
| 1 | 1629630_0022300503 | Ja Morant | MEM | 3 | 2024-01-04T12:00:00-05:00 | 3.3409722222222222 | 3.341666666666667 | 2 | 1 | 0 | 0 |
| 0 | 1631222_0022300560 | Jake LaRavia | MEM | 3 | 2024-01-10T12:00:00-05:00 | 5.258333333333334 | 5.259027777777778 | 2 | 1 | 0 | 0 |
| 1 | 1631222_0022300560 | Jake LaRavia | MEM | 2 | 2024-01-11T12:00:00-05:00 | 4.258333333333334 | 4.259027777777778 | 1 | 1 | 0 | 0 |
| 0 | 1628384_0022300657 | OG Anunoby | NYK | 7 | 2024-01-16T12:00:00-05:00 | 13.299305555555556 | 13.3 | 1 | 2 | 4 | 0 |
| 1 | 1628384_0022300657 | OG Anunoby | NYK | 7 | 2024-01-17T12:00:00-05:00 | 12.299305555555556 | 12.3 | 2 | 1 | 4 | 0 |
| 0 | 1629027_0022300821 | Trae Young | ATL | 2 | 2024-02-13T12:00:00-05:00 | 12.299305555555556 | 12.3 | 0 | 0 | 2 | 0 |
| 1 | 1629027_0022300821 | Trae Young | ATL | 2 | 2024-02-12T12:00:00-05:00 | 13.299305555555556 | 13.3 | 0 | 0 | 2 | 0 |
| 0 | 1630168_0022300777 | Onyeka Okongwu | ATL | 7 | 2024-02-03T12:00:00-05:00 | 11.299305555555556 | 11.3 | 1 | 3 | 3 | 0 |
| 1 | 1630168_0022300777 | Onyeka Okongwu | ATL | 7 | 2024-02-01T12:00:00-05:00 | 13.299305555555556 | 13.3 | 1 | 2 | 4 | 0 |
| 0 | 203957_0022300651 | Danté Exum | DAL | 2 | 2024-01-25T12:00:00-05:00 | 2.3833333333333333 | 2.384027777777778 | 2 | 0 | 0 | 0 |
| 1 | 203957_0022300651 | Danté Exum | DAL | 1 | 2024-01-26T12:00:00-05:00 | 1.3833333333333333 | 1.3840277777777779 | 1 | 0 | 0 | 0 |
| 0 | 1630590_0022300783 | Scotty Pippen Jr. | MEM | 4 | 2024-02-02T12:00:00-05:00 | 12.340972222222222 | 12.341666666666667 | 1 | 1 | 2 | 0 |
| 1 | 1630590_0022300783 | Scotty Pippen Jr. | MEM | 3 | 2024-02-03T12:00:00-05:00 | 11.340972222222222 | 11.341666666666667 | 0 | 1 | 2 | 0 |
| 0 | 203114_0022300738 | Khris Middleton | MIL | 4 | 2024-01-27T12:00:00-05:00 | 12.342361111111112 | 12.343055555555555 | 0 | 1 | 3 | 0 |
| 1 | 203114_0022300738 | Khris Middleton | MIL | 5 | 2024-01-26T12:00:00-05:00 | 13.342361111111112 | 13.343055555555555 | 0 | 2 | 3 | 0 |
| 0 | 1630163_0022300647 | LaMelo Ball | CHA | 6 | 2024-01-15T12:00:00-05:00 | 12.299305555555556 | 12.3 | 2 | 1 | 3 | 0 |
| 1 | 1630163_0022300647 | LaMelo Ball | CHA | 6 | 2024-01-14T12:00:00-05:00 | 13.299305555555556 | 13.3 | 1 | 2 | 3 | 0 |
| 0 | 1631101_0022300538 | Shaedon Sharpe | POR | 6 | 2024-01-02T12:00:00-05:00 | 10.340972222222222 | 10.341666666666667 | 2 | 2 | 2 | 0 |
| 1 | 1631101_0022300538 | Shaedon Sharpe | POR | 5 | 2024-01-03T12:00:00-05:00 | 9.340972222222222 | 9.341666666666667 | 1 | 2 | 2 | 0 |
| 0 | 1629650_0022300472 | Moses Brown | POR | 1 | 2024-01-02T12:00:00-05:00 | 1.3618055555555555 | 1.3625 | 1 | 0 | 0 | 0 |
| 1 | 1629650_0022300472 | Moses Brown | POR | 1 | 2024-01-03T12:00:00-05:00 | 0.36180555555555555 | 0.3625 | 1 | 0 | 0 | 0 |
| 0 | 1627751_0022300516 | Jakob Poeltl | TOR | 4 | 2024-01-02T12:00:00-05:00 | 7.445138888888889 | 7.445833333333334 | 1 | 2 | 1 | 0 |
| 1 | 1627751_0022300516 | Jakob Poeltl | TOR | 3 | 2024-01-03T12:00:00-05:00 | 6.445138888888889 | 6.445833333333334 | 1 | 2 | 0 | 0 |
| 0 | 1630567_0022300875 | Scottie Barnes | TOR | 0 |  |  |  | 0 | 0 | 0 | 0 |
| 1 | 1630567_0022300875 | Scottie Barnes | TOR | 0 |  |  |  | 0 | 0 | 0 | 0 |
| 0 | 1630549_0022300527 | Day'Ron Sharpe | BKN | 4 | 2024-01-03T12:00:00-05:00 | 8.090972222222222 | 8.091666666666667 | 0 | 2 | 2 | 0 |
| 1 | 1630549_0022300527 | Day'Ron Sharpe | BKN | 4 | 2024-01-04T12:00:00-05:00 | 7.090972222222222 | 7.091666666666667 | 1 | 2 | 1 | 0 |
| 0 | 1627732_0022300833 | Ben Simmons | BKN | 1 | 2024-02-14T12:00:00-05:00 | 13.299305555555556 | 13.3 | 0 | 0 | 1 | 0 |
| 1 | 1627732_0022300833 | Ben Simmons | BKN | 1 | 2024-02-15T12:00:00-05:00 | 12.299305555555556 | 12.3 | 0 | 0 | 1 | 0 |
| 0 | 1630172_0022300656 | Patrick Williams | CHI | 4 | 2024-01-19T12:00:00-05:00 | 9.383333333333333 | 9.384027777777778 | 1 | 1 | 2 | 0 |
| 1 | 1630172_0022300656 | Patrick Williams | CHI | 4 | 2024-01-20T12:00:00-05:00 | 8.383333333333333 | 8.384027777777778 | 1 | 2 | 1 | 0 |
| 0 | 1631106_0022300469 | Tari Eason | HOU | 1 | 2024-01-02T12:00:00-05:00 | 1.3416666666666666 | 1.3423611111111111 | 1 | 0 | 0 | 0 |
| 1 | 1631106_0022300469 | Tari Eason | HOU | 1 | 2024-01-03T12:00:00-05:00 | 0.3416666666666667 | 0.3423611111111111 | 1 | 0 | 0 | 0 |
| 0 | 101108_0022300504 | Chris Paul | GSW | 2 | 2024-01-03T12:00:00-05:00 | 4.363194444444445 | 4.363888888888889 | 1 | 1 | 0 | 0 |
| 1 | 101108_0022300504 | Chris Paul | GSW | 2 | 2024-01-04T12:00:00-05:00 | 3.3631944444444444 | 3.363888888888889 | 1 | 1 | 0 | 0 |
| 0 | 1627780_0022300478 | Gary Payton II | GSW | 0 |  |  |  | 0 | 0 | 0 | 0 |
| 1 | 1627780_0022300478 | Gary Payton II | GSW | 0 |  |  |  | 0 | 0 | 0 | 0 |
| 0 | 1630700_0022300758 | Dyson Daniels | NOP | 7 | 2024-01-28T12:00:00-05:00 | 13.426388888888889 | 13.427083333333334 | 2 | 1 | 4 | 0 |
| 1 | 1630700_0022300758 | Dyson Daniels | NOP | 7 | 2024-01-28T12:00:00-05:00 | 13.426388888888889 | 13.427083333333334 | 1 | 2 | 4 | 0 |
| 0 | 1629629_0022300633 | Cam Reddish | LAL | 3 | 2024-01-12T12:00:00-05:00 | 13.44513888888889 | 13.445833333333333 | 0 | 1 | 2 | 0 |
| 1 | 1629629_0022300633 | Cam Reddish | LAL | 2 | 2024-01-13T12:00:00-05:00 | 12.44513888888889 | 12.445833333333333 | 1 | 0 | 1 | 0 |
| 0 | 1629020_0022300701 | Jarred Vanderbilt | LAL | 6 | 2024-01-22T12:00:00-05:00 | 12.3625 | 12.363194444444444 | 0 | 3 | 3 | 0 |
| 1 | 1629020_0022300701 | Jarred Vanderbilt | LAL | 7 | 2024-01-21T12:00:00-05:00 | 13.3625 | 13.363194444444444 | 1 | 2 | 4 | 0 |
| 0 | 1626174_0022300802 | Christian Wood | LAL | 4 | 2024-02-09T12:00:00-05:00 | 13.427777777777777 | 13.428472222222222 | 0 | 0 | 4 | 0 |
| 1 | 1626174_0022300802 | Christian Wood | LAL | 3 | 2024-02-10T12:00:00-05:00 | 12.427777777777777 | 12.428472222222222 | 0 | 0 | 3 | 0 |
| 0 | 1626196_0022300773 | Josh Richardson | MIA | 5 | 2024-02-01T12:00:00-05:00 | 12.340972222222222 | 12.341666666666667 | 0 | 2 | 3 | 0 |
| 1 | 1626196_0022300773 | Josh Richardson | MIA | 6 | 2024-01-31T12:00:00-05:00 | 13.340972222222222 | 13.341666666666667 | 0 | 2 | 4 | 0 |
| 0 | 201566_0022300873 | Russell Westbrook | LAC | 0 |  |  |  | 0 | 0 | 0 | 0 |
| 1 | 201566_0022300873 | Russell Westbrook | LAC | 0 |  |  |  | 0 | 0 | 0 | 0 |

Counts aggregated by player (related runs remain grouped):

| lag | player_id | player | qualifying_runs | events_with_opportunities | positive_decisions |
| --- | --- | --- | --- | --- | --- |
| 0 | 101108 | Chris Paul | 1 | 1 | 2 |
| 0 | 1626174 | Christian Wood | 1 | 1 | 4 |
| 0 | 1626196 | Josh Richardson | 1 | 1 | 5 |
| 0 | 1627732 | Ben Simmons | 1 | 1 | 1 |
| 0 | 1627751 | Jakob Poeltl | 1 | 1 | 4 |
| 0 | 1627780 | Gary Payton II | 1 | 0 | 0 |
| 0 | 1628384 | OG Anunoby | 1 | 1 | 7 |
| 0 | 1628426 | Sasha Vezenkov | 1 | 1 | 2 |
| 0 | 1629001 | De'Anthony Melton | 1 | 1 | 2 |
| 0 | 1629020 | Jarred Vanderbilt | 1 | 1 | 6 |
| 0 | 1629027 | Trae Young | 1 | 1 | 2 |
| 0 | 1629629 | Cam Reddish | 1 | 1 | 3 |
| 0 | 1629630 | Ja Morant | 1 | 1 | 3 |
| 0 | 1629650 | Moses Brown | 1 | 1 | 1 |
| 0 | 1630163 | LaMelo Ball | 1 | 1 | 6 |
| 0 | 1630168 | Onyeka Okongwu | 1 | 1 | 7 |
| 0 | 1630172 | Patrick Williams | 1 | 1 | 4 |
| 0 | 1630217 | Desmond Bane | 1 | 1 | 5 |
| 0 | 1630549 | Day'Ron Sharpe | 1 | 1 | 4 |
| 0 | 1630567 | Scottie Barnes | 1 | 0 | 0 |
| 0 | 1630587 | Isaiah Livers | 1 | 1 | 2 |
| 0 | 1630590 | Scotty Pippen Jr. | 1 | 1 | 4 |
| 0 | 1630700 | Dyson Daniels | 1 | 1 | 7 |
| 0 | 1631101 | Shaedon Sharpe | 1 | 1 | 6 |
| 0 | 1631106 | Tari Eason | 1 | 1 | 1 |
| 0 | 1631124 | Julian Strawther | 1 | 1 | 2 |
| 0 | 1631222 | Jake LaRavia | 1 | 1 | 3 |
| 0 | 1631321 | Sidy Cissoko | 1 | 0 | 0 |
| 0 | 201565 | Derrick Rose | 2 | 1 | 1 |
| 0 | 201566 | Russell Westbrook | 1 | 0 | 0 |
| 0 | 203114 | Khris Middleton | 1 | 1 | 4 |
| 0 | 203914 | Gary Harris | 1 | 1 | 1 |
| 0 | 203935 | Marcus Smart | 1 | 1 | 4 |
| 0 | 203944 | Julius Randle | 1 | 1 | 6 |
| 0 | 203954 | Joel Embiid | 1 | 1 | 4 |
| 0 | 203957 | Danté Exum | 1 | 1 | 2 |
| 1 | 101108 | Chris Paul | 1 | 1 | 2 |
| 1 | 1626174 | Christian Wood | 1 | 1 | 3 |
| 1 | 1626196 | Josh Richardson | 1 | 1 | 6 |
| 1 | 1627732 | Ben Simmons | 1 | 1 | 1 |
| 1 | 1627751 | Jakob Poeltl | 1 | 1 | 3 |
| 1 | 1627780 | Gary Payton II | 1 | 0 | 0 |
| 1 | 1628384 | OG Anunoby | 1 | 1 | 7 |
| 1 | 1628426 | Sasha Vezenkov | 1 | 1 | 1 |
| 1 | 1629001 | De'Anthony Melton | 1 | 1 | 2 |
| 1 | 1629020 | Jarred Vanderbilt | 1 | 1 | 7 |
| 1 | 1629027 | Trae Young | 1 | 1 | 2 |
| 1 | 1629629 | Cam Reddish | 1 | 1 | 2 |
| 1 | 1629630 | Ja Morant | 1 | 1 | 3 |
| 1 | 1629650 | Moses Brown | 1 | 1 | 1 |
| 1 | 1630163 | LaMelo Ball | 1 | 1 | 6 |
| 1 | 1630168 | Onyeka Okongwu | 1 | 1 | 7 |
| 1 | 1630172 | Patrick Williams | 1 | 1 | 4 |
| 1 | 1630217 | Desmond Bane | 1 | 1 | 5 |
| 1 | 1630549 | Day'Ron Sharpe | 1 | 1 | 4 |
| 1 | 1630567 | Scottie Barnes | 1 | 0 | 0 |
| 1 | 1630587 | Isaiah Livers | 1 | 1 | 3 |
| 1 | 1630590 | Scotty Pippen Jr. | 1 | 1 | 3 |
| 1 | 1630700 | Dyson Daniels | 1 | 1 | 7 |
| 1 | 1631101 | Shaedon Sharpe | 1 | 1 | 5 |
| 1 | 1631106 | Tari Eason | 1 | 1 | 1 |
| 1 | 1631124 | Julian Strawther | 1 | 1 | 1 |
| 1 | 1631222 | Jake LaRavia | 1 | 1 | 2 |
| 1 | 1631321 | Sidy Cissoko | 1 | 0 | 0 |
| 1 | 201565 | Derrick Rose | 2 | 0 | 0 |
| 1 | 201566 | Russell Westbrook | 1 | 0 | 0 |
| 1 | 203114 | Khris Middleton | 1 | 1 | 5 |
| 1 | 203914 | Gary Harris | 1 | 1 | 1 |
| 1 | 203935 | Marcus Smart | 1 | 1 | 4 |
| 1 | 203944 | Julius Randle | 1 | 1 | 6 |
| 1 | 203954 | Joel Embiid | 1 | 1 | 4 |
| 1 | 203957 | Danté Exum | 1 | 1 | 1 |

Lead bins (row counts and distinct events; event totals overlap across bins):

| extra_lag_days | lead_time_bin | positive_rows | events |
| --- | --- | --- | --- |
| 0 | >0-3d | 24 | 19 |
| 0 | >3-7d | 36 | 23 |
| 0 | >7-14d | 55 | 21 |
| 0 | boundary_uncertain | 0 | 0 |
| 1 | >0-3d | 24 | 22 |
| 1 | >3-7d | 32 | 20 |
| 1 | >7-14d | 53 | 20 |
| 1 | boundary_uncertain | 0 | 0 |

Counts by prediction team (transfer events may occur across teams, so event totals across teams can overlap):

| lag | team | positive_decisions | players | events |
| --- | --- | --- | --- | --- |
| 0 | ATL | 9 | 2 | 2 |
| 0 | BKN | 5 | 2 | 2 |
| 0 | BOS | 0 | 0 | 0 |
| 0 | CHA | 6 | 1 | 1 |
| 0 | CHI | 4 | 1 | 1 |
| 0 | CLE | 0 | 0 | 0 |
| 0 | DAL | 2 | 1 | 1 |
| 0 | DEN | 2 | 1 | 1 |
| 0 | DET | 2 | 1 | 1 |
| 0 | GSW | 2 | 1 | 1 |
| 0 | HOU | 1 | 1 | 1 |
| 0 | IND | 0 | 0 | 0 |
| 0 | LAC | 0 | 0 | 0 |
| 0 | LAL | 13 | 3 | 3 |
| 0 | MEM | 20 | 6 | 6 |
| 0 | MIA | 5 | 1 | 1 |
| 0 | MIL | 4 | 1 | 1 |
| 0 | MIN | 0 | 0 | 0 |
| 0 | NOP | 7 | 1 | 1 |
| 0 | NYK | 13 | 2 | 2 |
| 0 | OKC | 0 | 0 | 0 |
| 0 | ORL | 1 | 1 | 1 |
| 0 | PHI | 6 | 2 | 2 |
| 0 | PHX | 0 | 0 | 0 |
| 0 | POR | 7 | 2 | 2 |
| 0 | SAC | 2 | 1 | 1 |
| 0 | SAS | 0 | 0 | 0 |
| 0 | TOR | 4 | 1 | 1 |
| 0 | UTA | 0 | 0 | 0 |
| 0 | WAS | 0 | 0 | 0 |
| 1 | ATL | 9 | 2 | 2 |
| 1 | BKN | 5 | 2 | 2 |
| 1 | BOS | 0 | 0 | 0 |
| 1 | CHA | 6 | 1 | 1 |
| 1 | CHI | 4 | 1 | 1 |
| 1 | CLE | 0 | 0 | 0 |
| 1 | DAL | 1 | 1 | 1 |
| 1 | DEN | 1 | 1 | 1 |
| 1 | DET | 3 | 1 | 1 |
| 1 | GSW | 2 | 1 | 1 |
| 1 | HOU | 1 | 1 | 1 |
| 1 | IND | 0 | 0 | 0 |
| 1 | LAC | 0 | 0 | 0 |
| 1 | LAL | 12 | 3 | 3 |
| 1 | MEM | 17 | 5 | 5 |
| 1 | MIA | 6 | 1 | 1 |
| 1 | MIL | 5 | 1 | 1 |
| 1 | MIN | 0 | 0 | 0 |
| 1 | NOP | 7 | 1 | 1 |
| 1 | NYK | 13 | 2 | 2 |
| 1 | OKC | 0 | 0 | 0 |
| 1 | ORL | 1 | 1 | 1 |
| 1 | PHI | 6 | 2 | 2 |
| 1 | PHX | 0 | 0 | 0 |
| 1 | POR | 6 | 2 | 2 |
| 1 | SAC | 1 | 1 | 1 |
| 1 | SAS | 0 | 0 | 0 |
| 1 | TOR | 3 | 1 | 1 |
| 1 | UTA | 0 | 0 | 0 |
| 1 | WAS | 0 | 0 | 0 |

Mutually exclusive positive-row knowledge hierarchy under B timing; overlapping raw source flags remain in `tables/opportunities.csv`:

| lag | group | rows | events |
| --- | --- | --- | --- |
| 0 | same_acute_event_disclosed | 0 | 0 |
| 0 | recent_symptoms_or_injury_evidence | 63 | 20 |
| 0 | prior_acquired_history_without_recent_evidence | 3 | 2 |
| 0 | no_signal_found_under_bounded_search | 49 | 13 |
| 0 | unresolved_timing | 0 | 0 |
| 1 | same_acute_event_disclosed | 2 | 2 |
| 1 | recent_symptoms_or_injury_evidence | 58 | 20 |
| 1 | prior_acquired_history_without_recent_evidence | 5 | 3 |
| 1 | no_signal_found_under_bounded_search | 44 | 11 |
| 1 | unresolved_timing | 0 | 0 |

Different decisions for one event may fall in different knowledge groups; event counts across groups overlap. A original-publication timing is unverified for all rows. C links prior acute disclosures to eventual runs for description only, never prediction. No searched signal means no signal found within the bounded source process, not biologically symptom-free.

Supported ordering before an acquired linked acute disclosure (B assumed availability only):

| lag | events_with_supported_pre_disclosure_opportunity | events_with_linked_disclosure | ordering_unverified |
| --- | --- | --- | --- |
| 0 | 10 | 11 | 26 |
| 1 | 9 | 11 | 26 |

Unlinked disclosures cannot be ordered merely because the same-event flag is false. `tables/disclosure_ordering.csv` retains timestamps and unresolved ordering. No verified A pre-injury warning is established.

Already-disclosed-acute sensitivity (outcome-conditioned C linkage; not a deployable eligibility filter):

| lag | acute_excluded | sensitivity_denominator | sensitivity_positive | sensitivity_events |
| --- | --- | --- | --- | --- |
| 0 | 0 | 7108 | 115 | 32 |
| 1 | 2 | 6860 | 107 | 30 |

## Review preparation

Prepared 99 shuffled conclusion-blinded cases: all37 currently qualifying runs, 32 consequential unresolved runs and30 seeded negative decisions, one/team (seed20240221). Unknown cases are every canonical unknown run linked to an included unknown decision with possible/true onset-window membership, not merely the earlier top-ten queues. Their exact selection and original conclusions are in the separate answer key. First-pass packet contains raw factual game timelines, reasons, direct URLs, source hashes, short capped excerpts, locators and blank structured reviewer fields. Public narratives and selection may reveal case type, so this is conclusion-blinded rather than perfectly blinded. 0 unresolved source URLs; 0 narrative references lack exact paragraph locators and are explicitly marked for source inspection. No invented locators or excerpts. Factual game rows still identify exact game/player entries. Case facts use the original batch-selected receipt hashes, not a silent replacement by the latest/global cache; `review/source_version_audit.csv` preserves the comparison. Global receipts only supply otherwise unavailable retrospective C supplements. Independent human reviews: **0**.

Distribute only `review/first_pass/` to a separate human; retain `review/answer_key.csv`, this report and historical judgments separately until first-pass completion. Review attribution, continuity, original anchor, consecutive medical games, competing reasons, censoring and transfers. No need to wait to complete preparation, but final labels, event opportunity claims and later model interpretation depend on review. No human conclusions are invented.

## Feature availability and fixed comparison

Age/DOB is unavailable in the existing feature tables. M1 is explicitly an exposure/known-injury alternative, not an age-adjusted risk model. M0 is constant training known-label event-row fraction; M1 uses recent acquired28-day evidence, cumulative acquired history and prior28-day mean minutes per appearance excluding latest; M2 adds only7-day minus prior7-day minutes and index-game back-to-back indicator. No player/team IDs, C acute links or outcome fields are predictors. Full formulas, L2 C=0.1 settings, missing indicators, training-only imputation/scaling, weights and metric/alert definitions are fixed in `protocol/study_protocol.md` and `protocol/config.json`.

| lag | feature | rows | missing | min | max |
| --- | --- | --- | --- | --- | --- |
| 0 | recent_evidence_28d | 7108 | 244 | 0.0 | 1.0 |
| 0 | older_or_recent_history | 7108 | 244 | 0.0 | 1.0 |
| 0 | past_mean_minutes | 7108 | 196 | 0.5 | 41.0241 |
| 0 | workload_change_minutes_7d | 7108 | 131 | -124.5333 | 146.25 |
| 0 | index_back_to_back | 7108 | 131 | 0.0 | 1.0 |
| 1 | recent_evidence_28d | 6862 | 234 | 0.0 | 1.0 |
| 1 | older_or_recent_history | 6862 | 234 | 0.0 | 1.0 |
| 1 | past_mean_minutes | 6862 | 189 | 0.5 | 41.0241 |
| 1 | workload_change_minutes_7d | 6862 | 125 | -115.45 | 145.05 |
| 1 | index_back_to_back | 6862 | 125 | 0.0 | 1.0 |

Incomplete history makes exposure/rest features missing rather than zero. Boston legacy injury-memory fields are missing, not falsely equated to modern fields. Missing features stay in paired evaluation with training-only imputation and fixed indicators. The decision-to-last-appearance interval was rejected after inspection because it mainly encodes the noon decision convention; the back-to-back indicator is the fixed rest alternative. No imputer/scaler has been fitted. Actual workload latest-input and acquired-signal identity/timing checks found no future B inputs; this verifies assumption-based clocks, not original A publication. Predictor allowlist rejects extra columns. Detailed selection by team, player, exposure band and acquired risk is in `tables/selection_missingness.csv`; summaries by exposure/risk follow.

| lag | dimension | value | rows | players | positive | negative | unknown | any_missing_predictor |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 0 | exposure_band | <20 minutes | 2787 | 289 | 25 | 2497 | 265 | 89 |
| 0 | exposure_band | >=20 minutes | 4125 | 281 | 86 | 3903 | 136 | 154 |
| 0 | exposure_band | missing | 196 | 100 | 4 | 160 | 32 | 196 |
| 1 | exposure_band | <20 minutes | 2681 | 285 | 19 | 2406 | 256 | 85 |
| 1 | exposure_band | >=20 minutes | 3992 | 278 | 86 | 3771 | 135 | 148 |
| 1 | exposure_band | missing | 189 | 99 | 4 | 152 | 33 | 189 |
| 0 | risk_information | missing | 244 | 16 | 0 | 244 | 0 | 244 |
| 0 | risk_information | no recent acquired evidence | 4146 | 415 | 52 | 3779 | 315 | 151 |
| 0 | risk_information | recent | 2718 | 261 | 63 | 2537 | 118 | 44 |
| 1 | risk_information | missing | 234 | 16 | 0 | 234 | 0 | 234 |
| 1 | risk_information | no recent acquired evidence | 3963 | 411 | 49 | 3603 | 311 | 144 |
| 1 | risk_information | recent | 2665 | 263 | 60 | 2492 | 113 | 44 |

## Deterministic grouped feasibility

Five player folds use SHA256 with fixed prefix/seed, modulo5, without label stratification or redraw. All transfer spells/episodes stay together. Counts below are actual train/test labels and events before any fitting. Memphis sensitivity removes every row of a player with any included MEM decision, including transfer rows; original folds remain fixed. Team/calendar dependence remains. These are planning counts, not validation results or a pristine holdout.

| lag | sensitivity | fold | role | rows | players | positive_players | positive_events | positive | negative | unknown |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 0 | all | 0 | test | 1144 | 81 | 6 | 6 | 21 | 1027 | 96 |
| 0 | all | 0 | train | 5964 | 416 | 26 | 26 | 94 | 5533 | 337 |
| 0 | all | 1 | test | 1346 | 96 | 3 | 3 | 13 | 1271 | 62 |
| 0 | all | 1 | train | 5762 | 401 | 29 | 29 | 102 | 5289 | 371 |
| 0 | all | 2 | test | 1484 | 96 | 5 | 5 | 17 | 1417 | 50 |
| 0 | all | 2 | train | 5624 | 401 | 27 | 27 | 98 | 5143 | 383 |
| 0 | all | 3 | test | 1721 | 124 | 12 | 12 | 37 | 1562 | 122 |
| 0 | all | 3 | train | 5387 | 373 | 20 | 20 | 78 | 4998 | 311 |
| 0 | all | 4 | test | 1413 | 100 | 6 | 6 | 27 | 1283 | 103 |
| 0 | all | 4 | train | 5695 | 397 | 26 | 26 | 88 | 5277 | 330 |
| 0 | exclude_MEM_players | 0 | test | 1097 | 77 | 5 | 5 | 16 | 989 | 92 |
| 0 | exclude_MEM_players | 0 | train | 5759 | 397 | 21 | 21 | 79 | 5390 | 290 |
| 0 | exclude_MEM_players | 1 | test | 1269 | 91 | 3 | 3 | 13 | 1195 | 61 |
| 0 | exclude_MEM_players | 1 | train | 5587 | 383 | 23 | 23 | 82 | 5184 | 321 |
| 0 | exclude_MEM_players | 2 | test | 1466 | 95 | 5 | 5 | 17 | 1399 | 50 |
| 0 | exclude_MEM_players | 2 | train | 5390 | 379 | 21 | 21 | 78 | 4980 | 332 |
| 0 | exclude_MEM_players | 3 | test | 1659 | 116 | 8 | 8 | 25 | 1542 | 92 |
| 0 | exclude_MEM_players | 3 | train | 5197 | 358 | 18 | 18 | 70 | 4837 | 290 |
| 0 | exclude_MEM_players | 4 | test | 1365 | 95 | 5 | 5 | 24 | 1254 | 87 |
| 0 | exclude_MEM_players | 4 | train | 5491 | 379 | 21 | 21 | 71 | 5125 | 295 |
| 1 | all | 0 | test | 1102 | 81 | 6 | 6 | 20 | 992 | 90 |
| 1 | all | 0 | train | 5760 | 415 | 25 | 25 | 89 | 5337 | 334 |
| 1 | all | 1 | test | 1311 | 96 | 3 | 3 | 11 | 1235 | 65 |
| 1 | all | 1 | train | 5551 | 400 | 28 | 28 | 98 | 5094 | 359 |
| 1 | all | 2 | test | 1431 | 96 | 5 | 5 | 19 | 1363 | 49 |
| 1 | all | 2 | train | 5431 | 400 | 26 | 26 | 90 | 4966 | 375 |
| 1 | all | 3 | test | 1662 | 124 | 11 | 11 | 34 | 1505 | 123 |
| 1 | all | 3 | train | 5200 | 372 | 20 | 20 | 75 | 4824 | 301 |
| 1 | all | 4 | test | 1356 | 99 | 6 | 6 | 25 | 1234 | 97 |
| 1 | all | 4 | train | 5506 | 397 | 25 | 25 | 84 | 5095 | 327 |
| 1 | exclude_MEM_players | 0 | test | 1058 | 77 | 5 | 5 | 15 | 957 | 86 |
| 1 | exclude_MEM_players | 0 | train | 5560 | 396 | 21 | 21 | 77 | 5199 | 284 |
| 1 | exclude_MEM_players | 1 | test | 1234 | 91 | 3 | 3 | 11 | 1161 | 62 |
| 1 | exclude_MEM_players | 1 | train | 5384 | 382 | 23 | 23 | 81 | 4995 | 308 |
| 1 | exclude_MEM_players | 2 | test | 1413 | 95 | 5 | 5 | 19 | 1345 | 49 |
| 1 | exclude_MEM_players | 2 | train | 5205 | 378 | 21 | 21 | 73 | 4811 | 321 |
| 1 | exclude_MEM_players | 3 | test | 1602 | 116 | 8 | 8 | 24 | 1486 | 92 |
| 1 | exclude_MEM_players | 3 | train | 5016 | 357 | 18 | 18 | 68 | 4670 | 278 |
| 1 | exclude_MEM_players | 4 | test | 1311 | 94 | 5 | 5 | 23 | 1207 | 81 |
| 1 | exclude_MEM_players | 4 | train | 5307 | 379 | 21 | 21 | 69 | 4949 | 289 |

Recommended next step: independent human adjudication and resolution/logging of consequential uncertainty, **not an immediate exploratory fit**. Fold counts support only bounded internal-study planning; sparse positive players/events, Memphis concentration (7/37 runs), missing labels, one narrow season and assumed clocks preclude confirmatory claims. If reviewed labels remain usable, separately authorize the fixed player-grouped exploratory comparison. Call it exploratory internal validation, not prospective/temporal generalization. A later separately authorized2024-10-22–2024-12-31 evaluation period (onset through2025-01-14, severity through2025-04-13) is a candidate only and was not accessed. Historical label maturity at training cutoffs remains unverified; assumptions must be distinguished from verified availability before any temporal study.

The protocol fixes AP/PR-AUC with prevalence reference, Brier/calibration, paired identical-row M2-M1 differences, player-bootstrap uncertainty, unknown-label selection/ranges and training-only nested threshold selection. Alerts merge within7 days of the first alert, match each canonical run once within14 days, and keep unresolved/redundant alerts separate. Denominator is observed eligible decisions, never invented player-weeks. Row weights remain1; no event reweighting then probability-calibration claim.

## Commands and freeze

```sh
export PYTHONPATH=basketball/nba/injury-warning/src:basketball/nba/injury-warning
python3 -m phase3a.study --prepare  # deterministic preparation; never fits
python3 -m phase3a.study            # default: verify snapshot/config and show dry-run status
python3 -m unittest discover -s basketball/nba/injury-warning/tests -p test_phase3a.py -v
# --execute-fit is intentionally refused in this phase, even if supplied.
```

See `protocol/study_protocol.md` for exact definitions and `commit_receipt.json` for protocol commit/hash after freeze. Historical tests are run on their scientific snapshot because preservation manifests deliberately freeze the old module README. The Phase1D preservation list additionally hashes three ignored local bytecode files: exact offline reproduction requires these original bytes and PYTHONDONTWRITEBYTECODE=1, plus the checksummed 2023–24 schedule cache and pre-existing local root README. These machine-cache dependencies are a historical portability limitation, not files to distribute or silently remove from registrations. Raw cache requirements remain those of Phase2D; no full bodies or PDFs are redistributed. This protocol was designed after outcome inspection and is not pre-data preregistration. Pending human review has not been represented as complete.
