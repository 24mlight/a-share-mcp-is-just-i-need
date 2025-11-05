"""
MCP 工具的基础实用程序。
用于以一致的格式和错误处理方式调用数据源的共享辅助函数。
"""
import logging
from typing import Callable, Optional
import pandas as pd

from src.formatting.markdown_formatter import format_df_to_markdown, format_table_output
from src.data_source_interface import NoDataFoundError, LoginError, DataSourceError

logger = logging.getLogger(__name__)


def call_financial_data_tool(
    tool_name: str,
    data_source_method: Callable,
    data_type_name: str,
    code: str,
    year: str,
    quarter: int,
    *,
    limit: int = 250,
    format: str = "markdown",
) -> str:
    """
    为财务数据工具减少重复代码的辅助函数。

    Args:
        tool_name (str): 工具名称，用于日志记录。
        data_source_method (Callable): 要在数据源上调用的方法。
        data_type_name (str): 财务数据的类型（用于日志记录）。
        code (str): 股票代码。
        year (str): 查询年份。
        quarter (int): 查询季度。
        limit (int, optional): 返回的最大行数。默认为 250。
        format (str, optional): 输出格式 ('markdown', 'json', 'csv')。默认为 "markdown"。

    Returns:
        str: 带有结果或错误消息的格式化字符串。
    """
    logger.info(f"工具 '{tool_name}' 已为 {code}, {year}Q{quarter} 调用")
    try:
        if not year.isdigit() or len(year) != 4:
            logger.warning(f"请求了无效的年份格式: {year}")
            return f"错误: 无效的年份 '{year}'。请输入4位数字的年份。"
        if not 1 <= quarter <= 4:
            logger.warning(f"请求了无效的季度: {quarter}")
            return f"错误: 无效的季度 '{quarter}'。必须在 1 到 4 之间。"

        df = data_source_method(code=code, year=year, quarter=quarter)
        logger.info(
            f"已成功检索 {data_type_name} 数据，代码 {code}, {year}Q{quarter}。")
        meta = {"code": code, "year": year, "quarter": quarter, "dataset": data_type_name}
        return format_table_output(df, format=format, max_rows=limit, meta=meta)

    except NoDataFoundError as e:
        logger.warning(f"未找到数据错误 for {code}, {year}Q{quarter}: {e}")
        return f"错误: {e}"
    except LoginError as e:
        logger.error(f"登录错误 for {code}: {e}")
        return f"错误: 无法连接到数据源。{e}"
    except DataSourceError as e:
        logger.error(f"数据源错误 for {code}: {e}")
        return f"错误: 获取数据时发生错误。{e}"
    except ValueError as e:
        logger.warning(f"值错误处理请求 for {code}: {e}")
        return f"错误: 无效的输入参数。{e}"
    except Exception as e:
        logger.exception(
            f"处理 {tool_name} for {code} 时发生意外异常: {e}")
        return f"错误: 发生意外错误: {e}"


def call_macro_data_tool(
    tool_name: str,
    data_source_method: Callable,
    data_type_name: str,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    *,
    limit: int = 250,
    format: str = "markdown",
    **kwargs
) -> str:
    """
    宏观经济数据工具的辅助函数。

    Args:
        tool_name (str): 工具名称，用于日志记录。
        data_source_method (Callable): 要在数据源上调用的方法。
        data_type_name (str): 数据类型（用于日志记录）。
        start_date (Optional[str], optional): 开始日期。
        end_date (Optional[str], optional): 结束日期。
        limit (int, optional): 返回的最大行数。默认为 250。
        format (str, optional): 输出格式 ('markdown', 'json', 'csv')。默认为 "markdown"。
        **kwargs: 传递给 data_source_method 的其他关键字参数。

    Returns:
        str: 带有结果或错误消息的格式化字符串。
    """
    date_range_log = f"从 {start_date or '默认'} 到 {end_date or '默认'}"
    kwargs_log = f", 额外参数={kwargs}" if kwargs else ""
    logger.info(f"工具 '{tool_name}' 已调用 {date_range_log}{kwargs_log}")
    try:
        df = data_source_method(start_date=start_date, end_date=end_date, **kwargs)
        logger.info(f"已成功检索 {data_type_name} 数据。")
        meta = {"dataset": data_type_name, "start_date": start_date, "end_date": end_date} | ({"extra": kwargs} if kwargs else {})
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
        logger.exception(f"处理 {tool_name} 时发生意外异常: {e}")
        return f"错误: 发生意外错误: {e}"


def call_index_constituent_tool(
    tool_name: str,
    data_source_method: Callable,
    index_name: str,
    date: Optional[str] = None,
    *,
    limit: int = 250,
    format: str = "markdown",
) -> str:
    """
    指数成分股工具的辅助函数。

    Args:
        tool_name (str): 工具名称，用于日志记录。
        data_source_method (Callable): 要在数据源上调用的方法。
        index_name (str): 指数名称（用于日志记录）。
        date (Optional[str], optional): 查询日期。
        limit (int, optional): 返回的最大行数。默认为 250。
        format (str, optional): 输出格式 ('markdown', 'json', 'csv')。默认为 "markdown"。

    Returns:
        str: 带有结果或错误消息的格式化字符串。
    """
    log_msg = f"工具 '{tool_name}' 已为日期={date or '最新'} 调用"
    logger.info(log_msg)
    try:
        df = data_source_method(date=date)
        logger.info(
            f"已成功检索 {index_name} 成分股，日期为 {date or '最新'}。")
        meta = {"index": index_name, "as_of": date or "latest"}
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
        logger.exception(f"处理 {tool_name} 时发生意外异常: {e}")
        return f"错误: 发生意外错误: {e}"
