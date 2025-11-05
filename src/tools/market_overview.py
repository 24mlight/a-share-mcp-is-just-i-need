"""
注册并实现与市场概览相关的MCP工具。

该模块提供的工具用于获取市场的宏观信息，例如：
- 交易日历 (`get_trade_dates`)
- 每日所有股票列表 (`get_all_stock`)
- 根据关键词搜索股票 (`search_stocks`)
- 获取当日停牌股票列表 (`get_suspensions`)

这些工具帮助用户了解市场的整体状态和特定日期的交易情况。
"""
import logging
from typing import Optional

from mcp.server.fastmcp import FastMCP
from src.data_source_interface import FinancialDataSource, NoDataFoundError, LoginError, DataSourceError
from src.formatting.markdown_formatter import format_df_to_markdown, format_table_output

logger = logging.getLogger(__name__)


def register_market_overview_tools(app: FastMCP, active_data_source: FinancialDataSource):
    """
    向MCP应用注册所有与市场概览相关的工具。

    Args:
        app (FastMCP): FastMCP应用实例。
        active_data_source (FinancialDataSource): 已激活并实例化的金融数据源。
    """

    @app.tool()
    def get_trade_dates(start_date: Optional[str] = None, end_date: Optional[str] = None, limit: int = 250, format: str = "markdown") -> str:
        """
        获取指定范围内的交易日。

        Args:
            start_date (Optional[str], optional): 'YYYY-MM-DD'格式的开始日期。如果为None，默认为'2015-01-01'。
            end_date (Optional[str], optional): 'YYYY-MM-DD'格式的结束日期。如果为None，默认为当前日期。
            limit (int, optional): 返回的最大行数。默认为 250。
            format (str, optional): 输出格式: 'markdown' | 'json' | 'csv'。默认为 'markdown'。

        Returns:
            str: 包含'is_trading_day'列（1=交易日, 0=非交易日）的Markdown表格。
        """
        logger.info(
            f"Tool 'get_trade_dates' called for range {start_date or 'default'} to {end_date or 'default'}")
        try:
            # Add date validation if desired
            df = active_data_source.get_trade_dates(
                start_date=start_date, end_date=end_date)
            logger.info("Successfully retrieved trade dates.")
            meta = {"start_date": start_date or "default", "end_date": end_date or "default"}
            return format_table_output(df, format=format, max_rows=limit, meta=meta)

        except NoDataFoundError as e:
            logger.warning(f"NoDataFoundError: {e}")
            return f"Error: {e}"
        except LoginError as e:
            logger.error(f"LoginError: {e}")
            return f"Error: Could not connect to data source. {e}"
        except DataSourceError as e:
            logger.error(f"DataSourceError: {e}")
            return f"Error: An error occurred while fetching data. {e}"
        except ValueError as e:
            logger.warning(f"ValueError: {e}")
            return f"Error: Invalid input parameter. {e}"
        except Exception as e:
            logger.exception(
                f"Unexpected Exception processing get_trade_dates: {e}")
            return f"Error: An unexpected error occurred: {e}"

    @app.tool()
    def get_all_stock(date: Optional[str] = None, limit: int = 250, format: str = "markdown") -> str:
        """
        获取指定日期的所有股票（A股和指数）列表及其交易状态。

        Args:
            date (Optional[str], optional): 'YYYY-MM-DD'格式的日期。如果为None，则使用当前日期。
            limit (int, optional): 返回的最大行数。默认为 250。
            format (str, optional): 输出格式: 'markdown' | 'json' | 'csv'。默认为 'markdown'。

        Returns:
            str: 列出股票代码和交易状态（1=交易, 0=停牌）的Markdown表格。
        """
        logger.info(
            f"Tool 'get_all_stock' called for date={date or 'default'}")
        try:
            # Add date validation if desired
            df = active_data_source.get_all_stock(date=date)
            logger.info(
                f"Successfully retrieved stock list for {date or 'default'}.")
            meta = {"as_of": date or "default"}
            return format_table_output(df, format=format, max_rows=limit, meta=meta)

        except NoDataFoundError as e:
            logger.warning(f"NoDataFoundError: {e}")
            return f"Error: {e}"
        except LoginError as e:
            logger.error(f"LoginError: {e}")
            return f"Error: Could not connect to data source. {e}"
        except DataSourceError as e:
            logger.error(f"DataSourceError: {e}")
            return f"Error: An error occurred while fetching data. {e}"
        except ValueError as e:
            logger.warning(f"ValueError: {e}")
            return f"Error: Invalid input parameter. {e}"
        except Exception as e:
            logger.exception(
                f"Unexpected Exception processing get_all_stock: {e}")
            return f"Error: An unexpected error occurred: {e}"

    @app.tool()
    def search_stocks(keyword: str, date: Optional[str] = None, limit: int = 50, format: str = "markdown") -> str:
        """
        在指定日期通过代码子串搜索股票。

        Args:
            keyword (str): 要在股票代码中匹配的子串 (例如, '600', '000001')。
            date (Optional[str], optional): 'YYYY-MM-DD'格式的日期。如果为None，则使用当前日期。
            limit (int, optional): 返回的最大行数。默认为 50。
            format (str, optional): 输出格式: 'markdown' | 'json' | 'csv'。默认为 'markdown'。

        Returns:
            str: 匹配的股票代码及其交易状态。
        """
        logger.info("Tool 'search_stocks' called keyword=%s, date=%s, limit=%s, format=%s", keyword, date or "default", limit, format)
        try:
            if not keyword or not keyword.strip():
                return "Error: 'keyword' is required (substring of code)."
            df = active_data_source.get_all_stock(date=date)
            if df is None or df.empty:
                return "(No data available to display)"
            kw = keyword.strip().lower()
            # baostock returns 'code' like 'sh.600000'
            filtered = df[df["code"].str.lower().str.contains(kw, na=False)]
            meta = {"keyword": keyword, "as_of": date or "current"}
            return format_table_output(filtered, format=format, max_rows=limit, meta=meta)
        except Exception as e:
            logger.exception("Exception processing search_stocks: %s", e)
            return f"Error: An unexpected error occurred: {e}"

    @app.tool()
    def get_suspensions(date: Optional[str] = None, limit: int = 250, format: str = "markdown") -> str:
        """
        列出指定日期的停牌股票。

        Args:
            date (Optional[str], optional): 'YYYY-MM-DD'格式的日期。如果为None，则使用当前日期。
            limit (int, optional): 返回的最大行数。默认为 250。
            format (str, optional): 输出格式: 'markdown' | 'json' | 'csv'。默认为 'markdown'。

        Returns:
            str: 包含所有交易状态为0的股票的表格。
        """
        logger.info("Tool 'get_suspensions' called date=%s, limit=%s, format=%s", date or "current", limit, format)
        try:
            df = active_data_source.get_all_stock(date=date)
            if df is None or df.empty:
                return "(No data available to display)"
            # tradeStatus: '1' trading, '0' suspended
            if "tradeStatus" not in df.columns:
                return "Error: 'tradeStatus' column not present in data source response."
            suspended = df[df["tradeStatus"] == '0']
            meta = {"as_of": date or "current", "total_suspended": int(suspended.shape[0])}
            return format_table_output(suspended, format=format, max_rows=limit, meta=meta)
        except Exception as e:
            logger.exception("Exception processing get_suspensions: %s", e)
            return f"Error: An unexpected error occurred: {e}"
