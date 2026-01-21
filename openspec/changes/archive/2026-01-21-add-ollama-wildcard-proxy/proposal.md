# Change: Add Wildcard Proxy for Ollama API

## Why
Expose the full Ollama HTTP API through the gateway, including OpenAI-compatible endpoints (`/v1/chat/completions`, `/v1/completions`, `/v1/embeddings`, `/v1/models`). This eliminates the need to manually define each route and provides full API compatibility.

## What Changes
- Replace explicit Ollama routes with a wildcard proxy (`/ollama/{path:path}`)
- Gateway forwards requests to OllamaBackend which proxies to local Ollama server
- All Ollama endpoints become available: native API + OpenAI-compatible API

## Impact
- Affected specs: `ollama-deployment` (add wildcard proxy requirement)
- Affected code:
  - `serve.py` - Replace explicit routes with wildcard proxy
  - `backends/ollama/backend.py` - Add generic proxy method
