# Proposal: optimize-gpu-scaling

## Summary
Optimize GPU backend scaling for cost control: downgrade from A100-40GB to A10G (3x cheaper), add `max_containers=1` to prevent parallel scaling, and add gateway-only filters to handle telemetry/token-counting without waking GPU. Target: $40/month budget.

## Motivation
- Current A100-40GB is overkill for 7B quantized models
- No `max_containers` limit allows parallel container scaling during bursts, causing unexpected costs
- Personal use pattern only needs single container during work hours

## Scope
- **In scope:**
  - Downgrade GPU from A100-40GB to A10G
  - Add `max_containers=1` configuration
  - Update config module with new defaults
  - Add gateway filter for `/api/event_logging/*` (telemetry)
  - Add gateway filter for `/v1/messages/count_tokens` (token estimation)
- **Out of scope:**
  - Changing scaledown_window (keep at 300s)

## Approach
1. Add `OLLAMA_MAX_CONTAINERS` environment variable (default: 1)
2. Change `OLLAMA_GPU` default from `A100-40GB` to `A10G`
3. Update `serve.py` to use `max_containers` parameter
4. Add gateway filter for `/api/event_logging/*` - return `{"status": "ok"}` without waking GPU
5. Add gateway filter for `/v1/messages/count_tokens` - estimate tokens (~4 chars/token) without waking GPU

## Cost Analysis

| GPU | $/hr | $40/month = hours |
|-----|------|-------------------|
| A100-40GB (current) | $2.10 | 19 hrs |
| A10G (proposed) | $1.10 | 36 hrs |

With A10G at ~1.5 hrs/day × 20 workdays = ~$33/month ✅

## Risks
- A10G has less VRAM (24GB vs 40GB) - sufficient for 7B Q4/Q8 models but may need upgrade for larger models
- `max_containers=1` means requests queue during high load - acceptable for personal use

## Dependencies
None - standalone change to existing ollama-deployment capability.
