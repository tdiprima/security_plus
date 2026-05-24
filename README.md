### Structure
Six focused functions — `read_input_file`, `build_prompt`, `send_to_ollama`, `derive_output_path`,
`write_output`, and `main` for orchestration.

### Error handling
Specific exceptions for missing files, empty files, connection failures, timeouts, HTTP
errors, and empty API responses — each with a clear message and distinct exit code.

### Configuration
- `input_file` — positional argument (required)
- `--model` — defaults to gemma3
- `--url` — defaults to http://localhost:11434/api/generate
- `--timeout` — defaults to 300 seconds
- `LOG_LEVEL` env var controls logging verbosity

### Example usage

```sh
python3 ollama_teach.py notes.txt
python3 ollama_teach.py chapter5.txt --model gemma3 --timeout 600
```

This reads notes.txt, sends it to Ollama with the Security+ teaching prompt, prints the response, and
writes it to notes.md.

### Dependency
Requires requests (`pip install requests`).

<br>
