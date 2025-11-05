"""
提供通用工具函数，包括Baostock登录上下文管理器和日志设置。

该模块包含项目范围内可重用的辅助函数，主要功能有：
- `setup_logging`: 配置应用程序的基础日志记录。
- `baostock_login_context`: 一个上下文管理器，用于自动处理Baostock的登录和登出，
  并抑制其在标准输出中产生的消息，使得日志更加清晰。
"""
import baostock as bs
import os
import sys
import logging
from contextlib import contextmanager
from .data_source_interface import LoginError

# --- Logging Setup ---
def setup_logging(level=logging.INFO):
    """
    为应用程序配置基础日志记录。

    Args:
        level (int, optional): 设置日志记录的级别。默认为 `logging.INFO`。
    """
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    # Optionally silence logs from dependencies if they are too verbose
    # logging.getLogger("mcp").setLevel(logging.WARNING)

# Get a logger instance for this module (optional, but good practice)
logger = logging.getLogger(__name__)

# --- Baostock Context Manager ---
@contextmanager
def baostock_login_context():
    """
    一个处理Baostock登录和登出的上下文管理器，同时抑制stdout消息。

    这个上下文管理器封装了`bs.login()`和`bs.logout()`的调用。
    它通过临时重定向标准输出来抑制Baostock库打印的"login success!"和"logout success!"消息，
    使得程序的日志输出更加干净。

    Yields:
        None

    Raises:
        LoginError: 如果Baostock登录失败。
    """
    # Redirect stdout to suppress login/logout messages
    original_stdout_fd = sys.stdout.fileno()
    saved_stdout_fd = os.dup(original_stdout_fd)
    devnull_fd = os.open(os.devnull, os.O_WRONLY)

    os.dup2(devnull_fd, original_stdout_fd)
    os.close(devnull_fd)

    logger.debug("Attempting Baostock login...")
    lg = bs.login()
    logger.debug(f"Login result: code={lg.error_code}, msg={lg.error_msg}")

    # Restore stdout
    os.dup2(saved_stdout_fd, original_stdout_fd)
    os.close(saved_stdout_fd)

    if lg.error_code != '0':
        # Log error before raising
        logger.error(f"Baostock login failed: {lg.error_msg}")
        raise LoginError(f"Baostock login failed: {lg.error_msg}")

    logger.info("Baostock login successful.")
    try:
        yield  # API calls happen here
    finally:
        # Redirect stdout again for logout
        original_stdout_fd = sys.stdout.fileno()
        saved_stdout_fd = os.dup(original_stdout_fd)
        devnull_fd = os.open(os.devnull, os.O_WRONLY)

        os.dup2(devnull_fd, original_stdout_fd)
        os.close(devnull_fd)

        logger.debug("Attempting Baostock logout...")
        bs.logout()
        logger.debug("Logout completed.")

        # Restore stdout
        os.dup2(saved_stdout_fd, original_stdout_fd)
        os.close(saved_stdout_fd)
        logger.info("Baostock logout successful.")

# You can add other utility functions or classes here if needed
