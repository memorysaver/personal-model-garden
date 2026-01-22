"""Global configuration for the Personal Model Garden."""

import os

# App identity
APP_NAME = "personal-model-garden"

# Gateway settings (CPU, always warm)
GATEWAY_MIN_CONTAINERS = int(os.environ.get("GATEWAY_MIN_CONTAINERS", "1"))

# Ollama backend settings (GPU, separate lifecycle)
OLLAMA_GPU = os.environ.get("OLLAMA_GPU", "A10G")
OLLAMA_MAX_CONTAINERS = int(os.environ.get("OLLAMA_MAX_CONTAINERS", "1"))
OLLAMA_SCALEDOWN = int(os.environ.get("OLLAMA_SCALEDOWN", "300"))
OLLAMA_TIMEOUT = int(os.environ.get("OLLAMA_TIMEOUT", "1800"))
