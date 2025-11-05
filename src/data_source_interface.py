# 定义金融数据源的抽象接口
from abc import ABC, abstractmethod
import pandas as pd
from typing import Optional, List

class DataSourceError(Exception):
    """数据源错误基类。"""
    pass


class LoginError(DataSourceError):
    """数据源登录失败时引发的异常。"""
    pass


class NoDataFoundError(DataSourceError):
    """当查询不到指定数据时引发的异常。"""
    pass


class FinancialDataSource(ABC):
    """
    定义金融数据源接口的抽象基类。
    该类的实现为特定的金融数据API（如 Baostock, Akshare）提供访问。
    """

    @abstractmethod
    def get_historical_k_data(
        self,
        code: str,
        start_date: str,
        end_date: str,
        frequency: str = "d",
        adjust_flag: str = "3",
        fields: Optional[List[str]] = None,
    ) -> pd.DataFrame:
        """
        获取指定股票代码的历史K线（OHLCV）数据。

        Args:
            code (str): 股票代码 (例如, 'sh.600000', 'sz.000001')。
            start_date (str): 开始日期，格式为 'YYYY-MM-DD'。
            end_date (str): 结束日期，格式为 'YYYY-MM-DD'。
            frequency (str, optional): 数据频率。常见取值依赖于底层数据源
                                       (例如, 'd' 代表日线, 'w' 代表周线, 'm' 代表月线,
                                       '5', '15', '30', '60' 代表分钟线)。默认为 'd'。
            adjust_flag (str, optional): 复权标志。常见取值依赖于数据源
                                         (例如, '1' 代表前复权, '2' 代表后复权, '3' 代表不复权)。
                                         默认为 '3'。
            fields (Optional[List[str]], optional): 需要检索的特定字段列表。如果为 None，
                                                    则检索由实现定义的默认字段。

        Returns:
            pd.DataFrame: 包含历史K线数据的 pandas DataFrame，列名对应请求的字段。

        Raises:
            LoginError: 如果数据源登录失败。
            NoDataFoundError: 如果查询不到数据。
            DataSourceError: 对于其他数据源相关的错误。
            ValueError: 如果输入参数无效。
        """
        pass

    @abstractmethod
    def get_stock_basic_info(self, code: str) -> pd.DataFrame:
        """
        获取指定股票代码的基本信息。

        Args:
            code (str): 股票代码 (例如, 'sh.600000', 'sz.000001')。

        Returns:
            pd.DataFrame: 包含股票基本信息的 pandas DataFrame。
                          其结构和列依赖于底层数据源。
                          通常包含名称、行业、上市日期等信息。

        Raises:
            LoginError: 如果数据源登录失败。
            NoDataFoundError: 如果查询不到数据。
            DataSourceError: 对于其他数据源相关的错误。
            ValueError: 如果输入的代码无效。
        """
        pass

    @abstractmethod
    def get_trade_dates(self, start_date: Optional[str] = None, end_date: Optional[str] = None) -> pd.DataFrame:
        """获取指定范围内的交易日信息。"""
        pass

    @abstractmethod
    def get_all_stock(self, date: Optional[str] = None) -> pd.DataFrame:
        """获取指定日期的所有股票列表及其交易状态。"""
        pass

    @abstractmethod
    def get_deposit_rate_data(self, start_date: Optional[str] = None, end_date: Optional[str] = None) -> pd.DataFrame:
        """获取存款基准利率。"""
        pass

    @abstractmethod
    def get_loan_rate_data(self, start_date: Optional[str] = None, end_date: Optional[str] = None) -> pd.DataFrame:
        """获取贷款基准利率。"""
        pass

    @abstractmethod
    def get_required_reserve_ratio_data(self, start_date: Optional[str] = None, end_date: Optional[str] = None, year_type: str = '0') -> pd.DataFrame:
        """获取存款准备金率数据。"""
        pass

    @abstractmethod
    def get_money_supply_data_month(self, start_date: Optional[str] = None, end_date: Optional[str] = None) -> pd.DataFrame:
        """获取月度货币供应量数据 (M0, M1, M2)。"""
        pass

    @abstractmethod
    def get_money_supply_data_year(self, start_date: Optional[str] = None, end_date: Optional[str] = None) -> pd.DataFrame:
        """获取年度货币供应量数据 (M0, M1, M2 - 年末余额)。"""
        pass

    # 注意: SHIBOR 在当前的 Baostock 绑定中未实现; 此处没有抽象方法。
