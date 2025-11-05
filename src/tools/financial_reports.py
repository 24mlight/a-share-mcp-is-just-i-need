"""
MCP 服务器的财务报告工具。
提供清晰、强类型的参数；一致的输出选项。
"""
import logging
from typing import List, Optional

from mcp.server.fastmcp import FastMCP
from src.data_source_interface import FinancialDataSource
from src.tools.base import call_financial_data_tool

logger = logging.getLogger(__name__)


def register_financial_report_tools(app: FastMCP, active_data_source: FinancialDataSource):
    """
    向 MCP 应用注册财务报告相关工具。

    Args:
        app (FastMCP): FastMCP 应用实例。
        active_data_source (FinancialDataSource): 激活的金融数据源。
    """

    @app.tool()
    def get_profit_data(code: str, year: str, quarter: int, limit: int = 250, format: str = "markdown") -> str:
        """
        获取股票的季度盈利能力数据（例如，净资产收益率，净利润率）。

        Args:
            code (str): 股票代码 (例如, 'sh.600000')。
            year (str): 4位数字的年份 (例如, '2023')。
            quarter (int): 季度 (1, 2, 3, 或 4)。
            limit (int, optional): 返回的最大行数。默认为 250。
            format (str, optional): 输出格式。默认为 'markdown'。

        Returns:
            str: 盈利能力指标表。
        """
        return call_financial_data_tool(
            "get_profit_data",
            active_data_source.get_profit_data,
            "盈利能力",
            code, year, quarter,
            limit=limit, format=format
        )

    @app.tool()
    def get_operation_data(code: str, year: str, quarter: int, limit: int = 250, format: str = "markdown") -> str:
        """
        获取股票的季度运营能力数据（例如，周转率）。

        Args:
            code (str): 股票代码 (例如, 'sh.600000')。
            year (str): 4位数字的年份 (例如, '2023')。
            quarter (int): 季度 (1, 2, 3, 或 4)。
            limit (int, optional): 返回的最大行数。默认为 250。
            format (str, optional): 输出格式。默认为 'markdown'。

        Returns:
            str: 运营能力指标表。
        """
        return call_financial_data_tool(
            "get_operation_data",
            active_data_source.get_operation_data,
            "运营能力",
            code, year, quarter,
            limit=limit, format=format
        )

    @app.tool()
    def get_growth_data(code: str, year: str, quarter: int, limit: int = 250, format: str = "markdown") -> str:
        """
        获取股票的季度成长能力数据（例如，同比增长率）。

        Args:
            code (str): 股票代码 (例如, 'sh.600000')。
            year (str): 4位数字的年份 (例如, '2023')。
            quarter (int): 季度 (1, 2, 3, 或 4)。
            limit (int, optional): 返回的最大行数。默认为 250。
            format (str, optional): 输出格式。默认为 'markdown'。

        Returns:
            str: 成长能力指标表。
        """
        return call_financial_data_tool(
            "get_growth_data",
            active_data_source.get_growth_data,
            "成长能力",
            code, year, quarter,
            limit=limit, format=format
        )

    @app.tool()
    def get_balance_data(code: str, year: str, quarter: int, limit: int = 250, format: str = "markdown") -> str:
        """
        获取股票的季度资产负债/偿债能力数据（例如，流动比率，资产负债率）。

        Args:
            code (str): 股票代码 (例如, 'sh.600000')。
            year (str): 4位数字的年份 (例如, '2023')。
            quarter (int): 季度 (1, 2, 3, 或 4)。
            limit (int, optional): 返回的最大行数。默认为 250。
            format (str, optional): 输出格式。默认为 'markdown'。

        Returns:
            str: 资产负债指标表。
        """
        return call_financial_data_tool(
            "get_balance_data",
            active_data_source.get_balance_data,
            "资产负债",
            code, year, quarter,
            limit=limit, format=format
        )

    @app.tool()
    def get_cash_flow_data(code: str, year: str, quarter: int, limit: int = 250, format: str = "markdown") -> str:
        """
        获取股票的季度现金流量数据（例如，现金流量/营业收入比率）。

        Args:
            code (str): 股票代码 (例如, 'sh.600000')。
            year (str): 4位数字的年份 (例如, '2023')。
            quarter (int): 季度 (1, 2, 3, 或 4)。
            limit (int, optional): 返回的最大行数。默认为 250。
            format (str, optional): 输出格式。默认为 'markdown'。

        Returns:
            str: 现金流量指标表。
        """
        return call_financial_data_tool(
            "get_cash_flow_data",
            active_data_source.get_cash_flow_data,
            "现金流量",
            code, year, quarter,
            limit=limit, format=format
        )

    @app.tool()
    def get_dupont_data(code: str, year: str, quarter: int, limit: int = 250, format: str = "markdown") -> str:
        """
        获取股票的季度杜邦分析数据（净资产收益率分解）。

        Args:
            code (str): 股票代码 (例如, 'sh.600000')。
            year (str): 4位数字的年份 (例如, '2023')。
            quarter (int): 季度 (1, 2, 3, 或 4)。
            limit (int, optional): 返回的最大行数。默认为 250。
            format (str, optional): 输出格式。默认为 'markdown'。

        Returns:
            str: 杜邦分析指标表。
        """
        return call_financial_data_tool(
            "get_dupont_data",
            active_data_source.get_dupont_data,
            "杜邦分析",
            code, year, quarter,
            limit=limit, format=format
        )

    @app.tool()
    def get_performance_express_report(code: str, start_date: str, end_date: str, limit: int = 250, format: str = "markdown") -> str:
        """
        获取指定日期范围内股票的业绩快报。
        注意: 除特定情况外，公司无需发布这些报告。

        Args:
            code (str): 股票代码 (例如, 'sh.600000')。
            start_date (str): 开始日期 (报告发布/更新)，格式为 'YYYY-MM-DD'。
            end_date (str): 结束日期 (报告发布/更新)，格式为 'YYYY-MM-DD'。
            limit (int, optional): 返回的最大行数。默认为 250。
            format (str, optional): 输出格式。默认为 'markdown'。

        Returns:
            str: 包含业绩快报数据的 Markdown 表格或错误消息。
        """
        logger.info(
            f"工具 'get_performance_express_report' 已为 {code} 调用 ({start_date} 到 {end_date})")
        try:
            df = active_data_source.get_performance_express_report(
                code=code, start_date=start_date, end_date=end_date)
            logger.info(
                f"已成功检索 {code} 的业绩快报。")
            from src.formatting.markdown_formatter import format_table_output
            meta = {"code": code, "start_date": start_date, "end_date": end_date, "dataset": "performance_express"}
            return format_table_output(df, format=format, max_rows=limit, meta=meta)

        except Exception as e:
            logger.exception(
                f"处理 get_performance_express_report for {code} 时发生异常: {e}")
            return f"错误: 发生意外错误: {e}"

    @app.tool()
    def get_forecast_report(code: str, start_date: str, end_date: str, limit: int = 250, format: str = "markdown") -> str:
        """
        获取指定日期范围内股票的业绩预告。
        注意: 除特定情况外，公司无需发布这些报告。

        Args:
            code (str): 股票代码 (例如, 'sh.600000')。
            start_date (str): 开始日期 (报告发布/更新)，格式为 'YYYY-MM-DD'。
            end_date (str): 结束日期 (报告发布/更新)，格式为 'YYYY-MM-DD'。
            limit (int, optional): 返回的最大行数。默认为 250。
            format (str, optional): 输出格式。默认为 'markdown'。

        Returns:
            str: 包含业绩预告数据的 Markdown 表格或错误消息。
        """
        logger.info(
            f"工具 'get_forecast_report' 已为 {code} 调用 ({start_date} 到 {end_date})")
        try:
            df = active_data_source.get_forecast_report(
                code=code, start_date=start_date, end_date=end_date)
            logger.info(
                f"已成功检索 {code} 的业绩预告。")
            from src.formatting.markdown_formatter import format_table_output
            meta = {"code": code, "start_date": start_date, "end_date": end_date, "dataset": "forecast"}
            return format_table_output(df, format=format, max_rows=limit, meta=meta)

        except Exception as e:
            logger.exception(
                f"处理 get_forecast_report for {code} 时发生异常: {e}")
            return f"错误: 发生意外错误: {e}"
