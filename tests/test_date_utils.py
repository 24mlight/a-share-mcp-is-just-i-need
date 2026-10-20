from datetime import datetime

import pandas as pd

from src.use_cases import date_utils


class CalendarDataSource:
    def __init__(self):
        self.requested_range = None

    def get_trade_dates(self, *, start_date, end_date):
        self.requested_range = (start_date, end_date)
        trading_days = ["2026-10-28", "2026-10-29", "2026-10-30"]
        return pd.DataFrame(
            [
                {"calendar_date": day, "is_trading_day": "1"}
                for day in trading_days
                if start_date <= day <= end_date
            ]
        )


def test_latest_trading_date_includes_dates_after_day_28(monkeypatch):
    class FixedDateTime(datetime):
        @classmethod
        def now(cls, tz=None):
            return cls(2026, 10, 31)

    monkeypatch.setattr(date_utils, "datetime", FixedDateTime)
    data_source = CalendarDataSource()

    assert date_utils.get_latest_trading_date(data_source) == "2026-10-30"
    assert data_source.requested_range == ("2026-10-01", "2026-10-31")
