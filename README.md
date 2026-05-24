### Structure

Four modules, each with a single responsibility:

- `config.py` — `Config` dataclass built from CLI args; validated at startup; defines `INPUT_DIR` and `OUTPUT_DIR`
- `llm_client.py` — `LLMClient` protocol + `OllamaClient` adapter
- `prompt_builder.py` — loads prompt template from file, env var, or built-in default
- `teacher.py` — orchestration only: discover inputs, build prompt, call LLM, write output

### Error handling
Specific exceptions for missing directory, empty files, connection failures, timeouts, HTTP
errors, and empty API responses — each with a clear message and distinct exit code. Halts on
the first file that fails.

### Input / output

Place `.txt` or `.md` files in the `input/` folder. Results are written as `.md` files to
the `output/` folder (created automatically if absent). Output filenames match input stems:
`input/chapter5.txt` → `output/chapter5.md`.

### Configuration
- `--model` — defaults to gemma3
- `--url` — defaults to http://localhost:11434/api/generate
- `--timeout` — defaults to 300 seconds
- `--prompt-file` — path to a custom prompt template (overrides built-in default)
- `LOG_LEVEL` env var controls logging verbosity
- `PROMPT_FILE` env var sets the prompt template path (overridden by `--prompt-file`)

### Example usage

```sh
# Process all files in ./input/, write results to ./output/
python3 teacher.py
python3 teacher.py --model gemma3 --timeout 600
python3 teacher.py --prompt-file my_prompt.txt
PROMPT_FILE=my_prompt.txt python3 teacher.py
```

### Dependencies
Requires requests (`pip install requests`).

<br>
