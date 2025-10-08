# Vector-Store

## Overview
A pragmatic MVP for document vector storage and retrieval, built for speed and clarity. Integrates AWS Bedrock AgentCore for all LLM/model operations. Designed for maintainability and rapid iteration.

## Features
- Document upload, listing, and deletion
- Text embedding and vector search
- LLM chat and generation via AgentCoreProvider
- Modular service/controller separation
- Simple config and migration (see MIGRATION.md)
- Thorough test suite (see tests/llm/test_agentcore_provider.py)

## AgentCore Integration
- Uses AgentCoreProvider for all LLM/model calls
- Follows official Bedrock SDK import paths and runtime patterns
- Example usage:

```python
from main.llm.AgentCoreProvider import AgentCoreProvider
llm = AgentCoreProvider()
result = llm.chat([...])
embeddings = llm.embed(["text"])
```

## Directory Structure
- `src/main/agentcore_setup/` – AgentCoreClient, bootstrap, config
- `src/main/llm/` – AgentCoreProvider, LlmProvider
- `src/main/service/` – Vector and text services
- `src/main/controllers/` – API endpoints
- `src/main/utils/` – Prompt and markdown utilities
- `tests/llm/` – LLM and AgentCoreProvider tests

## Configuration & Migration
- See MIGRATION.md for environment/config setup and migration steps
- Uses `.env` for AWS and model settings

## Testing
- Run all tests with:
  ```sh
  PYTHONPATH=src pytest tests/llm/test_agentcore_provider.py -v
  ```
- Test suite uses a fake AgentCore for fast, isolated runs

## Notes
- MVP: prioritises working code, safe defaults, and clarity
- Extend AgentCoreClient for real Bedrock logic as needed
- For advanced usage, see official Bedrock AgentCore docs
