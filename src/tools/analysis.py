"""
Analysis tools for MCP server.
Delegates heavy lifting to use-case layer.
"""
import logging

from mcp.server.fastmcp import FastMCP
from src.data_source_interface import FinancialDataSource
from src.services.tool_runner import run_tool_with_handling
from src.use_cases.analysis import build_stock_analysis_report

logger = logging.getLogger(__name__)


def register_analysis_tools(app: FastMCP, active_data_source: FinancialDataSource):
    """Register analysis tools."""

    @app.tool()
    def get_stock_analysis(code: str, analysis_type: str = "fundamental") -> str:
        """
        提供基于数据的股票分析报告，而非投资建议。

        Args:
            code: 股票代码，如'sh.600000'
            analysis_type: 'fundamental'|'technical'|'comprehensive'
        """
        logger.info(f"Tool 'get_stock_analysis' called for {code}, type={analysis_type}")
        return run_tool_with_handling(
            lambda: build_stock_analysis_report(active_data_source, code=code, analysis_type=analysis_type),
            context=f"get_stock_analysis:{code}:{analysis_type}",
        )
