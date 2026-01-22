# Personal Model Garden

Deploy your own AI model garden on [Modal.com](https://modal.com) with a unified API gateway.

- Run open-source LLMs and image generation models
- Pay only for what you use (serverless, per-second billing)
- OpenAI and Anthropic compatible APIs for easy integration
- Works with Claude Code as a custom API provider

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     FastAPI Gateway (CPU)                    │
│                      Always warm, routes requests            │
└─────────────────┬─────────────────────────┬─────────────────┘
                  │                         │
                  ▼                         ▼
┌─────────────────────────────┐ ┌─────────────────────────────┐
│    Ollama Backend (GPU)     │ │   Diffusers Backend (GPU)   │
│    Text generation          │ │   Image generation          │
│    Scales to zero           │ │   Scales to zero            │
└─────────────────────────────┘ └─────────────────────────────┘
```

## Curated Models

### Text Generation (Ollama)

| Model | Quantization | GPU | Notes |
|-------|-------------|-----|-------|
| [glm-4.7-flash](https://ollama.com/library/glm-4.7-flash) | q4_K_M | A10G | Default, good balance of speed and quality |
| [glm-4.7-flash](https://ollama.com/library/glm-4.7-flash) | q8_0 | A10G | Higher quality, larger |

### Image Generation (Diffusers)

| Model | GPU | VRAM | Notes |
|-------|-----|------|-------|
| zai-org/GLM-Image | L40S | ~25GB | Multi-modal capable |
| stabilityai/stable-diffusion-xl-base-1.0 | L40S | ~48GB | Established, high-quality |

## Quick Start

### Prerequisites

- [Modal.com](https://modal.com) account
- Python 3.11+
- `modal` CLI installed

### Deploy

```bash
# 1. Clone the repo
git clone https://github.com/your-username/personal-model-deploy-to-modal.git
cd personal-model-deploy-to-modal

# 2. Install Modal CLI
pip install modal

# 3. Authenticate with Modal
modal setup

# 4. Deploy
modal deploy serve.py
```

### Local Testing

```bash
modal serve serve.py
```

This starts a local dev server with live reload. The URL will be printed to the console.

## API Usage

### Chat Completion (OpenAI-compatible)

```bash
curl https://<your-modal-url>/ollama/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "glm-4.7-flash:q4_K_M",
    "messages": [{"role": "user", "content": "Hello!"}]
  }'
```

> **Note:** `glm-4.7-flash` defaults to `q4_K_M` quantization, so you can also use just `"model": "glm-4.7-flash"`.

### Streaming Chat

```bash
curl https://<your-modal-url>/ollama/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "glm-4.7-flash:q4_K_M",
    "messages": [{"role": "user", "content": "Tell me a story"}],
    "stream": true
  }'
```

### Text Generation (Native Ollama)

```bash
curl https://<your-modal-url>/ollama/api/generate \
  -H "Content-Type: application/json" \
  -d '{
    "model": "glm-4.7-flash:q4_K_M",
    "prompt": "Why is the sky blue?"
  }'
```

### Image Generation

```bash
curl https://<your-modal-url>/diffusers/generate \
  -H "Content-Type: application/json" \
  -d '{
    "model_id": "zai-org/GLM-Image",
    "inputs": "A sunset over mountains",
    "parameters": {
      "height": 1024,
      "width": 1152,
      "num_inference_steps": 30
    }
  }' \
  --output image.png
```

### Anthropic-compatible API

Ollama also supports the Anthropic Messages API format:

```bash
curl https://<your-modal-url>/ollama/v1/messages \
  -H "Content-Type: application/json" \
  -d '{
    "model": "glm-4.7-flash:q4_K_M",
    "max_tokens": 1024,
    "messages": [{"role": "user", "content": "Hello!"}]
  }'
```

### List Available Models

```bash
# Ollama models
curl https://<your-modal-url>/ollama/api/tags

# Diffusers models
curl https://<your-modal-url>/diffusers/models
```

## Claude Code Integration

You can use your Personal Model Garden as a custom API provider for [Claude Code](https://docs.anthropic.com/en/docs/claude-code).

### Setup

Add to your Claude Code configuration (`~/.claude/settings.json`):

```json
{
  "apiProvider": "anthropic-custom",
  "anthropicBaseUrl": "https://<your-modal-url>/ollama",
  "anthropicModelId": "glm-4.7-flash:q4_K_M"
}
```

Or set environment variables:

```bash
export ANTHROPIC_BASE_URL="https://<your-modal-url>/ollama"
export ANTHROPIC_MODEL="glm-4.7-flash:q4_K_M"
```

Then run Claude Code:

```bash
claude
```

Your requests will be routed to your self-hosted model on Modal.

## Configuration

Environment variables can be set in Modal's dashboard or via `modal.Secret`.

### Gateway

| Variable | Default | Description |
|----------|---------|-------------|
| `GATEWAY_MIN_CONTAINERS` | 1 | Minimum warm gateway instances |

### Ollama Backend

| Variable | Default | Description |
|----------|---------|-------------|
| `OLLAMA_MODELS` | `glm-4.7-flash:q4_K_M,glm-4.7-flash:q4_K_M` | Models to preload (comma-separated) |
| `OLLAMA_GPU` | `A10G` | GPU type for Ollama |
| `OLLAMA_MAX_CONTAINERS` | 1 | Max concurrent GPU instances |
| `OLLAMA_SCALEDOWN` | 300 | Seconds before scale to zero |
| `OLLAMA_TIMEOUT` | 1800 | Request timeout in seconds |

### Diffusers Backend

| Variable | Default | Description |
|----------|---------|-------------|
| `DIFFUSERS_L40S_MAX_CONTAINERS` | 1 | Max L40S GPU instances |
| `DIFFUSERS_L40S_SCALEDOWN` | 300 | Seconds before scale to zero |
| `DIFFUSERS_L40S_TIMEOUT` | 1800 | Request timeout in seconds |
| `DIFFUSERS_A10G_MAX_CONTAINERS` | 1 | Max A10G GPU instances |
| `DIFFUSERS_A10G_SCALEDOWN` | 300 | Seconds before scale to zero |
| `DIFFUSERS_A10G_TIMEOUT` | 1800 | Request timeout in seconds |

## API Reference

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | API information |
| `/health` | GET | Gateway health check |
| `/ollama/api/tags` | GET | List Ollama models |
| `/ollama/api/generate` | POST | Generate text (native API) |
| `/ollama/api/chat` | POST | Chat completion (native API) |
| `/ollama/v1/models` | GET | List models (OpenAI-compatible) |
| `/ollama/v1/chat/completions` | POST | Chat completion (OpenAI-compatible) |
| `/ollama/v1/messages` | POST | Messages API (Anthropic-compatible) |
| `/diffusers/models` | GET | List supported image models |
| `/diffusers/generate` | POST | Generate images |

## About Modal

[Modal](https://modal.com) is a serverless platform for running code in the cloud with:

- GPU support (A10G, L40S, H100, etc.)
- Per-second billing
- Automatic scaling to zero
- Simple Python SDK

Learn more at [modal.com/docs](https://modal.com/docs).

## License

MIT
