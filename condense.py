# =============================================================================
# ADHD Text Condenser
# -----------------------------------------------------------------------------
# Reads input.txt, sends to Ollama to condense in an ADHD-friendly format.
# One-shot, no loop. Writes output to condensed/ directory as numbered
# markdown files. Configure via config.toml.
# =============================================================================
import sys
from pathlib import Path

from openai import OpenAI

from config import load_config
from file_io import write_output

_CFG = load_config()

OLLAMA_BASE_URL = _CFG.ollama.base_url
MODEL = _CFG.ollama.model
MAX_WORDS = _CFG.condenser.max_words
INPUT_FILE = Path(_CFG.condenser.input_file)
OUTPUT_DIR = Path(_CFG.condenser.output_dir)
TEMPERATURE = _CFG.condenser.temperature

PROMPT_TEMPLATE = f"""\
Condense the following text to {MAX_WORDS} words or less.

Make it easy for an ADHD brain to memorize:
- Short punchy sentences
- Bullet points over paragraphs
- Bold key terms
- Group related ideas together
- Use patterns and mnemonics where possible
- Lead with the most important stuff

Skip any preamble. Start directly with the condensed content.
No closing remarks or motivational lines.

---

{{text}}
"""


def read_input(input_path: Path) -> str:
    """Read and return contents of input file."""
    if not input_path.exists():
        print(f"Error: {input_path} not found.", file=sys.stderr)
        sys.exit(1)
    text = input_path.read_text(encoding="utf-8").strip()
    if not text:
        print(f"Error: {input_path} is empty.", file=sys.stderr)
        sys.exit(1)
    return text


def query_ollama(text: str) -> str:
    """Send text to Ollama for condensing and return the response."""
    client = OpenAI(base_url=OLLAMA_BASE_URL, api_key="ollama")
    prompt = PROMPT_TEMPLATE.format(text=text)
    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": "You are a concise, clear writing assistant."},
            {"role": "user", "content": prompt},
        ],
        temperature=TEMPERATURE,
    )
    return response.choices[0].message.content


def main():
    """Read input.txt, condense via Ollama, save result."""
    text = read_input(INPUT_FILE)

    print(f"Condensing {len(text.split())} words via {MODEL}...\n")
    try:
        content = query_ollama(text)
    except Exception as exc:
        print(f"Error querying Ollama: {exc}", file=sys.stderr)
        sys.exit(1)

    filepath = write_output(OUTPUT_DIR, content)
    print(content)
    print(f"\nSaved to: {filepath}")


if __name__ == "__main__":
    main()
