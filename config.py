"""Unified configuration: build from CLI args + env vars, validate at startup."""

import dataclasses
import os
from pathlib import Path
from typing import Optional
from urllib.parse import urlparse

DEFAULT_MODEL = "gemma4"
DEFAULT_OLLAMA_URL = "http://localhost:11434/api/generate"
DEFAULT_TIMEOUT_SECONDS = 300

INPUT_DIR = Path("input")
OUTPUT_DIR = Path("output")


@dataclasses.dataclass(frozen=True)
class Config:
    model: str
    ollama_url: str
    timeout: int
    prompt_file: Optional[str] = None

    def __post_init__(self):
        if self.timeout <= 0:
            raise ValueError(f"Timeout must be positive, got {self.timeout}")
        parsed = urlparse(self.ollama_url)
        if parsed.scheme not in ("http", "https"):
            raise ValueError(f"Invalid Ollama URL scheme: {self.ollama_url!r}")
        if not self.model.strip():
            raise ValueError("Model name must not be empty")
