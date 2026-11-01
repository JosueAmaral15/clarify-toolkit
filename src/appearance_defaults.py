"""Shared appearance defaults and explicit Qt opacity conversion."""

DEFAULT_THEME = "dark"
DEFAULT_WINDOW_OPACITY_PERCENT = 96
MIN_WINDOW_OPACITY_PERCENT = 0
MAX_WINDOW_OPACITY_PERCENT = 100


def normalize_opacity_percent(value) -> int:
    """Return a bounded opacity percentage, falling back for invalid values."""
    try:
        percent = int(value)
    except (TypeError, ValueError):
        percent = DEFAULT_WINDOW_OPACITY_PERCENT
    return max(MIN_WINDOW_OPACITY_PERCENT, min(MAX_WINDOW_OPACITY_PERCENT, percent))


def opacity_percent_to_qt(value) -> float:
    """Convert displayed opacity percent to Qt's 0.0-1.0 opacity scale."""
    return normalize_opacity_percent(value) / 100.0
