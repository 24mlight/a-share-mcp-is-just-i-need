"""Use cases for macroeconomic data tools."""
from typing import Optional

from src.data_source_interface import FinancialDataSource
from src.formatting.markdown_formatter import format_table_output
from src.services.validation import validate_output_format, validate_year_type_reserve


def fetch_deposit_rate_data(data_source: FinancialDataSource, *, start_date: Optional[str], end_date: Optional[str], limit: int, format: str) -> str:
    validate_output_format(format)
    df = data_source.get_deposit_rate_data(start_date=start_date, end_date=end_date)
    meta = {"dataset": "deposit_rate", "start_date": start_date, "end_date": end_date}
    return format_table_output(df, format=format, max_rows=limit, meta=meta)


def fetch_loan_rate_data(data_source: FinancialDataSource, *, start_date: Optional[str], end_date: Optional[str], limit: int, format: str) -> str:
    validate_output_format(format)
    df = data_source.get_loan_rate_data(start_date=start_date, end_date=end_date)
    meta = {"dataset": "loan_rate", "start_date": start_date, "end_date": end_date}
    return format_table_output(df, format=format, max_rows=limit, meta=meta)


def fetch_required_reserve_ratio_data(data_source: FinancialDataSource, *, start_date: Optional[str], end_date: Optional[str], year_type: str, limit: int, format: str) -> str:
    validate_output_format(format)
    validate_year_type_reserve(year_type)
    df = data_source.get_required_reserve_ratio_data(start_date=start_date, end_date=end_date, year_type=year_type)
    meta = {"dataset": "required_reserve_ratio", "start_date": start_date, "end_date": end_date, "year_type": year_type}
    return format_table_output(df, format=format, max_rows=limit, meta=meta)


def fetch_money_supply_data_month(data_source: FinancialDataSource, *, start_date: Optional[str], end_date: Optional[str], limit: int, format: str) -> str:
    validate_output_format(format)
    df = data_source.get_money_supply_data_month(start_date=start_date, end_date=end_date)
    meta = {"dataset": "money_supply_month", "start_date": start_date, "end_date": end_date}
    return format_table_output(df, format=format, max_rows=limit, meta=meta)


def fetch_money_supply_data_year(data_source: FinancialDataSource, *, start_date: Optional[str], end_date: Optional[str], limit: int, format: str) -> str:
    validate_output_format(format)
    df = data_source.get_money_supply_data_year(start_date=start_date, end_date=end_date)
    meta = {"dataset": "money_supply_year", "start_date": start_date, "end_date": end_date}
    return format_table_output(df, format=format, max_rows=limit, meta=meta)
