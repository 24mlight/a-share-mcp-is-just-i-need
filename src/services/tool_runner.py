"""Common error handling for MCP tools."""
import logging
from typing import Callable

from src.data_source_interface import NoDataFoundError, LoginError, DataSourceError

logger = logging.getLogger(__name__)


def run_tool_with_handling(action: Callable[[], str], context: str) -> str:
    """
    Executes a callable and normalizes exceptions to user-friendly strings.

    Args:
        action: Callable returning a string (typically formatted output).
        context: Short description for logs.
    """
    try:
        return action()
    except NoDataFoundError as e:
        logger.warning(f"{context}: No data found: {e}")
        return f"Error: {e}"
    except LoginError as e:
        logger.error(f"{context}: Login error: {e}")
        return f"Error: Could not connect to data source. {e}"
    except DataSourceError as e:
        logger.error(f"{context}: Data source error: {e}")
        return f"Error: An error occurred while fetching data. {e}"
    except ValueError as e:
        logger.warning(f"{context}: Validation error: {e}")
        return f"Error: Invalid input parameter. {e}"
    except Exception as e:  # Catch-all
        logger.exception(f"{context}: Unexpected error: {e}")
        return f"Error: An unexpected error occurred: {e}"
