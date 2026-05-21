import re
from pathlib import Path


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


def write_output(output_dir: Path, content: str, slug: str = "condensed") -> Path:
    """Write content to a numbered markdown file; return the file path."""
    output_dir.mkdir(parents=True, exist_ok=True)
    file_number = get_next_file_number(output_dir)
    filename = f"{file_number:03d}-{slug}.md"
    filepath = output_dir / filename
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)
        f.write("\n\n<br>\n\n")
    return filepath
