"""
Index-related tools for the MCP server.
Delegates to use-case layer for validation and formatting.
"""
import logging
from typing import Optional

from mcp.server.fastmcp import FastMCP
from src.data_source_interface import FinancialDataSource
from src.services.tool_runner import run_tool_with_handling
from src.use_cases.indices import (
    fetch_index_constituents,
    fetch_industry_members,
    fetch_list_industries,
    fetch_stock_industry,
)

logger = logging.getLogger(__name__)


def register_index_tools(app: FastMCP, active_data_source: FinancialDataSource):
    """Register index related tools with the MCP app."""

    @app.tool()
    def get_stock_industry(code: Optional[str] = None, date: Optional[str] = None, limit: int = 250, format: str = "markdown") -> str:
        """Get industry classification for a specific stock or all stocks on a date."""
        logger.info(f"Tool 'get_stock_industry' called for code={code or 'all'}, date={date or 'latest'}")
        return run_tool_with_handling(
            lambda: fetch_stock_industry(active_data_source, code=code, date=date, limit=limit, format=format),
            context=f"get_stock_industry:{code or 'all'}",
        )

    @app.tool()
    def get_sz50_stocks(date: Optional[str] = None, limit: int = 250, format: str = "markdown") -> str:
        """SZSE 50 constituents."""
        return run_tool_with_handling(
            lambda: fetch_index_constituents(active_data_source, index="sz50", date=date, limit=limit, format=format),
            context="get_sz50_stocks",
        )

    @app.tool()
    def get_hs300_stocks(date: Optional[str] = None, limit: int = 250, format: str = "markdown") -> str:
        """CSI 300 constituents."""
        return run_tool_with_handling(
            lambda: fetch_index_constituents(active_data_source, index="hs300", date=date, limit=limit, format=format),
            context="get_hs300_stocks",
        )

    @app.tool()
    def get_zz500_stocks(date: Optional[str] = None, limit: int = 250, format: str = "markdown") -> str:
        """CSI 500 constituents."""
        return run_tool_with_handling(
            lambda: fetch_index_constituents(active_data_source, index="zz500", date=date, limit=limit, format=format),
            context="get_zz500_stocks",
        )

    @app.tool()
    def get_index_constituents(index: str, date: Optional[str] = None, limit: int = 250, format: str = "markdown") -> str:
        """Generic index constituent fetch (hs300/sz50/zz500)."""
        return run_tool_with_handling(
            lambda: fetch_index_constituents(active_data_source, index=index, date=date, limit=limit, format=format),
            context=f"get_index_constituents:{index}",
        )

    @app.tool()
    def list_industries(date: Optional[str] = None, format: str = "markdown") -> str:
        """List distinct industries for a given date."""
        logger.info("Tool 'list_industries' called date=%s", date or "latest")
        return run_tool_with_handling(
            lambda: fetch_list_industries(active_data_source, date=date, format=format),
            context="list_industries",
        )

    @app.tool()
    def get_industry_members(industry: str, date: Optional[str] = None, limit: int = 250, format: str = "markdown") -> str:
        """Get all stocks in a given industry on a date."""
        logger.info("Tool 'get_industry_members' called industry=%s, date=%s", industry, date or "latest")
        return run_tool_with_handling(
            lambda: fetch_industry_members(active_data_source, industry=industry, date=date, limit=limit, format=format),
            context=f"get_industry_members:{industry}",
        )
