import unittest
from injury_warning.rules import (future_window, severity, risk_eligible, group_reports,
    validate_features, training_row_allowed, cohort_label, normalize_status, workload,
    onset_day_interval, active_calendar_days)

T = '2024-01-01T00:00:00Z'


class Boundaries(unittest.TestCase):
    def test_same_game_injury_is_not_future(self):
        self.assertFalse(future_window(T, T, T))

    def test_strict_start_inclusive_end(self):
        self.assertTrue(future_window(T, '2024-01-15T00:00:00Z', '2024-01-15T00:00:00Z'))
        self.assertFalse(future_window(T, '2024-01-15T00:00:01Z', '2024-01-15T00:00:01Z'))

    def test_interval_straddling_boundary_unknown(self):
        self.assertIsNone(future_window(T, T, '2024-01-02T00:00:00Z'))
        self.assertIsNone(future_window(T, None, None))

    def test_timezone_required(self):
        with self.assertRaises(ValueError):
            future_window('2024-01-01', T, T)

    def test_reversed_interval_rejected(self):
        with self.assertRaises(ValueError):
            future_window(T, '2024-01-02T00:00:00Z', T)

    def test_28_days_strict(self):
        self.assertEqual(severity(injury_related=True, days_lower=28, days_upper=28)['primary'], 'negative')
        self.assertEqual(severity(injury_related=True, days_lower=29)['primary'], 'positive')

    def test_10_games_inclusive(self):
        self.assertEqual(severity(injury_related=True, consecutive_games_lower=10)['secondary'], 'positive')
        self.assertEqual(severity(injury_related=True, consecutive_games_upper=9)['secondary'], 'negative')

    def test_censoring_never_auto_negative(self):
        self.assertEqual(severity(injury_related=True, days_lower=10)['primary'], 'unknown')
        self.assertEqual(severity(injury_related=True)['secondary'], 'unknown')

    def test_no_injury_evidence(self):
        self.assertEqual(severity(injury_related=None, days_lower=60)['primary'], 'unknown')
        self.assertEqual(severity(injury_related=False, excluded_reason=True)['primary'], 'excluded')

    def test_invalid_duration(self):
        for kw in ({'days_lower': -1}, {'days_lower': 30, 'days_upper': 20}):
            with self.assertRaises(ValueError):
                severity(injury_related=True, **kw)

    def test_episode_identity_required(self):
        reports = [dict(player_id='1', episode_id='a'), dict(player_id='1', episode_id='a'),
                   dict(player_id='1', episode_id='b'), dict(player_id='2', episode_id='a')]
        groups = group_reports(reports)
        self.assertEqual(sorted(map(len, groups.values())), [1, 1, 2])
        with self.assertRaises(ValueError):
            group_reports([dict(player_id='1', diagnosis='ankle')])

    def test_known_available_only(self):
        args = dict(prediction_at=T, game_ended_at=T, status='available', status_known_at=T, season_type='Regular Season')
        self.assertTrue(risk_eligible(**args))
        for change in ({'status': 'unavailable'}, {'status_known_at': '2024-01-02T00:00:00Z'},
                       {'status_known_at': None}, {'season_type': 'Playoffs'}):
            self.assertFalse(risk_eligible(**dict(args, **change)))

    def test_predictor_role_and_time(self):
        good = dict(value=30, max_input_known_at=T, evidence_role='predictor')
        validate_features({'age': good}, T)
        for features in ({'return_date': good}, {'public_symptoms': good},
                         {'age': dict(good, max_input_known_at='2025-01-01T00:00:00Z')},
                         {'age': dict(good, evidence_role='outcome_only')}):
            with self.assertRaises(ValueError):
                validate_features(features, T)

    def test_split_embargo_label_maturity_episode_purge(self):
        args = dict(prediction_at=T, window_end='2024-01-15T00:00:00Z',
                    label_known_at='2024-02-15T00:00:00Z', cutoff='2024-03-01T00:00:00Z', episode_id='a')
        self.assertTrue(training_row_allowed(**args))
        for change in ({'label_known_at': None}, {'cutoff': '2024-01-15T00:00:00Z'},
                       {'cutoff': '2024-02-01T00:00:00Z'}, {'evaluation_episode_ids': ('a',)}):
            self.assertFalse(training_row_allowed(**dict(args, **change)))

    def test_no_event_not_necessarily_negative(self):
        self.assertEqual(cohort_label(eligible=True, event_results=[], complete_onset_surveillance=False), 'unknown')
        self.assertEqual(cohort_label(eligible=True, event_results=[], complete_onset_surveillance=True), 'negative')
        self.assertEqual(cohort_label(eligible=True, event_results=[(True, 'unknown')], complete_onset_surveillance=True), 'unknown')
        self.assertEqual(cohort_label(eligible=True, event_results=[(True, 'positive')], complete_onset_surveillance=False), 'positive')

    def test_status_normalization(self):
        self.assertEqual(normalize_status('Questionable', 'Rest'), 'excluded_noninjury')
        self.assertEqual(normalize_status('Probable', 'Injury management'), 'unknown')
        self.assertEqual(normalize_status('', ''), 'unknown')

    def test_workload_past_only(self):
        rows = [dict(game_id='1', minutes=20, game_ended_at=T, known_at=T),
                dict(game_id='2', minutes=30, game_ended_at=T, known_at='2024-01-02T00:00:00Z'),
                dict(game_id='3', minutes=40, game_ended_at='2023-12-25T00:00:00Z', known_at=T)]
        self.assertEqual(workload(rows, T, 7), {'minutes': 20, 'appearances': 1})
        with self.assertRaises(ValueError):
            workload([rows[0], rows[0]], T, 7)

    def test_calendar_day_boundaries(self):
        args = ('2024-02-01', '2024-02-29', '2023-10-24', '2024-04-15')
        self.assertEqual(active_calendar_days(*args, continuity_confirmed=True), 28)
        self.assertIsNone(active_calendar_days(*args, continuity_confirmed=False))
        self.assertIsNone(active_calendar_days('2024-04-01', '2024-10-01',
                                              '2023-10-24', '2024-04-15', continuity_confirmed=True))

    def test_dst_date_interval_retains_uncertainty(self):
        from datetime import timedelta
        from injury_warning.rules import utc
        lo, hi = onset_day_interval('2024-03-10', 'America/New_York')
        # DST day is 23 elapsed hours, not a fabricated exact onset at midnight.
        self.assertEqual(utc(hi).astimezone(__import__('datetime').timezone.utc) -
                         utc(lo).astimezone(__import__('datetime').timezone.utc),
                         timedelta(hours=23, microseconds=-1))
        self.assertIsNone(future_window(lo, lo, hi))


if __name__ == '__main__':
    unittest.main()
