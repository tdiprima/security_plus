import sys
import tomllib
from dataclasses import dataclass
from pathlib import Path

_CONFIG_FILE = Path(__file__).parent / "config.toml"


@dataclass(frozen=True)
class OllamaConfig:
    base_url: str
    model: str


@dataclass(frozen=True)
class SharedConfig:
    max_words: int
    output_dir: str
    temperature: float


@dataclass(frozen=True)
class CondenserConfig:
    input_file: str


@dataclass(frozen=True)
class AppConfig:
    ollama: OllamaConfig
    shared: SharedConfig
    condenser: CondenserConfig


def load_config() -> AppConfig:
    """Load, validate, and return typed config from config.toml."""
    if not _CONFIG_FILE.exists():
        print(f"Error: config file not found: {_CONFIG_FILE}", file=sys.stderr)
        sys.exit(1)
    with open(_CONFIG_FILE, "rb") as f:
        raw = tomllib.load(f)
    try:
        return AppConfig(
            ollama=OllamaConfig(**raw["ollama"]),
            shared=SharedConfig(**raw["shared"]),
            condenser=CondenserConfig(**raw["condenser"]),
        )
    except (KeyError, TypeError) as exc:
        print(f"Error: invalid config: {exc}", file=sys.stderr)
        sys.exit(1)
