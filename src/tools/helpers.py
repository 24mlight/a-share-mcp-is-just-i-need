"""
注册并实现与代码规范化和常量发现相关的辅助工具。

这些工具旨在为AI代理（Agent）提供便利，使其能够：
- 将各种格式的股票代码规范化为Baostock所需的标准格式 (`normalize_stock_code`)。
- 查询其他工具中使用的有效常量值及其含义 (`list_tool_constants`)，例如`frequency`、`adjust_flag`等。

这有助于提高代理与工具集交互的健壮性和准确性。
"""
import logging
import re
from typing import Optional

from mcp.server.fastmcp import FastMCP

logger = logging.getLogger(__name__)


def register_helpers_tools(app: FastMCP):
    """
    向MCP应用注册所有辅助工具。

    Args:
        app (FastMCP): FastMCP应用实例。
    """

    @app.tool()
    def normalize_stock_code(code: str) -> str:
        """
        将股票代码规范化为Baostock格式。

        规则:
            - 如果是6位数字且以'6'开头 -> 'sh.<code>'
            - 如果是6位数字且以其他数字开头 -> 'sz.<code>'
            - 接受'600000.SH'/'000001.SZ' -> 转换为小写并重排为'sh.600000'/'sz.000001'
            - 接受'sh600000'/'sz000001' -> 插入点'.'

        Args:
            code (str): 原始股票代码 (例如, '600000', '000001.SZ', 'sh600000')。

        Returns:
            str: 规范化后的代码，如'sh.600000'，如果无效则返回错误字符串。

        Examples:
            - normalize_stock_code('600000') -> 'sh.600000'
            - normalize_stock_code('000001.SZ') -> 'sz.000001'
        """
        logger.info("Tool 'normalize_stock_code' called with input=%s", code)
        try:
            raw = (code or "").strip()
            if not raw:
                return "Error: 'code' is required."

            # Patterns
            m = re.fullmatch(r"(?i)(sh|sz)[\.]?(\d{6})", raw)
            if m:
                ex = m.group(1).lower()
                num = m.group(2)
                return f"{ex}.{num}"

            m2 = re.fullmatch(r"(\d{6})[\.]?(?i)(sh|sz)", raw)
            if m2:
                num = m2.group(1)
                ex = m2.group(2).lower()
                return f"{ex}.{num}"

            m3 = re.fullmatch(r"(\d{6})", raw)
            if m3:
                num = m3.group(1)
                ex = "sh" if num.startswith("6") else "sz"
                return f"{ex}.{num}"

            return "Error: Unsupported code format. Examples: 'sh.600000', '600000', '000001.SZ'."
        except Exception as e:
            logger.exception("Exception in normalize_stock_code: %s", e)
            return f"Error: {e}"

    @app.tool()
    def list_tool_constants(kind: Optional[str] = None) -> str:
        """
        列出工具参数的有效常量值。

        Args:
            kind (Optional[str], optional): 可选的筛选条件: 'frequency' | 'adjust_flag' | 'year_type' | 'index'。
                                            如果为None，则显示所有类型的常量。

        Returns:
            str: 包含常量及其含义的Markdown表格。
        """
        logger.info("Tool 'list_tool_constants' called kind=%s", kind or "all")
        freq = [
            ("d", "daily"), ("w", "weekly"), ("m", "monthly"),
            ("5", "5 minutes"), ("15", "15 minutes"), ("30", "30 minutes"), ("60", "60 minutes"),
        ]
        adjust = [("1", "forward adjusted"), ("2", "backward adjusted"), ("3", "unadjusted")]
        year_type = [("report", "announcement year"), ("operate", "ex-dividend year")]
        index = [("hs300", "CSI 300"), ("sz50", "SSE 50"), ("zz500", "CSI 500")]

        sections = []
        def as_md(title: str, rows):
            if not rows:
                return ""
            header = f"### {title}\n\n| value | meaning |\n|---|---|\n"
            lines = [f"| {v} | {m} |" for (v, m) in rows]
            return header + "\n".join(lines) + "\n"

        k = (kind or "").strip().lower()
        if k in ("", "frequency"):
            sections.append(as_md("frequency", freq))
        if k in ("", "adjust_flag"):
            sections.append(as_md("adjust_flag", adjust))
        if k in ("", "year_type"):
            sections.append(as_md("year_type", year_type))
        if k in ("", "index"):
            sections.append(as_md("index", index))

        out = "\n".join(s for s in sections if s)
        if not out:
            return "Error: Invalid kind. Use one of 'frequency', 'adjust_flag', 'year_type', 'index'."
        return out

