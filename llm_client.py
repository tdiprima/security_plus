"""LLM backend seam: protocol + Ollama adapter."""

import logging
from typing import Protocol

import requests

logger = logging.getLogger(__name__)


class LLMClient(Protocol):
    def generate(self, prompt: str) -> str:
        ...


class OllamaClient:
    """Adapter for the Ollama /api/generate endpoint."""

    def __init__(self, model: str, url: str, timeout: int):
        self._model = model
        self._url = url
        self._timeout = timeout

    def generate(self, prompt: str) -> str:
        payload = {"model": self._model, "prompt": prompt, "stream": False}
        logger.info("Sending request to %s using model '%s'...", self._url, self._model)

        try:
            response = requests.post(self._url, json=payload, timeout=self._timeout)
            response.raise_for_status()
        except requests.ConnectionError as exc:
            raise ConnectionError(
                f"Cannot connect to Ollama at {self._url}. Is Ollama running?"
            ) from exc
        except requests.Timeout as exc:
            raise TimeoutError(
                f"Request timed out after {self._timeout}s. "
                "Try increasing --timeout or using a smaller input file."
            ) from exc
        except requests.HTTPError as exc:
            raise RuntimeError(
                f"Ollama returned HTTP {response.status_code}: {response.text}"
            ) from exc

        data = response.json()
        text = data.get("response", "").strip()

        if not text:
            raise ValueError("Ollama returned an empty response. Check the model and input.")

        logger.info("Received %d characters from Ollama", len(text))
        return text
