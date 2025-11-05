"""
MCP 服务器的股票市场工具。
提供历史价格、基本信息、股息和复权因子，选项清晰。
"""
import logging
from typing import List, Optional

from mcp.server.fastmcp import FastMCP
from src.data_source_interface import FinancialDataSource, NoDataFoundError, LoginError, DataSourceError
from src.formatting.markdown_formatter import format_df_to_markdown, format_table_output

logger = logging.getLogger(__name__)


def register_stock_market_tools(app: FastMCP, active_data_source: FinancialDataSource):
    """
    向 MCP 应用注册股票市场数据工具。

    Args:
        app (FastMCP): FastMCP 应用实例。
        active_data_source (FinancialDataSource): 激活的金融数据源。
    """

    @app.tool()
    def get_historical_k_data(
        code: str,
        start_date: str,
        end_date: str,
        frequency: str = "d",
        adjust_flag: str = "3",
        fields: Optional[List[str]] = None,
        limit: int = 250,
        format: str = "markdown",
    ) -> str:
        """
        获取中国A股股票的历史K线（OHLCV）数据。

        Args:
            code (str): Baostock 格式的股票代码 (例如, 'sh.600000', 'sz.000001')。
            start_date (str): 开始日期，格式为 'YYYY-MM-DD'。
            end_date (str): 结束日期，格式为 'YYYY-MM-DD'。
            frequency (str, optional): 数据频率。有效选项 (来自 Baostock):
                                       'd': 日线
                                       'w': 周线
                                       'm': 月线
                                       '5': 5分钟线
                                       '15': 15分钟线
                                       '30': 30分钟线
                                       '60': 60分钟线
                                     默认为 'd'。
            adjust_flag (str, optional): 价格/成交量复权标志。有效选项 (来自 Baostock):
                                         '1': 后复权
                                         '2': 前复权
                                         '3': 不复权
                                       默认为 '3'。
            fields (Optional[List[str]], optional): 要检索的特定数据字段的可选列表 (必须是有效的 Baostock 字段)。
                                                    如果为 None 或为空，将使用默认字段 (例如, date, code, open, high, low, close, volume, amount, pctChg)。
            limit (int, optional): 返回的最大行数。默认为 250。
            format (str, optional): 输出格式: 'markdown' | 'json' | 'csv'。默认为 'markdown'。

        Returns:
            str: 包含K线数据表的 Markdown 格式字符串，或错误消息。
                 如果结果集太大，表格可能会被截断。
        """
        logger.info(
            f"工具 'get_historical_k_data' 已为 {code} 调用 ({start_date}-{end_date}, 频率={frequency}, 复权={adjust_flag}, 字段={fields})")
        try:
            valid_freqs = ['d', 'w', 'm', '5', '15', '30', '60']
            valid_adjusts = ['1', '2', '3']
            if frequency not in valid_freqs:
                logger.warning(f"请求了无效的频率: {frequency}")
                return f"错误: 无效的频率 '{frequency}'。有效选项为: {valid_freqs}"
            if adjust_flag not in valid_adjusts:
                logger.warning(f"请求了无效的复权标志: {adjust_flag}")
                return f"错误: 无效的复权标志 '{adjust_flag}'。有效选项为: {valid_adjusts}"

            df = active_data_source.get_historical_k_data(
                code=code,
                start_date=start_date,
                end_date=end_date,
                frequency=frequency,
                adjust_flag=adjust_flag,
                fields=fields,
            )
            logger.info(
                f"已成功检索 {code} 的K线数据，正在格式化输出。")
            meta = {"code": code, "start_date": start_date, "end_date": end_date, "frequency": frequency, "adjust_flag": adjust_flag}
            return format_table_output(df, format=format, max_rows=limit, meta=meta)

        except NoDataFoundError as e:
            logger.warning(f"未找到数据错误 for {code}: {e}")
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
                f"处理 get_historical_k_data for {code} 时发生意外异常: {e}")
            return f"错误: 发生意外错误: {e}"

    @app.tool()
    def get_stock_basic_info(code: str, fields: Optional[List[str]] = None, format: str = "markdown") -> str:
        """
        获取给定中国A股股票的基本信息。

        Args:
            code (str): Baostock 格式的股票代码 (例如, 'sh.600000', 'sz.000001')。
            fields (Optional[List[str]], optional): 从可用的基本信息中选择特定列的可选列表
                                                    (例如, ['code', 'code_name', 'industry', 'listingDate'])。
                                                    如果为 None 或为空，则返回 Baostock 提供的所有可用基本信息列。
            format (str, optional): 输出格式。默认为 'markdown'。

        Returns:
            str: 请求格式的股票基本信息。
        """
        logger.info(
            f"工具 'get_stock_basic_info' 已为 {code} 调用 (字段={fields})")
        try:
            df = active_data_source.get_stock_basic_info(
                code=code, fields=fields)

            logger.info(
                f"已成功检索 {code} 的基本信息，正在格式化输出。")
            meta = {"code": code}
            return format_table_output(df, format=format, max_rows=df.shape[0] if df is not None else 0, meta=meta)

        except NoDataFoundError as e:
            logger.warning(f"未找到数据错误 for {code}: {e}")
            return f"错误: {e}"
        except LoginError as e:
            logger.error(f"登录错误 for {code}: {e}")
            return f"错误: 无法连接到数据源。{e}"
        except DataSourceError as e:
            logger.error(f"数据源错误 for {code}: {e}")
            return f"错误: 获取数据时发生错误。{e}"
        except ValueError as e:
            logger.warning(f"值错误处理请求 for {code}: {e}")
            return f"错误: 无效的输入参数或请求的字段不可用。{e}"
        except Exception as e:
            logger.exception(
                f"处理 get_stock_basic_info for {code} 时发生意外异常: {e}")
            return f"错误: 发生意外错误: {e}"

    @app.tool()
    def get_dividend_data(code: str, year: str, year_type: str = "report", limit: int = 250, format: str = "markdown") -> str:
        """
        获取给定股票代码和年份的股息信息。

        Args:
            code (str): Baostock 格式的股票代码 (例如, 'sh.600000', 'sz.000001')。
            year (str): 查询年份 (例如, '2023')。
            year_type (str, optional): 年份类型。有效选项 (来自 Baostock):
                                       'report': 预案公告年份
                                       'operate': 除权除息年份
                                     默认为 'report'。
            limit (int, optional): 返回的最大行数。默认为 250。
            format (str, optional): 输出格式。默认为 'markdown'。

        Returns:
            str: 股息记录表。
        """
        logger.info(
            f"工具 'get_dividend_data' 已为 {code} 调用，年份={year}，年份类型={year_type}")
        try:
            if year_type not in ['report', 'operate']:
                logger.warning(f"请求了无效的年份类型: {year_type}")
                return f"错误: 无效的年份类型 '{year_type}'。有效选项为: 'report', 'operate'"
            if not year.isdigit() or len(year) != 4:
                logger.warning(f"请求了无效的年份格式: {year}")
                return f"错误: 无效的年份 '{year}'。请输入4位数字的年份。"

            df = active_data_source.get_dividend_data(
                code=code, year=year, year_type=year_type)
            logger.info(
                f"已成功检索 {code} 在 {year} 年的股息数据。")
            meta = {"code": code, "year": year, "year_type": year_type}
            return format_table_output(df, format=format, max_rows=limit, meta=meta)

        except NoDataFoundError as e:
            logger.warning(f"未找到数据错误 for {code}, year {year}: {e}")
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
                f"处理 get_dividend_data for {code} 时发生意外异常: {e}")
            return f"错误: 发生意外错误: {e}"

    @app.tool()
    def get_adjust_factor_data(code: str, start_date: str, end_date: str, limit: int = 250, format: str = "markdown") -> str:
        """
        获取给定股票代码和日期范围的复权因子数据。
        使用 Baostock 的“涨跌幅复权算法”因子。可用于计算复权价格。

        Args:
            code (str): Baostock 格式的股票代码 (例如, 'sh.600000', 'sz.000001')。
            start_date (str): 开始日期，格式为 'YYYY-MM-DD'。
            end_date (str): 结束日期，格式为 'YYYY-MM-DD'。
            limit (int, optional): 返回的最大行数。默认为 250。
            format (str, optional): 输出格式。默认为 'markdown'。

        Returns:
            str: 复权因子表。
        """
        logger.info(
            f"工具 'get_adjust_factor_data' 已为 {code} 调用 ({start_date} 到 {end_date})")
        try:
            df = active_data_source.get_adjust_factor_data(
                code=code, start_date=start_date, end_date=end_date)
            logger.info(
                f"已成功检索 {code} 的复权因子数据。")
            meta = {"code": code, "start_date": start_date, "end_date": end_date}
            return format_table_output(df, format=format, max_rows=limit, meta=meta)

        except NoDataFoundError as e:
            logger.warning(f"未找到数据错误 for {code}: {e}")
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
                f"处理 get_adjust_factor_data for {code} 时发生意外异常: {e}")
            return f"错误: 发生意外错误: {e}"
