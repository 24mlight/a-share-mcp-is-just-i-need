# Defines the abstract interface for financial data sources
from abc import ABC, abstractmethod
import pandas as pd
from typing import Optional, List

class DataSourceError(Exception):
    """Base exception for data source errors."""
    pass


class LoginError(DataSourceError):
    """Exception raised for login failures to the data source."""
    pass


class NoDataFoundError(DataSourceError):
    """Exception raised when no data is found for the given query."""
    pass


class FinancialDataSource(ABC):
    """
    Abstract base class defining the interface for financial data sources.
    Implementations of this class provide access to specific financial data APIs
    (e.g., Baostock, Akshare).
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
        Fetches historical K-line (OHLCV) data for a given stock code.

        Args:
            code: The stock code (e.g., 'sh.600000', 'sz.000001').
            start_date: Start date in 'YYYY-MM-DD' format.
            end_date: End date in 'YYYY-MM-DD' format.
            frequency: Data frequency. Common values depend on the underlying
                       source (e.g., 'd' for daily, 'w' for weekly, 'm' for monthly,
                       '5', '15', '30', '60' for minutes). Defaults to 'd'.
            adjust_flag: Adjustment flag for historical data. Common values
                         depend on the source (e.g., '1' for forward adjusted,
                         '2' for backward adjusted, '3' for non-adjusted).
                         Defaults to '3'.
            fields: Optional list of specific fields to retrieve. If None,
                    retrieves default fields defined by the implementation.

        Returns:
            A pandas DataFrame containing the historical K-line data, with
            columns corresponding to the requested fields.

        Raises:
            LoginError: If login to the data source fails.
            NoDataFoundError: If no data is found for the query.
            DataSourceError: For other data source related errors.
            ValueError: If input parameters are invalid.
        """
        pass

    @abstractmethod
    def get_stock_basic_info(self, code: str) -> pd.DataFrame:
        """
        Fetches basic information for a given stock code.

        Args:
            code: The stock code (e.g., 'sh.600000', 'sz.000001').

        Returns:
            A pandas DataFrame containing the basic stock information.
            The structure and columns depend on the underlying data source.
            Typically contains info like name, industry, listing date, etc.

        Raises:
            LoginError: If login to the data source fails.
            NoDataFoundError: If no data is found for the query.
            DataSourceError: For other data source related errors.
            ValueError: If the input code is invalid.
        """
        pass

    @abstractmethod
    def get_trade_dates(self, start_date: Optional[str] = None, end_date: Optional[str] = None) -> pd.DataFrame:
        """Fetches trading dates information within a range."""
        pass

    @abstractmethod
    def get_all_stock(self, date: Optional[str] = None) -> pd.DataFrame:
        """Fetches list of all stocks and their trading status on a given date."""
        pass

    @abstractmethod
    def get_deposit_rate_data(self, start_date: Optional[str] = None, end_date: Optional[str] = None) -> pd.DataFrame:
        """Fetches benchmark deposit rates."""
        pass

    @abstractmethod
    def get_loan_rate_data(self, start_date: Optional[str] = None, end_date: Optional[str] = None) -> pd.DataFrame:
        """Fetches benchmark loan rates."""
        pass

    @abstractmethod
    def get_required_reserve_ratio_data(self, start_date: Optional[str] = None, end_date: Optional[str] = None, year_type: str = '0') -> pd.DataFrame:
        """Fetches required reserve ratio data."""
        pass

    @abstractmethod
    def get_money_supply_data_month(self, start_date: Optional[str] = None, end_date: Optional[str] = None) -> pd.DataFrame:
        """Fetches monthly money supply data (M0, M1, M2)."""
        pass

    @abstractmethod
    def get_money_supply_data_year(self, start_date: Optional[str] = None, end_date: Optional[str] = None) -> pd.DataFrame:
        """Fetches yearly money supply data (M0, M1, M2 - year end balance)."""
        pass

    @abstractmethod
    def get_dividend_data(self, code: str, year: str, year_type: str = "report") -> pd.DataFrame:
        """Fetches dividend information for a stock and year."""
        pass

    @abstractmethod
    def get_adjust_factor_data(self, code: str, start_date: str, end_date: str) -> pd.DataFrame:
        """Fetches adjustment factor data used for price adjustments."""
        pass

    # Financial report datasets
    @abstractmethod
    def get_profit_data(self, code: str, year: str, quarter: int) -> pd.DataFrame:
        pass

    @abstractmethod
    def get_operation_data(self, code: str, year: str, quarter: int) -> pd.DataFrame:
        pass

    @abstractmethod
    def get_growth_data(self, code: str, year: str, quarter: int) -> pd.DataFrame:
        pass

    @abstractmethod
    def get_balance_data(self, code: str, year: str, quarter: int) -> pd.DataFrame:
        pass

    @abstractmethod
    def get_cash_flow_data(self, code: str, year: str, quarter: int) -> pd.DataFrame:
        pass

    @abstractmethod
    def get_dupont_data(self, code: str, year: str, quarter: int) -> pd.DataFrame:
        pass

    @abstractmethod
    def get_performance_express_report(self, code: str, start_date: str, end_date: str) -> pd.DataFrame:
        pass

    @abstractmethod
    def get_forecast_report(self, code: str, start_date: str, end_date: str) -> pd.DataFrame:
        pass

    @abstractmethod
    def get_fina_indicator(self, code: str, start_date: str, end_date: str) -> pd.DataFrame:
        """
        Fetches financial indicators (ROE, gross margin, net margin, etc.) within a date range.

        Args:
            code: The stock code (e.g., 'sh.600000', 'sz.000001').
            start_date: Start date in 'YYYY-MM-DD' format.
            end_date: End date in 'YYYY-MM-DD' format.

        Returns:
            A pandas DataFrame containing financial indicators such as:
            - roe, roe_yearly (Return on Equity)
            - netprofit_margin, grossprofit_margin (Profitability ratios)
            - expense_ratio, netprofit_ratio
            - current_ratio, quick_ratio (Liquidity ratios)
            - etc.
        """
        pass

    # Index / industry
    @abstractmethod
    def get_stock_industry(self, code: Optional[str] = None, date: Optional[str] = None) -> pd.DataFrame:
        pass

    @abstractmethod
    def get_hs300_stocks(self, date: Optional[str] = None) -> pd.DataFrame:
        pass

    @abstractmethod
    def get_sz50_stocks(self, date: Optional[str] = None) -> pd.DataFrame:
        pass

    @abstractmethod
    def get_zz500_stocks(self, date: Optional[str] = None) -> pd.DataFrame:
        pass

    # Market overview
    @abstractmethod
    def get_all_stock(self, date: Optional[str] = None) -> pd.DataFrame:
        pass
    # Note: SHIBOR is not implemented in current Baostock bindings; no abstract method here.
