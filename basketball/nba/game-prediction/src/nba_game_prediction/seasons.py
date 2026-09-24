"""Audited regular-season scope, not an all-season API. Holdout excluded by design."""
from dataclasses import dataclass
import pandas as pd

@dataclass(frozen=True)
class SeasonScope:
    season: str
    start: str
    end: str
    games_per_team: int | None = 82
    cup_final: str | None = None
    bubble_start: str | None = None
    suspension_start: str | None = None

    @property
    def source_season_id(self): return '2'+self.season[:4]
    @property
    def game_prefix(self): return '002'+self.season[2:4]

SCOPES = {
    s.season:s for s in [
        SeasonScope('2015-16','2015-10-27','2016-04-13'),
        SeasonScope('2016-17','2016-10-25','2017-04-12'),
        SeasonScope('2017-18','2017-10-17','2018-04-11'),
        SeasonScope('2018-19','2018-10-16','2019-04-10'),
        SeasonScope('2019-20','2019-10-22','2020-08-14',None,None,'2020-07-30','2020-03-12'),
        SeasonScope('2020-21','2020-12-22','2021-05-16',72),
        SeasonScope('2021-22','2021-10-19','2022-04-10'),
        SeasonScope('2022-23','2022-10-18','2023-04-09'),
        SeasonScope('2023-24','2023-10-24','2024-04-14',82,'2023-12-09'),
        SeasonScope('2024-25','2024-10-22','2025-04-13',82,'2024-12-17'),
    ]
}


def get_scope(season):
    if season not in SCOPES:
        raise ValueError(f'Season {season!r} is outside audited 2015-16..2024-25 scope; final holdout is forbidden')
    return SCOPES[season]


def season_range(start,end):
    get_scope(start);get_scope(end)
    seasons=[s for s in SCOPES if start<=s<=end]
    if not seasons:raise ValueError('Invalid season range')
    return seasons


def date_in_scope(date,scope):
    if pd.isna(date): return False
    if not pd.Timestamp(scope.start)<=date<=pd.Timestamp(scope.end):return False
    if scope.suspension_start and pd.Timestamp(scope.suspension_start)<=date<pd.Timestamp(scope.bubble_start):return False
    return True
