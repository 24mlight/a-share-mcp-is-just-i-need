"""
注册并实现与宏观经济数据相关的MCP工具。

该模块提供了查询关键宏观经济指标的功能，包括：
- 存款利率 (`get_deposit_rate_data`)
- 贷款利率 (`get_loan_rate_data`)
- 存款准备金率 (`get_required_reserve_ratio_data`)
- 货币供应量（月度/年度） (`get_money_supply_data_month`, `get_money_supply_data_year`)

这些工具为分析市场整体流动性和货币政策提供了数据支持。
"""
import logging
from typing import Optional

from mcp.server.fastmcp import FastMCP
from src.data_source_interface import FinancialDataSource
from src.tools.base import call_macro_data_tool

logger = logging.getLogger(__name__)


def register_macroeconomic_tools(app: FastMCP, active_data_source: FinancialDataSource):
    """
    向MCP应用注册所有与宏观经济数据相关的工具。

    Args:
        app (FastMCP): FastMCP应用实例。
        active_data_source (FinancialDataSource): 已激活并实例化的金融数据源。
    """

    @app.tool()
    def get_deposit_rate_data(start_date: Optional[str] = None, end_date: Optional[str] = None, limit: int = 250, format: str = "markdown") -> str:
        """
        获取指定日期范围内的基准存款利率（活期、定期）。

        Args:
            start_date (Optional[str], optional): 'YYYY-MM-DD'格式的开始日期。
            end_date (Optional[str], optional): 'YYYY-MM-DD'格式的结束日期。
            limit (int, optional): 返回的最大行数。默认为 250。
            format (str, optional): 输出格式: 'markdown' | 'json' | 'csv'。默认为 'markdown'。

        Returns:
            str: 包含存款利率数据的Markdown表格或错误消息。
        """
        return call_macro_data_tool(
            "get_deposit_rate_data",
            active_data_source.get_deposit_rate_data,
            "Deposit Rate",
            start_date, end_date,
            limit=limit, format=format
        )

    @app.tool()
    def get_loan_rate_data(start_date: Optional[str] = None, end_date: Optional[str] = None, limit: int = 250, format: str = "markdown") -> str:
        """
        获取指定日期范围内的基准贷款利率。

        Args:
            start_date (Optional[str], optional): 'YYYY-MM-DD'格式的开始日期。
            end_date (Optional[str], optional): 'YYYY-MM-DD'格式的结束日期。
            limit (int, optional): 返回的最大行数。默认为 250。
            format (str, optional): 输出格式: 'markdown' | 'json' | 'csv'。默认为 'markdown'。

        Returns:
            str: 包含贷款利率数据的Markdown表格或错误消息。
        """
        return call_macro_data_tool(
            "get_loan_rate_data",
            active_data_source.get_loan_rate_data,
            "Loan Rate",
            start_date, end_date,
            limit=limit, format=format
        )

    @app.tool()
    def get_required_reserve_ratio_data(start_date: Optional[str] = None, end_date: Optional[str] = None, year_type: str = '0', limit: int = 250, format: str = "markdown") -> str:
        """
        获取指定日期范围内的存款准备金率数据。

        Args:
            start_date (Optional[str], optional): 'YYYY-MM-DD'格式的开始日期。
            end_date (Optional[str], optional): 'YYYY-MM-DD'格式的结束日期。
            year_type (str, optional): 日期筛选的年份类型。'0'为公告日期（默认），'1'为生效日期。
            limit (int, optional): 返回的最大行数。默认为 250。
            format (str, optional): 输出格式: 'markdown' | 'json' | 'csv'。默认为 'markdown'。

        Returns:
            str: 包含存款准备金率数据的Markdown表格或错误消息。
        """
        # Basic validation for year_type
        if year_type not in ['0', '1']:
            logger.warning(f"Invalid year_type requested: {year_type}")
            return "Error: Invalid year_type '{year_type}'. Valid options are '0' (announcement date) or '1' (effective date)."

        return call_macro_data_tool(
            "get_required_reserve_ratio_data",
            active_data_source.get_required_reserve_ratio_data,
            "Required Reserve Ratio",
            start_date, end_date,
            limit=limit, format=format,
            yearType=year_type  # Pass the extra arg correctly named for Baostock
        )

    @app.tool()
    def get_money_supply_data_month(start_date: Optional[str] = None, end_date: Optional[str] = None, limit: int = 250, format: str = "markdown") -> str:
        """
        获取指定日期范围内的月度货币供应量数据（M0, M1, M2）。

        Args:
            start_date (Optional[str], optional): 'YYYY-MM'格式的开始日期。
            end_date (Optional[str], optional): 'YYYY-MM'格式的结束日期。
            limit (int, optional): 返回的最大行数。默认为 250。
            format (str, optional): 输出格式: 'markdown' | 'json' | 'csv'。默认为 'markdown'。

        Returns:
            str: 包含月度货币供应量数据的Markdown表格或错误消息。
        """
        # Add specific validation for YYYY-MM format if desired
        return call_macro_data_tool(
            "get_money_supply_data_month",
            active_data_source.get_money_supply_data_month,
            "Monthly Money Supply",
            start_date, end_date,
            limit=limit, format=format
        )

    @app.tool()
    def get_money_supply_data_year(start_date: Optional[str] = None, end_date: Optional[str] = None, limit: int = 250, format: str = "markdown") -> str:
        """
        获取指定年份范围内的年度货币供应量数据（M0, M1, M2 - 年末余额）。

        Args:
            start_date (Optional[str], optional): 'YYYY'格式的开始年份。
            end_date (Optional[str], optional): 'YYYY'格式的结束年份。
            limit (int, optional): 返回的最大行数。默认为 250。
            format (str, optional): 输出格式: 'markdown' | 'json' | 'csv'。默认为 'markdown'。

        Returns:
            str: 包含年度货币供应量数据的Markdown表格或错误消息。
        """
        # Add specific validation for YYYY format if desired
        return call_macro_data_tool(
            "get_money_supply_data_year",
            active_data_source.get_money_supply_data_year,
            "Yearly Money Supply",
            start_date, end_date,
            limit=limit, format=format
        )

    # Note: SHIBOR 查询未在当前 baostock 绑定中提供，对应工具不实现。
