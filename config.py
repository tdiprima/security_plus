import sys
import tomllib
from pathlib import Path

_CONFIG_FILE = Path(__file__).parent / "config.toml"


def load_config() -> dict:
    """Load and return settings from config.toml."""
    if not _CONFIG_FILE.exists():
        print(f"Error: config file not found: {_CONFIG_FILE}", file=sys.stderr)
        sys.exit(1)
    with open(_CONFIG_FILE, "rb") as f:
        return tomllib.load(f)
