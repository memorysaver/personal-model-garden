## ADDED Requirements

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
