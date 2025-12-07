"""Use cases for market overview tools."""
from typing import Optional

from src.data_source_interface import FinancialDataSource
from src.formatting.markdown_formatter import format_table_output
from src.services.validation import validate_output_format, validate_non_empty_str


def fetch_trade_dates(data_source: FinancialDataSource, *, start_date: Optional[str], end_date: Optional[str], limit: int, format: str) -> str:
    validate_output_format(format)
    df = data_source.get_trade_dates(start_date=start_date, end_date=end_date)
    meta = {"start_date": start_date or "default", "end_date": end_date or "default"}
    return format_table_output(df, format=format, max_rows=limit, meta=meta)


def fetch_all_stock(data_source: FinancialDataSource, *, date: Optional[str], limit: int, format: str) -> str:
    validate_output_format(format)
    df = data_source.get_all_stock(date=date)
    meta = {"as_of": date or "default"}
    return format_table_output(df, format=format, max_rows=limit, meta=meta)


def fetch_search_stocks(data_source: FinancialDataSource, *, keyword: str, date: Optional[str], limit: int, format: str) -> str:
    validate_output_format(format)
    validate_non_empty_str(keyword, "keyword")
    df = data_source.get_all_stock(date=date)
    if df is None or df.empty:
        return "(No data available to display)"
    kw = keyword.strip().lower()
    filtered = df[df["code"].str.lower().str.contains(kw, na=False)]
    meta = {"keyword": keyword, "as_of": date or "current"}
    return format_table_output(filtered, format=format, max_rows=limit, meta=meta)


def fetch_suspensions(data_source: FinancialDataSource, *, date: Optional[str], limit: int, format: str) -> str:
    validate_output_format(format)
    df = data_source.get_all_stock(date=date)
    if df is None or df.empty:
        return "(No data available to display)"
    if "tradeStatus" not in df.columns:
        raise ValueError("'tradeStatus' column not present in data source response.")
    suspended = df[df["tradeStatus"] == '0']
    meta = {"as_of": date or "current", "total_suspended": int(suspended.shape[0])}
    return format_table_output(suspended, format=format, max_rows=limit, meta=meta)
