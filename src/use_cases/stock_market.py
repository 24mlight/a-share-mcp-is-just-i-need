"""Stock market use cases orchestrating data fetch and formatting."""
from typing import List, Optional

import pandas as pd

from src.data_source_interface import FinancialDataSource
from src.formatting.markdown_formatter import format_table_output
from src.services.validation import (
    validate_adjust_flag,
    validate_frequency,
    validate_output_format,
    validate_year,
    validate_year_type,
)


def fetch_historical_k_data(
    data_source: FinancialDataSource,
    *,
    code: str,
    start_date: str,
    end_date: str,
    frequency: str = "d",
    adjust_flag: str = "3",
    fields: Optional[List[str]] = None,
    limit: int = 250,
    format: str = "markdown",
) -> str:
    validate_frequency(frequency)
    validate_adjust_flag(adjust_flag)
    validate_output_format(format)

    df = data_source.get_historical_k_data(
        code=code,
        start_date=start_date,
        end_date=end_date,
        frequency=frequency,
        adjust_flag=adjust_flag,
        fields=fields,
    )
    meta = {
        "code": code,
        "start_date": start_date,
        "end_date": end_date,
        "frequency": frequency,
        "adjust_flag": adjust_flag,
    }
    return format_table_output(df, format=format, max_rows=limit, meta=meta)


def fetch_stock_basic_info(
    data_source: FinancialDataSource,
    *,
    code: str,
    fields: Optional[List[str]] = None,
    format: str = "markdown",
) -> str:
    validate_output_format(format)
    df = data_source.get_stock_basic_info(code=code, fields=fields)
    meta = {"code": code}
    return format_table_output(df, format=format, max_rows=df.shape[0] if df is not None else 0, meta=meta)


def fetch_dividend_data(
    data_source: FinancialDataSource,
    *,
    code: str,
    year: str,
    year_type: str = "report",
    limit: int = 250,
    format: str = "markdown",
) -> str:
    validate_year(year)
    validate_year_type(year_type)
    validate_output_format(format)

    df = data_source.get_dividend_data(code=code, year=year, year_type=year_type)
    meta = {"code": code, "year": year, "year_type": year_type}
    return format_table_output(df, format=format, max_rows=limit, meta=meta)


def fetch_adjust_factor_data(
    data_source: FinancialDataSource,
    *,
    code: str,
    start_date: str,
    end_date: str,
    limit: int = 250,
    format: str = "markdown",
) -> str:
    validate_output_format(format)
    df = data_source.get_adjust_factor_data(code=code, start_date=start_date, end_date=end_date)
    meta = {"code": code, "start_date": start_date, "end_date": end_date}
    return format_table_output(df, format=format, max_rows=limit, meta=meta)
