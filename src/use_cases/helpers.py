"""Helper use cases for normalization utilities."""
import re

from src.services.validation import validate_non_empty_str


def normalize_stock_code_logic(code: str) -> str:
    validate_non_empty_str(code, "code")
    raw = code.strip()

    m = re.fullmatch(r"(?i)(sh|sz)[.]?(\d{6})", raw)
    if m:
        ex, num = m.group(1).lower(), m.group(2)
        return f"{ex}.{num}"

    m2 = re.fullmatch(r"(\d{6})[.]?(?i:(sh|sz))", raw)
    if m2:
        num, ex = m2.group(1), m2.group(2).lower()
        return f"{ex}.{num}"

    m3 = re.fullmatch(r"(\d{6})", raw)
    if m3:
        num = m3.group(1)
        ex = "sh" if num.startswith("6") else "sz"
        return f"{ex}.{num}"

    raise ValueError("Unsupported code format. Examples: 'sh.600000', '600000', '000001.SZ'.")


def normalize_index_code_logic(code: str) -> str:
    validate_non_empty_str(code, "code")
    raw = code.strip().upper()
    if raw in {"000300", "CSI300", "HS300"}:
        return "sh.000300"
    if raw in {"000016", "SSE50", "SZ50"}:
        return "sh.000016"
    if raw in {"000905", "ZZ500", "CSI500"}:
        return "sh.000905"
    raise ValueError("Unsupported index code. Examples: 000300/CSI300/HS300, 000016, 000905.")
