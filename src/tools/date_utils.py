"""
Date utility tools for the MCP server.
Delegates to use-case layer for consistent behavior.
"""
import logging
from typing import Optional

from mcp.server.fastmcp import FastMCP
from src.data_source_interface import FinancialDataSource
from src.services.tool_runner import run_tool_with_handling
from src.use_cases import date_utils as uc_date

logger = logging.getLogger(__name__)


def register_date_utils_tools(app: FastMCP, active_data_source: FinancialDataSource):
    """Register date utility tools."""

    @app.tool()
    def get_latest_trading_date() -> str:
        """Get the latest trading date up to today."""
        logger.info("Tool 'get_latest_trading_date' called")
        return run_tool_with_handling(
            lambda: uc_date.get_latest_trading_date(active_data_source),
            context="get_latest_trading_date",
        )

    @app.tool()
    def get_market_analysis_timeframe(period: str = "recent") -> str:
        """Return a human-friendly timeframe label."""
        logger.info(f"Tool 'get_market_analysis_timeframe' called with period={period}")
        return run_tool_with_handling(
            lambda: uc_date.get_market_analysis_timeframe(period=period),
            context="get_market_analysis_timeframe",
        )

    @app.tool()
    def is_trading_day(date: str) -> str:
        """Check if a specific date is a trading day."""
        return run_tool_with_handling(
            lambda: uc_date.is_trading_day(active_data_source, date=date),
            context=f"is_trading_day:{date}",
        )

    @app.tool()
    def previous_trading_day(date: str) -> str:
        """Get the previous trading day before the given date."""
        return run_tool_with_handling(
            lambda: uc_date.previous_trading_day(active_data_source, date=date),
            context=f"previous_trading_day:{date}",
        )

    @app.tool()
    def next_trading_day(date: str) -> str:
        """Get the next trading day after the given date."""
        return run_tool_with_handling(
            lambda: uc_date.next_trading_day(active_data_source, date=date),
            context=f"next_trading_day:{date}",
        )

    @app.tool()
    def get_last_n_trading_days(days: int = 5) -> str:
        """Return the last N trading dates."""
        return run_tool_with_handling(
            lambda: uc_date.get_last_n_trading_days(active_data_source, days=days),
            context=f"get_last_n_trading_days:{days}",
        )

    @app.tool()
    def get_recent_trading_range(days: int = 5) -> str:
        """Return a date range string covering the recent N trading days."""
        return run_tool_with_handling(
            lambda: uc_date.get_recent_trading_range(active_data_source, days=days),
            context=f"get_recent_trading_range:{days}",
        )

    @app.tool()
    def get_month_end_trading_dates(year: int) -> str:
        """Return month-end trading dates for a given year."""
        return run_tool_with_handling(
            lambda: uc_date.get_month_end_trading_dates(active_data_source, year=year),
            context=f"get_month_end_trading_dates:{year}",
        )
