"""
MCP 服务器的指数相关工具。
包括指数成分股和行业实用工具，参数清晰易发现。
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
    向 MCP 应用注册指数相关工具。

    Args:
        app (FastMCP): FastMCP 应用实例。
        active_data_source (FinancialDataSource): 激活的金融数据源。
    """

    @app.tool()
    def get_stock_industry(code: Optional[str] = None, date: Optional[str] = None, limit: int = 250, format: str = "markdown") -> str:
        """
        获取特定股票或指定日期所有股票的行业分类。

        Args:
            code (Optional[str], optional): Baostock 格式的可选股票代码 (例如, 'sh.600000')。如果为 None，则返回所有股票。
            date (Optional[str], optional): 可选的 'YYYY-MM-DD' 格式日期。如果为 None，则使用最新的可用日期。
            limit (int, optional): 返回的最大行数。默认为 250。
            format (str, optional): 输出格式。默认为 'markdown'。

        Returns:
            str: 包含行业数据的 Markdown 表格或错误消息。
        """
        log_msg = f"工具 'get_stock_industry' 已为代码={code or '全部'}, 日期={date or '最新'} 调用"
        logger.info(log_msg)
        try:
            df = active_data_source.get_stock_industry(code=code, date=date)
            logger.info(
                f"已成功检索代码为 {code or '全部'}, 日期为 {date or '最新'} 的行业数据。")
            meta = {"code": code or "all", "as_of": date or "latest"}
            return format_table_output(df, format=format, max_rows=limit, meta=meta)

        except Exception as e:
            logger.exception(
                f"处理 get_stock_industry 时发生异常: {e}")
            return f"错误: 发生意外错误: {e}"

    @app.tool()
    def get_sz50_stocks(date: Optional[str] = None, limit: int = 250, format: str = "markdown") -> str:
        """
        获取给定日期的上证50指数成分股。

        Args:
            date (Optional[str], optional): 可选的 'YYYY-MM-DD' 格式日期。如果为 None，则使用最新的可用日期。
            limit (int, optional): 返回的最大行数。默认为 250。
            format (str, optional): 输出格式。默认为 'markdown'。

        Returns:
            str: 包含上证50成分股的 Markdown 表格或错误消息。
        """
        return call_index_constituent_tool(
            "get_sz50_stocks",
            active_data_source.get_sz50_stocks,
            "上证50",
            date,
            limit=limit, format=format
        )

    @app.tool()
    def get_hs300_stocks(date: Optional[str] = None, limit: int = 250, format: str = "markdown") -> str:
        """
        获取给定日期的沪深300指数成分股。

        Args:
            date (Optional[str], optional): 可选的 'YYYY-MM-DD' 格式日期。如果为 None，则使用最新的可用日期。
            limit (int, optional): 返回的最大行数。默认为 250。
            format (str, optional): 输出格式。默认为 'markdown'。

        Returns:
            str: 包含沪深300成分股的 Markdown 表格或错误消息。
        """
        return call_index_constituent_tool(
            "get_hs300_stocks",
            active_data_source.get_hs300_stocks,
            "沪深300",
            date,
            limit=limit, format=format
        )

    @app.tool()
    def get_zz500_stocks(date: Optional[str] = None, limit: int = 250, format: str = "markdown") -> str:
        """
        获取给定日期的中证500指数成分股。

        Args:
            date (Optional[str], optional): 可选的 'YYYY-MM-DD' 格式日期。如果为 None，则使用最新的可用日期。
            limit (int, optional): 返回的最大行数。默认为 250。
            format (str, optional): 输出格式。默认为 'markdown'。

        Returns:
            str: 包含中证500成分股的 Markdown 表格或错误消息。
        """
        return call_index_constituent_tool(
            "get_zz500_stocks",
            active_data_source.get_zz500_stocks,
            "中证500",
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
            index (str): 'hs300' (沪深300), 'sz50' (上证50), 'zz500' (中证500) 之一。
            date (Optional[str], optional): 可选的 'YYYY-MM-DD' 格式日期。如果为 None，则使用最新的可用日期。
            limit (int, optional): 返回的最大行数 (分页辅助)。默认为 250。
            format (str, optional): 输出格式: 'markdown' | 'json' | 'csv'。默认为 'markdown'。

        Returns:
            str: 请求格式的指数成分股表格。默认为 Markdown。

        Examples:
            - get_index_constituents(index='hs300')
            - get_index_constituents(index='sz50', date='2024-12-31', format='json', limit=100)
        """
        logger.info(
            f"工具 'get_index_constituents' 已调用 index={index}, date={date or '最新'}, limit={limit}, format={format}")
        try:
            key = (index or "").strip().lower()
            if key not in {"hs300", "sz50", "zz500"}:
                return "错误: 无效的指数。有效选项为 'hs300', 'sz50', 'zz500'。"

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
            logger.exception("处理 get_index_constituents 时发生异常: %s", e)
            return f"错误: 发生意外错误: {e}"

    @app.tool()
    def list_industries(date: Optional[str] = None, format: str = "markdown") -> str:
        """
        列出给定日期的不同行业。

        Args:
            date (Optional[str], optional): 可选的 'YYYY-MM-DD' 格式日期。如果为 None，则使用最新的可用日期。
            format (str, optional): 输出格式: 'markdown' | 'json' | 'csv'。默认为 'markdown'。

        Returns:
            str: 单列的行业表格。
        """
        logger.info("工具 'list_industries' 已调用 date=%s", date or "最新")
        try:
            df = active_data_source.get_stock_industry(code=None, date=date)
            if df is None or df.empty:
                return "(无可用数据显示)"
            col = "industry" if "industry" in df.columns else df.columns[-1]
            out = df[[col]].drop_duplicates().sort_values(by=col)
            out = out.rename(columns={col: "industry"})
            meta = {"as_of": date or "latest", "count": int(out.shape[0])}
            return format_table_output(out, format=format, max_rows=out.shape[0], meta=meta)
        except Exception as e:
            logger.exception("处理 list_industries 时发生异常: %s", e)
            return f"错误: 发生意外错误: {e}"

    @app.tool()
    def get_industry_members(
        industry: str,
        date: Optional[str] = None,
        limit: int = 250,
        format: str = "markdown",
    ) -> str:
        """
        获取在指定日期属于给定行业的所有股票。

        Args:
            industry (str): 要筛选的精确行业名称 (参见 list_industries)。
            date (Optional[str], optional): 可选的 'YYYY-MM-DD' 格式日期。如果为 None，则使用最新的可用日期。
            limit (int, optional): 返回的最大行数。默认为 250。
            format (str, optional): 输出格式: 'markdown' | 'json' | 'csv'。默认为 'markdown'。

        Returns:
            str: 给定行业中的股票表格。
        """
        logger.info(
            "工具 'get_industry_members' 已调用 industry=%s, date=%s, limit=%s, format=%s",
            industry, date or "最新", limit, format,
        )
        try:
            if not industry or not industry.strip():
                return "错误: 'industry' 是必需的。调用 list_industries() 来发现可用的值。"
            df = active_data_source.get_stock_industry(code=None, date=date)
            if df is None or df.empty:
                return "(无可用数据显示)"
            col = "industry" if "industry" in df.columns else df.columns[-1]
            filtered = df[df[col] == industry].copy()
            meta = {"industry": industry, "as_of": date or "latest"}
            return format_table_output(filtered, format=format, max_rows=limit, meta=meta)
        except Exception as e:
            logger.exception("处理 get_industry_members 时发生异常: %s", e)
            return f"错误: 发生意外错误: {e}"
