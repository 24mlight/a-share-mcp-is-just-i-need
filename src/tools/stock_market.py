"""
Stock market tools for the MCP server.
Thin wrappers that delegate to use cases with shared validation and error handling.
"""
import logging
from typing import List, Optional

from mcp.server.fastmcp import FastMCP
from src.data_source_interface import FinancialDataSource
from src.services.tool_runner import run_tool_with_handling
from src.use_cases.stock_market import (
    fetch_adjust_factor_data,
    fetch_dividend_data,
    fetch_historical_k_data,
    fetch_stock_basic_info,
)

logger = logging.getLogger(__name__)


def register_stock_market_tools(app: FastMCP, active_data_source: FinancialDataSource):
    """
    Register stock market data tools with the MCP app.

    Args:
        app: The FastMCP app instance
        active_data_source: The active financial data source
    """

    @app.tool()
    def get_historical_k_data(
        code: str,
        start_date: str,
        end_date: str,
        frequency: str = "d",
        adjust_flag: str = "3",
        fields: Optional[List[str]] = None,
        limit: int = 250,
        format: str = "markdown",
    ) -> str:
        """
        Fetches historical K-line (OHLCV) data for a Chinese A-share stock.

        Args:
            code: The stock code in Baostock format (e.g., 'sh.600000', 'sz.000001').
            start_date: Start date in 'YYYY-MM-DD' format.
            end_date: End date in 'YYYY-MM-DD' format.
            frequency: Data frequency. Valid options (from Baostock):
                         'd': daily
                         'w': weekly
                         'm': monthly
                         '5': 5 minutes
                         '15': 15 minutes
                         '30': 30 minutes
                         '60': 60 minutes
                       Defaults to 'd'.
            adjust_flag: Adjustment flag for price/volume. Valid options (from Baostock):
                           '1': Forward adjusted (后复权)
                           '2': Backward adjusted (前复权)
                           '3': Non-adjusted (不复权)
                         Defaults to '3'.
            fields: Optional list of specific data fields to retrieve (must be valid Baostock fields).
                    If None or empty, default fields will be used (e.g., date, code, open, high, low, close, volume, amount, pctChg).
            limit: Max rows to return. Defaults to 250.
            format: Output format: 'markdown' | 'json' | 'csv'. Defaults to 'markdown'.

            Returns:
                A Markdown formatted string containing the K-line data table, or an error message.
                The table might be truncated if the result set is too large.
            """
        logger.info(
            f"Tool 'get_historical_k_data' called for {code} ({start_date}-{end_date}, freq={frequency}, adj={adjust_flag}, fields={fields})"
        )
        return run_tool_with_handling(
            lambda: fetch_historical_k_data(
                active_data_source,
                code=code,
                start_date=start_date,
                end_date=end_date,
                frequency=frequency,
                adjust_flag=adjust_flag,
                fields=fields,
                limit=limit,
                format=format,
            ),
            context=f"get_historical_k_data:{code}",
        )

    @app.tool()
    def get_stock_basic_info(code: str, fields: Optional[List[str]] = None, format: str = "markdown") -> str:
        """
        Fetches basic information for a given Chinese A-share stock.

        Args:
            code: The stock code in Baostock format (e.g., 'sh.600000', 'sz.000001').
            fields: Optional list to select specific columns from the available basic info
                    (e.g., ['code', 'code_name', 'industry', 'listingDate']).
                    If None or empty, returns all available basic info columns from Baostock.

        Returns:
            Basic stock information in the requested format.
        """
        logger.info(f"Tool 'get_stock_basic_info' called for {code} (fields={fields})")
        return run_tool_with_handling(
            lambda: fetch_stock_basic_info(
                active_data_source, code=code, fields=fields, format=format
            ),
            context=f"get_stock_basic_info:{code}",
        )

    @app.tool()
    def get_dividend_data(code: str, year: str, year_type: str = "report", limit: int = 250, format: str = "markdown") -> str:
        """
        Fetches dividend information for a given stock code and year.

        Args:
            code: The stock code in Baostock format (e.g., 'sh.600000', 'sz.000001').
            year: The year to query (e.g., '2023').
            year_type: Type of year. Valid options (from Baostock):
                         'report': Announcement year (预案公告年份)
                         'operate': Ex-dividend year (除权除息年份)
                       Defaults to 'report'.

        Returns:
            Dividend records table.
        """
        logger.info(f"Tool 'get_dividend_data' called for {code}, year={year}, year_type={year_type}")
        return run_tool_with_handling(
            lambda: fetch_dividend_data(
                active_data_source,
                code=code,
                year=year,
                year_type=year_type,
                limit=limit,
                format=format,
            ),
            context=f"get_dividend_data:{code}:{year}",
        )

    @app.tool()
    def get_adjust_factor_data(code: str, start_date: str, end_date: str, limit: int = 250, format: str = "markdown") -> str:
        """
        Fetches adjustment factor data for a given stock code and date range.
        Uses Baostock's "涨跌幅复权算法" factors. Useful for calculating adjusted prices.

        Args:
            code: The stock code in Baostock format (e.g., 'sh.600000', 'sz.000001').
            start_date: Start date in 'YYYY-MM-DD' format.
            end_date: End date in 'YYYY-MM-DD' format.

        Returns:
            Adjustment factors table.
        """
        logger.info(f"Tool 'get_adjust_factor_data' called for {code} ({start_date} to {end_date})")
        return run_tool_with_handling(
            lambda: fetch_adjust_factor_data(
                active_data_source,
                code=code,
                start_date=start_date,
                end_date=end_date,
                limit=limit,
                format=format,
            ),
            context=f"get_adjust_factor_data:{code}",
        )
