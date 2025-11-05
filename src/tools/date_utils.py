"""
MCP 服务器的日期实用工具。
围绕交易日和分析时间范围的便捷辅助工具。
"""
import logging
from datetime import datetime, timedelta
import calendar

from mcp.server.fastmcp import FastMCP
from src.data_source_interface import FinancialDataSource

logger = logging.getLogger(__name__)


def register_date_utils_tools(app: FastMCP, active_data_source: FinancialDataSource):
    """
    向 MCP 应用注册日期实用工具。

    Args:
        app (FastMCP): FastMCP 应用实例。
        active_data_source (FinancialDataSource): 激活的金融数据源。
    """

    @app.tool()
    def get_latest_trading_date() -> str:
        """
        获取截至今日的最新交易日。

        Returns:
            str: 'YYYY-MM-DD' 格式的最新交易日。
        """
        logger.info("工具 'get_latest_trading_date' 已调用")
        try:
            today = datetime.now().strftime("%Y-%m-%d")
            # 查询当月（安全边界）
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
                logger.info("找到最新交易日: %s", latest_trading_date)
                return latest_trading_date
            else:
                logger.warning("今天之前未找到交易日，返回今天日期")
                return today

        except Exception as e:
            logger.exception("确定最新交易日时出错: %s", e)
            return datetime.now().strftime("%Y-%m-%d")

    @app.tool()
    def get_market_analysis_timeframe(period: str = "recent") -> str:
        """
        获取根据当前日历上下文调整的市场分析时间范围标签。

        Args:
            period (str, optional): 'recent' (默认), 'quarter', 'half_year', 'year' 之一。

        Returns:
            str: 一个易于理解的标签加上ISO范围，例如 "2025年1月-3月 (ISO: 2025-01-01 至 2025-03-31)"。
        """
        logger.info(
            f"工具 'get_market_analysis_timeframe' 已调用，周期={period}")

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
        logger.info(f"生成的市场分析时间范围: {result}")
        return result

    @app.tool()
    def is_trading_day(date: str) -> str:
        """
        检查给定日期是否为交易日。

        Args:
            date (str): 'YYYY-MM-DD' 格式的日期。

        Returns:
            str: '是' 或 '否'。

        Examples:
            - is_trading_day('2025-01-03')
        """
        logger.info("工具 'is_trading_day' 已调用 date=%s", date)
        try:
            df = active_data_source.get_trade_dates(start_date=date, end_date=date)
            if df is None or df.empty:
                return "否"
            flag_col = 'is_trading_day' if 'is_trading_day' in df.columns else df.columns[-1]
            val = str(df.iloc[0][flag_col])
            return "是" if val == '1' else "否"
        except Exception as e:
            logger.exception("处理 is_trading_day 时发生异常: %s", e)
            return f"错误: {e}"

    @app.tool()
    def previous_trading_day(date: str) -> str:
        """
        获取给定日期之前的上一个交易日。

        Args:
            date (str): 'YYYY-MM-DD' 格式的日期。

        Returns:
            str: 'YYYY-MM-DD' 格式的上一个交易日。如果在附近找不到，则返回输入日期。
        """
        logger.info("工具 'previous_trading_day' 已调用 date=%s", date)
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
            logger.exception("处理 previous_trading_day 时发生异常: %s", e)
            return f"错误: {e}"

    @app.tool()
    def next_trading_day(date: str) -> str:
        """
        获取给定日期之后的下一个交易日。

        Args:
            date (str): 'YYYY-MM-DD' 格式的日期。

        Returns:
            str: 'YYYY-MM-DD' 格式的下一个交易日。如果在附近找不到，则返回输入日期。
        """
        logger.info("工具 'next_trading_day' 已调用 date=%s", date)
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
            logger.exception("处理 next_trading_day 时发生异常: %s", e)
            return f"错误: {e}"
