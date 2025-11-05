"""
注册并实现与指数和行业相关的MCP工具。

该模块提供了以下功能：
- 获取股票所属行业 (`get_stock_industry`)
- 获取主要指数（上证50、沪深300、中证500）的成分股 (`get_sz50_stocks`, `get_hs300_stocks`, `get_zz500_stocks`, `get_index_constituents`)
- 列出所有行业分类 (`list_industries`)
- 获取特定行业的成分股 (`get_industry_members`)

这些工具旨在为用户提供关于市场结构和分类的宏观视角。
"""
import logging
from typing import Optional, List

from mcp.server.fastmcp import FastMCP
from src.data_source_interface import FinancialDataSource
from src.tools.base import call_index_constituent_tool
from src.formatting.markdown_formatter import format_table_output

logger = logging.getLogger(__name__)


def register_index_tools(app: FastMCP, active_data_source: FinancialDataSource):
    """
    向MCP应用注册所有与指数和行业相关的工具。

    Args:
        app (FastMCP): FastMCP应用实例。
        active_data_source (FinancialDataSource): 已激活并实例化的金融数据源。
    """

    @app.tool()
    def get_stock_industry(code: Optional[str] = None, date: Optional[str] = None, limit: int = 250, format: str = "markdown") -> str:
        """
        获取指定日期单个股票或所有股票的行业分类。

        Args:
            code (Optional[str], optional): Baostock格式的可选股票代码 (例如, 'sh.600000')。如果为None，则返回所有股票的行业信息。
            date (Optional[str], optional): 可选的 'YYYY-MM-DD' 格式日期。如果为None，则使用最新可用日期。
            limit (int, optional): 返回的最大行数。默认为 250。
            format (str, optional): 输出格式: 'markdown' | 'json' | 'csv'。默认为 'markdown'。

        Returns:
            str: 包含行业数据的Markdown表格或错误消息。
        """
        log_msg = f"Tool 'get_stock_industry' called for code={code or 'all'}, date={date or 'latest'}"
        logger.info(log_msg)
        try:
            # Add date validation if desired
            df = active_data_source.get_stock_industry(code=code, date=date)
            logger.info(
                f"Successfully retrieved industry data for {code or 'all'}, {date or 'latest'}.")
            meta = {"code": code or "all", "as_of": date or "latest"}
            return format_table_output(df, format=format, max_rows=limit, meta=meta)

        except Exception as e:
            logger.exception(
                f"Exception processing get_stock_industry: {e}")
            return f"Error: An unexpected error occurred: {e}"

    @app.tool()
    def get_sz50_stocks(date: Optional[str] = None, limit: int = 250, format: str = "markdown") -> str:
        """
        获取指定日期的上证50指数成分股。

        Args:
            date (Optional[str], optional): 'YYYY-MM-DD'格式的日期。如果为None，则使用最新可用日期。
            limit (int, optional): 返回的最大行数。默认为 250。
            format (str, optional): 输出格式: 'markdown' | 'json' | 'csv'。默认为 'markdown'。

        Returns:
            str: 包含上证50成分股的Markdown表格或错误消息。
        """
        return call_index_constituent_tool(
            "get_sz50_stocks",
            active_data_source.get_sz50_stocks,
            "SZSE 50",
            date,
            limit=limit, format=format
        )

    @app.tool()
    def get_hs300_stocks(date: Optional[str] = None, limit: int = 250, format: str = "markdown") -> str:
        """
        获取指定日期的沪深300指数成分股。

        Args:
            date (Optional[str], optional): 'YYYY-MM-DD'格式的日期。如果为None，则使用最新可用日期。
            limit (int, optional): 返回的最大行数。默认为 250。
            format (str, optional): 输出格式: 'markdown' | 'json' | 'csv'。默认为 'markdown'。

        Returns:
            str: 包含沪深300成分股的Markdown表格或错误消息。
        """
        return call_index_constituent_tool(
            "get_hs300_stocks",
            active_data_source.get_hs300_stocks,
            "CSI 300",
            date,
            limit=limit, format=format
        )

    @app.tool()
    def get_zz500_stocks(date: Optional[str] = None, limit: int = 250, format: str = "markdown") -> str:
        """
        获取指定日期的中证500指数成分股。

        Args:
            date (Optional[str], optional): 'YYYY-MM-DD'格式的日期。如果为None，则使用最新可用日期。
            limit (int, optional): 返回的最大行数。默认为 250。
            format (str, optional): 输出格式: 'markdown' | 'json' | 'csv'。默认为 'markdown'。

        Returns:
            str: 包含中证500成分股的Markdown表格或错误消息。
        """
        return call_index_constituent_tool(
            "get_zz500_stocks",
            active_data_source.get_zz500_stocks,
            "CSI 500",
            date,
            limit=limit, format=format
        )

    @app.tool()
    def get_index_constituents(
        index: str,
        date: Optional[str] = None,
        limit: int = 250,
        format: str = "markdown",
    ) -> str:
        """
        获取主要指数的成分股。

        Args:
            index (str): 'hs300' (沪深300), 'sz50' (上证50), 'zz500' (中证500)之一。
            date (Optional[str], optional): 'YYYY-MM-DD'格式的日期。如果为None，则使用最新可用日期。
            limit (int, optional): 返回的最大行数。默认为 250。
            format (str, optional): 输出格式: 'markdown' | 'json' | 'csv'。默认为 'markdown'。

        Returns:
            str: 按请求格式（默认为Markdown）输出的指数成分股表格。

        Examples:
            - get_index_constituents(index='hs300')
            - get_index_constituents(index='sz50', date='2024-12-31', format='json', limit=100)
        """
        logger.info(
            f"Tool 'get_index_constituents' called index={index}, date={date or 'latest'}, limit={limit}, format={format}")
        try:
            key = (index or "").strip().lower()
            if key not in {"hs300", "sz50", "zz500"}:
                return "Error: Invalid index. Valid options are 'hs300', 'sz50', 'zz500'."

            if key == "hs300":
                df = active_data_source.get_hs300_stocks(date=date)
            elif key == "sz50":
                df = active_data_source.get_sz50_stocks(date=date)
            else:
                df = active_data_source.get_zz500_stocks(date=date)

            meta = {
                "index": key,
                "as_of": date or "latest",
            }
            return format_table_output(df, format=format, max_rows=limit, meta=meta)
        except Exception as e:
            logger.exception("Exception processing get_index_constituents: %s", e)
            return f"Error: An unexpected error occurred: {e}"

    @app.tool()
    def list_industries(date: Optional[str] = None, format: str = "markdown") -> str:
        """
        列出指定日期的所有不同行业。

        Args:
            date (Optional[str], optional): 'YYYY-MM-DD'格式的日期。如果为None，则使用最新可用日期。
            format (str, optional): 输出格式: 'markdown' | 'json' | 'csv'。默认为 'markdown'。

        Returns:
            str: 包含所有行业的单列表格。
        """
        logger.info("Tool 'list_industries' called date=%s", date or "latest")
        try:
            df = active_data_source.get_stock_industry(code=None, date=date)
            if df is None or df.empty:
                return "(No data available to display)"
            col = "industry" if "industry" in df.columns else df.columns[-1]
            out = df[[col]].drop_duplicates().sort_values(by=col)
            out = out.rename(columns={col: "industry"})
            meta = {"as_of": date or "latest", "count": int(out.shape[0])}
            return format_table_output(out, format=format, max_rows=out.shape[0], meta=meta)
        except Exception as e:
            logger.exception("Exception processing list_industries: %s", e)
            return f"Error: An unexpected error occurred: {e}"

    @app.tool()
    def get_industry_members(
        industry: str,
        date: Optional[str] = None,
        limit: int = 250,
        format: str = "markdown",
    ) -> str:
        """
        获取在指定日期属于某一特定行业的所有股票。

        Args:
            industry (str): 要筛选的精确行业名称 (可参考 `list_industries` 的输出)。
            date (Optional[str], optional): 'YYYY-MM-DD'格式的日期。如果为None，则使用最新可用日期。
            limit (int, optional): 返回的最大行数。默认为 250。
            format (str, optional): 输出格式: 'markdown' | 'json' | 'csv'。默认为 'markdown'。

        Returns:
            str: 包含指定行业内所有股票的表格。
        """
        logger.info(
            "Tool 'get_industry_members' called industry=%s, date=%s, limit=%s, format=%s",
            industry, date or "latest", limit, format,
        )
        try:
            if not industry or not industry.strip():
                return "Error: 'industry' is required. Call list_industries() to discover available values."
            df = active_data_source.get_stock_industry(code=None, date=date)
            if df is None or df.empty:
                return "(No data available to display)"
            col = "industry" if "industry" in df.columns else df.columns[-1]
            filtered = df[df[col] == industry].copy()
            meta = {"industry": industry, "as_of": date or "latest"}
            return format_table_output(filtered, format=format, max_rows=limit, meta=meta)
        except Exception as e:
            logger.exception("Exception processing get_industry_members: %s", e)
            return f"Error: An unexpected error occurred: {e}"
