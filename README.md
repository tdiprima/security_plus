### Structure

Four modules, each with a single responsibility:

- `config.py` — `Config` dataclass built from CLI args; validated at startup
- `llm_client.py` — `LLMClient` protocol + `OllamaClient` adapter
- `prompt_builder.py` — loads prompt template from file, env var, or built-in default
- `teacher.py` — orchestration only: read input, build prompt, call LLM, write output

### Error handling
Specific exceptions for missing files, empty files, connection failures, timeouts, HTTP
errors, and empty API responses — each with a clear message and distinct exit code.

### Configuration
- `input_file` — positional argument (required)
- `--model` — defaults to gemma3
- `--url` — defaults to http://localhost:11434/api/generate
- `--timeout` — defaults to 300 seconds
- `--prompt-file` — path to a custom prompt template (overrides built-in default)
- `LOG_LEVEL` env var controls logging verbosity
- `PROMPT_FILE` env var sets the prompt template path (overridden by `--prompt-file`)

### Example usage

```sh
python3 teacher.py notes.txt
python3 teacher.py chapter5.txt --model gemma3 --timeout 600
python3 teacher.py notes.txt --prompt-file my_prompt.txt
PROMPT_FILE=my_prompt.txt python3 teacher.py notes.txt
```

This reads the input file, sends it to Ollama with the Security+ teaching prompt, prints the response, and
writes it to a `.md` file with the same name.

### Dependencies
Requires requests (`pip install requests`).

<br>
