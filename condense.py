# =============================================================================
# ADHD Text Condenser
# -----------------------------------------------------------------------------
# Reads input.txt, sends to Ollama (gemma3:latest) to condense to 350 words
# or less in an ADHD-friendly format. One-shot, no loop. Writes output to
# condensed/ directory as numbered markdown files.
# =============================================================================
import re
import sys
from pathlib import Path

from openai import OpenAI

OLLAMA_BASE_URL = "http://localhost:11434/v1"
MODEL = "gemma3:latest"
INPUT_FILE = Path("input.txt")
OUTPUT_DIR = Path("condensed")

PROMPT_TEMPLATE = """\
Condense the following text to 350 words or less.

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

{text}
"""


def get_next_file_number(output_dir: Path) -> int:
    """Return the next sequential 3-digit file number based on existing files."""
    existing = list(output_dir.glob("[0-9][0-9][0-9]-*.md"))
    if not existing:
        return 1
    numbers = []
    for filepath in existing:
        match = re.match(r"^(\d{3})-", filepath.name)
        if match:
            numbers.append(int(match.group(1)))
    return max(numbers) + 1 if numbers else 1


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
        temperature=0.7,
    )
    return response.choices[0].message.content


def write_output(output_dir: Path, file_number: int, content: str) -> Path:
    """Write condensed content to a numbered markdown file."""
    output_dir.mkdir(parents=True, exist_ok=True)
    filename = f"{file_number:03d}-condensed.md"
    filepath = output_dir / filename
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)
        f.write("\n\n<br>\n\n")
    return filepath


def main():
    """Read input.txt, condense via Ollama, save result."""
    text = read_input(INPUT_FILE)
    file_number = get_next_file_number(OUTPUT_DIR)

    print(f"Condensing {len(text.split())} words via {MODEL}...\n")
    try:
        content = query_ollama(text)
    except Exception as e:
        print(f"Error querying Ollama: {e}", file=sys.stderr)
        sys.exit(1)

    filepath = write_output(OUTPUT_DIR, file_number, content)
    print(content)
    print(f"\nSaved to: {filepath}")


if __name__ == "__main__":
    main()
