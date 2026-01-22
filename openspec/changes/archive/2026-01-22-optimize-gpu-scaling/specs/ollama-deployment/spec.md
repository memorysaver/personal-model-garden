# Spec Delta: ollama-deployment

## MODIFIED Requirements

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

## ADDED Requirements

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
