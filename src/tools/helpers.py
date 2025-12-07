"""
Helper tools for code normalization and constants discovery.
Uses shared validation and helper logic.
"""
import logging
from typing import Optional

from mcp.server.fastmcp import FastMCP
from src.services.tool_runner import run_tool_with_handling
from src.use_cases.helpers import normalize_index_code_logic, normalize_stock_code_logic

logger = logging.getLogger(__name__)


def register_helpers_tools(app: FastMCP):
    """Register helper/utility tools with the MCP app."""

    @app.tool()
    def normalize_stock_code(code: str) -> str:
        """Normalize a stock code to Baostock format."""
        logger.info("Tool 'normalize_stock_code' called with input=%s", code)
        return run_tool_with_handling(
            lambda: normalize_stock_code_logic(code),
            context="normalize_stock_code",
        )

    @app.tool()
    def normalize_index_code(code: str) -> str:
        """Normalize common index codes to Baostock format."""
        logger.info("Tool 'normalize_index_code' called with input=%s", code)
        return run_tool_with_handling(
            lambda: normalize_index_code_logic(code),
            context="normalize_index_code",
        )

    @app.tool()
    def list_tool_constants(kind: Optional[str] = None) -> str:
        """
        List valid constants for tool parameters.

        Args:
            kind: Optional filter: 'frequency' | 'adjust_flag' | 'year_type' | 'index'. If None, show all.
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
