"""
Configuration Helpers — centralized config management for AI Analyst Plus.

Reads settings from .knowledge/config.yaml and provides convenience functions
for path resolution, database conventions, and system defaults.

Usage:
    from helpers.config_helpers import (
        get_output_dir,
        get_analysis_path,
        get_chart_path,
        get_deck_path,
        get_data_export_path,
        get_config,
        get_column_quoting_strategy,
    )

    # Get output directory (respects config.yaml setting)
    output_dir = get_output_dir()  # Returns "reports" or "outputs"

    # Get specific subdirectory paths
    analysis_path = get_analysis_path("my_analysis.md")
    chart_path = get_chart_path("my_chart.png")
    deck_path = get_deck_path("my_deck.pdf")
"""

from pathlib import Path

try:
    import yaml
    _YAML_AVAILABLE = True
except ImportError:
    _YAML_AVAILABLE = False


# ---------------------------------------------------------------------------
# Config loading
# ---------------------------------------------------------------------------

_CONFIG_PATH = Path(".knowledge/config.yaml")
_cached_config = None


def get_config(reload=False):
    """Load configuration from .knowledge/config.yaml.

    Caches the config on first load. Pass reload=True to force reload.

    Args:
        reload: If True, reloads config from disk

    Returns:
        dict with config values, or empty dict if config file not found
    """
    global _cached_config

    if _cached_config is not None and not reload:
        return _cached_config

    if not _YAML_AVAILABLE:
        print("[config_helpers] PyYAML not installed. Using defaults.")
        _cached_config = _default_config()
        return _cached_config

    if not _CONFIG_PATH.exists():
        print(f"[config_helpers] Config file not found: {_CONFIG_PATH}")
        print("  Using default configuration.")
        _cached_config = _default_config()
        return _cached_config

    try:
        with open(_CONFIG_PATH) as f:
            config = yaml.safe_load(f)
        _cached_config = config if isinstance(config, dict) else _default_config()
        return _cached_config
    except Exception as exc:
        print(f"[config_helpers] Failed to load config: {exc}")
        print("  Using default configuration.")
        _cached_config = _default_config()
        return _cached_config


def _default_config():
    """Return default configuration values."""
    return {
        "output_dir": "outputs",
        "database": {
            "default_schema": "public",
            "column_quoting": "auto",
        },
        "analysis": {
            "confidence_level": 0.95,
            "validation_strictness": "moderate",
            "auto_archive": True,
        },
        "charts": {
            "default_theme": "swd",
            "dpi": 300,
            "format": "png",
        },
        "presentations": {
            "default_theme": "analytics",
        },
        "dev_mode": False,
    }


# ---------------------------------------------------------------------------
# Path resolution
# ---------------------------------------------------------------------------

def get_output_dir():
    """Get the configured output directory name.

    Returns:
        str: Output directory name (e.g., "reports" or "outputs")
    """
    config = get_config()
    return config.get("output_dir", "outputs")


def get_analysis_path(filename=None):
    """Get path to the analyses subdirectory.

    Args:
        filename: Optional filename to append to the path

    Returns:
        Path object for {output_dir}/analyses/ or {output_dir}/analyses/{filename}
    """
    base = Path(get_output_dir()) / "analyses"
    return base / filename if filename else base


def get_chart_path(filename=None):
    """Get path to the charts subdirectory.

    Args:
        filename: Optional filename to append to the path

    Returns:
        Path object for {output_dir}/charts/ or {output_dir}/charts/{filename}
    """
    base = Path(get_output_dir()) / "charts"
    return base / filename if filename else base


def get_deck_path(filename=None):
    """Get path to the decks subdirectory.

    Args:
        filename: Optional filename to append to the path

    Returns:
        Path object for {output_dir}/decks/ or {output_dir}/decks/{filename}
    """
    base = Path(get_output_dir()) / "decks"
    return base / filename if filename else base


def get_data_export_path(filename=None):
    """Get path to the data exports subdirectory.

    Args:
        filename: Optional filename to append to the path

    Returns:
        Path object for {output_dir}/data/ or {output_dir}/data/{filename}
    """
    base = Path(get_output_dir()) / "data"
    return base / filename if filename else base


def ensure_output_dirs():
    """Create output directory structure if it doesn't exist.

    Creates:
        {output_dir}/
        {output_dir}/analyses/
        {output_dir}/charts/
        {output_dir}/decks/
        {output_dir}/data/
    """
    for path_func in [get_analysis_path, get_chart_path, get_deck_path, get_data_export_path]:
        path = path_func()
        path.mkdir(parents=True, exist_ok=True)


# ---------------------------------------------------------------------------
# Database configuration
# ---------------------------------------------------------------------------

def get_column_quoting_strategy():
    """Get the configured column quoting strategy.

    Returns:
        str: "auto", "always", or "never"
    """
    config = get_config()
    return config.get("database", {}).get("column_quoting", "auto")


def should_quote_column(column_name):
    """Determine if a column name should be quoted in SQL.

    Uses the configured quoting strategy:
    - "always": Always quote
    - "never": Never quote
    - "auto": Quote if name contains mixed case or special chars

    Args:
        column_name: Column name to check

    Returns:
        bool: True if column should be quoted
    """
    strategy = get_column_quoting_strategy()

    if strategy == "always":
        return True
    elif strategy == "never":
        return False
    else:  # "auto"
        # Quote if contains mixed case or special characters
        has_mixed_case = any(c.isupper() for c in column_name) and any(c.islower() for c in column_name)
        has_special = not column_name.replace("_", "").isalnum()
        return has_mixed_case or has_special


def get_default_schema():
    """Get the default database schema.

    Returns:
        str: Default schema name (e.g., "public")
    """
    config = get_config()
    return config.get("database", {}).get("default_schema", "public")


# ---------------------------------------------------------------------------
# Analysis configuration
# ---------------------------------------------------------------------------

def get_confidence_level():
    """Get the default confidence level for statistical tests.

    Returns:
        float: Confidence level (e.g., 0.95)
    """
    config = get_config()
    return config.get("analysis", {}).get("confidence_level", 0.95)


def get_validation_strictness():
    """Get the validation strictness level.

    Returns:
        str: "strict", "moderate", or "lenient"
    """
    config = get_config()
    return config.get("analysis", {}).get("validation_strictness", "moderate")


def should_auto_archive():
    """Check if analyses should be auto-archived after completion.

    Returns:
        bool: True if auto-archive is enabled
    """
    config = get_config()
    return config.get("analysis", {}).get("auto_archive", True)


# ---------------------------------------------------------------------------
# Chart configuration
# ---------------------------------------------------------------------------

def get_default_chart_theme():
    """Get the default chart theme.

    Returns:
        str: Theme name (e.g., "swd")
    """
    config = get_config()
    return config.get("charts", {}).get("default_theme", "swd")


def get_chart_dpi():
    """Get the default DPI for saved charts.

    Returns:
        int: DPI value (e.g., 300)
    """
    config = get_config()
    return config.get("charts", {}).get("dpi", 300)


def get_chart_format():
    """Get the default format for exported charts.

    Returns:
        str: Format (e.g., "png", "svg", "pdf")
    """
    config = get_config()
    return config.get("charts", {}).get("format", "png")


# ---------------------------------------------------------------------------
# Presentation configuration
# ---------------------------------------------------------------------------

def get_default_presentation_theme():
    """Get the default presentation theme.

    Returns:
        str: Theme name (e.g., "analytics", "analytics-dark")
    """
    config = get_config()
    return config.get("presentations", {}).get("default_theme", "analytics")


# ---------------------------------------------------------------------------
# Development mode
# ---------------------------------------------------------------------------

def is_dev_mode():
    """Check if development mode is enabled.

    Returns:
        bool: True if dev_mode is enabled
    """
    config = get_config()
    return config.get("dev_mode", False)
