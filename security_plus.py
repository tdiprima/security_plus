# =============================================================================
# CompTIA Security+ Study Assistant
# -----------------------------------------------------------------------------
# Queries Ollama (gemma4:latest) with a Security+ study prompt tailored for
# ADHD learners. Interactive: prompts for topic, writes numbered markdown files
# to study_notes/. Files named like 001-fundamentals.md.
# =============================================================================
import re
from pathlib import Path

from openai import OpenAI

OLLAMA_BASE_URL = "http://localhost:11434/v1"
MODEL = "gemma4:latest"
OUTPUT_DIR = Path("study_notes")

PROMPT_TEMPLATE = """\
I'm looking to take the 'CompTIA Security+' certification.
I'm a beginner who's looking to understand some things up front.

Teach me about:
{topic}

With ADHD, my brain tends to remember:
- interesting things
- emotionally charged things
- hands-on things
- stories
- patterns
So use those ideas when teaching me these concepts.

In 500 words or less.

I already know that using certain commands & tools on networks you do not own or have permission to test can get you in trouble.
So don't mention it.

Don't make any further recommendations at the end.
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


def topic_to_slug(topic: str) -> str:
    """Derive a short hyphenated filename slug from the topic string."""
    slug = topic.lower()
    slug = re.sub(r"[^a-z0-9]+", "-", slug)
    slug = slug.strip("-")
    if len(slug) > 30:
        slug = slug[:30]
        last_hyphen = slug.rfind("-")
        if last_hyphen > 10:
            slug = slug[:last_hyphen]
    return slug


def query_ollama(topic: str) -> str:
    """Send prompt to Ollama and return the response text."""
    client = OpenAI(base_url=OLLAMA_BASE_URL, api_key="ollama")
    prompt = PROMPT_TEMPLATE.format(topic=topic)
    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": "You are a helpful, witty, and friendly assistant."},
            {"role": "user", "content": prompt},
        ],
        temperature=1,
    )
    return response.choices[0].message.content


def write_output(output_dir: Path, file_number: int, slug: str, content: str) -> Path:
    """Write content to a numbered markdown file, appending a trailing <br>."""
    output_dir.mkdir(parents=True, exist_ok=True)
    filename = f"{file_number:03d}-{slug}.md"
    filepath = output_dir / filename
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)
        f.write("\n<br>\n")
    return filepath


def research_topic():
    """Prompt for a topic, query Ollama, and save the result to a markdown file."""
    topic = input("Teach me about (or 'q' to quit): ").strip()
    if not topic:
        print("No topic provided. Skipping.")
        return True
    if topic.lower() in ("q", "quit", "exit"):
        return False

    file_number = get_next_file_number(OUTPUT_DIR)
    slug = topic_to_slug(topic)

    print(f"\nQuerying {MODEL}...\n")
    try:
        content = query_ollama(topic)
    except Exception as e:
        print(f"Error querying Ollama: {e}")
        return True

    filepath = write_output(OUTPUT_DIR, file_number, slug, content)
    print(content)
    print(f"\nSaved to: {filepath}")
    return True


def main():
    """Loop: prompt for topics until user quits."""
    print("Security+ Study Assistant. Enter topics to research. Type 'q' to quit.\n")
    while research_topic():
        print()


if __name__ == "__main__":
    main()
