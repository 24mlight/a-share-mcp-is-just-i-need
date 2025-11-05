"""
用于代码规范化和常量发现的辅助工具。
这些是代理友好的实用程序，具有清晰、明确的参数。
"""
import logging
import re
from typing import Optional

from mcp.server.fastmcp import FastMCP

logger = logging.getLogger(__name__)


def register_helpers_tools(app: FastMCP):
    """
    向 MCP 应用注册辅助/实用工具。
    """

    @app.tool()
    def normalize_stock_code(code: str) -> str:
        """
        将股票代码规范化为 Baostock 格式。

        规则:
            - 如果是6位数字且以 '6' 开头 -> 'sh.<code>'
            - 如果是6位数字且以其他数字开头 -> 'sz.<code>'
            - 接受 '600000.SH'/'000001.SZ' -> 转换为小写并重新排序为 'sh.600000'/'sz.000001'
            - 接受 'sh600000'/'sz000001' -> 插入点

        Args:
            code (str): 原始股票代码 (例如, '600000', '000001.SZ', 'sh600000')。

        Returns:
            str: 规范化后的代码，如 'sh.600000'，如果无效则返回错误字符串。

        Examples:
            - normalize_stock_code('600000') -> 'sh.600000'
            - normalize_stock_code('000001.SZ') -> 'sz.000001'
        """
        logger.info("工具 'normalize_stock_code' 已使用输入=%s 调用", code)
        try:
            raw = (code or "").strip()
            if not raw:
                return "错误: 'code' 是必需的。"

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

            return "错误: 不支持的代码格式。示例: 'sh.600000', '600000', '000001.SZ'。"
        except Exception as e:
            logger.exception("normalize_stock_code 中发生异常: %s", e)
            return f"错误: {e}"

    @app.tool()
    def list_tool_constants(kind: Optional[str] = None) -> str:
        """
        列出工具参数的有效常量。

        Args:
            kind (Optional[str], optional): 可选过滤器: 'frequency' | 'adjust_flag' | 'year_type' | 'index'。如果为 None，则显示所有。

        Returns:
            str: 常量及其含义的 Markdown 表格。
        """
        logger.info("工具 'list_tool_constants' 已调用 kind=%s", kind or "所有")
        freq = [
            ("d", "每日"), ("w", "每周"), ("m", "每月"),
            ("5", "5分钟"), ("15", "15分钟"), ("30", "30分钟"), ("60", "60分钟"),
        ]
        adjust = [("1", "后复权"), ("2", "前复权"), ("3", "不复权")]
        year_type = [("report", "公告年份"), ("operate", "除权除息年份")]
        index = [("hs300", "沪深300"), ("sz50", "上证50"), ("zz500", "中证500")]

        sections = []
        def as_md(title: str, rows):
            if not rows:
                return ""
            header = f"### {title}\n\n| 值 | 含义 |\n|---|---|\n"
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
            return "错误: 无效的类型。请使用 'frequency', 'adjust_flag', 'year_type', 'index' 之一。"
        return out
