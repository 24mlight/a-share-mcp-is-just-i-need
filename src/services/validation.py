"""Validation utilities for tool inputs."""
from typing import Iterable

VALID_FREQS = ["d", "w", "m", "5", "15", "30", "60"]
VALID_ADJUST_FLAGS = ["1", "2", "3"]
VALID_FORMATS = ["markdown", "json", "csv"]
VALID_YEAR_TYPES = ["report", "operate"]
VALID_RESERVE_YEAR_TYPES = ["0", "1", "2"]


def _ensure_in(value: str, allowed: Iterable[str], label: str) -> None:
    if value not in allowed:
        raise ValueError(f"Invalid {label} '{value}'. Valid options are: {list(allowed)}")


def validate_frequency(frequency: str) -> None:
    _ensure_in(frequency, VALID_FREQS, "frequency")


def validate_adjust_flag(adjust_flag: str) -> None:
    _ensure_in(adjust_flag, VALID_ADJUST_FLAGS, "adjust_flag")


def validate_output_format(fmt: str) -> None:
    _ensure_in(fmt, VALID_FORMATS, "format")


def validate_year(year: str) -> None:
    if not year.isdigit() or len(year) != 4:
        raise ValueError(f"Invalid year '{year}'. Please provide a 4-digit year.")


def validate_year_type(year_type: str) -> None:
    _ensure_in(year_type, VALID_YEAR_TYPES, "year_type")


def validate_quarter(quarter: int) -> None:
    if quarter not in (1, 2, 3, 4):
        raise ValueError("Invalid quarter. Must be between 1 and 4.")


def validate_non_empty_str(value: str, label: str) -> None:
    if value is None or not str(value).strip():
        raise ValueError(f"'{label}' is required.")


def validate_index_key(value: str, mapping: dict) -> str:
    key = mapping.get(value.lower()) if isinstance(value, str) else None
    if not key:
        raise ValueError(f"Invalid index '{value}'. Valid options: {sorted(set(mapping.values()))}")
    return key


def validate_year_type_reserve(year_type: str) -> None:
    _ensure_in(year_type, VALID_RESERVE_YEAR_TYPES, "year_type")


def validate_limit(limit: int) -> None:
    if limit <= 0:
        raise ValueError("limit must be positive.")
