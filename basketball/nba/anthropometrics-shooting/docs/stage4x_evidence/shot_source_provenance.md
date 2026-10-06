# Stage 4X source provenance

The repository schema inventory found aggregate box scores and season totals, but no preexisting shot-zone event table. Historical endpoint documentation is a schema reference, not shot data.

New secondary source: [DomSamangy NBA_Shots_04_25](https://github.com/DomSamangy/NBA_Shots_04_25), revision `69e63559bc17393312ad258c11f93d78be002079`. The author attributes the source to NBA.com. This attribution does not make the downloaded archive an independently validated official capture. Fourteen season ZIPs covering 2010–11 through 2023–24 were obtained. Files are retained unchanged in `data/raw/stage4x`; SHA-256 hashes, exported schemas, and Git blob hashes are in downloaded_sources.json. All blobs match the retrieved directory listing. The 2023–24 pilot was fetched at main and verified against that listing; other seasons used the pinned revision. Directory, commit response and README are retained.

The archive includes PLAYER_ID, GAME_ID, SEASON_2, SHOT_MADE, SHOT_TYPE, BASIC_ZONE, ZONE_NAME, ZONE_RANGE, distance and transformed coordinates. GAME_EVENT_ID is absent. Exported position fields are not used for adjustment or linkage. PLAYER_ID is matched exactly to the frozen anthropometric identity vector.

Reconciliation targets: the unchanged Stage3 all-player season panel (3PM/3PA) and NocturneBear player-game archives identified in docs/stage3_evidence/shooting_archive_provenance.json (FGM/FGA/3PM/3PA). The latter are a second secondary archive, not fresh official event records. Stage3's official full-player census crosscheck supports 2010–11, 2016–17 and 2023–24 season totals; other seasons retain their historical provenance limitations.

A fresh official NBA shotchartdetail request timed out after 20 seconds with zero bytes. The NBA shooting webpage exposed filters but no shot table in the inspected rendering. These are access observations in this environment, not a claim that official data do not exist. The complete source gate is blocked by unresolved zone/type inconsistencies, not merely by access failure. No silent cleaning, deduplication, zone reassignment, season omission, or coefficient-driven decisions were performed.
