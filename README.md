# 🛡️ CompTIA Security+ Study Assistant

An AI-powered study tool that generates ADHD-friendly explanations of Security+ exam topics using a local LLM, saving each session as a numbered markdown file.

## 📚 Certification Prep Is Dense and Boring by Default

Security+ covers a massive range of concepts — cryptography, network protocols, threat actors, identity management — and most study materials dump walls of dry text. For learners with ADHD, that's a fast path to burnout and forgotten content.

## 🧠 Learning That Sticks

This tool sends your chosen topic to a locally running Ollama model (Gemma 4) with a prompt engineered for ADHD retention: stories, patterns, emotional hooks, and hands-on framing — all in 500 words or less. Each response is automatically saved to `study_notes/` as a sequentially numbered markdown file so your notes build up session by session.

## 💡 Example

```
$ python security_plus.py
Teach me about: symmetric vs asymmetric encryption

Querying gemma4:latest...

[AI-generated explanation using stories and patterns]

Saved to: study_notes/001-symmetric-vs-asymmetric-enc.md
```

Each subsequent run increments the file number: `002-`, `003-`, and so on.

## 🚀 Usage

**Prerequisites:** [Ollama](https://ollama.com) running locally with the `gemma4:latest` model pulled.

```bash
ollama pull gemma4:latest
ollama serve
```

**Install dependencies:**

```bash
pip install uv
uv sync
```

**Run:**

```bash
python security_plus.py
```

Enter any Security+ topic at the prompt. The explanation is printed to the terminal and saved to `study_notes/`.

<br>
