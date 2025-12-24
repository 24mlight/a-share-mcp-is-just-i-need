# Implementation of the FinancialDataSource interface using Baostock
import baostock as bs
import pandas as pd
from typing import List, Optional
import logging
from .data_source_interface import FinancialDataSource, DataSourceError, NoDataFoundError, LoginError
from .utils import baostock_login_context

# Get a logger instance for this module
logger = logging.getLogger(__name__)

DEFAULT_K_FIELDS = [
    "date", "code", "open", "high", "low", "close", "preclose",
    "volume", "amount", "adjustflag", "turn", "tradestatus",
    "pctChg", "peTTM", "pbMRQ", "psTTM", "pcfNcfTTM", "isST"
]

DEFAULT_BASIC_FIELDS = [
    "code", "tradeStatus", "code_name"
    # Add more default fields as needed, e.g., "industry", "listingDate"
]

# Helper function to reduce repetition in financial data fetching


def _fetch_financial_data(
    bs_query_func,
    data_type_name: str,
    code: str,
    year: str,
    quarter: int
) -> pd.DataFrame:
    logger.info(
        f"Fetching {data_type_name} data for {code}, year={year}, quarter={quarter}")
    try:
        with baostock_login_context():
            # Assuming all these functions take code, year, quarter
            rs = bs_query_func(code=code, year=year, quarter=quarter)

            if rs.error_code != '0':
                logger.error(
                    f"Baostock API error ({data_type_name}) for {code}: {rs.error_msg} (code: {rs.error_code})")
                if "no record found" in rs.error_msg.lower() or rs.error_code == '10002':
                    raise NoDataFoundError(
                        f"No {data_type_name} data found for {code}, {year}Q{quarter}. Baostock msg: {rs.error_msg}")
                else:
                    raise DataSourceError(
                        f"Baostock API error fetching {data_type_name} data: {rs.error_msg} (code: {rs.error_code})")

            data_list = []
            while rs.next():
                data_list.append(rs.get_row_data())

            if not data_list:
                logger.warning(
                    f"No {data_type_name} data found for {code}, {year}Q{quarter} (empty result set from Baostock).")
                raise NoDataFoundError(
                    f"No {data_type_name} data found for {code}, {year}Q{quarter} (empty result set).")

            result_df = pd.DataFrame(data_list, columns=rs.fields)
            logger.info(
                f"Retrieved {len(result_df)} {data_type_name} records for {code}, {year}Q{quarter}.")
            return result_df

    except (LoginError, NoDataFoundError, DataSourceError, ValueError) as e:
        logger.warning(
            f"Caught known error fetching {data_type_name} data for {code}: {type(e).__name__}")
        raise e
    except Exception as e:
        logger.exception(
            f"Unexpected error fetching {data_type_name} data for {code}: {e}")
        raise DataSourceError(
            f"Unexpected error fetching {data_type_name} data for {code}: {e}")

# Helper function to reduce repetition for index constituent data fetching


def _fetch_index_constituent_data(
    bs_query_func,
    index_name: str,
    date: Optional[str] = None
) -> pd.DataFrame:
    logger.info(
        f"Fetching {index_name} constituents for date={date or 'latest'}")
    try:
        with baostock_login_context():
            # date is optional, defaults to latest
            rs = bs_query_func(date=date)

            if rs.error_code != '0':
                logger.error(
                    f"Baostock API error ({index_name} Constituents) for date {date}: {rs.error_msg} (code: {rs.error_code})")
                if "no record found" in rs.error_msg.lower() or rs.error_code == '10002':
                    raise NoDataFoundError(
                        f"No {index_name} constituent data found for date {date}. Baostock msg: {rs.error_msg}")
                else:
                    raise DataSourceError(
                        f"Baostock API error fetching {index_name} constituents: {rs.error_msg} (code: {rs.error_code})")

            data_list = []
            while rs.next():
                data_list.append(rs.get_row_data())

            if not data_list:
                logger.warning(
                    f"No {index_name} constituent data found for date {date} (empty result set).")
                raise NoDataFoundError(
                    f"No {index_name} constituent data found for date {date} (empty result set).")

            result_df = pd.DataFrame(data_list, columns=rs.fields)
            logger.info(
                f"Retrieved {len(result_df)} {index_name} constituents for date {date or 'latest'}.")
            return result_df

    except (LoginError, NoDataFoundError, DataSourceError, ValueError) as e:
        logger.warning(
            f"Caught known error fetching {index_name} constituents for date {date}: {type(e).__name__}")
        raise e
    except Exception as e:
        logger.exception(
            f"Unexpected error fetching {index_name} constituents for date {date}: {e}")
        raise DataSourceError(
            f"Unexpected error fetching {index_name} constituents for date {date}: {e}")

# Helper function to reduce repetition for macroeconomic data fetching


def _fetch_macro_data(
    bs_query_func,
    data_type_name: str,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    **kwargs  # For extra params like yearType
) -> pd.DataFrame:
    date_range_log = f"from {start_date or 'default'} to {end_date or 'default'}"
    kwargs_log = f", extra_args={kwargs}" if kwargs else ""
    logger.info(f"Fetching {data_type_name} data {date_range_log}{kwargs_log}")
    try:
        with baostock_login_context():
            rs = bs_query_func(start_date=start_date,
                               end_date=end_date, **kwargs)

            if rs.error_code != '0':
                logger.error(
                    f"Baostock API error ({data_type_name}): {rs.error_msg} (code: {rs.error_code})")
                if "no record found" in rs.error_msg.lower() or rs.error_code == '10002':
                    raise NoDataFoundError(
                        f"No {data_type_name} data found for the specified criteria. Baostock msg: {rs.error_msg}")
                else:
                    raise DataSourceError(
                        f"Baostock API error fetching {data_type_name} data: {rs.error_msg} (code: {rs.error_code})")

            data_list = []
            while rs.next():
                data_list.append(rs.get_row_data())

            if not data_list:
                logger.warning(
                    f"No {data_type_name} data found for the specified criteria (empty result set).")
                raise NoDataFoundError(
                    f"No {data_type_name} data found for the specified criteria (empty result set).")

            result_df = pd.DataFrame(data_list, columns=rs.fields)
            logger.info(
                f"Retrieved {len(result_df)} {data_type_name} records.")
            return result_df

    except (LoginError, NoDataFoundError, DataSourceError, ValueError) as e:
        logger.warning(
            f"Caught known error fetching {data_type_name} data: {type(e).__name__}")
        raise e
    except Exception as e:
        logger.exception(
            f"Unexpected error fetching {data_type_name} data: {e}")
        raise DataSourceError(
            f"Unexpected error fetching {data_type_name} data: {e}")


class BaostockDataSource(FinancialDataSource):
    """
    Concrete implementation of FinancialDataSource using the Baostock library.
    """

    def _format_fields(self, fields: Optional[List[str]], default_fields: List[str]) -> str:
        """Formats the list of fields into a comma-separated string for Baostock."""
        if fields is None or not fields:
            logger.debug(
                f"No specific fields requested, using defaults: {default_fields}")
            return ",".join(default_fields)
        # Basic validation: ensure requested fields are strings
        if not all(isinstance(f, str) for f in fields):
            raise ValueError("All items in the fields list must be strings.")
        logger.debug(f"Using requested fields: {fields}")
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
        """Fetches historical K-line data using Baostock."""
        logger.info(
            f"Fetching K-data for {code} ({start_date} to {end_date}), freq={frequency}, adjust={adjust_flag}")
        try:
            formatted_fields = self._format_fields(fields, DEFAULT_K_FIELDS)
            logger.debug(
                f"Requesting fields from Baostock: {formatted_fields}")

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
                        f"Baostock API error (K-data) for {code}: {rs.error_msg} (code: {rs.error_code})")
                    # Check common error codes, e.g., for no data
                    if "no record found" in rs.error_msg.lower() or rs.error_code == '10002':  # Example error code
                        raise NoDataFoundError(
                            f"No historical data found for {code} in the specified range. Baostock msg: {rs.error_msg}")
                    else:
                        raise DataSourceError(
                            f"Baostock API error fetching K-data: {rs.error_msg} (code: {rs.error_code})")

                data_list = []
                while rs.next():
                    data_list.append(rs.get_row_data())

                if not data_list:
                    logger.warning(
                        f"No historical data found for {code} in range (empty result set from Baostock).")
                    raise NoDataFoundError(
                        f"No historical data found for {code} in the specified range (empty result set).")

                # Crucial: Use rs.fields for column names
                result_df = pd.DataFrame(data_list, columns=rs.fields)
                logger.info(f"Retrieved {len(result_df)} records for {code}.")
                return result_df

        except (LoginError, NoDataFoundError, DataSourceError, ValueError) as e:
            # Re-raise known errors
            logger.warning(
                f"Caught known error fetching K-data for {code}: {type(e).__name__}")
            raise e
        except Exception as e:
            # Wrap unexpected errors
            # Use logger.exception to include traceback
            logger.exception(
                f"Unexpected error fetching K-data for {code}: {e}")
            raise DataSourceError(
                f"Unexpected error fetching K-data for {code}: {e}")

    def get_stock_basic_info(self, code: str, fields: Optional[List[str]] = None) -> pd.DataFrame:
        """Fetches basic stock information using Baostock."""
        logger.info(f"Fetching basic info for {code}")
        try:
            # Note: query_stock_basic doesn't seem to have a fields parameter in docs,
            # but we keep the signature consistent. It returns a fixed set.
            # We will use the `fields` argument post-query to select columns if needed.
            logger.debug(
                f"Requesting basic info for {code}. Optional fields requested: {fields}")

            with baostock_login_context():
                # Example: Fetch basic info; adjust API call if needed based on baostock docs
                # rs = bs.query_stock_basic(code=code, code_name=code_name) # If supporting name lookup
                rs = bs.query_stock_basic(code=code)

                if rs.error_code != '0':
                    logger.error(
                        f"Baostock API error (Basic Info) for {code}: {rs.error_msg} (code: {rs.error_code})")
                    if "no record found" in rs.error_msg.lower() or rs.error_code == '10002':
                        raise NoDataFoundError(
                            f"No basic info found for {code}. Baostock msg: {rs.error_msg}")
                    else:
                        raise DataSourceError(
                            f"Baostock API error fetching basic info: {rs.error_msg} (code: {rs.error_code})")

                data_list = []
                while rs.next():
                    data_list.append(rs.get_row_data())

                if not data_list:
                    logger.warning(
                        f"No basic info found for {code} (empty result set from Baostock).")
                    raise NoDataFoundError(
                        f"No basic info found for {code} (empty result set).")

                # Crucial: Use rs.fields for column names
                result_df = pd.DataFrame(data_list, columns=rs.fields)
                logger.info(
                    f"Retrieved basic info for {code}. Columns: {result_df.columns.tolist()}")

                # Optional: Select subset of columns if `fields` argument was provided
                if fields:
                    available_cols = [
                        col for col in fields if col in result_df.columns]
                    if not available_cols:
                        raise ValueError(
                            f"None of the requested fields {fields} are available in the basic info result.")
                    logger.debug(
                        f"Selecting columns: {available_cols} from basic info for {code}")
                    result_df = result_df[available_cols]

                return result_df

        except (LoginError, NoDataFoundError, DataSourceError, ValueError) as e:
            logger.warning(
                f"Caught known error fetching basic info for {code}: {type(e).__name__}")
            raise e
        except Exception as e:
            logger.exception(
                f"Unexpected error fetching basic info for {code}: {e}")
            raise DataSourceError(
                f"Unexpected error fetching basic info for {code}: {e}")

    def get_dividend_data(self, code: str, year: str, year_type: str = "report") -> pd.DataFrame:
        """Fetches dividend information using Baostock."""
        logger.info(
            f"Fetching dividend data for {code}, year={year}, year_type={year_type}")
        try:
            with baostock_login_context():
                rs = bs.query_dividend_data(
                    code=code, year=year, yearType=year_type)

                if rs.error_code != '0':
                    logger.error(
                        f"Baostock API error (Dividend) for {code}: {rs.error_msg} (code: {rs.error_code})")
                    if "no record found" in rs.error_msg.lower() or rs.error_code == '10002':
                        raise NoDataFoundError(
                            f"No dividend data found for {code} and year {year}. Baostock msg: {rs.error_msg}")
                    else:
                        raise DataSourceError(
                            f"Baostock API error fetching dividend data: {rs.error_msg} (code: {rs.error_code})")

                data_list = []
                while rs.next():
                    data_list.append(rs.get_row_data())

                if not data_list:
                    logger.warning(
                        f"No dividend data found for {code}, year {year} (empty result set from Baostock).")
                    raise NoDataFoundError(
                        f"No dividend data found for {code}, year {year} (empty result set).")

                result_df = pd.DataFrame(data_list, columns=rs.fields)
                logger.info(
                    f"Retrieved {len(result_df)} dividend records for {code}, year {year}.")
                return result_df

        except (LoginError, NoDataFoundError, DataSourceError, ValueError) as e:
            logger.warning(
                f"Caught known error fetching dividend data for {code}: {type(e).__name__}")
            raise e
        except Exception as e:
            logger.exception(
                f"Unexpected error fetching dividend data for {code}: {e}")
            raise DataSourceError(
                f"Unexpected error fetching dividend data for {code}: {e}")

    def get_adjust_factor_data(self, code: str, start_date: str, end_date: str) -> pd.DataFrame:
        """Fetches adjustment factor data using Baostock."""
        logger.info(
            f"Fetching adjustment factor data for {code} ({start_date} to {end_date})")
        try:
            with baostock_login_context():
                rs = bs.query_adjust_factor(
                    code=code, start_date=start_date, end_date=end_date)

                if rs.error_code != '0':
                    logger.error(
                        f"Baostock API error (Adjust Factor) for {code}: {rs.error_msg} (code: {rs.error_code})")
                    if "no record found" in rs.error_msg.lower() or rs.error_code == '10002':
                        raise NoDataFoundError(
                            f"No adjustment factor data found for {code} in the specified range. Baostock msg: {rs.error_msg}")
                    else:
                        raise DataSourceError(
                            f"Baostock API error fetching adjust factor data: {rs.error_msg} (code: {rs.error_code})")

                data_list = []
                while rs.next():
                    data_list.append(rs.get_row_data())

                if not data_list:
                    logger.warning(
                        f"No adjustment factor data found for {code} in range (empty result set from Baostock).")
                    raise NoDataFoundError(
                        f"No adjustment factor data found for {code} in the specified range (empty result set).")

                result_df = pd.DataFrame(data_list, columns=rs.fields)
                logger.info(
                    f"Retrieved {len(result_df)} adjustment factor records for {code}.")
                return result_df

        except (LoginError, NoDataFoundError, DataSourceError, ValueError) as e:
            logger.warning(
                f"Caught known error fetching adjust factor data for {code}: {type(e).__name__}")
            raise e
        except Exception as e:
            logger.exception(
                f"Unexpected error fetching adjust factor data for {code}: {e}")
            raise DataSourceError(
                f"Unexpected error fetching adjust factor data for {code}: {e}")

    def get_profit_data(self, code: str, year: str, quarter: int) -> pd.DataFrame:
        """Fetches quarterly profitability data using Baostock."""
        return _fetch_financial_data(bs.query_profit_data, "Profitability", code, year, quarter)

    def get_operation_data(self, code: str, year: str, quarter: int) -> pd.DataFrame:
        """Fetches quarterly operation capability data using Baostock."""
        return _fetch_financial_data(bs.query_operation_data, "Operation Capability", code, year, quarter)

    def get_growth_data(self, code: str, year: str, quarter: int) -> pd.DataFrame:
        """Fetches quarterly growth capability data using Baostock."""
        return _fetch_financial_data(bs.query_growth_data, "Growth Capability", code, year, quarter)

    def get_balance_data(self, code: str, year: str, quarter: int) -> pd.DataFrame:
        """Fetches quarterly balance sheet data (solvency) using Baostock."""
        return _fetch_financial_data(bs.query_balance_data, "Balance Sheet", code, year, quarter)

    def get_cash_flow_data(self, code: str, year: str, quarter: int) -> pd.DataFrame:
        """Fetches quarterly cash flow data using Baostock."""
        return _fetch_financial_data(bs.query_cash_flow_data, "Cash Flow", code, year, quarter)

    def get_dupont_data(self, code: str, year: str, quarter: int) -> pd.DataFrame:
        """Fetches quarterly DuPont analysis data using Baostock."""
        return _fetch_financial_data(bs.query_dupont_data, "DuPont Analysis", code, year, quarter)

    def get_performance_express_report(self, code: str, start_date: str, end_date: str) -> pd.DataFrame:
        """Fetches performance express reports (业绩快报) using Baostock."""
        logger.info(
            f"Fetching Performance Express Report for {code} ({start_date} to {end_date})")
        try:
            with baostock_login_context():
                rs = bs.query_performance_express_report(
                    code=code, start_date=start_date, end_date=end_date)

                if rs.error_code != '0':
                    logger.error(
                        f"Baostock API error (Perf Express) for {code}: {rs.error_msg} (code: {rs.error_code})")
                    if "no record found" in rs.error_msg.lower() or rs.error_code == '10002':
                        raise NoDataFoundError(
                            f"No performance express report found for {code} in range {start_date}-{end_date}. Baostock msg: {rs.error_msg}")
                    else:
                        raise DataSourceError(
                            f"Baostock API error fetching performance express report: {rs.error_msg} (code: {rs.error_code})")

                data_list = []
                while rs.next():
                    data_list.append(rs.get_row_data())

                if not data_list:
                    logger.warning(
                        f"No performance express report found for {code} in range {start_date}-{end_date} (empty result set).")
                    raise NoDataFoundError(
                        f"No performance express report found for {code} in range {start_date}-{end_date} (empty result set).")

                result_df = pd.DataFrame(data_list, columns=rs.fields)
                logger.info(
                    f"Retrieved {len(result_df)} performance express report records for {code}.")
                return result_df

        except (LoginError, NoDataFoundError, DataSourceError, ValueError) as e:
            logger.warning(
                f"Caught known error fetching performance express report for {code}: {type(e).__name__}")
            raise e
        except Exception as e:
            logger.exception(
                f"Unexpected error fetching performance express report for {code}: {e}")
            raise DataSourceError(
                f"Unexpected error fetching performance express report for {code}: {e}")

    def get_forecast_report(self, code: str, start_date: str, end_date: str) -> pd.DataFrame:
        """Fetches performance forecast reports (业绩预告) using Baostock."""
        logger.info(
            f"Fetching Performance Forecast Report for {code} ({start_date} to {end_date})")
        try:
            with baostock_login_context():
                rs = bs.query_forecast_report(
                    code=code, start_date=start_date, end_date=end_date)
                # Note: Baostock docs mention pagination for this, but the Python API doesn't seem to expose it directly.
                # We fetch all available pages in the loop below.

                if rs.error_code != '0':
                    logger.error(
                        f"Baostock API error (Forecast) for {code}: {rs.error_msg} (code: {rs.error_code})")
                    if "no record found" in rs.error_msg.lower() or rs.error_code == '10002':
                        raise NoDataFoundError(
                            f"No performance forecast report found for {code} in range {start_date}-{end_date}. Baostock msg: {rs.error_msg}")
                    else:
                        raise DataSourceError(
                            f"Baostock API error fetching performance forecast report: {rs.error_msg} (code: {rs.error_code})")

                data_list = []
                while rs.next():  # Loop should handle pagination implicitly if rs manages it
                    data_list.append(rs.get_row_data())

                if not data_list:
                    logger.warning(
                        f"No performance forecast report found for {code} in range {start_date}-{end_date} (empty result set).")
                    raise NoDataFoundError(
                        f"No performance forecast report found for {code} in range {start_date}-{end_date} (empty result set).")

                result_df = pd.DataFrame(data_list, columns=rs.fields)
                logger.info(
                    f"Retrieved {len(result_df)} performance forecast report records for {code}.")
                return result_df

        except (LoginError, NoDataFoundError, DataSourceError, ValueError) as e:
            logger.warning(
                f"Caught known error fetching performance forecast report for {code}: {type(e).__name__}")
            raise e
        except Exception as e:
            logger.exception(
                f"Unexpected error fetching performance forecast report for {code}: {e}")
            raise DataSourceError(
                f"Unexpected error fetching performance forecast report for {code}: {e}")

    def get_stock_industry(self, code: Optional[str] = None, date: Optional[str] = None) -> pd.DataFrame:
        """Fetches industry classification using Baostock."""
        log_msg = f"Fetching industry data for code={code or 'all'}, date={date or 'latest'}"
        logger.info(log_msg)
        try:
            with baostock_login_context():
                rs = bs.query_stock_industry(code=code, date=date)

                if rs.error_code != '0':
                    logger.error(
                        f"Baostock API error (Industry) for {code}, {date}: {rs.error_msg} (code: {rs.error_code})")
                    if "no record found" in rs.error_msg.lower() or rs.error_code == '10002':
                        raise NoDataFoundError(
                            f"No industry data found for {code}, {date}. Baostock msg: {rs.error_msg}")
                    else:
                        raise DataSourceError(
                            f"Baostock API error fetching industry data: {rs.error_msg} (code: {rs.error_code})")

                data_list = []
                while rs.next():
                    data_list.append(rs.get_row_data())

                if not data_list:
                    logger.warning(
                        f"No industry data found for {code}, {date} (empty result set).")
                    raise NoDataFoundError(
                        f"No industry data found for {code}, {date} (empty result set).")

                result_df = pd.DataFrame(data_list, columns=rs.fields)
                logger.info(
                    f"Retrieved {len(result_df)} industry records for {code or 'all'}, {date or 'latest'}.")
                return result_df

        except (LoginError, NoDataFoundError, DataSourceError, ValueError) as e:
            logger.warning(
                f"Caught known error fetching industry data for {code}, {date}: {type(e).__name__}")
            raise e
        except Exception as e:
            logger.exception(
                f"Unexpected error fetching industry data for {code}, {date}: {e}")
            raise DataSourceError(
                f"Unexpected error fetching industry data for {code}, {date}: {e}")

    def get_sz50_stocks(self, date: Optional[str] = None) -> pd.DataFrame:
        """Fetches SZSE 50 index constituents using Baostock."""
        return _fetch_index_constituent_data(bs.query_sz50_stocks, "SZSE 50", date)

    def get_hs300_stocks(self, date: Optional[str] = None) -> pd.DataFrame:
        """Fetches CSI 300 index constituents using Baostock."""
        return _fetch_index_constituent_data(bs.query_hs300_stocks, "CSI 300", date)

    def get_zz500_stocks(self, date: Optional[str] = None) -> pd.DataFrame:
        """Fetches CSI 500 index constituents using Baostock."""
        return _fetch_index_constituent_data(bs.query_zz500_stocks, "CSI 500", date)

    def get_trade_dates(self, start_date: Optional[str] = None, end_date: Optional[str] = None) -> pd.DataFrame:
        """Fetches trading dates using Baostock."""
        logger.info(
            f"Fetching trade dates from {start_date or 'default'} to {end_date or 'default'}")
        try:
            with baostock_login_context():  # Login might not be strictly needed for this, but keeping consistent
                rs = bs.query_trade_dates(
                    start_date=start_date, end_date=end_date)

                if rs.error_code != '0':
                    logger.error(
                        f"Baostock API error (Trade Dates): {rs.error_msg} (code: {rs.error_code})")
                    # Unlikely to have 'no record found' for dates, but handle API errors
                    raise DataSourceError(
                        f"Baostock API error fetching trade dates: {rs.error_msg} (code: {rs.error_code})")

                data_list = []
                while rs.next():
                    data_list.append(rs.get_row_data())

                if not data_list:
                    # This case should ideally not happen if the API returns a valid range
                    logger.warning(
                        f"No trade dates returned for range {start_date}-{end_date} (empty result set).")
                    raise NoDataFoundError(
                        f"No trade dates found for range {start_date}-{end_date} (empty result set).")

                result_df = pd.DataFrame(data_list, columns=rs.fields)
                logger.info(f"Retrieved {len(result_df)} trade date records.")
                return result_df

        except (LoginError, NoDataFoundError, DataSourceError, ValueError) as e:
            logger.warning(
                f"Caught known error fetching trade dates: {type(e).__name__}")
            raise e
        except Exception as e:
            logger.exception(f"Unexpected error fetching trade dates: {e}")
            raise DataSourceError(
                f"Unexpected error fetching trade dates: {e}")

    def get_all_stock(self, date: Optional[str] = None) -> pd.DataFrame:
        """Fetches all stock list for a given date using Baostock."""
        logger.info(f"Fetching all stock list for date={date or 'default'}")
        try:
            with baostock_login_context():
                rs = bs.query_all_stock(day=date)

                if rs.error_code != '0':
                    logger.error(
                        f"Baostock API error (All Stock) for date {date}: {rs.error_msg} (code: {rs.error_code})")
                    if "no record found" in rs.error_msg.lower() or rs.error_code == '10002':  # Check if this applies
                        raise NoDataFoundError(
                            f"No stock data found for date {date}. Baostock msg: {rs.error_msg}")
                    else:
                        raise DataSourceError(
                            f"Baostock API error fetching all stock list: {rs.error_msg} (code: {rs.error_code})")

                data_list = []
                while rs.next():
                    data_list.append(rs.get_row_data())

                if not data_list:
                    logger.warning(
                        f"No stock list returned for date {date} (empty result set).")
                    raise NoDataFoundError(
                        f"No stock list found for date {date} (empty result set).")

                result_df = pd.DataFrame(data_list, columns=rs.fields)
                logger.info(
                    f"Retrieved {len(result_df)} stock records for date {date or 'default'}.")
                return result_df

        except (LoginError, NoDataFoundError, DataSourceError, ValueError) as e:
            logger.warning(
                f"Caught known error fetching all stock list for date {date}: {type(e).__name__}")
            raise e
        except Exception as e:
            logger.exception(
                f"Unexpected error fetching all stock list for date {date}: {e}")
            raise DataSourceError(
                f"Unexpected error fetching all stock list for date {date}: {e}")

    def get_deposit_rate_data(self, start_date: Optional[str] = None, end_date: Optional[str] = None) -> pd.DataFrame:
        """Fetches benchmark deposit rates using Baostock."""
        return _fetch_macro_data(bs.query_deposit_rate_data, "Deposit Rate", start_date, end_date)

    def get_loan_rate_data(self, start_date: Optional[str] = None, end_date: Optional[str] = None) -> pd.DataFrame:
        """Fetches benchmark loan rates using Baostock."""
        return _fetch_macro_data(bs.query_loan_rate_data, "Loan Rate", start_date, end_date)

    def get_required_reserve_ratio_data(self, start_date: Optional[str] = None, end_date: Optional[str] = None, year_type: str = '0') -> pd.DataFrame:
        """Fetches required reserve ratio data using Baostock."""
        # Note the extra yearType parameter handled by kwargs
        return _fetch_macro_data(bs.query_required_reserve_ratio_data, "Required Reserve Ratio", start_date, end_date, yearType=year_type)

    def get_money_supply_data_month(self, start_date: Optional[str] = None, end_date: Optional[str] = None) -> pd.DataFrame:
        """Fetches monthly money supply data (M0, M1, M2) using Baostock."""
        # Baostock expects YYYY-MM format for dates here
        return _fetch_macro_data(bs.query_money_supply_data_month, "Monthly Money Supply", start_date, end_date)

    def get_money_supply_data_year(self, start_date: Optional[str] = None, end_date: Optional[str] = None) -> pd.DataFrame:
        """Fetches yearly money supply data (M0, M1, M2 - year end balance) using Baostock."""
        # Baostock expects YYYY format for dates here
        return _fetch_macro_data(bs.query_money_supply_data_year, "Yearly Money Supply", start_date, end_date)

    def get_fina_indicator(self, code: str, start_date: str, end_date: str) -> pd.DataFrame:
        """
        Fetches comprehensive financial indicators by aggregating multiple Baostock APIs.

        Aggregates data from:
        - Profitability (盈利能力)
        - Operation Capability (营运能力)
        - Growth Capability (成长能力)
        - Balance Sheet/Solvency (偿债能力)
        - Cash Flow (现金流量)
        - DuPont Analysis (杜邦分析)
        """
        logger.info(f"Fetching aggregated financial indicators for {code} ({start_date} to {end_date})")

        # 解析日期范围，获取年份列表
        from datetime import datetime
        try:
            start = datetime.strptime(start_date, "%Y-%m-%d")
            end = datetime.strptime(end_date, "%Y-%m-%d")
        except ValueError:
            raise ValueError(f"Invalid date format. Expected YYYY-MM-DD, got {start_date} to {end_date}")

        years = set(str(y) for y in range(start.year, end.year + 1))

        all_results = []

        try:
            with baostock_login_context():
                for year in years:
                    for quarter in [1, 2, 3, 4]:
                        # 检查季度是否在日期范围内
                        quarter_start_month = (quarter - 1) * 3
                        quarter_start = datetime(int(year), quarter_start_month + 1, 1)
                        if quarter_start > end:
                            continue

                        record = {"code": code, "year": year, "quarter": quarter}

                        # 1. 盈利能力
                        try:
                            rs = bs.query_profit_data(code=code, year=year, quarter=quarter)
                            if rs.error_code == '0' and rs.next():
                                row = rs.get_row_data()
                                for i, field in enumerate(rs.fields):
                                    record[f"profit_{field}"] = row[i] if i < len(row) else None
                        except Exception as e:
                            logger.debug(f"Failed to fetch profit data for {code} {year}Q{quarter}: {e}")

                        # 2. 营运能力
                        try:
                            rs = bs.query_operation_data(code=code, year=year, quarter=quarter)
                            if rs.error_code == '0' and rs.next():
                                row = rs.get_row_data()
                                for i, field in enumerate(rs.fields):
                                    record[f"operation_{field}"] = row[i] if i < len(row) else None
                        except Exception as e:
                            logger.debug(f"Failed to fetch operation data for {code} {year}Q{quarter}: {e}")

                        # 3. 成长能力
                        try:
                            rs = bs.query_growth_data(code=code, year=year, quarter=quarter)
                            if rs.error_code == '0' and rs.next():
                                row = rs.get_row_data()
                                for i, field in enumerate(rs.fields):
                                    record[f"growth_{field}"] = row[i] if i < len(row) else None
                        except Exception as e:
                            logger.debug(f"Failed to fetch growth data for {code} {year}Q{quarter}: {e}")

                        # 4. 偿债能力
                        try:
                            rs = bs.query_balance_data(code=code, year=year, quarter=quarter)
                            if rs.error_code == '0' and rs.next():
                                row = rs.get_row_data()
                                for i, field in enumerate(rs.fields):
                                    record[f"balance_{field}"] = row[i] if i < len(row) else None
                        except Exception as e:
                            logger.debug(f"Failed to fetch balance data for {code} {year}Q{quarter}: {e}")

                        # 5. 现金流量
                        try:
                            rs = bs.query_cash_flow_data(code=code, year=year, quarter=quarter)
                            if rs.error_code == '0' and rs.next():
                                row = rs.get_row_data()
                                for i, field in enumerate(rs.fields):
                                    record[f"cashflow_{field}"] = row[i] if i < len(row) else None
                        except Exception as e:
                            logger.debug(f"Failed to fetch cash flow data for {code} {year}Q{quarter}: {e}")

                        # 6. 杜邦分析
                        try:
                            rs = bs.query_dupont_data(code=code, year=year, quarter=quarter)
                            if rs.error_code == '0' and rs.next():
                                row = rs.get_row_data()
                                for i, field in enumerate(rs.fields):
                                    record[f"dupont_{field}"] = row[i] if i < len(row) else None
                        except Exception as e:
                            logger.debug(f"Failed to fetch dupont data for {code} {year}Q{quarter}: {e}")

                        # 只有当有数据时才添加记录
                        if len(record) > 3:  # code + year + quarter + at least one data field
                            all_results.append(record)

                if not all_results:
                    raise NoDataFoundError(
                        f"No financial indicator data found for {code} in range {start_date}-{end_date}")

                result_df = pd.DataFrame(all_results)
                logger.info(f"Retrieved {len(result_df)} aggregated financial indicator records for {code}.")
                return result_df

        except (LoginError, NoDataFoundError, DataSourceError, ValueError) as e:
            logger.warning(f"Known error fetching financial indicators for {code}: {type(e).__name__}")
            raise e
        except Exception as e:
            logger.exception(f"Unexpected error fetching financial indicators for {code}: {e}")
            raise DataSourceError(f"Unexpected error fetching financial indicators for {code}: {e}")

    # Note: SHIBOR is not available in current Baostock API bindings used; not implemented.
