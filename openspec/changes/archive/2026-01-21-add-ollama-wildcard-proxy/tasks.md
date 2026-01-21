## 1. Backend Proxy Method ✅
- [x] 1.1 Add `proxy(method, path, body)` method to `OllamaBackend`
- [x] 1.2 Method forwards request to local Ollama server and returns response

## 2. Gateway Wildcard Route ✅
- [x] 2.1 Remove explicit Ollama routes from `serve.py`
- [x] 2.2 Add wildcard route `/{path:path}` under `/ollama` prefix
- [x] 2.3 Forward GET/POST/DELETE requests to `OllamaBackend().proxy.remote()`

## 3. Validation ✅
- [x] 3.1 Test native Ollama API: `GET /ollama/api/tags`
- [x] 3.2 Test native Ollama API: `POST /ollama/api/generate`
- [x] 3.3 Test OpenAI-compatible: `GET /ollama/v1/models`
- [x] 3.4 Test OpenAI-compatible: `POST /ollama/v1/chat/completions`
