"""Use cases for index and industry related tools."""
from typing import Optional

from src.data_source_interface import FinancialDataSource
from src.formatting.markdown_formatter import format_table_output
from src.services.validation import validate_output_format, validate_index_key, validate_non_empty_str

INDEX_MAP = {
    "hs300": "hs300",
    "沪深300": "hs300",
    "zz500": "zz500",
    "中证500": "zz500",
    "sz50": "sz50",
    "上证50": "sz50",
}


def fetch_stock_industry(data_source: FinancialDataSource, *, code: Optional[str], date: Optional[str], limit: int, format: str) -> str:
    validate_output_format(format)
    df = data_source.get_stock_industry(code=code, date=date)
    meta = {"code": code or "all", "as_of": date or "latest"}
    return format_table_output(df, format=format, max_rows=limit, meta=meta)


def fetch_index_constituents(data_source: FinancialDataSource, *, index: str, date: Optional[str], limit: int, format: str) -> str:
    validate_output_format(format)
    key = validate_index_key(index, INDEX_MAP)
    if key == "hs300":
        df = data_source.get_hs300_stocks(date=date)
    elif key == "sz50":
        df = data_source.get_sz50_stocks(date=date)
    else:
        df = data_source.get_zz500_stocks(date=date)
    meta = {"index": key, "as_of": date or "latest"}
    return format_table_output(df, format=format, max_rows=limit, meta=meta)


def fetch_list_industries(data_source: FinancialDataSource, *, date: Optional[str], format: str) -> str:
    validate_output_format(format)
    df = data_source.get_stock_industry(code=None, date=date)
    if df is None or df.empty:
        return "(No data available to display)"
    col = "industry" if "industry" in df.columns else df.columns[-1]
    out = df[[col]].drop_duplicates().sort_values(by=col)
    out = out.rename(columns={col: "industry"})
    meta = {"as_of": date or "latest", "count": int(out.shape[0])}
    return format_table_output(out, format=format, max_rows=out.shape[0], meta=meta)


def fetch_industry_members(data_source: FinancialDataSource, *, industry: str, date: Optional[str], limit: int, format: str) -> str:
    validate_output_format(format)
    validate_non_empty_str(industry, "industry")
    df = data_source.get_stock_industry(code=None, date=date)
    if df is None or df.empty:
        return "(No data available to display)"
    col = "industry" if "industry" in df.columns else df.columns[-1]
    filtered = df[df[col] == industry].copy()
    meta = {"industry": industry, "as_of": date or "latest"}
    return format_table_output(filtered, format=format, max_rows=limit, meta=meta)
