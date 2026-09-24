"""Date-only schedule features: earlier dates, never inferred intraday ordering."""
import numpy as np
import pandas as pd


def schedule_features(dates):
    dates = pd.Series(dates).reset_index(drop=True)
    if dates.isna().any() or not dates.is_monotonic_increasing or dates.duplicated().any():
        raise ValueError('Schedule requires distinct, increasing, nonmissing dates')
    if dates.dt.tz is not None or not dates.eq(dates.dt.normalize()).all():
        raise ValueError('Schedule requires timezone-naive calendar dates')
    previous = dates.shift(1)
    rest = ((dates - previous).dt.days - 1).astype('Int64')
    left = dates.searchsorted(dates - pd.Timedelta(days=7), side='left')
    return pd.DataFrame({
        'rest_days': rest,
        'is_back_to_back': rest.eq(0).fillna(False).astype('Int64'),
        'games_last_7_days': pd.Series(np.arange(len(dates)) - left, dtype='Int64'),
    })
