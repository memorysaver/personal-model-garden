"""Ollama backend implementation."""

import os
import subprocess
import time

import httpx

from backends.base import BaseBackend
from backends import register_backend
from backends.ollama.config import OllamaConfig


@register_backend
class OllamaService(BaseBackend):
    """Ollama model serving backend - manages local Ollama server."""

    name = "ollama"

    def __init__(self, config: OllamaConfig | None = None, volume=None):
        self.config = config or OllamaConfig()
        self.volume = volume
        self._process = None

    def start(self) -> None:
        """Start Ollama server and pull configured models."""
        # Start ollama serve in background
        self._process = subprocess.Popen(
            ["ollama", "serve"],
            env={**os.environ, "OLLAMA_HOST": "0.0.0.0"},
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        time.sleep(5)

        # Pull models if not already cached
        result = subprocess.run(["ollama", "list"], capture_output=True, text=True)
        pulled_any = False

        for model in self.config.models:
            if model not in result.stdout:
                print(f"Pulling model {model}...")
                subprocess.run(["ollama", "pull", model], check=True)
                pulled_any = True
                print(f"Model {model} pulled.")
            else:
                print(f"Model {model} already cached.")

        # Commit volume if we pulled new models
        if pulled_any and self.volume is not None:
            self.volume.commit()
            print("All new models cached to volume.")

    def health_check(self) -> dict:
        """Check if Ollama server is responding."""
        try:
            with httpx.Client(timeout=5.0) as client:
                response = client.get(f"http://localhost:{self.config.port}/")
                if response.status_code == 200:
                    return {"status": "healthy", "port": self.config.port}
        except Exception as e:
            return {"status": "unhealthy", "error": str(e)}
        return {"status": "unhealthy"}

    # =========================================================================
    # Methods for remote invocation via @modal.method()
    # =========================================================================

    def generate(self, model: str, prompt: str, **kwargs) -> dict:
        """Generate text using Ollama.

        Args:
            model: Model name to use
            prompt: Text prompt for generation
            **kwargs: Additional Ollama options (temperature, top_p, etc.)

        Returns:
            Generation response dict
        """
        with httpx.Client(timeout=600.0) as client:
            response = client.post(
                f"http://localhost:{self.config.port}/api/generate",
                json={"model": model, "prompt": prompt, "stream": False, **kwargs},
            )
            return response.json()

    def chat(self, model: str, messages: list, **kwargs) -> dict:
        """Chat completion using Ollama.

        Args:
            model: Model name to use
            messages: List of message dicts with 'role' and 'content'
            **kwargs: Additional Ollama options

        Returns:
            Chat completion response dict
        """
        with httpx.Client(timeout=600.0) as client:
            response = client.post(
                f"http://localhost:{self.config.port}/api/chat",
                json={"model": model, "messages": messages, "stream": False, **kwargs},
            )
            return response.json()

    def list_models(self) -> dict:
        """List available models.

        Returns:
            Dict with 'models' key containing list of model info
        """
        with httpx.Client(timeout=10.0) as client:
            response = client.get(f"http://localhost:{self.config.port}/api/tags")
            return response.json()

    def show_model(self, name: str) -> dict:
        """Show model information.

        Args:
            name: Model name

        Returns:
            Model information dict
        """
        with httpx.Client(timeout=10.0) as client:
            response = client.post(
                f"http://localhost:{self.config.port}/api/show",
                json={"name": name},
            )
            return response.json()

    def embeddings(self, model: str, input: str | list[str], **kwargs) -> dict:
        """Generate embeddings.

        Args:
            model: Model name to use
            input: Text or list of texts to embed
            **kwargs: Additional options

        Returns:
            Embeddings response dict
        """
        with httpx.Client(timeout=300.0) as client:
            response = client.post(
                f"http://localhost:{self.config.port}/api/embed",
                json={"model": model, "input": input, **kwargs},
            )
            return response.json()

    def proxy(self, method: str, path: str, body: dict | None = None) -> dict:
        """Generic proxy to forward requests to local Ollama server.

        Args:
            method: HTTP method (GET, POST, DELETE)
            path: Request path (e.g., '/api/tags', '/v1/chat/completions')
            body: Request body for POST requests

        Returns:
            Dict with 'status_code' and 'body' from Ollama response
        """
        url = f"http://localhost:{self.config.port}{path}"
        with httpx.Client(timeout=600.0) as client:
            if method == "GET":
                response = client.get(url)
            elif method == "POST":
                response = client.post(url, json=body)
            elif method == "DELETE":
                response = client.delete(url)
            else:
                return {"status_code": 405, "body": {"error": f"Method {method} not allowed"}}

            try:
                return {"status_code": response.status_code, "body": response.json()}
            except Exception:
                return {"status_code": response.status_code, "body": response.text}
