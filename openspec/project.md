# Project Context

## Purpose
Personal platform for deploying and testing state-of-the-art ML models using Modal.com.
Goals:
- Deploy SOTA models for personal use
- Evaluate models against custom criteria
- Maintain cost-effective infrastructure

## Tech Stack
- Python 3.10+
- Modal SDK (serverless GPU compute)
- FastAPI (REST endpoints)
- Pydantic (request/response validation)

## Project Conventions

### Code Style
- Follow PEP 8
- Type hints required for function signatures
- Docstrings for public functions

### Architecture Patterns
- Each model deployment is a separate Modal app
- Shared utilities in `common/` directory
- Configuration via environment variables

### Testing Strategy
- Unit tests for utilities
- Integration tests against deployed endpoints
- Personal benchmarks tracked in results/

### Git Workflow
- Main branch for stable deployments
- Feature branches for new models/capabilities
- Conventional commits (feat:, fix:, docs:)

## Domain Context
- Modal.com provides serverless GPU infrastructure
- Models are deployed as web endpoints or batch jobs
- Focus on inference, not training

## Important Constraints
- Personal use only (not production scale)
- Cost-conscious deployment decisions
- SOTA models selected based on personal benchmarks

## External Dependencies
- Modal.com (compute platform)
- Hugging Face (model weights)
- Model-specific dependencies per deployment
