# src/main/service/ChatService.py
"""
ChatService: Handles chat workflow for /chat endpoint.
- Manages conversation history per session
- Searches vector store for relevant context
- Builds prompt with history and context
- Calls agent client
- Returns answer and metadata
"""
from typing import Optional, List
import uuid
import logging

logger = logging.getLogger(__name__)


class ChatServiceError(Exception):
    pass

DEFAULT_SYSTEM = (
    "You are a helpful AI tutor for programming students. Use the provided context to answer accurately and clearly. "
    "If the context is insufficient, use your knowledge to be helpful while noting any uncertainty. "
    "If asking clarifying questions would be more helpful, do so. "
    "Provide explanations that promote understanding, not just answers. "
    "When referencing previous conversation, be natural and helpful."
)

class ChatService:
    def __init__(
        self,
        vector_service,
        agent_client,
        memory,  # NEW: ConversationMemory instance
        *,
        max_context_chars: int = 8000,
        max_history_messages: int = 10,  # NEW: Limit conversation history
        system_preamble: Optional[str] = None,
    ):
        self.vector_service = vector_service
        self.agent_client = agent_client
        self.memory = memory
        self.max_context_chars = max_context_chars
        self.max_history_messages = max_history_messages
        self.system_preamble = system_preamble or DEFAULT_SYSTEM
        logger.info(f"ChatService initialized with max_context_chars={max_context_chars}, max_history_messages={max_history_messages}")

    def chat(
        self, 
        query: str, 
        top_k: int = 5, 
        session_id: Optional[str] = None,
        include_history: bool = True
    ) -> dict:
        """
        Process a chat query with conversation history and context retrieval.
        
        Args:
            query: User's question
            top_k: Number of context chunks to retrieve
            session_id: Optional session ID (auto-generated if None)
            include_history: Whether to include conversation history
        
        Returns:
            dict with keys: answer, session_id, is_new_session, history_length, 
                           context_ids, tokens_input, tokens_output, model_id
        """
        # Step 1: Handle session ID (hybrid approach)
        if session_id is None:
            session_id = str(uuid.uuid4())
            is_new_session = True
            logger.info(f"Generated new session ID: {session_id[:8]}...")
        else:
            is_new_session = not self.memory.session_exists(session_id)
            if is_new_session:
                logger.info(f"First message for session: {session_id[:8]}...")
            else:
                logger.debug(f"Continuing session: {session_id[:8]}...")
        
        # Step 2: Retrieve conversation history
        history = []
        if include_history and not is_new_session:
            history = self.memory.get_history(session_id, max_messages=self.max_history_messages)
            logger.debug(f"Retrieved {len(history)} previous messages for session {session_id[:8]}...")
        
        # Step 3: Perform vector search for relevant context
        try:
            results = self.vector_service.semantic_search(query=query, top_k=top_k)
            logger.debug(f"Vector search returned {len(results)} results")
        except Exception as e:
            raise ChatServiceError(f"Vector search failed: {e}")
        
        context_chunks = [r["text"] for r in results]
        context_ids = [r["id"] for r in results]
        context_str = "\n---\n".join(context_chunks)
        
        if len(context_str) > self.max_context_chars:
            context_str = context_str[:self.max_context_chars]
            logger.debug(f"Truncated context to {self.max_context_chars} chars")
        
        # Step 4: Build messages with system prompt, history, context, and query
        messages = self._build_messages(query, context_str, history)
        
        # Step 5: Call LLM
        logger.info(f"[ChatService] query='{query[:50]}...', top_k={top_k}, context_len={len(context_str)}, history_len={len(history)}")
        
        try:
            result = self.agent_client.chat(messages)
        except Exception as e:
            raise ChatServiceError(f"Agent call failed: {e}")
        
        # Step 6: Extract answer and metadata
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
        
        # Step 7: Store this conversation exchange in memory
        self.memory.add_message(
            session_id=session_id,
            role="user",
            content=query,
            tokens=tokens_input
        )
        self.memory.add_message(
            session_id=session_id,
            role="assistant",
            content=answer,
            tokens=tokens_output,
            context_ids=context_ids
        )
        
        logger.info(f"Stored conversation exchange in session {session_id[:8]}...")
        
        # Step 8: Return enhanced response
        return {
            "answer": answer,
            "session_id": session_id,
            "is_new_session": is_new_session,
            "history_length": len(history),
            "context_ids": context_ids,
            "tokens_input": tokens_input,
            "tokens_output": tokens_output,
            "model_id": model_id,
        }
    
    def _build_messages(
        self, 
        query: str, 
        context_str: str, 
        history: List[dict]
    ) -> List[dict]:
        """
        Build the messages array for the LLM with proper formatting.
        
        Format:
        - System preamble
        - Conversation history (if any)
        - Document context
        - Current question
        """
        content_parts = []
        
        # 1. System preamble
        content_parts.append({"text": self.system_preamble})
        
        # 2. Add conversation history if present
        if history:
            history_text = self._format_history(history)
            content_parts.append({"text": history_text})
        
        # 3. Add retrieved document context
        if context_str:
            content_parts.append({"text": f"Relevant course materials:\n{context_str}"})
        
        # 4. Add current question
        content_parts.append({"text": f"Current question:\n{query}"})
        
        return [
            {"role": "user", "content": content_parts}
        ]
    
    def _format_history(self, history: List[dict]) -> str:
        """
        Format conversation history for inclusion in prompt.
        """
        if not history:
            return ""
        
        lines = ["Previous conversation in this session:"]
        for msg in history:
            role_label = "Student" if msg["role"] == "user" else "Tutor"
            content = msg["content"]
            # Truncate very long messages to save tokens
            if len(content) > 500:
                content = content[:500] + "..."
            lines.append(f"{role_label}: {content}")
        
        lines.append("")  # Blank line separator
        return "\n".join(lines)
