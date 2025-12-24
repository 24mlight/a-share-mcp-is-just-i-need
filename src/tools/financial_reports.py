"""
Financial report tools for the MCP server.
Thin wrappers delegating to use cases with shared validation and error handling.
"""
import logging
from typing import Optional

from mcp.server.fastmcp import FastMCP
from src.data_source_interface import FinancialDataSource
from src.services.tool_runner import run_tool_with_handling
from src.use_cases.financial_reports import (
    fetch_balance_data,
    fetch_cash_flow_data,
    fetch_dupont_data,
    fetch_fina_indicator,
    fetch_forecast_report,
    fetch_growth_data,
    fetch_operation_data,
    fetch_performance_express_report,
    fetch_profit_data,
)

logger = logging.getLogger(__name__)


def register_financial_report_tools(app: FastMCP, active_data_source: FinancialDataSource):
    """
    Register financial report related tools with the MCP app.
    """

    @app.tool()
    def get_profit_data(code: str, year: str, quarter: int, limit: int = 250, format: str = "markdown") -> str:
        """Quarterly profitability data."""
        return run_tool_with_handling(
            lambda: fetch_profit_data(active_data_source, code=code, year=year, quarter=quarter, limit=limit, format=format),
            context=f"get_profit_data:{code}:{year}Q{quarter}",
        )

    @app.tool()
    def get_operation_data(code: str, year: str, quarter: int, limit: int = 250, format: str = "markdown") -> str:
        """Quarterly operation capability data."""
        return run_tool_with_handling(
            lambda: fetch_operation_data(active_data_source, code=code, year=year, quarter=quarter, limit=limit, format=format),
            context=f"get_operation_data:{code}:{year}Q{quarter}",
        )

    @app.tool()
    def get_growth_data(code: str, year: str, quarter: int, limit: int = 250, format: str = "markdown") -> str:
        """Quarterly growth capability data."""
        return run_tool_with_handling(
            lambda: fetch_growth_data(active_data_source, code=code, year=year, quarter=quarter, limit=limit, format=format),
            context=f"get_growth_data:{code}:{year}Q{quarter}",
        )

    @app.tool()
    def get_balance_data(code: str, year: str, quarter: int, limit: int = 250, format: str = "markdown") -> str:
        """Quarterly balance sheet data."""
        return run_tool_with_handling(
            lambda: fetch_balance_data(active_data_source, code=code, year=year, quarter=quarter, limit=limit, format=format),
            context=f"get_balance_data:{code}:{year}Q{quarter}",
        )

    @app.tool()
    def get_cash_flow_data(code: str, year: str, quarter: int, limit: int = 250, format: str = "markdown") -> str:
        """Quarterly cash flow data."""
        return run_tool_with_handling(
            lambda: fetch_cash_flow_data(active_data_source, code=code, year=year, quarter=quarter, limit=limit, format=format),
            context=f"get_cash_flow_data:{code}:{year}Q{quarter}",
        )

    @app.tool()
    def get_dupont_data(code: str, year: str, quarter: int, limit: int = 250, format: str = "markdown") -> str:
        """Quarterly Dupont analysis data."""
        return run_tool_with_handling(
            lambda: fetch_dupont_data(active_data_source, code=code, year=year, quarter=quarter, limit=limit, format=format),
            context=f"get_dupont_data:{code}:{year}Q{quarter}",
        )

    @app.tool()
    def get_performance_express_report(code: str, start_date: str, end_date: str, limit: int = 250, format: str = "markdown") -> str:
        """Performance express report within date range."""
        return run_tool_with_handling(
            lambda: fetch_performance_express_report(
                active_data_source, code=code, start_date=start_date, end_date=end_date, limit=limit, format=format
            ),
            context=f"get_performance_express_report:{code}:{start_date}-{end_date}",
        )

    @app.tool()
    def get_forecast_report(code: str, start_date: str, end_date: str, limit: int = 250, format: str = "markdown") -> str:
        """Earnings forecast report within date range."""
        return run_tool_with_handling(
            lambda: fetch_forecast_report(
                active_data_source, code=code, start_date=start_date, end_date=end_date, limit=limit, format=format
            ),
            context=f"get_forecast_report:{code}:{start_date}-{end_date}",
        )

    @app.tool()
    def get_fina_indicator(code: str, start_date: str, end_date: str, limit: int = 250, format: str = "markdown") -> str:
        """
        Aggregated financial indicators from 6 Baostock APIs into one convenient query.

        **Data is returned by QUARTER** (Q1, Q2, Q3, Q4) based on financial report dates.
        Input date range determines which quarters to fetch.

        Combines data from:
        - 盈利能力 (Profitability): roeAvg, npMargin, gpMargin, epsTTM
        - 营运能力 (Operation): NRTurnRatio, INVTurnRatio, CATurnRatio
        - 成长能力 (Growth): YOYNI, YOYEquity, YOYAsset
        - 偿债能力 (Solvency): currentRatio, quickRatio, liabilityToAsset
        - 现金流量 (Cash Flow): CFOToOR, CFOToNP, CAToAsset
        - 杜邦分析 (DuPont): dupontROE, dupontAssetTurn, dupontPnitoni

        Output columns include prefixes: profit_*, operation_*, growth_*,
        balance_*, cashflow_*, dupont_* to distinguish data sources.
        """
        return run_tool_with_handling(
            lambda: fetch_fina_indicator(
                active_data_source, code=code, start_date=start_date, end_date=end_date, limit=limit, format=format
            ),
            context=f"get_fina_indicator:{code}:{start_date}-{end_date}",
        )
