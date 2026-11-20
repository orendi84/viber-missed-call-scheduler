"""Stdlib unittest. Run from the repo root: python3 -m unittest discover -s tests -v"""
import sys
import unittest
from datetime import datetime
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import viber_missed_calls_v2 as v


class BudapestToUtcTests(unittest.TestCase):
    def test_winter_is_utc_plus_1(self):
        self.assertEqual(v.budapest_local_to_utc(datetime(2026, 1, 15, 18, 0)),
                         datetime(2026, 1, 15, 17, 0))

    def test_summer_is_utc_plus_2(self):
        self.assertEqual(v.budapest_local_to_utc(datetime(2026, 7, 15, 18, 0)),
                         datetime(2026, 7, 15, 16, 0))

    def test_spring_forward_day_2026_03_29(self):
        # 02:00 CET jumps to 03:00 CEST. Before: +1, after: +2.
        self.assertEqual(v.budapest_local_to_utc(datetime(2026, 3, 29, 1, 30)),
                         datetime(2026, 3, 29, 0, 30))
        self.assertEqual(v.budapest_local_to_utc(datetime(2026, 3, 29, 18, 0)),
                         datetime(2026, 3, 29, 16, 0))
        self.assertEqual(v.budapest_local_to_utc(datetime(2026, 3, 28, 18, 0)),
                         datetime(2026, 3, 28, 17, 0))

    def test_fall_back_day_2026_10_25(self):
        # 03:00 CEST falls back to 02:00 CET. Before: +2, after: +1.
        self.assertEqual(v.budapest_local_to_utc(datetime(2026, 10, 25, 1, 30)),
                         datetime(2026, 10, 24, 23, 30))
        self.assertEqual(v.budapest_local_to_utc(datetime(2026, 10, 25, 18, 0)),
                         datetime(2026, 10, 25, 17, 0))
        self.assertEqual(v.budapest_local_to_utc(datetime(2026, 10, 24, 18, 0)),
                         datetime(2026, 10, 24, 16, 0))

    def test_result_is_naive(self):
        self.assertIsNone(v.budapest_local_to_utc(datetime(2026, 1, 1, 12)).tzinfo)


class CallerParsingTests(unittest.TestCase):
    def setUp(self):
        # Bypass __init__ (needs Google auth); parsing only needs a logger.
        self.t = v.ViberMissedCallTracker.__new__(v.ViberMissedCallTracker)
        self.t.logger = mock.Mock()

    def test_supported_format_not_flagged(self):
        calls = self.t.parse_viber_notifications(["2026-01-01 10:00|Missed call from Anna"])
        self.assertEqual(calls[0]['caller'], 'Anna')
        self.assertFalse(calls[0]['caller_unmatched'])
        self.t.logger.warning.assert_not_called()

    def test_unmatched_is_logged_truncated_and_flagged(self):
        payload = "missed call " + "x" * 500
        calls = self.t.parse_viber_notifications([f"2026-01-01 10:00|{payload}"])
        self.assertEqual(calls[0]['caller'], v.UNKNOWN_CALLER)
        self.assertTrue(calls[0]['caller_unmatched'])
        self.t.logger.warning.assert_called_once()
        logged = self.t.logger.warning.call_args[0][1]
        self.assertLessEqual(len(logged), v.MAX_LOGGED_PAYLOAD_CHARS + 2)  # repr quotes

    def test_empty_name_match_is_skipped(self):
        self.assertEqual(self.t.parse_viber_notifications(["t|Missed call from   "]), [])

    def test_legacy_extract_still_returns_placeholder(self):
        self.assertEqual(self.t.extract_caller_from_notification("no pattern here"),
                         v.UNKNOWN_CALLER)

    def test_monitor_alias_delegates_to_manual(self):
        with mock.patch.object(self.t, 'check_manual_missed_calls', return_value=['x']):
            self.assertEqual(self.t.monitor_viber_activity(), ['x'])


if __name__ == '__main__':
    unittest.main()
