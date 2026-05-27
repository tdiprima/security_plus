# Security+ Teacher 🎓

An AI-powered study tool that transforms raw CompTIA Security+ notes into engaging, beginner-friendly lessons — complete with real-world examples, memory tricks, and quiz questions.

## 😩 Studying from Raw Docs Is Brutal

Security+ material is dense. Official study guides are accurate, but they read like technical manuals — walls of jargon with no analogies, no stories, and no hooks to make concepts stick. Reviewing notes you copied from a textbook barely moves the needle, and expensive tutors or video courses aren't always an option.

## 🤖 A Local AI That Teaches, Not Just Summarizes

Security+ Teacher feeds your notes to a locally-running LLM (via [Ollama](https://ollama.com)) using a carefully tuned prompt that instructs the model to behave like an enthusiastic, college senior-level classroom teacher. Every concept comes back structured with a plain-English explanation, a real-world analogy, a memory trick, and a quick-check quiz question — formatted in clean Markdown, ready to review anywhere.

No cloud API keys. No data leaving your machine. Drop files in, get lessons out.

## 📖 Concrete Example

Drop a raw notes file into `input/`:

```
input/cryptography.txt
```

```
Asymmetric encryption uses a public key to encrypt and a private key to decrypt.
RSA is the most common algorithm. Key sizes of 2048 bits or higher are recommended.
```

Run the tool:

```sh
python3 teacher.py
```

Get a rich lesson in `output/cryptography.md`:

```markdown
## 🔑 Asymmetric Encryption

📘 **Simple Explanation**
Think of asymmetric encryption like a padlock you hand out to anyone...

🧠 **Why It Matters**
This is how HTTPS keeps your bank login safe every single day...

🔐 **Real-World Example**
When you see the padlock icon in your browser, RSA is likely doing the heavy lifting...

⚡ **Memory Trick**
Public = Post Office Box (anyone can drop mail in). Private = your house key (only you get it out).

✅ **Quick Check**
Which key do you share freely — the public key or the private key?
```

## 🚀 Usage

### Prerequisites
Python 3.11+, [Ollama](https://ollama.com) running locally, and at least one model pulled (default: `gemma3`).

```sh
# Pull the default model (first time only)
ollama pull gemma3

# Install dependencies
pip install requests

# Place .txt or .md files in ./input/, then run
python3 teacher.py
```

### Options

| Flag | Default | Description |
|---|---|---|
| `--model` | `gemma3` | Any Ollama model name |
| `--url` | `http://localhost:11434/api/generate` | Ollama API endpoint |
| `--timeout` | `300` | Request timeout in seconds |
| `--prompt-file` | *(built-in)* | Path to a custom prompt template |

### Environment variables

| Variable | Description |
|---|---|
| `PROMPT_FILE` | Prompt template path (overridden by `--prompt-file`) |
| `LOG_LEVEL` | Logging verbosity (`DEBUG`, `INFO`, `WARNING`) |

### Examples

```sh
# Use a different model with a longer timeout
python3 teacher.py --model llama3.2 --timeout 600

# Bring your own prompt template
python3 teacher.py --prompt-file my_prompt.txt

# Set prompt via env var
PROMPT_FILE=my_prompt.txt python3 teacher.py

# Verbose logging
LOG_LEVEL=DEBUG python3 teacher.py
```

Output files are written to `./output/` (created automatically). Input and output filenames match: `input/chapter5.txt` → `output/chapter5.md`.

<br>
