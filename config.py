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
class CondenserConfig:
    max_words: int
    input_file: str
    output_dir: str
    temperature: float


@dataclass(frozen=True)
class StudyAssistantConfig:
    max_words: int
    output_dir: str
    temperature: float


@dataclass(frozen=True)
class AppConfig:
    ollama: OllamaConfig
    condenser: CondenserConfig
    study_assistant: StudyAssistantConfig


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
            condenser=CondenserConfig(**raw["condenser"]),
            study_assistant=StudyAssistantConfig(**raw["study_assistant"]),
        )
    except (KeyError, TypeError) as exc:
        print(f"Error: invalid config: {exc}", file=sys.stderr)
        sys.exit(1)
