"""
memory.py
Stateless and pluggable memory/session interface for AgentCore.
"""
from typing import Any, Dict

class ConversationMemory:
    """
    Stateless by default. Extend for Redis or other backends.
    """
    def __init__(self):
        self.state = {}

    def get_state(self, session_id: str) -> Dict[str, Any]:
        return self.state.get(session_id, {})

    def set_state(self, session_id: str, state: Dict[str, Any]):
        self.state[session_id] = state

    def clear_state(self, session_id: str):
        if session_id in self.state:
            del self.state[session_id]

# Extension point: plug in Redis or other stores here
"""
LlmProvider.py
Abstract base/protocol for LLM operations.
"""
from typing import Protocol, Generator, List, Dict, Union

class LlmProvider(Protocol):
    def generate(self, prompt: str, **kwargs) -> Union[str, Generator[str, None, None]]:
        ...
    def chat(self, messages: List[Dict], **kwargs) -> Union[str, Generator[str, None, None]]:
        ...
    def embed(self, texts: List[str]) -> List[List[float]]:
        ...

