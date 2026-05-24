#!/usr/bin/env python3
"""Process all .txt and .md files in ./input through Ollama and write results to ./output."""

import argparse
import logging
import os
import sys
from pathlib import Path

from config import Config, DEFAULT_MODEL, DEFAULT_OLLAMA_URL, DEFAULT_TIMEOUT_SECONDS, INPUT_DIR, OUTPUT_DIR
from llm_client import OllamaClient
from prompt_builder import build_prompt

logger = logging.getLogger(__name__)

_INPUT_EXTENSIONS = {".txt", ".md"}


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
        description="Process all .txt/.md files in ./input through Ollama and write to ./output.",
        epilog="Example: python3 teacher.py --model gemma3",
    )
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
        model=args.model,
        ollama_url=args.url,
        timeout=args.timeout,
        prompt_file=args.prompt_file,
    )


def discover_input_files(input_dir: Path) -> list[Path]:
    """Return a sorted list of .txt and .md files in input_dir."""
    if not input_dir.exists():
        raise FileNotFoundError(f"Input directory not found: {input_dir}")
    if not input_dir.is_dir():
        raise ValueError(f"Input path is not a directory: {input_dir}")

    files = sorted(
        path for path in input_dir.iterdir()
        if path.is_file() and path.suffix in _INPUT_EXTENSIONS
    )
    return files


def ensure_output_dir(output_dir: Path) -> None:
    """Create the output directory if it does not already exist."""
    output_dir.mkdir(parents=True, exist_ok=True)
    logger.debug("Output directory ready: %s", output_dir)


def read_file(file_path: Path) -> str:
    """Read and return the contents of a file, raising on empty content."""
    content = file_path.read_text(encoding="utf-8")
    if not content.strip():
        raise ValueError(f"Input file is empty: {file_path}")
    logger.info("Read %d characters from %s", len(content), file_path.name)
    return content


def process_file(file_path: Path, config: Config, client: OllamaClient, output_dir: Path) -> None:
    """Read one input file, query Ollama, and write the markdown result to output_dir."""
    logger.info("Processing %s", file_path.name)
    file_contents = read_file(file_path)
    prompt = build_prompt(file_contents, config.prompt_file)
    response_text = client.generate(prompt)
    output_path = output_dir / (file_path.stem + ".md")
    output_path.write_text(response_text, encoding="utf-8")
    logger.info("Wrote output to %s", output_path)


def main():
    """Orchestrate: discover inputs, query Ollama for each, write outputs."""
    configure_logging()

    try:
        config = parse_config()
    except ValueError as exc:
        logger.error("Config error: %s", exc)
        sys.exit(1)

    try:
        input_files = discover_input_files(INPUT_DIR)
        if not input_files:
            logger.error("No .txt or .md files found in %s", INPUT_DIR)
            sys.exit(1)

        logger.info("Found %d file(s) to process in %s", len(input_files), INPUT_DIR)
        ensure_output_dir(OUTPUT_DIR)

        client = OllamaClient(config.model, config.ollama_url, config.timeout)

        for file_path in input_files:
            process_file(file_path, config, client, OUTPUT_DIR)

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
