import pytest

from prompt_builder import _DEFAULT_TEMPLATE, _load_template, build_prompt


def test_default_template_inserts_contents(monkeypatch):
    monkeypatch.delenv("PROMPT_FILE", raising=False)
    result = build_prompt("CIA triad")
    assert result == _DEFAULT_TEMPLATE.format(file_contents="CIA triad")
    assert result.endswith("CIA triad\n")


def test_explicit_prompt_file(tmp_path, monkeypatch):
    monkeypatch.delenv("PROMPT_FILE", raising=False)
    p = tmp_path / "custom.txt"
    p.write_text("Teach: {file_contents}", encoding="utf-8")
    assert build_prompt("hashing", str(p)) == "Teach: hashing"


def test_env_var_prompt_file(tmp_path, monkeypatch):
    p = tmp_path / "env.txt"
    p.write_text("ENV {file_contents}", encoding="utf-8")
    monkeypatch.setenv("PROMPT_FILE", str(p))
    assert build_prompt("ports") == "ENV ports"


def test_explicit_arg_overrides_env(tmp_path, monkeypatch):
    env_file = tmp_path / "env.txt"
    env_file.write_text("ENV {file_contents}", encoding="utf-8")
    arg_file = tmp_path / "arg.txt"
    arg_file.write_text("ARG {file_contents}", encoding="utf-8")
    monkeypatch.setenv("PROMPT_FILE", str(env_file))
    assert build_prompt("x", str(arg_file)) == "ARG x"


def test_missing_file_raises(tmp_path, monkeypatch):
    monkeypatch.delenv("PROMPT_FILE", raising=False)
    with pytest.raises(FileNotFoundError):
        _load_template(str(tmp_path / "nope.txt"))


def test_directory_raises(tmp_path, monkeypatch):
    monkeypatch.delenv("PROMPT_FILE", raising=False)
    with pytest.raises(ValueError):
        _load_template(str(tmp_path))


def test_empty_env_falls_back_to_default(monkeypatch):
    monkeypatch.setenv("PROMPT_FILE", "")
    assert _load_template(None) == _DEFAULT_TEMPLATE
