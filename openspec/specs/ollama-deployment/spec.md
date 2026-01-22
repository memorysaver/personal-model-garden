# ollama-deployment Specification

## Purpose
TBD - created by archiving change add-ollama-deployment. Update Purpose after archive.
## Requirements
### Requirement: Gateway + Backend Architecture
The system SHALL deploy a CPU-based gateway and GPU-based backends as separate Modal classes with independent lifecycles.

#### Scenario: Gateway always warm
- **WHEN** deploying the system
- **THEN** the gateway runs with `min_containers=1`
- **AND** responds instantly to health checks without triggering backend cold starts

#### Scenario: Backend separate lifecycle
- **WHEN** a request arrives for a backend endpoint
- **THEN** the gateway calls the backend via `@modal.method()` RPC
- **AND** the backend container starts if not already running (cold start)
- **AND** the backend scales down after idle timeout (default: 300s)

### Requirement: Ollama Backend
The system SHALL run Ollama as a GPU-based backend with model persistence.

#### Scenario: Multiple models support
- **WHEN** the OllamaBackend container starts
- **THEN** it pulls all models in the configured list (default: `glm-4.7-flash:q8_0,glm-4.7-flash:q4_K_M`)
- **AND** caches them to the `ollama-models` volume

#### Scenario: Model selection in API calls
- **WHEN** a client sends a request to `/ollama/api/generate` or `/ollama/api/chat`
- **THEN** the client specifies the model via the `model` field in the request body
- **AND** the system uses the specified model for inference

### Requirement: Configuration
The system SHALL be configurable via environment variables and config module.

#### Scenario: Backend configuration
- **WHEN** configuring the Ollama backend
- **THEN** `OLLAMA_GPU` controls GPU type (default: A10G)
- **AND** `OLLAMA_MAX_CONTAINERS` controls maximum parallel containers (default: 1)
- **AND** `OLLAMA_SCALEDOWN` controls idle timeout (default: 300s)
- **AND** `OLLAMA_TIMEOUT` controls request timeout (default: 1800s)

#### Scenario: Cost-optimized scaling
- **WHEN** multiple requests arrive simultaneously
- **THEN** the system queues requests to the single container
- **AND** does not spawn additional containers beyond `max_containers` limit

### Requirement: Gateway-Only Endpoints
The gateway SHALL handle certain endpoints directly without waking the GPU backend, to reduce costs.

#### Scenario: Event logging filter
- **WHEN** a request arrives at `/ollama/api/event_logging/*`
- **THEN** the gateway returns `{"status": "ok"}` with status 200
- **AND** does NOT forward the request to the GPU backend

#### Scenario: Token counting filter
- **WHEN** a request arrives at `/ollama/v1/messages/count_tokens`
- **THEN** the gateway estimates token count from message content (~4 chars per token)
- **AND** returns `{"input_tokens": N}` with status 200
- **AND** does NOT forward the request to the GPU backend

### Requirement: Wildcard Proxy
The gateway SHALL proxy all requests under `/ollama/*` to the Ollama backend server (except gateway-only endpoints).

#### Scenario: Native Ollama API
- **WHEN** a request arrives at `/ollama/api/*`
- **THEN** the gateway forwards it to `OllamaBackend().proxy.remote()`
- **AND** returns the Ollama server response unchanged

#### Scenario: OpenAI-compatible API
- **WHEN** a request arrives at `/ollama/v1/*`
- **THEN** the gateway forwards it to `OllamaBackend().proxy.remote()`
- **AND** returns the response in OpenAI-compatible format (handled by Ollama)

#### Scenario: Supported HTTP methods
- **WHEN** a GET, POST, or DELETE request arrives at `/ollama/*`
- **THEN** the gateway forwards the request with method, path, headers, and body
- **AND** returns the response with status code and body

### Requirement: SSE Streaming Support
The gateway SHALL support Server-Sent Events (SSE) streaming for requests with `stream: true`.

#### Scenario: Streaming request detection
- **WHEN** a POST request arrives at `/ollama/*` with `"stream": true` in the body
- **THEN** the gateway routes to the streaming handler
- **AND** uses `.remote_gen()` to stream from the backend generator

#### Scenario: Streaming response format
- **WHEN** a streaming request is processed
- **THEN** the gateway returns `StreamingResponse` with `media_type="text/event-stream"`
- **AND** yields raw bytes from the backend without JSON wrapping
- **AND** sets `Cache-Control: no-cache` and `Connection: keep-alive` headers

#### Scenario: Non-streaming backward compatibility
- **WHEN** a request has `"stream": false` or no `stream` field
- **THEN** the gateway uses `.remote()` (existing behavior)
- **AND** returns `JSONResponse` as before

#### Scenario: Supported streaming endpoints
- **WHEN** streaming is enabled
- **THEN** the following endpoints support SSE:
  - `POST /ollama/api/generate` (native Ollama)
  - `POST /ollama/api/chat` (native Ollama)
  - `POST /ollama/v1/chat/completions` (OpenAI-compatible)
  - `POST /ollama/v1/messages` (Anthropic-compatible)

