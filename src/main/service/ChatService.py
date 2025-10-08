# src/main/service/ChatService.py
"""
ChatService: Handles chat workflow for /chat endpoint.
- Searches vector store for relevant context
- Builds prompt
- Calls agent client
- Returns answer and metadata
"""
from typing import Optional, List

class ChatServiceError(Exception):
    pass

DEFAULT_SYSTEM = (
    "You are a helpful assistant. Use the provided context to answer accurately and concisely. "
    "If the context is insufficient, say so."
)

class ChatService:
    def __init__(
        self,
        vector_service,
        agent_client,
        *,
        max_context_chars: int = 8000,
        system_preamble: Optional[str] = None,
    ):
        self.vector_service = vector_service
        self.agent_client = agent_client
        self.max_context_chars = max_context_chars
        self.system_preamble = system_preamble or DEFAULT_SYSTEM

    def chat(self, query: str, top_k: int = 5, session_id: Optional[str] = None) -> dict:
        """
        Returns dict with keys: answer, context_ids, tokens_input, tokens_output, model_id.
        """
        try:
            results = self.vector_service.semantic_search(query=query, top_k=top_k)
        except Exception as e:
            raise ChatServiceError(f"Vector search failed: {e}")
        context_chunks = [r["text"] for r in results]
        context_ids = [r["id"] for r in results]
        context_str = "\n---\n".join(context_chunks)
        if len(context_str) > self.max_context_chars:
            context_str = context_str[:self.max_context_chars]
        # Agent expects message content as a list of dicts with only 'text' key
        user_content = [
            {"text": self.system_preamble},
            {"text": f"Context:\n{context_str}"},
            {"text": f"Question:\n{query}"}
        ]
        messages = [
            {"role": "user", "content": user_content},
        ]
        # NOTE: Logging (minimal)
        print(f"[ChatService] query='{query[:50]}', top_k={top_k}, results={len(results)}, context_len={len(context_str)}")
        try:
            result = self.agent_client.chat(messages)
        except Exception as e:
            raise ChatServiceError(f"Agent call failed: {e}")
        # Handle string or dict response
        if isinstance(result, str):
            answer = result
            tokens_input = None
            tokens_output = None
            model_id = None
        elif isinstance(result, dict):
            answer = result.get("content") or result.get("answer") or ""
            tokens_input = result.get("tokens_input")
            tokens_output = result.get("tokens_output")
            model_id = result.get("model_id")
        else:
            answer = str(result)
            tokens_input = None
            tokens_output = None
            model_id = None
        return {
            "answer": answer,
            "context_ids": context_ids,
            "tokens_input": tokens_input,
            "tokens_output": tokens_output,
            "model_id": model_id,
        }
