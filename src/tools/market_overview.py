"""
MCP 服务器的市场概览工具。
包括交易日历、股票列表和发现辅助工具。
"""
import logging
from typing import Optional

from mcp.server.fastmcp import FastMCP
from src.data_source_interface import FinancialDataSource, NoDataFoundError, LoginError, DataSourceError
from src.formatting.markdown_formatter import format_df_to_markdown, format_table_output

logger = logging.getLogger(__name__)


def register_market_overview_tools(app: FastMCP, active_data_source: FinancialDataSource):
    """
    向 MCP 应用注册市场概览工具。

    Args:
        app (FastMCP): FastMCP 应用实例。
        active_data_source (FinancialDataSource): 激活的金融数据源。
    """

    @app.tool()
    def get_trade_dates(start_date: Optional[str] = None, end_date: Optional[str] = None, limit: int = 250, format: str = "markdown") -> str:
        """
        获取指定范围内的交易日期。

        Args:
            start_date (Optional[str], optional): 开始日期，格式为 'YYYY-MM-DD'。如果为 None，默认为 2015-01-01。
            end_date (Optional[str], optional): 结束日期，格式为 'YYYY-MM-DD'。如果为 None，默认为当前日期。
            limit (int, optional): 返回的最大行数。默认为 250。
            format (str, optional): 输出格式。默认为 'markdown'。

        Returns:
            str: 包含 'is_trading_day' (1=交易日, 0=非交易日) 的 Markdown 表格。
        """
        logger.info(
            f"工具 'get_trade_dates' 已为范围 {start_date or '默认'} 到 {end_date or '默认'} 调用")
        try:
            df = active_data_source.get_trade_dates(
                start_date=start_date, end_date=end_date)
            logger.info("已成功检索交易日期。")
            meta = {"start_date": start_date or "default", "end_date": end_date or "default"}
            return format_table_output(df, format=format, max_rows=limit, meta=meta)

        except NoDataFoundError as e:
            logger.warning(f"未找到数据错误: {e}")
            return f"错误: {e}"
        except LoginError as e:
            logger.error(f"登录错误: {e}")
            return f"错误: 无法连接到数据源。{e}"
        except DataSourceError as e:
            logger.error(f"数据源错误: {e}")
            return f"错误: 获取数据时发生错误。{e}"
        except ValueError as e:
            logger.warning(f"值错误: {e}")
            return f"错误: 无效的输入参数。{e}"
        except Exception as e:
            logger.exception(
                f"处理 get_trade_dates 时发生意外异常: {e}")
            return f"错误: 发生意外错误: {e}"

    @app.tool()
    def get_all_stock(date: Optional[str] = None, limit: int = 250, format: str = "markdown") -> str:
        """
        获取指定日期的所有股票（A股和指数）列表及其交易状态。

        Args:
            date (Optional[str], optional): 日期，格式为 'YYYY-MM-DD'。如果为 None，则使用当前日期。
            limit (int, optional): 返回的最大行数。默认为 250。
            format (str, optional): 输出格式。默认为 'markdown'。

        Returns:
            str: 列出股票代码和交易状态 (1=交易, 0=停牌) 的 Markdown 表格。
        """
        logger.info(
            f"工具 'get_all_stock' 已为日期={date or '默认'} 调用")
        try:
            df = active_data_source.get_all_stock(date=date)
            logger.info(
                f"已成功检索日期为 {date or '默认'} 的股票列表。")
            meta = {"as_of": date or "default"}
            return format_table_output(df, format=format, max_rows=limit, meta=meta)

        except NoDataFoundError as e:
            logger.warning(f"未找到数据错误: {e}")
            return f"错误: {e}"
        except LoginError as e:
            logger.error(f"登录错误: {e}")
            return f"错误: 无法连接到数据源。{e}"
        except DataSourceError as e:
            logger.error(f"数据源错误: {e}")
            return f"错误: 获取数据时发生错误。{e}"
        except ValueError as e:
            logger.warning(f"值错误: {e}")
            return f"错误: 无效的输入参数。{e}"
        except Exception as e:
            logger.exception(
                f"处理 get_all_stock 时发生意外异常: {e}")
            return f"错误: 发生意外错误: {e}"

    @app.tool()
    def search_stocks(keyword: str, date: Optional[str] = None, limit: int = 50, format: str = "markdown") -> str:
        """
        按代码子串搜索指定日期的股票。

        Args:
            keyword (str): 股票代码中要匹配的子串 (例如, '600', '000001')。
            date (Optional[str], optional): 'YYYY-MM-DD' 格式的日期。如果为 None，则使用当前日期。
            limit (int, optional): 返回的最大行数。默认为 50。
            format (str, optional): 输出格式: 'markdown' | 'json' | 'csv'。默认为 'markdown'。

        Returns:
            str: 匹配的股票代码及其交易状态。
        """
        logger.info("工具 'search_stocks' 已调用 keyword=%s, date=%s, limit=%s, format=%s", keyword, date or "默认", limit, format)
        try:
            if not keyword or not keyword.strip():
                return "错误: 'keyword' 是必需的 (代码的子串)。"
            df = active_data_source.get_all_stock(date=date)
            if df is None or df.empty:
                return "(无可用数据显示)"
            kw = keyword.strip().lower()
            filtered = df[df["code"].str.lower().str.contains(kw, na=False)]
            meta = {"keyword": keyword, "as_of": date or "current"}
            return format_table_output(filtered, format=format, max_rows=limit, meta=meta)
        except Exception as e:
            logger.exception("处理 search_stocks 时发生异常: %s", e)
            return f"错误: 发生意外错误: {e}"

    @app.tool()
    def get_suspensions(date: Optional[str] = None, limit: int = 250, format: str = "markdown") -> str:
        """
        列出指定日期停牌的股票。

        Args:
            date (Optional[str], optional): 'YYYY-MM-DD' 格式的日期。如果为 None，则使用当前日期。
            limit (int, optional): 返回的最大行数。默认为 250。
            format (str, optional): 输出格式: 'markdown' | 'json' | 'csv'。默认为 'markdown'。

        Returns:
            str: tradeStatus==0 的股票表格。
        """
        logger.info("工具 'get_suspensions' 已调用 date=%s, limit=%s, format=%s", date or "current", limit, format)
        try:
            df = active_data_source.get_all_stock(date=date)
            if df is None or df.empty:
                return "(无可用数据显示)"
            if "tradeStatus" not in df.columns:
                return "错误: 数据源响应中不存在 'tradeStatus' 列。"
            suspended = df[df["tradeStatus"] == '0']
            meta = {"as_of": date or "current", "total_suspended": int(suspended.shape[0])}
            return format_table_output(suspended, format=format, max_rows=limit, meta=meta)
        except Exception as e:
            logger.exception("处理 get_suspensions 时发生异常: %s", e)
            return f"错误: 发生意外错误: {e}"
