# =============================================================================
# CompTIA Security+ Study Assistant
# -----------------------------------------------------------------------------
# Queries Ollama with a Security+ study prompt tailored for ADHD learners.
# Interactive: prompts for topic, writes numbered markdown files to
# study_notes/. Files named like 001-fundamentals.md. Configure via config.toml.
# =============================================================================
import re
from pathlib import Path

from openai import OpenAI

from config import load_config
from file_io import write_output

_CFG = load_config()

OLLAMA_BASE_URL = _CFG.ollama.base_url
MODEL = _CFG.ollama.model
MAX_WORDS = _CFG.study_assistant.max_words
OUTPUT_DIR = Path(_CFG.study_assistant.output_dir)
TEMPERATURE = _CFG.study_assistant.temperature

PROMPT_TEMPLATE = f"""\
I'm looking to take the 'CompTIA Security+' certification.
I'm a beginner who's looking to understand some things up front.

Teach me about:
{{topic}}

With ADHD, my brain tends to remember:
- interesting things
- emotionally charged things
- hands-on things
- stories
- patterns
So use those ideas when teaching me these concepts, but do not label or announce them (no "(Emotionally Charged)", "emotional consequence", "(Hands-On)", "(Pattern)", etc.).

In {MAX_WORDS} words or less.

I already know that using certain commands & tools on networks you do not own or have permission to test can get you in trouble.
So don't mention it.

Don't make any further recommendations at the end.

Skip any preamble or intro. Start directly with the content.
Skip any motivational closing ("You've got this!", "Good luck!", etc.). End with the last piece of content.
"""


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
        temperature=TEMPERATURE,
    )
    return response.choices[0].message.content


def research_topic() -> bool:
    """Prompt for a topic, query Ollama, and save the result to a markdown file."""
    topic = input("Teach me about (or 'q' to quit): ").strip()
    if not topic:
        print("No topic provided. Skipping.")
        return True
    if topic.lower() in ("q", "quit", "exit"):
        return False

    slug = topic_to_slug(topic)

    print(f"\nQuerying {MODEL}...\n")
    try:
        content = query_ollama(topic)
    except Exception as exc:
        print(f"Error querying Ollama: {exc}")
        return True

    filepath = write_output(OUTPUT_DIR, content, slug)
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
