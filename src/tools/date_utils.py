"""
注册并实现与日期相关的实用工具。

该模块提供了处理交易日历和分析时间范围的便捷工具，包括：
- 获取最近的交易日 (`get_latest_trading_date`)
- 根据当前上下文生成市场分析的时间范围标签 (`get_market_analysis_timeframe`)
- 检查指定日期是否为交易日 (`is_trading_day`)
- 获取指定日期的上一个或下一个交易日 (`previous_trading_day`, `next_trading_day`)

这些工具为处理金融数据中常见的日期和时间问题提供了支持。
"""
import logging
from datetime import datetime, timedelta
import calendar

from mcp.server.fastmcp import FastMCP
from src.data_source_interface import FinancialDataSource

logger = logging.getLogger(__name__)


def register_date_utils_tools(app: FastMCP, active_data_source: FinancialDataSource):
    """
    向MCP应用注册所有与日期工具相关的工具。

    Args:
        app (FastMCP): FastMCP应用实例。
        active_data_source (FinancialDataSource): 已激活并实例化的金融数据源。
    """

    @app.tool()
    def get_latest_trading_date() -> str:
        """
        获取截至今日的最近一个交易日。

        Returns:
            str: 'YYYY-MM-DD'格式的最近交易日。
        """
        logger.info("Tool 'get_latest_trading_date' called")
        try:
            today = datetime.now().strftime("%Y-%m-%d")
            # Query within the current month (safe bound)
            start_date = (datetime.now().replace(day=1)).strftime("%Y-%m-%d")
            end_date = (datetime.now().replace(day=28)).strftime("%Y-%m-%d")

            df = active_data_source.get_trade_dates(
                start_date=start_date, end_date=end_date)

            valid_trading_days = df[df['is_trading_day'] == '1']['calendar_date'].tolist()

            latest_trading_date = None
            for dstr in valid_trading_days:
                if dstr <= today and (latest_trading_date is None or dstr > latest_trading_date):
                    latest_trading_date = dstr

            if latest_trading_date:
                logger.info("Latest trading date found: %s", latest_trading_date)
                return latest_trading_date
            else:
                logger.warning("No trading dates found before today, returning today's date")
                return today

        except Exception as e:
            logger.exception("Error determining latest trading date: %s", e)
            return datetime.now().strftime("%Y-%m-%d")

    @app.tool()
    def get_market_analysis_timeframe(period: str = "recent") -> str:
        """
        根据当前日历上下文，获取一个用于市场分析的时间范围标签。

        Args:
            period (str, optional): 'recent' (默认), 'quarter', 'half_year', 'year'之一。

        Returns:
            str: 一个人类友好的标签，附加ISO格式的日期范围，例如 "2025年1月-3月 (ISO: 2025-01-01 to 2025-03-31)"。
        """
        logger.info(
            f"Tool 'get_market_analysis_timeframe' called with period={period}")

        now = datetime.now()
        end_date = now

        if period == "recent":
            if now.day < 15:
                if now.month == 1:
                    start_date = datetime(now.year - 1, 11, 1)
                    middle_date = datetime(now.year - 1, 12, 1)
                elif now.month == 2:
                    start_date = datetime(now.year, 1, 1)
                    middle_date = start_date
                else:
                    start_date = datetime(now.year, now.month - 2, 1)
                    middle_date = datetime(now.year, now.month - 1, 1)
            else:
                if now.month == 1:
                    start_date = datetime(now.year - 1, 12, 1)
                    middle_date = start_date
                else:
                    start_date = datetime(now.year, now.month - 1, 1)
                    middle_date = start_date

        elif period == "quarter":
            if now.month <= 3:
                start_date = datetime(now.year - 1, now.month + 9, 1)
            else:
                start_date = datetime(now.year, now.month - 3, 1)
            middle_date = start_date

        elif period == "half_year":
            if now.month <= 6:
                start_date = datetime(now.year - 1, now.month + 6, 1)
            else:
                start_date = datetime(now.year, now.month - 6, 1)
            middle_date = datetime(start_date.year, start_date.month + 3, 1) if start_date.month <= 9 else \
                datetime(start_date.year + 1, start_date.month - 9, 1)

        elif period == "year":
            start_date = datetime(now.year - 1, now.month, 1)
            middle_date = datetime(start_date.year, start_date.month + 6, 1) if start_date.month <= 6 else \
                datetime(start_date.year + 1, start_date.month - 6, 1)
        else:
            if now.month == 1:
                start_date = datetime(now.year - 1, 12, 1)
            else:
                start_date = datetime(now.year, now.month - 1, 1)
            middle_date = start_date

        def get_month_end_day(year, month):
            return calendar.monthrange(year, month)[1]

        end_day = min(get_month_end_day(end_date.year, end_date.month), end_date.day)
        end_iso_date = f"{end_date.year}-{end_date.month:02d}-{end_day:02d}"

        start_iso_date = f"{start_date.year}-{start_date.month:02d}-01"

        if start_date.year != end_date.year:
            date_range = f"{start_date.year}年{start_date.month}月-{end_date.year}年{end_date.month}月"
        elif middle_date.month != start_date.month and middle_date.month != end_date.month:
            date_range = f"{start_date.year}年{start_date.month}月-{middle_date.month}月-{end_date.month}月"
        elif start_date.month != end_date.month:
            date_range = f"{start_date.year}年{start_date.month}月-{end_date.month}月"
        else:
            date_range = f"{start_date.year}年{start_date.month}月"

        result = f"{date_range} (ISO: {start_iso_date} to {end_iso_date})"
        logger.info(f"Generated market analysis timeframe: {result}")
        return result

    @app.tool()
    def is_trading_day(date: str) -> str:
        """
        检查给定日期是否为交易日。

        Args:
            date (str): 'YYYY-MM-DD'格式的日期。

        Returns:
            str: 'Yes' 或 'No'。

        Examples:
            - is_trading_day('2025-01-03')
        """
        logger.info("Tool 'is_trading_day' called date=%s", date)
        try:
            df = active_data_source.get_trade_dates(start_date=date, end_date=date)
            if df is None or df.empty:
                return "No"
            flag_col = 'is_trading_day' if 'is_trading_day' in df.columns else df.columns[-1]
            val = str(df.iloc[0][flag_col])
            return "Yes" if val == '1' else "No"
        except Exception as e:
            logger.exception("Exception processing is_trading_day: %s", e)
            return f"Error: {e}"

    @app.tool()
    def previous_trading_day(date: str) -> str:
        """
        获取给定日期之前的上一个交易日。

        Args:
            date (str): 'YYYY-MM-DD'格式的日期。

        Returns:
            str: 'YYYY-MM-DD'格式的上一个交易日。如果在附近未找到，则返回输入日期。
        """
        logger.info("Tool 'previous_trading_day' called date=%s", date)
        try:
            d = datetime.strptime(date, "%Y-%m-%d")
            start = (d - timedelta(days=30)).strftime("%Y-%m-%d")
            end = date
            df = active_data_source.get_trade_dates(start_date=start, end_date=end)
            if df is None or df.empty:
                return date
            flag_col = 'is_trading_day' if 'is_trading_day' in df.columns else df.columns[-1]
            day_col = 'calendar_date' if 'calendar_date' in df.columns else df.columns[0]
            candidates = df[(df[flag_col] == '1') & (df[day_col] < date)].sort_values(by=day_col)
            if candidates.empty:
                return date
            return str(candidates.iloc[-1][day_col])
        except Exception as e:
            logger.exception("Exception processing previous_trading_day: %s", e)
            return f"Error: {e}"

    @app.tool()
    def next_trading_day(date: str) -> str:
        """
        获取给定日期之后的下一个交易日。

        Args:
            date (str): 'YYYY-MM-DD'格式的日期。

        Returns:
            str: 'YYYY-MM-DD'格式的下一个交易日。如果在附近未找到，则返回输入日期。
        """
        logger.info("Tool 'next_trading_day' called date=%s", date)
        try:
            d = datetime.strptime(date, "%Y-%m-%d")
            start = date
            end = (d + timedelta(days=30)).strftime("%Y-%m-%d")
            df = active_data_source.get_trade_dates(start_date=start, end_date=end)
            if df is None or df.empty:
                return date
            flag_col = 'is_trading_day' if 'is_trading_day' in df.columns else df.columns[-1]
            day_col = 'calendar_date' if 'calendar_date' in df.columns else df.columns[0]
            candidates = df[(df[flag_col] == '1') & (df[day_col] > date)].sort_values(by=day_col)
            if candidates.empty:
                return date
            return str(candidates.iloc[0][day_col])
        except Exception as e:
            logger.exception("Exception processing next_trading_day: %s", e)
            return f"Error: {e}"

