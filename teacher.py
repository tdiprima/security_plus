#!/usr/bin/env python3
"""Send local text files to an Ollama model for Security+ teaching content generation."""

import argparse
import json
import logging
import os
import sys
from pathlib import Path

import requests

# Default configuration
DEFAULT_MODEL = "gemma3"
DEFAULT_OLLAMA_URL = "http://localhost:11434/api/generate"
DEFAULT_TIMEOUT_SECONDS = 300

# Prompt template — inserts file contents at the {file_contents} placeholder
PROMPT_TEMPLATE = """\
You are an engaging college professor and CompTIA Security+ expert teaching a \
complete beginner who learns best through short, interactive, memorable explanations.

Your job is to teach the provided Security+ content in a way that is:

* Easy to understand for a freshman level
* Highly engaging and conversational
* Structured for strong memory retention
* Broken into small chunks to maintain focus
* Practical and relatable using real-world examples, analogies, and mini stories
* Slightly humorous without becoming distracting

### Teaching Style

* Use clear headings with relevant emojis
* Keep paragraphs short (2–4 sentences max)
* Use bullet points often
* Highlight key terms and definitions
* Include quick knowledge checks or mini quizzes after major concepts
* Use memory tricks, analogies, and simple metaphors
* Repeat important ideas naturally for reinforcement
* Avoid overly technical jargon unless you explain it simply first

### Formatting Rules

For each major concept:

1. 📘 Simple Explanation
2. 🧠 Why It Matters
3. 🔐 Real-World Example
4. ⚡ Memory Trick
5. ✅ Quick Check Question

### Tone

* Friendly, energetic, and encouraging
* Teach like an awesome classroom teacher who keeps students engaged
* Never sound robotic or overly academic

### Important

* Do not mention learning styles, ADHD, or teaching techniques explicitly
* Focus entirely on making the material easy, memorable, and enjoyable

Here is the text to teach:
{file_contents}
"""

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


def parse_arguments():
    """Parse command-line arguments for input file, model, and Ollama URL."""
    parser = argparse.ArgumentParser(
        description="Send a text file to an Ollama model for Security+ teaching content.",
        epilog="Example: python3 ollama_teach.py notes.txt --model gemma3",
    )
    parser.add_argument(
        "input_file",
        type=str,
        help="Path to the .txt file to process",
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
    return parser.parse_args()


def read_input_file(file_path):
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


def build_prompt(file_contents):
    """Insert file contents into the prompt template."""
    return PROMPT_TEMPLATE.format(file_contents=file_contents)


def send_to_ollama(prompt, model, ollama_url, timeout):
    """Send the prompt to the Ollama API and return the full response text."""
    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False,
    }

    logger.info("Sending request to %s using model '%s'...", ollama_url, model)

    try:
        response = requests.post(
            ollama_url,
            json=payload,
            timeout=timeout,
        )
        response.raise_for_status()
    except requests.ConnectionError as exc:
        raise ConnectionError(
            f"Cannot connect to Ollama at {ollama_url}. Is Ollama running?"
        ) from exc
    except requests.Timeout as exc:
        raise TimeoutError(
            f"Request to Ollama timed out after {timeout}s. "
            "Try increasing --timeout or using a smaller input file."
        ) from exc
    except requests.HTTPError as exc:
        raise RuntimeError(
            f"Ollama returned HTTP {response.status_code}: {response.text}"
        ) from exc

    data = response.json()
    response_text = data.get("response", "").strip()

    if not response_text:
        raise ValueError("Ollama returned an empty response. Check the model and input.")

    logger.info("Received %d characters from Ollama", len(response_text))
    return response_text


def derive_output_path(input_path):
    """Convert input path from .txt to .md extension."""
    path = Path(input_path)
    return path.with_suffix(".md")


def write_output(output_path, content):
    """Write the model response to the output markdown file."""
    output_path.write_text(content, encoding="utf-8")
    logger.info("Wrote output to %s", output_path)


def main():
    """Orchestrate: read input, query Ollama, write output."""
    configure_logging()
    args = parse_arguments()

    try:
        # Step 1: Read the input file
        file_contents = read_input_file(args.input_file)

        # Step 2: Build the prompt with the file contents
        prompt = build_prompt(file_contents)

        # Step 3: Send to Ollama and get the response
        response_text = send_to_ollama(prompt, args.model, args.url, args.timeout)

        # Step 4: Display the response
        print(response_text)

        # Step 5: Write the response to a .md file
        output_path = derive_output_path(args.input_file)
        write_output(output_path, response_text)

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
