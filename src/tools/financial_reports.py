"""
注册并实现与财务报告相关的MCP工具。

该模块提供了一系列用于查询上市公司财务数据的工具，包括：
- 盈利能力 (`get_profit_data`)
- 营运能力 (`get_operation_data`)
- 成长能力 (`get_growth_data`)
- 偿债能力 (资产负债) (`get_balance_data`)
- 现金流量 (`get_cash_flow_data`)
- 杜邦分析 (`get_dupont_data`)
- 业绩快报 (`get_performance_express_report`)
- 业绩预告 (`get_forecast_report`)

这些工具大多利用了`src.tools.base`中的辅助函数来简化代码和统一错误处理。
"""
import logging
from typing import List, Optional

from mcp.server.fastmcp import FastMCP
from src.data_source_interface import FinancialDataSource
from src.tools.base import call_financial_data_tool

logger = logging.getLogger(__name__)


def register_financial_report_tools(app: FastMCP, active_data_source: FinancialDataSource):
    """
    向MCP应用注册所有与财务报告相关的工具。

    Args:
        app (FastMCP): FastMCP应用实例。
        active_data_source (FinancialDataSource): 已激活并实例化的金融数据源。
    """

    @app.tool()
    def get_profit_data(code: str, year: str, quarter: int, limit: int = 250, format: str = "markdown") -> str:
        """
        获取股票的季度盈利能力数据（例如，净资产收益率ROE、净利率）。

        Args:
            code (str): 股票代码 (例如, 'sh.600000')。
            year (str): 4位数字年份 (例如, '2023')。
            quarter (int): 季度 (1, 2, 3, 或 4)。
            limit (int, optional): 返回的最大行数。默认为 250。
            format (str, optional): 输出格式: 'markdown' | 'json' | 'csv'。默认为 'markdown'。

        Returns:
            str: 包含盈利能力指标的表格。
        """
        return call_financial_data_tool(
            "get_profit_data",
            active_data_source.get_profit_data,
            "Profitability",
            code, year, quarter,
            limit=limit, format=format
        )

    @app.tool()
    def get_operation_data(code: str, year: str, quarter: int, limit: int = 250, format: str = "markdown") -> str:
        """
        获取股票的季度营运能力数据（例如，周转率）。

        Args:
            code (str): 股票代码 (例如, 'sh.600000')。
            year (str): 4位数字年份 (例如, '2023')。
            quarter (int): 季度 (1, 2, 3, 或 4)。
            limit (int, optional): 返回的最大行数。默认为 250。
            format (str, optional): 输出格式: 'markdown' | 'json' | 'csv'。默认为 'markdown'。

        Returns:
            str: 包含营运能力指标的表格。
        """
        return call_financial_data_tool(
            "get_operation_data",
            active_data_source.get_operation_data,
            "Operation Capability",
            code, year, quarter,
            limit=limit, format=format
        )

    @app.tool()
    def get_growth_data(code: str, year: str, quarter: int, limit: int = 250, format: str = "markdown") -> str:
        """
        获取股票的季度成长能力数据（例如，同比增长率）。

        Args:
            code (str): 股票代码 (例如, 'sh.600000')。
            year (str): 4位数字年份 (例如, '2023')。
            quarter (int): 季度 (1, 2, 3, 或 4)。
            limit (int, optional): 返回的最大行数。默认为 250。
            format (str, optional): 输出格式: 'markdown' | 'json' | 'csv'。默认为 'markdown'。

        Returns:
            str: 包含成长能力指标的表格。
        """
        return call_financial_data_tool(
            "get_growth_data",
            active_data_source.get_growth_data,
            "Growth Capability",
            code, year, quarter,
            limit=limit, format=format
        )

    @app.tool()
    def get_balance_data(code: str, year: str, quarter: int, limit: int = 250, format: str = "markdown") -> str:
        """
        获取股票的季度偿债能力数据（例如，流动比率、资产负债率）。

        Args:
            code (str): 股票代码 (例如, 'sh.600000')。
            year (str): 4位数字年份 (例如, '2023')。
            quarter (int): 季度 (1, 2, 3, 或 4)。
            limit (int, optional): 返回的最大行数。默认为 250。
            format (str, optional): 输出格式: 'markdown' | 'json' | 'csv'。默认为 'markdown'。

        Returns:
            str: 包含偿债能力指标的表格。
        """
        return call_financial_data_tool(
            "get_balance_data",
            active_data_source.get_balance_data,
            "Balance Sheet",
            code, year, quarter,
            limit=limit, format=format
        )

    @app.tool()
    def get_cash_flow_data(code: str, year: str, quarter: int, limit: int = 250, format: str = "markdown") -> str:
        """
        获取股票的季度现金流量数据。

        Args:
            code (str): 股票代码 (例如, 'sh.600000')。
            year (str): 4位数字年份 (例如, '2023')。
            quarter (int): 季度 (1, 2, 3, 或 4)。
            limit (int, optional): 返回的最大行数。默认为 250。
            format (str, optional): 输出格式: 'markdown' | 'json' | 'csv'。默认为 'markdown'。

        Returns:
            str: 包含现金流量指标的表格。
        """
        return call_financial_data_tool(
            "get_cash_flow_data",
            active_data_source.get_cash_flow_data,
            "Cash Flow",
            code, year, quarter,
            limit=limit, format=format
        )

    @app.tool()
    def get_dupont_data(code: str, year: str, quarter: int, limit: int = 250, format: str = "markdown") -> str:
        """
        获取股票的季度杜邦分析数据（ROE分解）。

        Args:
            code (str): 股票代码 (例如, 'sh.600000')。
            year (str): 4位数字年份 (例如, '2023')。
            quarter (int): 季度 (1, 2, 3, 或 4)。
            limit (int, optional): 返回的最大行数。默认为 250。
            format (str, optional): 输出格式: 'markdown' | 'json' | 'csv'。默认为 'markdown'。

        Returns:
            str: 包含杜邦分析指标的表格。
        """
        return call_financial_data_tool(
            "get_dupont_data",
            active_data_source.get_dupont_data,
            "DuPont Analysis",
            code, year, quarter,
            limit=limit, format=format
        )

    @app.tool()
    def get_performance_express_report(code: str, start_date: str, end_date: str, limit: int = 250, format: str = "markdown") -> str:
        """
        获取指定日期范围内的股票业绩快报。
        注意：除非在特定情况下，否则公司不需要发布这些报告。

        Args:
            code (str): 股票代码 (例如, 'sh.600000')。
            start_date (str): 报告发布/更新的开始日期，格式为 'YYYY-MM-DD'。
            end_date (str): 报告发布/更新的结束日期，格式为 'YYYY-MM-DD'。
            limit (int, optional): 返回的最大行数。默认为 250。
            format (str, optional): 输出格式: 'markdown' | 'json' | 'csv'。默认为 'markdown'。

        Returns:
            str: 包含业绩快报数据的Markdown表格或错误消息。
        """
        logger.info(
            f"Tool 'get_performance_express_report' called for {code} ({start_date} to {end_date})")
        try:
            # Add date validation if desired
            df = active_data_source.get_performance_express_report(
                code=code, start_date=start_date, end_date=end_date)
            logger.info(
                f"Successfully retrieved performance express reports for {code}.")
            from src.formatting.markdown_formatter import format_table_output
            meta = {"code": code, "start_date": start_date, "end_date": end_date, "dataset": "performance_express"}
            return format_table_output(df, format=format, max_rows=limit, meta=meta)

        except Exception as e:
            logger.exception(
                f"Exception processing get_performance_express_report for {code}: {e}")
            return f"Error: An unexpected error occurred: {e}"

    @app.tool()
    def get_forecast_report(code: str, start_date: str, end_date: str, limit: int = 250, format: str = "markdown") -> str:
        """
        获取指定日期范围内的股票业绩预告。
        注意：除非在特定情况下，否则公司不需要发布这些报告。

        Args:
            code (str): 股票代码 (例如, 'sh.600000')。
            start_date (str): 报告发布/更新的开始日期，格式为 'YYYY-MM-DD'。
            end_date (str): 报告发布/更新的结束日期，格式为 'YYYY-MM-DD'。
            limit (int, optional): 返回的最大行数。默认为 250。
            format (str, optional): 输出格式: 'markdown' | 'json' | 'csv'。默认为 'markdown'。

        Returns:
            str: 包含业绩预告数据的Markdown表格或错误消息。
        """
        logger.info(
            f"Tool 'get_forecast_report' called for {code} ({start_date} to {end_date})")
        try:
            # Add date validation if desired
            df = active_data_source.get_forecast_report(
                code=code, start_date=start_date, end_date=end_date)
            logger.info(
                f"Successfully retrieved performance forecast reports for {code}.")
            from src.formatting.markdown_formatter import format_table_output
            meta = {"code": code, "start_date": start_date, "end_date": end_date, "dataset": "forecast"}
            return format_table_output(df, format=format, max_rows=limit, meta=meta)

        except Exception as e:
            logger.exception(
                f"Exception processing get_forecast_report for {code}: {e}")
            return f"Error: An unexpected error occurred: {e}"
