"""
MCP 服务器的宏观经济工具。
以一致的选项获取利率、货币供应量数据等。
"""
import logging
from typing import Optional

from mcp.server.fastmcp import FastMCP
from src.data_source_interface import FinancialDataSource
from src.tools.base import call_macro_data_tool

logger = logging.getLogger(__name__)


def register_macroeconomic_tools(app: FastMCP, active_data_source: FinancialDataSource):
    """
    向 MCP 应用注册宏观经济数据工具。

    Args:
        app (FastMCP): FastMCP 应用实例。
        active_data_source (FinancialDataSource): 激活的金融数据源。
    """

    @app.tool()
    def get_deposit_rate_data(start_date: Optional[str] = None, end_date: Optional[str] = None, limit: int = 250, format: str = "markdown") -> str:
        """
        获取指定日期范围内的存款基准利率（活期、定期）。

        Args:
            start_date (Optional[str], optional): 开始日期，格式为 'YYYY-MM-DD'。
            end_date (Optional[str], optional): 结束日期，格式为 'YYYY-MM-DD'。
            limit (int, optional): 返回的最大行数。默认为 250。
            format (str, optional): 输出格式。默认为 'markdown'。

        Returns:
            str: 包含存款利率数据的 Markdown 表格或错误消息。
        """
        return call_macro_data_tool(
            "get_deposit_rate_data",
            active_data_source.get_deposit_rate_data,
            "存款利率",
            start_date, end_date,
            limit=limit, format=format
        )

    @app.tool()
    def get_loan_rate_data(start_date: Optional[str] = None, end_date: Optional[str] = None, limit: int = 250, format: str = "markdown") -> str:
        """
        获取指定日期范围内的贷款基准利率。

        Args:
            start_date (Optional[str], optional): 开始日期，格式为 'YYYY-MM-DD'。
            end_date (Optional[str], optional): 结束日期，格式为 'YYYY-MM-DD'。
            limit (int, optional): 返回的最大行数。默认为 250。
            format (str, optional): 输出格式。默认为 'markdown'。

        Returns:
            str: 包含贷款利率数据的 Markdown 表格或错误消息。
        """
        return call_macro_data_tool(
            "get_loan_rate_data",
            active_data_source.get_loan_rate_data,
            "贷款利率",
            start_date, end_date,
            limit=limit, format=format
        )

    @app.tool()
    def get_required_reserve_ratio_data(start_date: Optional[str] = None, end_date: Optional[str] = None, year_type: str = '0', limit: int = 250, format: str = "markdown") -> str:
        """
        获取指定日期范围内的存款准备金率数据。

        Args:
            start_date (Optional[str], optional): 开始日期，格式为 'YYYY-MM-DD'。
            end_date (Optional[str], optional): 结束日期，格式为 'YYYY-MM-DD'。
            year_type (str, optional): 日期筛选的年份类型。'0' 为公告日期 (默认)，'1' 为生效日期。
            limit (int, optional): 返回的最大行数。默认为 250。
            format (str, optional): 输出格式。默认为 'markdown'。

        Returns:
            str: 包含存款准备金率数据的 Markdown 表格或错误消息。
        """
        if year_type not in ['0', '1']:
            logger.warning(f"请求了无效的年份类型: {year_type}")
            return "错误: 无效的年份类型 '{year_type}'。有效选项为 '0' (公告日期) 或 '1' (生效日期)。"

        return call_macro_data_tool(
            "get_required_reserve_ratio_data",
            active_data_source.get_required_reserve_ratio_data,
            "存款准备金率",
            start_date, end_date,
            limit=limit, format=format,
            yearType=year_type
        )

    @app.tool()
    def get_money_supply_data_month(start_date: Optional[str] = None, end_date: Optional[str] = None, limit: int = 250, format: str = "markdown") -> str:
        """
        获取指定日期范围内的月度货币供应量数据（M0, M1, M2）。

        Args:
            start_date (Optional[str], optional): 开始日期，格式为 'YYYY-MM'。
            end_date (Optional[str], optional): 结束日期，格式为 'YYYY-MM'。
            limit (int, optional): 返回的最大行数。默认为 250。
            format (str, optional): 输出格式。默认为 'markdown'。

        Returns:
            str: 包含月度货币供应量数据的 Markdown 表格或错误消息。
        """
        return call_macro_data_tool(
            "get_money_supply_data_month",
            active_data_source.get_money_supply_data_month,
            "月度货币供应量",
            start_date, end_date,
            limit=limit, format=format
        )

    @app.tool()
    def get_money_supply_data_year(start_date: Optional[str] = None, end_date: Optional[str] = None, limit: int = 250, format: str = "markdown") -> str:
        """
        获取指定日期范围内的年度货币供应量数据（M0, M1, M2 - 年末余额）。

        Args:
            start_date (Optional[str], optional): 开始年份，格式为 'YYYY'。
            end_date (Optional[str], optional): 结束年份，格式为 'YYYY'。
            limit (int, optional): 返回的最大行数。默认为 250。
            format (str, optional): 输出格式。默认为 'markdown'。

        Returns:
            str: 包含年度货币供应量数据的 Markdown 表格或错误消息。
        """
        return call_macro_data_tool(
            "get_money_supply_data_year",
            active_data_source.get_money_supply_data_year,
            "年度货币供应量",
            start_date, end_date,
            limit=limit, format=format
        )

    # 注意: SHIBOR 查询未在当前 baostock 绑定中提供，对应工具不实现。
