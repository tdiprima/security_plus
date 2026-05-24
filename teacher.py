#!/usr/bin/env python3
"""Send local text files to an Ollama model for Security+ teaching content generation."""

import argparse
import logging
import os
import sys
from pathlib import Path

from config import Config, DEFAULT_MODEL, DEFAULT_OLLAMA_URL, DEFAULT_TIMEOUT_SECONDS
from llm_client import OllamaClient
from prompt_builder import build_prompt

logger = logging.getLogger(__name__)


def configure_logging():
    """Set up structured console logging with level from LOG_LEVEL env var."""
    log_level = os.environ.get("LOG_LEVEL", "INFO").upper()
    logging.basicConfig(
        level=getattr(logging, log_level, logging.INFO),
        format="%(asctime)s [%(levelname)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        handlers=[logging.StreamHandler(sys.stderr)],
    )


def parse_config() -> Config:
    """Parse CLI args and construct a validated Config."""
    parser = argparse.ArgumentParser(
        description="Send a text file to an Ollama model for Security+ teaching content.",
        epilog="Example: python3 teacher.py notes.txt --model gemma3",
    )
    parser.add_argument("input_file", type=str, help="Path to the .txt file to process")
    parser.add_argument(
        "--model",
        type=str,
        default=DEFAULT_MODEL,
        help=f"Ollama model name (default: {DEFAULT_MODEL})",
    )
    parser.add_argument(
        "--url",
        type=str,
        default=DEFAULT_OLLAMA_URL,
        help=f"Ollama API endpoint (default: {DEFAULT_OLLAMA_URL})",
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=DEFAULT_TIMEOUT_SECONDS,
        help=f"Request timeout in seconds (default: {DEFAULT_TIMEOUT_SECONDS})",
    )
    parser.add_argument(
        "--prompt-file",
        type=str,
        default=None,
        help="Path to a custom prompt template file (overrides built-in default)",
    )
    args = parser.parse_args()
    return Config(
        input_file=args.input_file,
        model=args.model,
        ollama_url=args.url,
        timeout=args.timeout,
        prompt_file=args.prompt_file,
    )


def read_input_file(file_path: str) -> str:
    """Read and return the contents of the input text file."""
    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(f"Input file not found: {path}")
    if not path.is_file():
        raise ValueError(f"Path is not a file: {path}")

    content = path.read_text(encoding="utf-8")

    if not content.strip():
        raise ValueError(f"Input file is empty: {path}")

    logger.info("Read %d characters from %s", len(content), path.name)
    return content


def main():
    """Orchestrate: read input, query Ollama, write output."""
    configure_logging()

    try:
        config = parse_config()
    except ValueError as exc:
        logger.error("Config error: %s", exc)
        sys.exit(1)

    try:
        file_contents = read_input_file(config.input_file)
        prompt = build_prompt(file_contents, config.prompt_file)

        client = OllamaClient(config.model, config.ollama_url, config.timeout)
        response_text = client.generate(prompt)

        print(response_text)

        output_path = Path(config.input_file).with_suffix(".md")
        output_path.write_text(response_text, encoding="utf-8")
        logger.info("Wrote output to %s", output_path)

    except FileNotFoundError as exc:
        logger.error("File error: %s", exc)
        sys.exit(1)
    except ValueError as exc:
        logger.error("Validation error: %s", exc)
        sys.exit(1)
    except (ConnectionError, TimeoutError) as exc:
        logger.error("Connection error: %s", exc)
        sys.exit(2)
    except RuntimeError as exc:
        logger.error("API error: %s", exc)
        sys.exit(3)


if __name__ == "__main__":
    main()
