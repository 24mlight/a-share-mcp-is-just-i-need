# 使用 Baostock 实现 FinancialDataSource 接口
import baostock as bs
import pandas as pd
from typing import List, Optional
import logging
from .data_source_interface import FinancialDataSource, DataSourceError, NoDataFoundError, LoginError
from .utils import baostock_login_context

# 获取此模块的 logger 实例
logger = logging.getLogger(__name__)

DEFAULT_K_FIELDS = [
    "date", "code", "open", "high", "low", "close", "preclose",
    "volume", "amount", "adjustflag", "turn", "tradestatus",
    "pctChg", "peTTM", "pbMRQ", "psTTM", "pcfNcfTTM", "isST"
]

DEFAULT_BASIC_FIELDS = [
    "code", "tradeStatus", "code_name"
    # 可根据需要添加更多默认字段, 例如 "industry", "listingDate"
]

# 辅助函数，用于减少财务数据获取中的重复代码
def _fetch_financial_data(
    bs_query_func,
    data_type_name: str,
    code: str,
    year: str,
    quarter: int
) -> pd.DataFrame:
    """
    通用函数，用于从 Baostock 获取季度的财务数据。

    Args:
        bs_query_func (function): 用于查询的 Baostock 函数 (例如, bs.query_profit_data)。
        data_type_name (str): 数据类型的名称，用于日志记录 (例如, "Profitability")。
        code (str): 股票代码。
        year (str): 年份。
        quarter (int): 季度。

    Returns:
        pd.DataFrame: 包含财务数据的 pandas DataFrame。

    Raises:
        LoginError: 如果 Baostock 登录失败。
        NoDataFoundError: 如果未找到数据。
        DataSourceError: 如果发生其他 Baostock API 错误。
    """
    logger.info(
        f"正在获取 {data_type_name} 数据，代码: {code}，年份: {year}，季度: {quarter}")
    try:
        with baostock_login_context():
            rs = bs_query_func(code=code, year=year, quarter=quarter)

            if rs.error_code != '0':
                logger.error(
                    f"Baostock API 错误 ({data_type_name})，代码 {code}: {rs.error_msg} (错误码: {rs.error_code})")
                if "no record found" in rs.error_msg.lower() or rs.error_code == '10002':
                    raise NoDataFoundError(
                        f"未找到 {code} 在 {year}年Q{quarter} 的 {data_type_name} 数据。Baostock 消息: {rs.error_msg}")
                else:
                    raise DataSourceError(
                        f"获取 {data_type_name} 数据时 Baostock API 发生错误: {rs.error_msg} (错误码: {rs.error_code})")

            data_list = []
            while rs.next():
                data_list.append(rs.get_row_data())

            if not data_list:
                logger.warning(
                    f"未找到 {code} 在 {year}年Q{quarter} 的 {data_type_name} 数据 (Baostock 返回空结果集)。")
                raise NoDataFoundError(
                    f"未找到 {code} 在 {year}年Q{quarter} 的 {data_type_name} 数据 (空结果集)。")

            result_df = pd.DataFrame(data_list, columns=rs.fields)
            logger.info(
                f"已获取 {len(result_df)} 条关于 {code} 在 {year}年Q{quarter} 的 {data_type_name} 记录。")
            return result_df

    except (LoginError, NoDataFoundError, DataSourceError, ValueError) as e:
        logger.warning(
            f"获取 {data_type_name} 数据时捕获到已知错误，代码 {code}: {type(e).__name__}")
        raise e
    except Exception as e:
        logger.exception(
            f"获取 {data_type_name} 数据时发生未知错误，代码 {code}: {e}")
        raise DataSourceError(
            f"获取 {data_type_name} 数据时发生未知错误，代码 {code}: {e}")

# 辅助函数，用于减少指数成分股数据获取的重复代码
def _fetch_index_constituent_data(
    bs_query_func,
    index_name: str,
    date: Optional[str] = None
) -> pd.DataFrame:
    """
    通用函数，用于从 Baostock 获取指数成分股数据。

    Args:
        bs_query_func (function): 用于查询的 Baostock 函数 (例如, bs.query_sz50_stocks)。
        index_name (str): 指数名称，用于日志记录 (例如, "SZSE 50")。
        date (Optional[str], optional): 查询日期，格式 'YYYY-MM-DD'。默认为最新日期。

    Returns:
        pd.DataFrame: 包含指数成分股数据的 pandas DataFrame。
    """
    logger.info(
        f"正在获取 {index_name} 成分股，日期: {date or '最新'}")
    try:
        with baostock_login_context():
            rs = bs_query_func(date=date)

            if rs.error_code != '0':
                logger.error(
                    f"Baostock API 错误 ({index_name} 成分股)，日期 {date}: {rs.error_msg} (错误码: {rs.error_code})")
                if "no record found" in rs.error_msg.lower() or rs.error_code == '10002':
                    raise NoDataFoundError(
                        f"未找到日期为 {date} 的 {index_name} 成分股数据。Baostock 消息: {rs.error_msg}")
                else:
                    raise DataSourceError(
                        f"获取 {index_name} 成分股时 Baostock API 发生错误: {rs.error_msg} (错误码: {rs.error_code})")

            data_list = []
            while rs.next():
                data_list.append(rs.get_row_data())

            if not data_list:
                logger.warning(
                    f"未找到日期为 {date} 的 {index_name} 成分股数据 (空结果集)。")
                raise NoDataFoundError(
                    f"未找到日期为 {date} 的 {index_name} 成分股数据 (空结果集)。")

            result_df = pd.DataFrame(data_list, columns=rs.fields)
            logger.info(
                f"已获取 {len(result_df)} 条关于 {index_name} 的成分股记录，日期: {date or '最新'}")
            return result_df

    except (LoginError, NoDataFoundError, DataSourceError, ValueError) as e:
        logger.warning(
            f"获取 {index_name} 成分股时捕获到已知错误，日期 {date}: {type(e).__name__}")
        raise e
    except Exception as e:
        logger.exception(
            f"获取 {index_name} 成分股时发生未知错误，日期 {date}: {e}")
        raise DataSourceError(
            f"获取 {index_name} 成分股时发生未知错误，日期 {date}: {e}")

# 辅助函数，用于减少宏观经济数据获取的重复代码
def _fetch_macro_data(
    bs_query_func,
    data_type_name: str,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    **kwargs
) -> pd.DataFrame:
    """
    通用函数，用于从 Baostock 获取宏观经济数据。

    Args:
        bs_query_func (function): 用于查询的 Baostock 函数。
        data_type_name (str): 数据类型的名称，用于日志记录。
        start_date (Optional[str], optional): 开始日期。
        end_date (Optional[str], optional): 结束日期。
        **kwargs: 传递给 Baostock 函数的其他参数 (例如, yearType)。

    Returns:
        pd.DataFrame: 包含宏观经济数据的 pandas DataFrame。
    """
    date_range_log = f"从 {start_date or '默认'} 到 {end_date or '默认'}"
    kwargs_log = f", 额外参数={kwargs}" if kwargs else ""
    logger.info(f"正在获取 {data_type_name} 数据 {date_range_log}{kwargs_log}")
    try:
        with baostock_login_context():
            rs = bs_query_func(start_date=start_date,
                               end_date=end_date, **kwargs)

            if rs.error_code != '0':
                logger.error(
                    f"Baostock API 错误 ({data_type_name}): {rs.error_msg} (错误码: {rs.error_code})")
                if "no record found" in rs.error_msg.lower() or rs.error_code == '10002':
                    raise NoDataFoundError(
                        f"未找到符合条件的 {data_type_name} 数据。Baostock 消息: {rs.error_msg}")
                else:
                    raise DataSourceError(
                        f"获取 {data_type_name} 数据时 Baostock API 发生错误: {rs.error_msg} (错误码: {rs.error_code})")

            data_list = []
            while rs.next():
                data_list.append(rs.get_row_data())

            if not data_list:
                logger.warning(
                    f"未找到符合条件的 {data_type_name} 数据 (空结果集)。")
                raise NoDataFoundError(
                    f"未找到符合条件的 {data_type_name} 数据 (空结果集)。")

            result_df = pd.DataFrame(data_list, columns=rs.fields)
            logger.info(
                f"已获取 {len(result_df)} 条 {data_type_name} 记录。")
            return result_df

    except (LoginError, NoDataFoundError, DataSourceError, ValueError) as e:
        logger.warning(
            f"获取 {data_type_name} 数据时捕获到已知错误: {type(e).__name__}")
        raise e
    except Exception as e:
        logger.exception(
            f"获取 {data_type_name} 数据时发生未知错误: {e}")
        raise DataSourceError(
            f"获取 {data_type_name} 数据时发生未知错误: {e}")


class BaostockDataSource(FinancialDataSource):
    """
    使用 Baostock 库实现 FinancialDataSource 的具体类。
    """

    def _format_fields(self, fields: Optional[List[str]], default_fields: List[str]) -> str:
        """将字段列表格式化为 Baostock 需要的逗号分隔字符串。"""
        if fields is None or not fields:
            logger.debug(
                f"未请求特定字段，使用默认值: {default_fields}")
            return ",".join(default_fields)
        if not all(isinstance(f, str) for f in fields):
            raise ValueError("字段列表中的所有项都必须是字符串。")
        logger.debug(f"使用请求的字段: {fields}")
        return ",".join(fields)

    def get_historical_k_data(
        self,
        code: str,
        start_date: str,
        end_date: str,
        frequency: str = "d",
        adjust_flag: str = "3",
        fields: Optional[List[str]] = None,
    ) -> pd.DataFrame:
        """使用 Baostock 获取历史K线数据。"""
        logger.info(
            f"正在为 {code} 获取K线数据 ({start_date} 到 {end_date})，频率={frequency}，复权={adjust_flag}")
        try:
            formatted_fields = self._format_fields(fields, DEFAULT_K_FIELDS)
            logger.debug(
                f"向 Baostock 请求的字段: {formatted_fields}")

            with baostock_login_context():
                rs = bs.query_history_k_data_plus(
                    code,
                    formatted_fields,
                    start_date=start_date,
                    end_date=end_date,
                    frequency=frequency,
                    adjustflag=adjust_flag
                )

                if rs.error_code != '0':
                    logger.error(
                        f"Baostock API 错误 (K线数据) for {code}: {rs.error_msg} (错误码: {rs.error_code})")
                    if "no record found" in rs.error_msg.lower() or rs.error_code == '10002':
                        raise NoDataFoundError(
                            f"在指定范围内未找到 {code} 的历史数据。Baostock 消息: {rs.error_msg}")
                    else:
                        raise DataSourceError(
                            f"获取K线数据时 Baostock API 发生错误: {rs.error_msg} (错误码: {rs.error_code})")

                data_list = []
                while rs.next():
                    data_list.append(rs.get_row_data())

                if not data_list:
                    logger.warning(
                        f"在指定范围内未找到 {code} 的历史数据 (Baostock 返回空结果集)。")
                    raise NoDataFoundError(
                        f"在指定范围内未找到 {code} 的历史数据 (空结果集)。")

                result_df = pd.DataFrame(data_list, columns=rs.fields)
                logger.info(f"已为 {code} 获取 {len(result_df)} 条记录。")
                return result_df

        except (LoginError, NoDataFoundError, DataSourceError, ValueError) as e:
            logger.warning(
                f"为 {code} 获取K线数据时捕获到已知错误: {type(e).__name__}")
            raise e
        except Exception as e:
            logger.exception(
                f"为 {code} 获取K线数据时发生未知错误: {e}")
            raise DataSourceError(
                f"为 {code} 获取K线数据时发生未知错误: {e}")

    def get_stock_basic_info(self, code: str, fields: Optional[List[str]] = None) -> pd.DataFrame:
        """使用 Baostock 获取股票基本信息。"""
        logger.info(f"正在获取 {code} 的基本信息")
        try:
            logger.debug(
                f"正在请求 {code} 的基本信息。可选字段: {fields}")

            with baostock_login_context():
                rs = bs.query_stock_basic(code=code)

                if rs.error_code != '0':
                    logger.error(
                        f"Baostock API 错误 (基本信息) for {code}: {rs.error_msg} (错误码: {rs.error_code})")
                    if "no record found" in rs.error_msg.lower() or rs.error_code == '10002':
                        raise NoDataFoundError(
                            f"未找到 {code} 的基本信息。Baostock 消息: {rs.error_msg}")
                    else:
                        raise DataSourceError(
                            f"获取基本信息时 Baostock API 发生错误: {rs.error_msg} (错误码: {rs.error_code})")

                data_list = []
                while rs.next():
                    data_list.append(rs.get_row_data())

                if not data_list:
                    logger.warning(
                        f"未找到 {code} 的基本信息 (Baostock 返回空结果集)。")
                    raise NoDataFoundError(
                        f"未找到 {code} 的基本信息 (空结果集)。")

                result_df = pd.DataFrame(data_list, columns=rs.fields)
                logger.info(
                    f"已获取 {code} 的基本信息。列: {result_df.columns.tolist()}")

                if fields:
                    available_cols = [
                        col for col in fields if col in result_df.columns]
                    if not available_cols:
                        raise ValueError(
                            f"请求的字段 {fields} 在基本信息结果中均不可用。")
                    logger.debug(
                        f"为 {code} 的基本信息选择列: {available_cols}")
                    result_df = result_df[available_cols]

                return result_df

        except (LoginError, NoDataFoundError, DataSourceError, ValueError) as e:
            logger.warning(
                f"获取 {code} 的基本信息时捕获到已知错误: {type(e).__name__}")
            raise e
        except Exception as e:
            logger.exception(
                f"获取 {code} 的基本信息时发生未知错误: {e}")
            raise DataSourceError(
                f"获取 {code} 的基本信息时发生未知错误: {e}")

    def get_dividend_data(self, code: str, year: str, year_type: str = "report") -> pd.DataFrame:
        """使用 Baostock 获取分红信息。"""
        logger.info(
            f"正在获取 {code} 的分红数据，年份={year}，年份类型={year_type}")
        try:
            with baostock_login_context():
                rs = bs.query_dividend_data(
                    code=code, year=year, yearType=year_type)

                if rs.error_code != '0':
                    logger.error(
                        f"Baostock API 错误 (分红) for {code}: {rs.error_msg} (错误码: {rs.error_code})")
                    if "no record found" in rs.error_msg.lower() or rs.error_code == '10002':
                        raise NoDataFoundError(
                            f"未找到 {code} 在 {year} 年的分红数据。Baostock 消息: {rs.error_msg}")
                    else:
                        raise DataSourceError(
                            f"获取分红数据时 Baostock API 发生错误: {rs.error_msg} (错误码: {rs.error_code})")

                data_list = []
                while rs.next():
                    data_list.append(rs.get_row_data())

                if not data_list:
                    logger.warning(
                        f"未找到 {code} 在 {year} 年的分红数据 (Baostock 返回空结果集)。")
                    raise NoDataFoundError(
                        f"未找到 {code} 在 {year} 年的分红数据 (空结果集)。")

                result_df = pd.DataFrame(data_list, columns=rs.fields)
                logger.info(
                    f"已为 {code} 在 {year} 年获取 {len(result_df)} 条分红记录。")
                return result_df

        except (LoginError, NoDataFoundError, DataSourceError, ValueError) as e:
            logger.warning(
                f"获取 {code} 的分红数据时捕获到已知错误: {type(e).__name__}")
            raise e
        except Exception as e:
            logger.exception(
                f"获取 {code} 的分红数据时发生未知错误: {e}")
            raise DataSourceError(
                f"获取 {code} 的分红数据时发生未知错误: {e}")

    def get_adjust_factor_data(self, code: str, start_date: str, end_date: str) -> pd.DataFrame:
        """使用 Baostock 获取复权因子数据。"""
        logger.info(
            f"正在获取 {code} 的复权因子数据 ({start_date} 到 {end_date})")
        try:
            with baostock_login_context():
                rs = bs.query_adjust_factor(
                    code=code, start_date=start_date, end_date=end_date)

                if rs.error_code != '0':
                    logger.error(
                        f"Baostock API 错误 (复权因子) for {code}: {rs.error_msg} (错误码: {rs.error_code})")
                    if "no record found" in rs.error_msg.lower() or rs.error_code == '10002':
                        raise NoDataFoundError(
                            f"在指定范围内未找到 {code} 的复权因子数据。Baostock 消息: {rs.error_msg}")
                    else:
                        raise DataSourceError(
                            f"获取复权因子数据时 Baostock API 发生错误: {rs.error_msg} (错误码: {rs.error_code})")

                data_list = []
                while rs.next():
                    data_list.append(rs.get_row_data())

                if not data_list:
                    logger.warning(
                        f"在指定范围内未找到 {code} 的复权因子数据 (Baostock 返回空结果集)。")
                    raise NoDataFoundError(
                        f"在指定范围内未找到 {code} 的复权因子数据 (空结果集)。")

                result_df = pd.DataFrame(data_list, columns=rs.fields)
                logger.info(
                    f"已为 {code} 获取 {len(result_df)} 条复权因子记录。")
                return result_df

        except (LoginError, NoDataFoundError, DataSourceError, ValueError) as e:
            logger.warning(
                f"获取 {code} 的复权因子数据时捕获到已知错误: {type(e).__name__}")
            raise e
        except Exception as e:
            logger.exception(
                f"获取 {code} 的复权因子数据时发生未知错误: {e}")
            raise DataSourceError(
                f"获取 {code} 的复权因子数据时发生未知错误: {e}")

    def get_profit_data(self, code: str, year: str, quarter: int) -> pd.DataFrame:
        """使用 Baostock 获取季度盈利能力数据。"""
        return _fetch_financial_data(bs.query_profit_data, "盈利能力", code, year, quarter)

    def get_operation_data(self, code: str, year: str, quarter: int) -> pd.DataFrame:
        """使用 Baostock 获取季度运营能力数据。"""
        return _fetch_financial_data(bs.query_operation_data, "运营能力", code, year, quarter)

    def get_growth_data(self, code: str, year: str, quarter: int) -> pd.DataFrame:
        """使用 Baostock 获取季度成长能力数据。"""
        return _fetch_financial_data(bs.query_growth_data, "成长能力", code, year, quarter)

    def get_balance_data(self, code: str, year: str, quarter: int) -> pd.DataFrame:
        """使用 Baostock 获取季度偿债能力数据。"""
        return _fetch_financial_data(bs.query_balance_data, "资产负债", code, year, quarter)

    def get_cash_flow_data(self, code: str, year: str, quarter: int) -> pd.DataFrame:
        """使用 Baostock 获取季度现金流量数据。"""
        return _fetch_financial_data(bs.query_cash_flow_data, "现金流量", code, year, quarter)

    def get_dupont_data(self, code: str, year: str, quarter: int) -> pd.DataFrame:
        """使用 Baostock 获取季度杜邦指数数据。"""
        return _fetch_financial_data(bs.query_dupont_data, "杜邦指数", code, year, quarter)

    def get_performance_express_report(self, code: str, start_date: str, end_date: str) -> pd.DataFrame:
        """使用 Baostock 获取业绩快报。"""
        logger.info(
            f"正在获取 {code} 的业绩快报 ({start_date} 到 {end_date})")
        try:
            with baostock_login_context():
                rs = bs.query_performance_express_report(
                    code=code, start_date=start_date, end_date=end_date)

                if rs.error_code != '0':
                    logger.error(
                        f"Baostock API 错误 (业绩快报) for {code}: {rs.error_msg} (错误码: {rs.error_code})")
                    if "no record found" in rs.error_msg.lower() or rs.error_code == '10002':
                        raise NoDataFoundError(
                            f"在 {start_date}-{end_date} 范围内未找到 {code} 的业绩快报。Baostock 消息: {rs.error_msg}")
                    else:
                        raise DataSourceError(
                            f"获取业绩快报时 Baostock API 发生错误: {rs.error_msg} (错误码: {rs.error_code})")

                data_list = []
                while rs.next():
                    data_list.append(rs.get_row_data())

                if not data_list:
                    logger.warning(
                        f"在 {start_date}-{end_date} 范围内未找到 {code} 的业绩快报 (空结果集)。")
                    raise NoDataFoundError(
                        f"在 {start_date}-{end_date} 范围内未找到 {code} 的业绩快报 (空结果集)。")

                result_df = pd.DataFrame(data_list, columns=rs.fields)
                logger.info(
                    f"已为 {code} 获取 {len(result_df)} 条业绩快报记录。")
                return result_df

        except (LoginError, NoDataFoundError, DataSourceError, ValueError) as e:
            logger.warning(
                f"获取 {code} 的业绩快报时捕获到已知错误: {type(e).__name__}")
            raise e
        except Exception as e:
            logger.exception(
                f"获取 {code} 的业绩快报时发生未知错误: {e}")
            raise DataSourceError(
                f"获取 {code} 的业绩快报时发生未知错误: {e}")

    def get_forecast_report(self, code: str, start_date: str, end_date: str) -> pd.DataFrame:
        """使用 Baostock 获取业绩预告。"""
        logger.info(
            f"正在获取 {code} 的业绩预告 ({start_date} 到 {end_date})")
        try:
            with baostock_login_context():
                rs = bs.query_forecast_report(
                    code=code, start_date=start_date, end_date=end_date)

                if rs.error_code != '0':
                    logger.error(
                        f"Baostock API 错误 (业绩预告) for {code}: {rs.error_msg} (错误码: {rs.error_code})")
                    if "no record found" in rs.error_msg.lower() or rs.error_code == '10002':
                        raise NoDataFoundError(
                            f"在 {start_date}-{end_date} 范围内未找到 {code} 的业绩预告。Baostock 消息: {rs.error_msg}")
                    else:
                        raise DataSourceError(
                            f"获取业绩预告时 Baostock API 发生错误: {rs.error_msg} (错误码: {rs.error_code})")

                data_list = []
                while rs.next():
                    data_list.append(rs.get_row_data())

                if not data_list:
                    logger.warning(
                        f"在 {start_date}-{end_date} 范围内未找到 {code} 的业绩预告 (空结果集)。")
                    raise NoDataFoundError(
                        f"在 {start_date}-{end_date} 范围内未找到 {code} 的业绩预告 (空结果集)。")

                result_df = pd.DataFrame(data_list, columns=rs.fields)
                logger.info(
                    f"已为 {code} 获取 {len(result_df)} 条业绩预告记录。")
                return result_df

        except (LoginError, NoDataFoundError, DataSourceError, ValueError) as e:
            logger.warning(
                f"获取 {code} 的业绩预告时捕获到已知错误: {type(e).__name__}")
            raise e
        except Exception as e:
            logger.exception(
                f"获取 {code} 的业绩预告时发生未知错误: {e}")
            raise DataSourceError(
                f"获取 {code} 的业绩预告时发生未知错误: {e}")

    def get_stock_industry(self, code: Optional[str] = None, date: Optional[str] = None) -> pd.DataFrame:
        """使用 Baostock 获取行业分类数据。"""
        log_msg = f"正在获取行业数据，代码={code or '全部'}，日期={date or '最新'}"
        logger.info(log_msg)
        try:
            with baostock_login_context():
                rs = bs.query_stock_industry(code=code, date=date)

                if rs.error_code != '0':
                    logger.error(
                        f"Baostock API 错误 (行业) for {code}, {date}: {rs.error_msg} (错误码: {rs.error_code})")
                    if "no record found" in rs.error_msg.lower() or rs.error_code == '10002':
                        raise NoDataFoundError(
                            f"未找到 {code}, {date} 的行业数据。Baostock 消息: {rs.error_msg}")
                    else:
                        raise DataSourceError(
                            f"获取行业数据时 Baostock API 发生错误: {rs.error_msg} (错误码: {rs.error_code})")

                data_list = []
                while rs.next():
                    data_list.append(rs.get_row_data())

                if not data_list:
                    logger.warning(
                        f"未找到 {code}, {date} 的行业数据 (空结果集)。")
                    raise NoDataFoundError(
                        f"未找到 {code}, {date} 的行业数据 (空结果集)。")

                result_df = pd.DataFrame(data_list, columns=rs.fields)
                logger.info(
                    f"已为 {code or '全部'}, {date or '最新'} 获取 {len(result_df)} 条行业记录。")
                return result_df

        except (LoginError, NoDataFoundError, DataSourceError, ValueError) as e:
            logger.warning(
                f"获取 {code}, {date} 的行业数据时捕获到已知错误: {type(e).__name__}")
            raise e
        except Exception as e:
            logger.exception(
                f"获取 {code}, {date} 的行业数据时发生未知错误: {e}")
            raise DataSourceError(
                f"获取 {code}, {date} 的行业数据时发生未知错误: {e}")

    def get_sz50_stocks(self, date: Optional[str] = None) -> pd.DataFrame:
        """使用 Baostock 获取上证50指数成分股。"""
        return _fetch_index_constituent_data(bs.query_sz50_stocks, "上证50", date)

    def get_hs300_stocks(self, date: Optional[str] = None) -> pd.DataFrame:
        """使用 Baostock 获取沪深300指数成分股。"""
        return _fetch_index_constituent_data(bs.query_hs300_stocks, "沪深300", date)

    def get_zz500_stocks(self, date: Optional[str] = None) -> pd.DataFrame:
        """使用 Baostock 获取中证500指数成分股。"""
        return _fetch_index_constituent_data(bs.query_zz500_stocks, "中证500", date)

    def get_trade_dates(self, start_date: Optional[str] = None, end_date: Optional[str] = None) -> pd.DataFrame:
        """使用 Baostock 获取交易日。"""
        logger.info(
            f"正在获取交易日，从 {start_date or '默认'} 到 {end_date or '默认'}")
        try:
            with baostock_login_context():
                rs = bs.query_trade_dates(
                    start_date=start_date, end_date=end_date)

                if rs.error_code != '0':
                    logger.error(
                        f"Baostock API 错误 (交易日): {rs.error_msg} (错误码: {rs.error_code})")
                    raise DataSourceError(
                        f"获取交易日时 Baostock API 发生错误: {rs.error_msg} (错误码: {rs.error_code})")

                data_list = []
                while rs.next():
                    data_list.append(rs.get_row_data())

                if not data_list:
                    logger.warning(
                        f"在 {start_date}-{end_date} 范围内未返回交易日 (空结果集)。")
                    raise NoDataFoundError(
                        f"在 {start_date}-{end_date} 范围内未找到交易日 (空结果集)。")

                result_df = pd.DataFrame(data_list, columns=rs.fields)
                logger.info(f"已获取 {len(result_df)} 条交易日记录。")
                return result_df

        except (LoginError, NoDataFoundError, DataSourceError, ValueError) as e:
            logger.warning(
                f"获取交易日时捕获到已知错误: {type(e).__name__}")
            raise e
        except Exception as e:
            logger.exception(f"获取交易日时发生未知错误: {e}")
            raise DataSourceError(
                f"获取交易日时发生未知错误: {e}")

    def get_all_stock(self, date: Optional[str] = None) -> pd.DataFrame:
        """使用 Baostock 获取某日的全部股票列表。"""
        logger.info(f"正在获取全部股票列表，日期={date or '默认'}")
        try:
            with baostock_login_context():
                rs = bs.query_all_stock(day=date)

                if rs.error_code != '0':
                    logger.error(
                        f"Baostock API 错误 (全部股票) for date {date}: {rs.error_msg} (错误码: {rs.error_code})")
                    if "no record found" in rs.error_msg.lower() or rs.error_code == '10002':
                        raise NoDataFoundError(
                            f"未找到日期 {date} 的股票数据。Baostock 消息: {rs.error_msg}")
                    else:
                        raise DataSourceError(
                            f"获取全部股票列表时 Baostock API 发生错误: {rs.error_msg} (错误码: {rs.error_code})")

                data_list = []
                while rs.next():
                    data_list.append(rs.get_row_data())

                if not data_list:
                    logger.warning(
                        f"日期 {date} 未返回股票列表 (空结果集)。")
                    raise NoDataFoundError(
                        f"日期 {date} 未找到股票列表 (空结果集)。")

                result_df = pd.DataFrame(data_list, columns=rs.fields)
                logger.info(
                    f"已为日期 {date or '默认'} 获取 {len(result_df)} 条股票记录。")
                return result_df

        except (LoginError, NoDataFoundError, DataSourceError, ValueError) as e:
            logger.warning(
                f"为日期 {date} 获取全部股票列表时捕获到已知错误: {type(e).__name__}")
            raise e
        except Exception as e:
            logger.exception(
                f"为日期 {date} 获取全部股票列表时发生未知错误: {e}")
            raise DataSourceError(
                f"为日期 {date} 获取全部股票列表时发生未知错误: {e}")

    def get_deposit_rate_data(self, start_date: Optional[str] = None, end_date: Optional[str] = None) -> pd.DataFrame:
        """使用 Baostock 获取存款基准利率。"""
        return _fetch_macro_data(bs.query_deposit_rate_data, "存款利率", start_date, end_date)

    def get_loan_rate_data(self, start_date: Optional[str] = None, end_date: Optional[str] = None) -> pd.DataFrame:
        """使用 Baostock 获取贷款基准利率。"""
        return _fetch_macro_data(bs.query_loan_rate_data, "贷款利率", start_date, end_date)

    def get_required_reserve_ratio_data(self, start_date: Optional[str] = None, end_date: Optional[str] = None, year_type: str = '0') -> pd.DataFrame:
        """使用 Baostock 获取存款准备金率。"""
        return _fetch_macro_data(bs.query_required_reserve_ratio_data, "存款准备金率", start_date, end_date, yearType=year_type)

    def get_money_supply_data_month(self, start_date: Optional[str] = None, end_date: Optional[str] = None) -> pd.DataFrame:
        """使用 Baostock 获取月度货币供应量。"""
        return _fetch_macro_data(bs.query_money_supply_data_month, "月度货币供应量", start_date, end_date)

    def get_money_supply_data_year(self, start_date: Optional[str] = None, end_date: Optional[str] = None) -> pd.DataFrame:
        """使用 Baostock 获取年度货币供应量。"""
        return _fetch_macro_data(bs.query_money_supply_data_year, "年度货币供应量", start_date, end_date)

    # 注意: SHIBOR 在当前使用的 Baostock API 绑定中不可用; 未实现。
