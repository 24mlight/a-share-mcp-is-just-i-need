"""
定义了金融数据源的抽象接口。

该模块包含 `FinancialDataSource` 抽象基类以及相关的自定义异常类。
`FinancialDataSource` 定义了一个标准接口，所有具体的数据源实现（如Baostock、Akshare）都应遵循此接口。
这样设计使得在不同的数据源之间切换变得容易，而无需修改上层调用代码。
"""
from abc import ABC, abstractmethod
import pandas as pd
from typing import Optional, List

class DataSourceError(Exception):
    """数据源错误的基类异常。"""
    pass


class LoginError(DataSourceError):
    """当登录数据源失败时引发的异常。"""
    pass


class NoDataFoundError(DataSourceError):
    """当根据给定查询未找到任何数据时引发的异常。"""
    pass


class FinancialDataSource(ABC):
    """
    定义金融数据源接口的抽象基类。

    该类的实现负责提供对特定金融数据API（例如Baostock、Akshare）的访问。
    所有方法都应是抽象的，并由子类实现。
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
            frequency (str, optional): 数据频率。常见取值依赖于具体数据源
                                       (例如, 'd' 代表日线, 'w' 代表周线, 'm' 代表月线,
                                       '5', '15', '30', '60' 代表分钟线)。默认为 'd'。
            adjust_flag (str, optional): 复权标记。常见取值依赖于具体数据源
                                         (例如, '1' 代表后复权, '2' 代表前复权, '3' 代表不复权)。
                                         默认为 '3'。
            fields (Optional[List[str]], optional): 希望获取的特定字段列表。如果为None，
                                                    则获取由具体实现定义的默认字段。

        Returns:
            pd.DataFrame: 包含历史K线数据的pandas DataFrame，列名对应所请求的字段。

        Raises:
            LoginError: 如果登录数据源失败。
            NoDataFoundError: 如果查询不到任何数据。
            DataSourceError: 如果发生其他与数据源相关的错误。
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
            pd.DataFrame: 包含股票基本信息的pandas DataFrame。
                          其结构和列依赖于底层数据源，通常包含名称、行业、上市日期等信息。

        Raises:
            LoginError: 如果登录数据源失败。
            NoDataFoundError: 如果查询不到任何数据。
            DataSourceError: 如果发生其他与数据源相关的错误。
            ValueError: 如果输入的代码无效。
        """
        pass

    @abstractmethod
    def get_trade_dates(self, start_date: Optional[str] = None, end_date: Optional[str] = None) -> pd.DataFrame:
        """
        获取指定范围内的交易日信息。

        Args:
            start_date (Optional[str], optional): 开始日期，格式 'YYYY-MM-DD'。默认为None。
            end_date (Optional[str], optional): 结束日期，格式 'YYYY-MM-DD'。默认为None。

        Returns:
            pd.DataFrame: 包含交易日信息的DataFrame。
        """
        pass

    @abstractmethod
    def get_all_stock(self, date: Optional[str] = None) -> pd.DataFrame:
        """
        获取指定日期的所有股票列表及其交易状态。

        Args:
            date (Optional[str], optional): 查询日期，格式 'YYYY-MM-DD'。如果为None，则获取最新数据。默认为None。

        Returns:
            pd.DataFrame: 包含所有股票信息的DataFrame。
        """
        pass

    @abstractmethod
    def get_deposit_rate_data(self, start_date: Optional[str] = None, end_date: Optional[str] = None) -> pd.DataFrame:
        """
        获取存款基准利率。

        Args:
            start_date (Optional[str], optional): 开始日期，格式 'YYYY-MM-DD'。默认为None。
            end_date (Optional[str], optional): 结束日期，格式 'YYYY-MM-DD'。默认为None。

        Returns:
            pd.DataFrame: 包含存款利率数据的DataFrame。
        """
        pass

    @abstractmethod
    def get_loan_rate_data(self, start_date: Optional[str] = None, end_date: Optional[str] = None) -> pd.DataFrame:
        """
        获取贷款基准利率。

        Args:
            start_date (Optional[str], optional): 开始日期，格式 'YYYY-MM-DD'。默认为None。
            end_date (Optional[str], optional): 结束日期，格式 'YYYY-MM-DD'。默认为None。

        Returns:
            pd.DataFrame: 包含贷款利率数据的DataFrame。
        """
        pass

    @abstractmethod
    def get_required_reserve_ratio_data(self, start_date: Optional[str] = None, end_date: Optional[str] = None, year_type: str = '0') -> pd.DataFrame:
        """
        获取存款准备金率数据。

        Args:
            start_date (Optional[str], optional): 开始日期，格式 'YYYY-MM-DD'。默认为None。
            end_date (Optional[str], optional): 结束日期，格式 'YYYY-MM-DD'。默认为None。
            year_type (str, optional): 年份类型，具体含义取决于数据源。默认为 '0'。

        Returns:
            pd.DataFrame: 包含存款准备金率数据的DataFrame。
        """
        pass

    @abstractmethod
    def get_money_supply_data_month(self, start_date: Optional[str] = None, end_date: Optional[str] = None) -> pd.DataFrame:
        """
        获取月度货币供应量数据 (M0, M1, M2)。

        Args:
            start_date (Optional[str], optional): 开始日期，格式 'YYYY-MM'。默认为None。
            end_date (Optional[str], optional): 结束日期，格式 'YYYY-MM'。默认为None。

        Returns:
            pd.DataFrame: 包含月度货币供应量数据的DataFrame。
        """
        pass

    @abstractmethod
    def get_money_supply_data_year(self, start_date: Optional[str] = None, end_date: Optional[str] = None) -> pd.DataFrame:
        """
        获取年度货币供应量数据 (M0, M1, M2 - 年末余额)。

        Args:
            start_date (Optional[str], optional): 开始年份，格式 'YYYY'。默认为None。
            end_date (Optional[str], optional): 结束年份，格式 'YYYY'。默认为None。

        Returns:
            pd.DataFrame: 包含年度货币供应量数据的DataFrame。
        """
        pass

    # Note: SHIBOR is not implemented in current Baostock bindings; no abstract method here.
