# 工具函数，包括 Baostock 登录上下文管理器和日志设置
import baostock as bs
import os
import sys
import logging
from contextlib import contextmanager
from .data_source_interface import LoginError

# --- 日志设置 ---
def setup_logging(level=logging.INFO):
    """
    为应用程序配置基本日志。

    Args:
        level (int, optional): 日志级别。默认为 logging.INFO。
    """
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    # 如果依赖项的日志过于冗长，可以选择性地静默它们
    # logging.getLogger("mcp").setLevel(logging.WARNING)

# 获取此模块的 logger 实例 (可选，但是个好习惯)
logger = logging.getLogger(__name__)

# --- Baostock 上下文管理器 ---
@contextmanager
def baostock_login_context():
    """
    处理 Baostock 登录和登出的上下文管理器，同时抑制 stdout 消息。

    Yields:
        None

    Raises:
        LoginError: 如果 Baostock 登录失败。
    """
    # 重定向 stdout 以抑制登录/登出消息
    original_stdout_fd = sys.stdout.fileno()
    saved_stdout_fd = os.dup(original_stdout_fd)
    devnull_fd = os.open(os.devnull, os.O_WRONLY)

    os.dup2(devnull_fd, original_stdout_fd)
    os.close(devnull_fd)

    logger.debug("尝试 Baostock 登录...")
    lg = bs.login()
    logger.debug(f"登录结果: code={lg.error_code}, msg={lg.error_msg}")

    # 恢复 stdout
    os.dup2(saved_stdout_fd, original_stdout_fd)
    os.close(saved_stdout_fd)

    if lg.error_code != '0':
        # 在引发异常前记录错误
        logger.error(f"Baostock 登录失败: {lg.error_msg}")
        raise LoginError(f"Baostock 登录失败: {lg.error_msg}")

    logger.info("Baostock 登录成功。")
    try:
        yield  # API 调用在此处发生
    finally:
        # 再次为登出重定向 stdout
        original_stdout_fd = sys.stdout.fileno()
        saved_stdout_fd = os.dup(original_stdout_fd)
        devnull_fd = os.open(os.devnull, os.O_WRONLY)

        os.dup2(devnull_fd, original_stdout_fd)
        os.close(devnull_fd)

        logger.debug("尝试 Baostock 登出...")
        bs.logout()
        logger.debug("登出完成。")

        # 恢复 stdout
        os.dup2(saved_stdout_fd, original_stdout_fd)
        os.close(saved_stdout_fd)
        logger.info("Baostock 登出成功。")

# 如果需要，你可以在此处添加其他工具函数或类
