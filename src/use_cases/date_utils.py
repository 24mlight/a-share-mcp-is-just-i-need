"""Use cases for date utility tools."""
import calendar
from datetime import datetime, timedelta
from typing import Optional

import pandas as pd

from src.data_source_interface import FinancialDataSource


def _fetch_trading_days(data_source: FinancialDataSource, start_date: str, end_date: str) -> pd.DataFrame:
    return data_source.get_trade_dates(start_date=start_date, end_date=end_date)


def get_latest_trading_date(data_source: FinancialDataSource) -> str:
    today = datetime.now().strftime("%Y-%m-%d")
    start_date = datetime.now().replace(day=1).strftime("%Y-%m-%d")
    end_date = datetime.now().replace(day=28).strftime("%Y-%m-%d")
    df = _fetch_trading_days(data_source, start_date=start_date, end_date=end_date)
    valid_trading_days = df[df["is_trading_day"] == "1"]["calendar_date"].tolist()
    latest_trading_date = None
    for dstr in valid_trading_days:
        if dstr <= today and (latest_trading_date is None or dstr > latest_trading_date):
            latest_trading_date = dstr
    return latest_trading_date or today


def get_market_analysis_timeframe(period: str = "recent") -> str:
    now = datetime.now()
    end_date = now
    if period == "recent":
        if now.day < 15:
            if now.month == 1:
                start_date = datetime(now.year - 1, 11, 1)
            else:
                prev_month = now.month - 1
                start_month = prev_month if prev_month > 0 else 12
                start_year = now.year if prev_month > 0 else now.year - 1
                start_date = datetime(start_year, start_month, 1)
        else:
            start_date = datetime(now.year, now.month, 1)
    elif period == "quarter":
        quarter = (now.month - 1) // 3 + 1
        start_month = (quarter - 1) * 3 + 1
        start_date = datetime(now.year, start_month, 1)
    elif period == "half_year":
        start_month = 1 if now.month <= 6 else 7
        start_date = datetime(now.year, start_month, 1)
    elif period == "year":
        start_date = datetime(now.year, 1, 1)
    else:
        raise ValueError("Invalid period. Use 'recent', 'quarter', 'half_year', or 'year'.")
    return f"{start_date.strftime('%Y-%m-%d')} 至 {end_date.strftime('%Y-%m-%d')}"


def is_trading_day(data_source: FinancialDataSource, *, date: str) -> str:
    df = _fetch_trading_days(data_source, start_date=date, end_date=date)
    if df.empty:
        return "未知"
    row = df.iloc[0]
    return "是" if str(row.get("is_trading_day", "")) == "1" else "否"


def previous_trading_day(data_source: FinancialDataSource, *, date: str) -> str:
    target = datetime.strptime(date, "%Y-%m-%d")
    start = (target - timedelta(days=31)).strftime("%Y-%m-%d")
    df = _fetch_trading_days(data_source, start_date=start, end_date=date)
    days = df[df["is_trading_day"] == "1"]["calendar_date"].tolist()
    prev = max([d for d in days if d < date], default=None)
    return prev or date


def next_trading_day(data_source: FinancialDataSource, *, date: str) -> str:
    target = datetime.strptime(date, "%Y-%m-%d")
    end = (target + timedelta(days=31)).strftime("%Y-%m-%d")
    df = _fetch_trading_days(data_source, start_date=date, end_date=end)
    days = df[df["is_trading_day"] == "1"]["calendar_date"].tolist()
    next_day = min([d for d in days if d > date], default=None)
    return next_day or date


def get_last_n_trading_days(data_source: FinancialDataSource, *, days: int) -> str:
    today = datetime.now()
    start = (today - timedelta(days=days * 2)).strftime("%Y-%m-%d")
    end = today.strftime("%Y-%m-%d")
    df = _fetch_trading_days(data_source, start_date=start, end_date=end)
    trading_days = df[df["is_trading_day"] == "1"]["calendar_date"].tolist()
    return ", ".join(trading_days[-days:]) if trading_days else ""


def get_recent_trading_range(data_source: FinancialDataSource, *, days: int) -> str:
    today = datetime.now()
    start = (today - timedelta(days=days * 2)).strftime("%Y-%m-%d")
    end = today.strftime("%Y-%m-%d")
    df = _fetch_trading_days(data_source, start_date=start, end_date=end)
    trading_days = df[df["is_trading_day"] == "1"]["calendar_date"].tolist()
    if not trading_days:
        return ""
    return f"{trading_days[-days]} 至 {trading_days[-1]}" if len(trading_days) >= days else f"{trading_days[0]} 至 {trading_days[-1]}"


def get_month_end_trading_dates(data_source: FinancialDataSource, *, year: int) -> str:
    results = []
    for month in range(1, 13):
        last_day = calendar.monthrange(year, month)[1]
        start_date = datetime(year, month, last_day - 7).strftime("%Y-%m-%d")
        end_date = datetime(year, month, last_day).strftime("%Y-%m-%d")
        df = _fetch_trading_days(data_source, start_date=start_date, end_date=end_date)
        trading_days = df[df["is_trading_day"] == "1"]["calendar_date"].tolist()
        if trading_days:
            results.append(trading_days[-1])
    return ", ".join(results)
