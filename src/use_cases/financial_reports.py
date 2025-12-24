"""Use cases for financial report related tools."""
from typing import Optional

from src.data_source_interface import FinancialDataSource
from src.formatting.markdown_formatter import format_table_output
from src.services.validation import (
    validate_output_format,
    validate_quarter,
    validate_year,
)


def _format_financial_df(df, *, code: str, year: str | None, quarter: Optional[int], dataset: str, format: str, limit: int) -> str:
    meta = {"code": code, "dataset": dataset}
    if year:
        meta["year"] = year
    if quarter is not None:
        meta["quarter"] = quarter
    return format_table_output(df, format=format, max_rows=limit, meta=meta)


def fetch_profit_data(data_source: FinancialDataSource, *, code: str, year: str, quarter: int, limit: int, format: str) -> str:
    validate_year(year)
    validate_quarter(quarter)
    validate_output_format(format)
    df = data_source.get_profit_data(code=code, year=year, quarter=quarter)
    return _format_financial_df(df, code=code, year=year, quarter=quarter, dataset="Profitability", format=format, limit=limit)


def fetch_operation_data(data_source: FinancialDataSource, *, code: str, year: str, quarter: int, limit: int, format: str) -> str:
    validate_year(year)
    validate_quarter(quarter)
    validate_output_format(format)
    df = data_source.get_operation_data(code=code, year=year, quarter=quarter)
    return _format_financial_df(df, code=code, year=year, quarter=quarter, dataset="Operation Capability", format=format, limit=limit)


def fetch_growth_data(data_source: FinancialDataSource, *, code: str, year: str, quarter: int, limit: int, format: str) -> str:
    validate_year(year)
    validate_quarter(quarter)
    validate_output_format(format)
    df = data_source.get_growth_data(code=code, year=year, quarter=quarter)
    return _format_financial_df(df, code=code, year=year, quarter=quarter, dataset="Growth", format=format, limit=limit)


def fetch_balance_data(data_source: FinancialDataSource, *, code: str, year: str, quarter: int, limit: int, format: str) -> str:
    validate_year(year)
    validate_quarter(quarter)
    validate_output_format(format)
    df = data_source.get_balance_data(code=code, year=year, quarter=quarter)
    return _format_financial_df(df, code=code, year=year, quarter=quarter, dataset="Balance Sheet", format=format, limit=limit)


def fetch_cash_flow_data(data_source: FinancialDataSource, *, code: str, year: str, quarter: int, limit: int, format: str) -> str:
    validate_year(year)
    validate_quarter(quarter)
    validate_output_format(format)
    df = data_source.get_cash_flow_data(code=code, year=year, quarter=quarter)
    return _format_financial_df(df, code=code, year=year, quarter=quarter, dataset="Cash Flow", format=format, limit=limit)


def fetch_dupont_data(data_source: FinancialDataSource, *, code: str, year: str, quarter: int, limit: int, format: str) -> str:
    validate_year(year)
    validate_quarter(quarter)
    validate_output_format(format)
    df = data_source.get_dupont_data(code=code, year=year, quarter=quarter)
    return _format_financial_df(df, code=code, year=year, quarter=quarter, dataset="Dupont", format=format, limit=limit)


def fetch_performance_express_report(data_source: FinancialDataSource, *, code: str, start_date: str, end_date: str, limit: int, format: str) -> str:
    validate_output_format(format)
    df = data_source.get_performance_express_report(code=code, start_date=start_date, end_date=end_date)
    meta = {"code": code, "start_date": start_date, "end_date": end_date, "dataset": "Performance Express"}
    return format_table_output(df, format=format, max_rows=limit, meta=meta)


def fetch_forecast_report(data_source: FinancialDataSource, *, code: str, start_date: str, end_date: str, limit: int, format: str) -> str:
    validate_output_format(format)
    df = data_source.get_forecast_report(code=code, start_date=start_date, end_date=end_date)
    meta = {"code": code, "start_date": start_date, "end_date": end_date, "dataset": "Forecast"}
    return format_table_output(df, format=format, max_rows=limit, meta=meta)


def fetch_fina_indicator(data_source: FinancialDataSource, *, code: str, start_date: str, end_date: str, limit: int, format: str) -> str:
    """Fetch financial indicators (ROE, gross margin, net margin, etc.) within a date range."""
    validate_output_format(format)
    df = data_source.get_fina_indicator(code=code, start_date=start_date, end_date=end_date)
    meta = {"code": code, "start_date": start_date, "end_date": end_date, "dataset": "Financial Indicators"}
    return format_table_output(df, format=format, max_rows=limit, meta=meta)
