# Tasks: optimize-gpu-scaling

## Implementation Order

1. [x] **Update config module**
   - Add `OLLAMA_MAX_CONTAINERS` variable (default: 1)
   - Change `OLLAMA_GPU` default from `A100-40GB` to `A10G`
   - File: `config/__init__.py`

2. [x] **Update serve.py imports**
   - Import `OLLAMA_MAX_CONTAINERS` from config
   - File: `serve.py`

3. [x] **Add max_containers to OllamaBackend**
   - Add `max_containers=OLLAMA_MAX_CONTAINERS` to `@app.cls()` decorator
   - File: `serve.py`

4. [x] **Add gateway filter for event_logging**
   - Filter `/api/event_logging/*` requests in gateway
   - Return `{"status": "ok"}` without waking GPU
   - File: `serve.py`

5. [x] **Add gateway filter for token counting**
   - Filter `/v1/messages/count_tokens` requests in gateway
   - Estimate tokens from message content (~4 chars/token)
   - Return `{"input_tokens": N}` without waking GPU
   - File: `serve.py`

6. [x] **Deploy and verify**
   - Run `modal deploy serve.py`
   - Verify container uses A10G GPU
   - Verify gateway filters work correctly

## Validation

- [x] `modal deploy serve.py` succeeds
- [x] App redeployed with new settings (A10G, max_containers=1)
- [x] `/api/event_logging/batch` returns `{"status": "ok"}` from gateway
- [x] `/v1/messages/count_tokens` returns estimated tokens from gateway
- [x] `/v1/messages` correctly proxies to GPU backend
- [x] Streaming mode works correctly
