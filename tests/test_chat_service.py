# tests/test_chat_service.py
"""
Unit tests for ChatService
"""
import pytest
from src.main.service.ChatService import ChatService, ChatServiceError

class DummyVectorService:
    def semantic_search(self, query, top_k=5):
        if query == "fail":
            raise Exception("Vector fail")
        return [
            {"id": "c1", "text": "context1", "score": 0.9},
            {"id": "c2", "text": "context2", "score": 0.8},
        ]

class DummyAgentClient:
    def chat(self, messages):
        if messages[1]["content"].endswith("fail"):
            raise Exception("Agent fail")
        return {
            "content": "answer text",
            "tokens_input": 10,
            "tokens_output": 5,
            "model_id": "test-model"
        }

def test_chat_success():
    svc = ChatService(DummyVectorService(), DummyAgentClient())
    result = svc.chat("hello", top_k=2)
    assert result["answer"] == "answer text"
    assert result["context_ids"] == ["c1", "c2"]
    assert result["tokens_input"] == 10
    assert result["tokens_output"] == 5
    assert result["model_id"] == "test-model"

def test_vector_error():
    svc = ChatService(DummyVectorService(), DummyAgentClient())
    with pytest.raises(ChatServiceError):
        svc.chat("fail")

def test_agent_error():
    class BadAgent:
        def chat(self, messages):
            raise Exception("Agent fail")
    svc = ChatService(DummyVectorService(), BadAgent())
    with pytest.raises(ChatServiceError):
        svc.chat("hello")

def test_context_truncation():
    class LongVector:
        def semantic_search(self, query, top_k=5):
            return [{"id": "c1", "text": "x"*9000, "score": 1.0}]
    svc = ChatService(LongVector(), DummyAgentClient(), max_context_chars=8000)
    result = svc.chat("hello")
    assert len(result["answer"]) > 0

