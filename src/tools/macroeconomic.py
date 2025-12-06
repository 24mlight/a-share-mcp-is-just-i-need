"""
Macroeconomic tools for the MCP server.
Delegates to use cases with shared validation and error handling.
"""
import logging
from typing import Optional

from mcp.server.fastmcp import FastMCP
from src.data_source_interface import FinancialDataSource
from src.services.tool_runner import run_tool_with_handling
from src.use_cases.macroeconomic import (
    fetch_deposit_rate_data,
    fetch_loan_rate_data,
    fetch_money_supply_data_month,
    fetch_money_supply_data_year,
    fetch_required_reserve_ratio_data,
)

logger = logging.getLogger(__name__)


def register_macroeconomic_tools(app: FastMCP, active_data_source: FinancialDataSource):
    """Register macroeconomic tools."""

    @app.tool()
    def get_deposit_rate_data(start_date: Optional[str] = None, end_date: Optional[str] = None, limit: int = 250, format: str = "markdown") -> str:
        """Benchmark deposit rates."""
        return run_tool_with_handling(
            lambda: fetch_deposit_rate_data(active_data_source, start_date=start_date, end_date=end_date, limit=limit, format=format),
            context="get_deposit_rate_data",
        )

    @app.tool()
    def get_loan_rate_data(start_date: Optional[str] = None, end_date: Optional[str] = None, limit: int = 250, format: str = "markdown") -> str:
        """Benchmark loan rates."""
        return run_tool_with_handling(
            lambda: fetch_loan_rate_data(active_data_source, start_date=start_date, end_date=end_date, limit=limit, format=format),
            context="get_loan_rate_data",
        )

    @app.tool()
    def get_required_reserve_ratio_data(start_date: Optional[str] = None, end_date: Optional[str] = None, year_type: str = '0', limit: int = 250, format: str = "markdown") -> str:
        """Required reserve ratio data."""
        return run_tool_with_handling(
            lambda: fetch_required_reserve_ratio_data(
                active_data_source, start_date=start_date, end_date=end_date, year_type=year_type, limit=limit, format=format
            ),
            context="get_required_reserve_ratio_data",
        )

    @app.tool()
    def get_money_supply_data_month(start_date: Optional[str] = None, end_date: Optional[str] = None, limit: int = 250, format: str = "markdown") -> str:
        """Monthly money supply data."""
        return run_tool_with_handling(
            lambda: fetch_money_supply_data_month(
                active_data_source, start_date=start_date, end_date=end_date, limit=limit, format=format
            ),
            context="get_money_supply_data_month",
        )

    @app.tool()
    def get_money_supply_data_year(start_date: Optional[str] = None, end_date: Optional[str] = None, limit: int = 250, format: str = "markdown") -> str:
        """Yearly money supply data."""
        return run_tool_with_handling(
            lambda: fetch_money_supply_data_year(
                active_data_source, start_date=start_date, end_date=end_date, limit=limit, format=format
            ),
            context="get_money_supply_data_year",
        )
