"""
提供将pandas DataFrame格式化为不同字符串输出（如Markdown、JSON、CSV）的工具函数。

该模块的核心功能是`format_table_output`，它是一个通用的格式化函数，
可以根据指定的格式对DataFrame进行转换，并可选地添加元数据。
`format_df_to_markdown`则专门用于处理向后兼容的Markdown格式化，并支持行数截断。

这些函数旨在为MCP工具提供统一、灵活且对上下文长度友好的输出方式。
"""
import pandas as pd
import logging
import json

logger = logging.getLogger(__name__)

# Configuration: Max rows to display in string outputs to protect context length
MAX_MARKDOWN_ROWS = 250


def format_df_to_markdown(df: pd.DataFrame, max_rows: int = None) -> str:
    """
    将pandas DataFrame格式化为带行截断的Markdown字符串。

    Args:
        df (pd.DataFrame): 要格式化的DataFrame。
        max_rows (int, optional): 输出中要包含的最大行数。如果为None，则默认为`MAX_MARKDOWN_ROWS`。

    Returns:
        str: DataFrame的Markdown格式字符串表示。
    """
    if df is None or df.empty:
        logger.warning("Attempted to format an empty DataFrame to Markdown.")
        return "(No data available to display)"

    if max_rows is None:
        max_rows = MAX_MARKDOWN_ROWS

    original_rows = df.shape[0]
    rows_to_show = min(original_rows, max_rows)
    df_display = df.head(rows_to_show)

    truncated = original_rows > rows_to_show

    try:
        markdown_table = df_display.to_markdown(index=False)
    except Exception as e:
        logger.error("Error converting DataFrame to Markdown: %s", e, exc_info=True)
        return "Error: Could not format data into Markdown table."

    if truncated:
        notes = f"rows truncated to {rows_to_show} from {original_rows}"
        return f"Note: Data truncated ({notes}).\n\n{markdown_table}"
    return markdown_table


def format_table_output(
    df: pd.DataFrame,
    format: str = "markdown",
    max_rows: int | None = None,
    meta: dict | None = None,
) -> str:
    """
    将DataFrame格式化为请求的字符串格式，并可选择性地包含元数据。

    Args:
        df (pd.DataFrame): 要格式化的数据。
        format (str, optional): 'markdown' | 'json' | 'csv'。默认为 'markdown'。
        max_rows (int | None, optional): 要包含的最大行数（默认值取决于格式化程序）。
        meta (dict | None, optional): 要包含的可选元数据字典（对于markdown会前置，对于json会嵌入）。

    Returns:
        str: 适合工具响应的字符串。
    """
    fmt = (format or "markdown").lower()

    # Normalize row cap
    if max_rows is None:
        max_rows = MAX_MARKDOWN_ROWS if fmt == "markdown" else MAX_MARKDOWN_ROWS

    total_rows = 0 if df is None else int(df.shape[0])
    rows_to_show = 0 if df is None else min(total_rows, max_rows)
    truncated = total_rows > rows_to_show
    df_display = df.head(rows_to_show) if df is not None else pd.DataFrame()

    if fmt == "markdown":
        header = ""
        if meta:
            # Render a compact meta header
            lines = ["Meta:"]
            for k, v in meta.items():
                lines.append(f"- {k}: {v}")
            header = "\n".join(lines) + "\n\n"
        return header + format_df_to_markdown(df_display, max_rows=max_rows)

    if fmt == "csv":
        try:
            return df_display.to_csv(index=False)
        except Exception as e:
            logger.error("Error converting DataFrame to CSV: %s", e, exc_info=True)
            return "Error: Could not format data into CSV."

    if fmt == "json":
        try:
            payload = {
                "data": [] if df_display is None else df_display.to_dict(orient="records"),
                "meta": {
                    **(meta or {}),
                    "total_rows": total_rows,
                    "returned_rows": rows_to_show,
                    "truncated": truncated,
                    "columns": [] if df_display is None else list(df_display.columns),
                },
            }
            return json.dumps(payload, ensure_ascii=False)
        except Exception as e:
            logger.error("Error converting DataFrame to JSON: %s", e, exc_info=True)
            return "Error: Could not format data into JSON."

    # Fallback to markdown if unknown format
    logger.warning("Unknown format '%s', falling back to markdown", fmt)
    return format_df_to_markdown(df_display, max_rows=max_rows)
