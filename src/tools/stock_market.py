"""
注册并实现与股票市场数据相关的MCP工具。

该模块包含的工具能够获取：
- 历史K线数据 (`get_historical_k_data`)
- 股票基本信息 (`get_stock_basic_info`)
- 分红信息 (`get_dividend_data`)
- 复权因子数据 (`get_adjust_factor_data`)

所有工具都通过`register_stock_market_tools`函数进行注册，
并依赖于一个实现了`FinancialDataSource`接口的数据源实例。
"""
import logging
from typing import List, Optional

from mcp.server.fastmcp import FastMCP
from src.data_source_interface import FinancialDataSource, NoDataFoundError, LoginError, DataSourceError
from src.formatting.markdown_formatter import format_df_to_markdown, format_table_output

logger = logging.getLogger(__name__)


def register_stock_market_tools(app: FastMCP, active_data_source: FinancialDataSource):
    """
    向MCP应用注册所有与股票市场数据相关的工具。

    Args:
        app (FastMCP): FastMCP应用实例。
        active_data_source (FinancialDataSource): 已激活并实例化的金融数据源。
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
        获取中国A股市场的历史K线（OHLCV）数据。

        Args:
            code (str): Baostock格式的股票代码 (例如, 'sh.600000', 'sz.000001')。
            start_date (str): 开始日期，格式为 'YYYY-MM-DD'。
            end_date (str): 结束日期，格式为 'YYYY-MM-DD'。
            frequency (str, optional): 数据频率。有效选项 (来自Baostock):
                                       'd': 日线
                                       'w': 周线
                                       'm': 月线
                                       '5': 5分钟
                                       '15': 15分钟
                                       '30': 30分钟
                                       '60': 60分钟
                                     默认为 'd'。
            adjust_flag (str, optional): 价格/成交量的复权标记。有效选项 (来自Baostock):
                                         '1': 后复权
                                         '2': 前复权
                                         '3': 不复权
                                       默认为 '3'。
            fields (Optional[List[str]], optional): 要检索的特定数据字段的可选列表 (必须是有效的Baostock字段)。
                                                    如果为None或为空，则使用默认字段 (例如, date, code, open, high, low, close, volume, amount, pctChg)。
            limit (int, optional): 返回的最大行数。默认为 250。
            format (str, optional): 输出格式: 'markdown' | 'json' | 'csv'。默认为 'markdown'。

        Returns:
            str: 包含K线数据表的格式化字符串（默认为Markdown），或一条错误消息。
                 如果结果集太大，表格可能会被截断。
        """
        logger.info(
            f"Tool 'get_historical_k_data' called for {code} ({start_date}-{end_date}, freq={frequency}, adj={adjust_flag}, fields={fields})")
        try:
            # Validate frequency and adjust_flag if necessary (basic example)
            valid_freqs = ['d', 'w', 'm', '5', '15', '30', '60']
            valid_adjusts = ['1', '2', '3']
            if frequency not in valid_freqs:
                logger.warning(f"Invalid frequency requested: {frequency}")
                return f"Error: Invalid frequency '{frequency}'. Valid options are: {valid_freqs}"
            if adjust_flag not in valid_adjusts:
                logger.warning(f"Invalid adjust_flag requested: {adjust_flag}")
                return f"Error: Invalid adjust_flag '{adjust_flag}'. Valid options are: {valid_adjusts}"

            # Call the injected data source
            df = active_data_source.get_historical_k_data(
                code=code,
                start_date=start_date,
                end_date=end_date,
                frequency=frequency,
                adjust_flag=adjust_flag,
                fields=fields,
            )
            # Format the result
            logger.info(
                f"Successfully retrieved K-data for {code}, formatting output.")
            meta = {"code": code, "start_date": start_date, "end_date": end_date, "frequency": frequency, "adjust_flag": adjust_flag}
            return format_table_output(df, format=format, max_rows=limit, meta=meta)

        except NoDataFoundError as e:
            logger.warning(f"NoDataFoundError for {code}: {e}")
            return f"Error: {e}"
        except LoginError as e:
            logger.error(f"LoginError for {code}: {e}")
            return f"Error: Could not connect to data source. {e}"
        except DataSourceError as e:
            logger.error(f"DataSourceError for {code}: {e}")
            return f"Error: An error occurred while fetching data. {e}"
        except ValueError as e:
            logger.warning(f"ValueError processing request for {code}: {e}")
            return f"Error: Invalid input parameter. {e}"
        except Exception as e:
            # Catch-all for unexpected errors
            logger.exception(
                f"Unexpected Exception processing get_historical_k_data for {code}: {e}")
            return f"Error: An unexpected error occurred: {e}"

    @app.tool()
    def get_stock_basic_info(code: str, fields: Optional[List[str]] = None, format: str = "markdown") -> str:
        """
        获取指定中国A股的基本信息。

        Args:
            code (str): Baostock格式的股票代码 (例如, 'sh.600000', 'sz.000001')。
            fields (Optional[List[str]], optional): 从可用基本信息中选择特定列的可选列表
                                                    (例如, ['code', 'code_name', 'industry', 'listingDate'])。
                                                    如果为None或为空，则返回Baostock提供的所有可用基本信息列。
            format (str, optional): 输出格式: 'markdown' | 'json' | 'csv'。默认为 'markdown'。

        Returns:
            str: 按请求格式输出的股票基本信息。
        """
        logger.info(
            f"Tool 'get_stock_basic_info' called for {code} (fields={fields})")
        try:
            # Call the injected data source
            # Pass fields along; BaostockDataSource implementation handles selection
            df = active_data_source.get_stock_basic_info(
                code=code, fields=fields)

            # Format the result (basic info usually small)
            logger.info(
                f"Successfully retrieved basic info for {code}, formatting output.")
            meta = {"code": code}
            return format_table_output(df, format=format, max_rows=df.shape[0] if df is not None else 0, meta=meta)

        except NoDataFoundError as e:
            logger.warning(f"NoDataFoundError for {code}: {e}")
            return f"Error: {e}"
        except LoginError as e:
            logger.error(f"LoginError for {code}: {e}")
            return f"Error: Could not connect to data source. {e}"
        except DataSourceError as e:
            logger.error(f"DataSourceError for {code}: {e}")
            return f"Error: An error occurred while fetching data. {e}"
        except ValueError as e:
            logger.warning(f"ValueError processing request for {code}: {e}")
            return f"Error: Invalid input parameter or requested field not available. {e}"
        except Exception as e:
            logger.exception(
                f"Unexpected Exception processing get_stock_basic_info for {code}: {e}")
            return f"Error: An unexpected error occurred: {e}"

    @app.tool()
    def get_dividend_data(code: str, year: str, year_type: str = "report", limit: int = 250, format: str = "markdown") -> str:
        """
        获取指定股票代码和年份的分红信息。

        Args:
            code (str): Baostock格式的股票代码 (例如, 'sh.600000', 'sz.000001')。
            year (str): 查询的年份 (例如, '2023')。
            year_type (str, optional): 年份类型。有效选项 (来自Baostock):
                                       'report': 预案公告年份
                                       'operate': 除权除息年份
                                     默认为 'report'。
            limit (int, optional): 返回的最大行数。默认为 250。
            format (str, optional): 输出格式: 'markdown' | 'json' | 'csv'。默认为 'markdown'。

        Returns:
            str: 包含分红记录的表格。
        """
        logger.info(
            f"Tool 'get_dividend_data' called for {code}, year={year}, year_type={year_type}")
        try:
            # Basic validation
            if year_type not in ['report', 'operate']:
                logger.warning(f"Invalid year_type requested: {year_type}")
                return f"Error: Invalid year_type '{year_type}'. Valid options are: 'report', 'operate'"
            if not year.isdigit() or len(year) != 4:
                logger.warning(f"Invalid year format requested: {year}")
                return f"Error: Invalid year '{year}'. Please provide a 4-digit year."

            df = active_data_source.get_dividend_data(
                code=code, year=year, year_type=year_type)
            logger.info(
                f"Successfully retrieved dividend data for {code}, year {year}.")
            meta = {"code": code, "year": year, "year_type": year_type}
            return format_table_output(df, format=format, max_rows=limit, meta=meta)

        except NoDataFoundError as e:
            logger.warning(f"NoDataFoundError for {code}, year {year}: {e}")
            return f"Error: {e}"
        except LoginError as e:
            logger.error(f"LoginError for {code}: {e}")
            return f"Error: Could not connect to data source. {e}"
        except DataSourceError as e:
            logger.error(f"DataSourceError for {code}: {e}")
            return f"Error: An error occurred while fetching data. {e}"
        except ValueError as e:
            logger.warning(f"ValueError processing request for {code}: {e}")
            return f"Error: Invalid input parameter. {e}"
        except Exception as e:
            logger.exception(
                f"Unexpected Exception processing get_dividend_data for {code}: {e}")
            return f"Error: An unexpected error occurred: {e}"

    @app.tool()
    def get_adjust_factor_data(code: str, start_date: str, end_date: str, limit: int = 250, format: str = "markdown") -> str:
        """
        获取指定股票代码在特定日期范围内的复权因子数据。
        使用Baostock的“涨跌幅复权算法”因子，可用于计算复权价格。

        Args:
            code (str): Baostock格式的股票代码 (例如, 'sh.600000', 'sz.000001')。
            start_date (str): 开始日期，格式为 'YYYY-MM-DD'。
            end_date (str): 结束日期，格式为 'YYYY-MM-DD'。
            limit (int, optional): 返回的最大行数。默认为 250。
            format (str, optional): 输出格式: 'markdown' | 'json' | 'csv'。默认为 'markdown'。

        Returns:
            str: 包含复权因子数据的表格。
        """
        logger.info(
            f"Tool 'get_adjust_factor_data' called for {code} ({start_date} to {end_date})")
        try:
            # Basic date validation could be added here if desired
            df = active_data_source.get_adjust_factor_data(
                code=code, start_date=start_date, end_date=end_date)
            logger.info(
                f"Successfully retrieved adjustment factor data for {code}.")
            meta = {"code": code, "start_date": start_date, "end_date": end_date}
            return format_table_output(df, format=format, max_rows=limit, meta=meta)

        except NoDataFoundError as e:
            logger.warning(f"NoDataFoundError for {code}: {e}")
            return f"Error: {e}"
        except LoginError as e:
            logger.error(f"LoginError for {code}: {e}")
            return f"Error: Could not connect to data source. {e}"
        except DataSourceError as e:
            logger.error(f"DataSourceError for {code}: {e}")
            return f"Error: An error occurred while fetching data. {e}"
        except ValueError as e:
            logger.warning(f"ValueError processing request for {code}: {e}")
            return f"Error: Invalid input parameter. {e}"
        except Exception as e:
            logger.exception(
                f"Unexpected Exception processing get_adjust_factor_data for {code}: {e}")
            return f"Error: An unexpected error occurred: {e}"
