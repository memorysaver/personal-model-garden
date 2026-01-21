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

#### Scenario: Gateway configuration
- **WHEN** configuring the gateway
- **THEN** `GATEWAY_MIN_CONTAINERS` controls warm pool size (default: 1)

#### Scenario: Backend configuration
- **WHEN** configuring the Ollama backend
- **THEN** `OLLAMA_GPU` controls GPU type (default: A100-40GB)
- **AND** `OLLAMA_SCALEDOWN` controls idle timeout (default: 300s)
- **AND** `OLLAMA_TIMEOUT` controls request timeout (default: 1800s)

<!-- Note: Original proposal mentioned OpenAI-compatible API, separate directories, and ollama-<model> naming.
     These were descoped in favor of: native Ollama API, unified backends/ structure, and personal-model-garden app name. -->

### Requirement: Wildcard Proxy
The gateway SHALL proxy all requests under `/ollama/*` to the Ollama backend server.

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

