"""
Market overview tools for the MCP server.
Includes trading calendar, stock list, and discovery helpers.
"""
import logging
from typing import Optional

from mcp.server.fastmcp import FastMCP
from src.data_source_interface import FinancialDataSource
from src.services.tool_runner import run_tool_with_handling
from src.use_cases.market_overview import (
    fetch_all_stock,
    fetch_search_stocks,
    fetch_suspensions,
    fetch_trade_dates,
)

logger = logging.getLogger(__name__)


def register_market_overview_tools(app: FastMCP, active_data_source: FinancialDataSource):
    """
    Register market overview tools with the MCP app.

    Args:
        app: The FastMCP app instance
        active_data_source: The active financial data source
    """

    @app.tool()
    def get_trade_dates(start_date: Optional[str] = None, end_date: Optional[str] = None, limit: int = 250, format: str = "markdown") -> str:
        """
        Fetch trading dates within a specified range.

        Args:
            start_date: Optional. Start date in 'YYYY-MM-DD' format. Defaults to 2015-01-01 if None.
            end_date: Optional. End date in 'YYYY-MM-DD' format. Defaults to the current date if None.

        Returns:
            Markdown table with 'is_trading_day' (1=trading, 0=non-trading).
        """
        logger.info(f"Tool 'get_trade_dates' called for range {start_date or 'default'} to {end_date or 'default'}")
        return run_tool_with_handling(
            lambda: fetch_trade_dates(active_data_source, start_date=start_date, end_date=end_date, limit=limit, format=format),
            context="get_trade_dates",
        )

    @app.tool()
    def get_all_stock(date: Optional[str] = None, limit: int = 250, format: str = "markdown") -> str:
        """
        Fetch a list of all stocks (A-shares and indices) and their trading status for a date.

        Args:
            date: Optional. The date in 'YYYY-MM-DD' format. If None, uses the current date.

        Returns:
            Markdown table listing stock codes and trading status (1=trading, 0=suspended).
        """
        logger.info(f"Tool 'get_all_stock' called for date={date or 'default'}")
        return run_tool_with_handling(
            lambda: fetch_all_stock(active_data_source, date=date, limit=limit, format=format),
            context=f"get_all_stock:{date or 'default'}",
        )

    @app.tool()
    def search_stocks(keyword: str, date: Optional[str] = None, limit: int = 50, format: str = "markdown") -> str:
        """
        Search stocks by code substring on a date.

        Args:
            keyword: Substring to match in the stock code (e.g., '600', '000001').
            date: Optional 'YYYY-MM-DD'. If None, uses current date.
            limit: Max rows to return. Defaults to 50.
            format: Output format: 'markdown' | 'json' | 'csv'. Defaults to 'markdown'.

        Returns:
            Matching stock codes with their trading status.
        """
        logger.info("Tool 'search_stocks' called keyword=%s, date=%s, limit=%s, format=%s", keyword, date or "default", limit, format)
        return run_tool_with_handling(
            lambda: fetch_search_stocks(active_data_source, keyword=keyword, date=date, limit=limit, format=format),
            context=f"search_stocks:{keyword}",
        )

    @app.tool()
    def get_suspensions(date: Optional[str] = None, limit: int = 250, format: str = "markdown") -> str:
        """
        List suspended stocks for a date.

        Args:
            date: Optional 'YYYY-MM-DD'. If None, uses current date.
            limit: Max rows to return. Defaults to 250.
            format: Output format: 'markdown' | 'json' | 'csv'. Defaults to 'markdown'.

        Returns:
            Table of stocks where tradeStatus==0.
        """
        logger.info("Tool 'get_suspensions' called date=%s, limit=%s, format=%s", date or "current", limit, format)
        return run_tool_with_handling(
            lambda: fetch_suspensions(active_data_source, date=date, limit=limit, format=format),
            context=f"get_suspensions:{date or 'current'}",
        )
