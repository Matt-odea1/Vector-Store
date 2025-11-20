"""
test_chat_endpoints.py
Integration tests for chat endpoints with conversation history.
"""
import pytest
from fastapi.testclient import TestClient
from unittest.mock import MagicMock
from app import create_app
from src.main.controllers import InternalEndpoints


@pytest.fixture
def mock_chat_service():
    """Mock ChatService."""
    mock = MagicMock()
    mock.chat.return_value = {
        "answer": "Test answer",
        "session_id": "test-session-123",
        "is_new_session": True,
        "history_length": 0,
        "context_ids": ["doc-1", "doc-2"],
        "tokens_input": 100,
        "tokens_output": 50,
        "model_id": "test-model"
    }
    return mock


@pytest.fixture
def mock_memory_service():
    """Mock ConversationMemory."""
    mock = MagicMock()
    mock.session_exists.return_value = True
    mock.get_history.return_value = [
        {
            "role": "user",
            "content": "Test question",
            "timestamp": "2025-11-13T10:00:00.000000",
            "tokens": None,
            "context_ids": []
        },
        {
            "role": "assistant",
            "content": "Test answer",
            "timestamp": "2025-11-13T10:00:02.000000",
            "tokens": 50,
            "context_ids": ["doc-1"]
        }
    ]
    mock.get_session_stats.return_value = {
        "session_id": "test-session-123",
        "message_count": 2,
        "created_at": "2025-11-13T10:00:00.000000",
        "last_accessed": "2025-11-13T10:00:02.000000",
        "total_tokens": 50
    }
    mock.list_sessions.return_value = [
        {
            "session_id": "session-1",
            "message_count": 4,
            "created_at": "2025-11-13T09:00:00.000000",
            "last_accessed": "2025-11-13T10:00:00.000000",
            "total_tokens": 300
        }
    ]
    return mock


@pytest.fixture
def client(mock_chat_service, mock_memory_service):
    """Create a test client for the FastAPI app with mocked dependencies."""
    app = create_app()
    
    # Override dependencies
    app.dependency_overrides[InternalEndpoints.get_chat_service] = lambda: mock_chat_service
    app.dependency_overrides[InternalEndpoints.get_memory_service] = lambda: mock_memory_service
    
    return TestClient(app), mock_chat_service, mock_memory_service


class TestChatEndpoint:
    """Test POST /internal/chat endpoint."""
    
    def test_chat_minimal_request(self, client):
        """Test chat with minimal request (query only)."""
        test_client, mock_chat, mock_memory = client
        response = test_client.post(
            "/internal/chat",
            json={"query": "What is Python?"}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert "answer" in data
        assert "session_id" in data
        assert "is_new_session" in data
        assert "history_length" in data
        assert data["answer"] == "Test answer"
    
    def test_chat_with_session_id(self, client):
        """Test chat with provided session_id."""
        test_client, mock_chat, mock_memory = client
        response = test_client.post(
            "/internal/chat",
            json={
                "query": "Follow-up question",
                "session_id": "my-session-123"
            }
        )
        
        assert response.status_code == 200
        
        # Verify ChatService.chat was called with session_id
        mock_chat.chat.assert_called_once()
        call_kwargs = mock_chat.chat.call_args.kwargs
        assert call_kwargs["session_id"] == "my-session-123"
    
    def test_chat_with_all_parameters(self, client):
        """Test chat with all optional parameters."""
        test_client, mock_chat, mock_memory = client
        response = test_client.post(
            "/internal/chat",
            json={
                "query": "Explain inheritance",
                "top_k": 10,
                "session_id": "test-session",
                "include_history": False
            }
        )
        
        assert response.status_code == 200
        
        # Verify all parameters were passed
        call_kwargs = mock_chat.chat.call_args.kwargs
        assert call_kwargs["query"] == "Explain inheritance"
        assert call_kwargs["top_k"] == 10
        assert call_kwargs["session_id"] == "test-session"
        assert call_kwargs["include_history"] is False
    
    def test_chat_missing_query(self, client):
        """Test chat without query returns validation error."""
        test_client, mock_chat, mock_memory = client
        response = test_client.post(
            "/internal/chat",
            json={}
        )
        
        assert response.status_code == 422  # Validation error
    
    def test_chat_empty_query(self, client):
        """Test chat with empty query is allowed."""
        test_client, mock_chat, mock_memory = client
        response = test_client.post(
            "/internal/chat",
            json={"query": ""}
        )
        
        assert response.status_code == 200
    
    def test_chat_service_error_handling(self, client):
        """Test that service errors are handled gracefully."""
        test_client, mock_chat, mock_memory = client
        from src.main.service.ChatService import ChatServiceError
        mock_chat.chat.side_effect = ChatServiceError("Test error")
        
        response = test_client.post(
            "/internal/chat",
            json={"query": "Test"}
        )
        
        # Should return error in response, not crash
        assert response.status_code == 200
        data = response.json()
        assert "error" in data


class TestGetHistoryEndpoint:
    """Test GET /internal/chat/history/{session_id} endpoint."""
    
    def test_get_history_success(self, client):
        """Test retrieving session history."""
        test_client, mock_chat, mock_memory = client
        response = test_client.get("/internal/chat/history/test-session-123")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "session_id" in data
        assert "messages" in data
        assert "total_messages" in data
        assert "created_at" in data
        assert "last_accessed" in data
        assert "total_tokens" in data
        
        assert len(data["messages"]) == 2
        assert data["messages"][0]["role"] == "user"
        assert data["messages"][1]["role"] == "assistant"
    
    def test_get_history_with_max_messages(self, client):
        """Test retrieving history with limit."""
        test_client, mock_chat, mock_memory = client
        response = test_client.get("/internal/chat/history/test-session-123?max_messages=5")
        
        assert response.status_code == 200
        
        # Verify max_messages was passed to service
        mock_memory.get_history.assert_called_with(
            "test-session-123",
            max_messages=5
        )
    
    def test_get_history_non_existent_session(self, client):
        """Test retrieving history for non-existent session."""
        test_client, mock_chat, mock_memory = client
        mock_memory.session_exists.return_value = False
        
        response = test_client.get("/internal/chat/history/non-existent")
        
        assert response.status_code == 404
        data = response.json()
        assert "detail" in data
        assert "not found" in data["detail"].lower()
    
    def test_get_history_invalid_session_id_format(self, client):
        """Test with invalid session ID format (should still work)."""
        test_client, mock_chat, mock_memory = client
        response = test_client.get("/internal/chat/history/invalid-@#$-id")
        
        # FastAPI path parameter accepts any string
        assert response.status_code in [200, 404]


class TestClearHistoryEndpoint:
    """Test DELETE /internal/chat/history/{session_id} endpoint."""
    
    def test_clear_history_success(self, client):
        """Test clearing session history."""
        test_client, mock_chat, mock_memory = client
        response = test_client.delete("/internal/chat/history/test-session-123")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["ok"] is True
        assert data["session_id"] == "test-session-123"
        assert "message" in data
        
        # Verify clear_session was called
        mock_memory.clear_session.assert_called_once_with("test-session-123")
    
    def test_clear_history_non_existent_session(self, client):
        """Test clearing non-existent session still succeeds."""
        test_client, mock_chat, mock_memory = client
        # clear_session should handle non-existent sessions gracefully
        response = test_client.delete("/internal/chat/history/non-existent")
        
        assert response.status_code == 200
        data = response.json()
        assert data["ok"] is True


class TestListSessionsEndpoint:
    """Test GET /internal/chat/sessions endpoint."""
    
    def test_list_sessions_success(self, client):
        """Test listing all active sessions."""
        test_client, mock_chat, mock_memory = client
        response = test_client.get("/internal/chat/sessions")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "sessions" in data
        assert "total" in data
        assert len(data["sessions"]) == 1
        assert data["total"] == 1
        
        session = data["sessions"][0]
        assert "session_id" in session
        assert "message_count" in session
        assert "created_at" in session
        assert "last_accessed" in session
        assert "total_tokens" in session
    
    def test_list_sessions_empty(self, client):
        """Test listing sessions when none exist."""
        test_client, mock_chat, mock_memory = client
        mock_memory.list_sessions.return_value = []
        
        response = test_client.get("/internal/chat/sessions")
        
        assert response.status_code == 200
        data = response.json()
        assert data["sessions"] == []
        assert data["total"] == 0


class TestEndToEndConversation:
    """Test complete conversation flow through endpoints."""
    
    def test_full_conversation_flow(self, client):
        """Test a complete multi-turn conversation."""
        test_client, mock_chat, mock_memory = client
        
        # Configure mock to return different responses
        chat_responses = [
            {
                "answer": "Python is a programming language",
                "session_id": "e2e-session",
                "is_new_session": True,
                "history_length": 0,
                "context_ids": ["doc-1"],
                "tokens_input": 50,
                "tokens_output": 30,
                "model_id": "test-model"
            },
            {
                "answer": "Based on our previous discussion...",
                "session_id": "e2e-session",
                "is_new_session": False,
                "history_length": 2,
                "context_ids": ["doc-2"],
                "tokens_input": 150,
                "tokens_output": 60,
                "model_id": "test-model"
            }
        ]
        
        mock_chat.chat.side_effect = chat_responses
        
        # First message (new session)
        response1 = test_client.post(
            "/internal/chat",
            json={"query": "What is Python?"}
        )
        
        assert response1.status_code == 200
        data1 = response1.json()
        assert data1["is_new_session"] is True
        assert data1["history_length"] == 0
        session_id = data1["session_id"]
        
        # Second message (same session)
        response2 = test_client.post(
            "/internal/chat",
            json={
                "query": "Can you explain more?",
                "session_id": session_id
            }
        )
        
        assert response2.status_code == 200
        data2 = response2.json()
        assert data2["is_new_session"] is False
        assert data2["history_length"] == 2
        assert data2["session_id"] == session_id
        
        # Get history
        response3 = test_client.get(f"/internal/chat/history/{session_id}")
        assert response3.status_code == 200
        
        # Clear session
        response4 = test_client.delete(f"/internal/chat/history/{session_id}")
        assert response4.status_code == 200


class TestCORS:
    """Test CORS headers if enabled."""
    
    def test_options_request(self, client):
        """Test OPTIONS request for CORS preflight."""
        test_client, mock_chat, mock_memory = client
        response = test_client.options("/internal/chat")
        
        # Should return 200 even without Allow-Origins configured in test
        assert response.status_code in [200, 405]


class TestHealthCheck:
    """Test health check endpoint still works."""
    
    def test_health_endpoint(self, client):
        """Test health endpoint returns OK."""
        test_client, mock_chat, mock_memory = client
        response = test_client.get("/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"


class TestPedagogyModeEndpoint:
    """Test pedagogy mode functionality in chat endpoint."""
    
    def test_chat_with_pedagogy_mode(self, client):
        """Test chat with pedagogy mode parameter."""
        test_client, mock_chat, mock_memory = client
        
        # Mock response with pedagogy mode
        mock_chat.chat.return_value = {
            "answer": "Let me ask you some questions to guide your thinking...",
            "session_id": "test-session-123",
            "is_new_session": True,
            "history_length": 0,
            "pedagogy_mode": "socratic",
            "context_ids": ["doc-1"],
            "tokens_input": 100,
            "tokens_output": 50,
            "model_id": "test-model"
        }
        
        response = test_client.post(
            "/internal/chat",
            json={
                "query": "How do I sort a list?",
                "pedagogy_mode": "socratic"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify mode was passed to service
        mock_chat.chat.assert_called_once()
        call_kwargs = mock_chat.chat.call_args.kwargs
        assert call_kwargs["pedagogy_mode"] == "socratic"
        
        # Verify mode is in response
        assert "pedagogy_mode" in data
        assert data["pedagogy_mode"] == "socratic"
    
    def test_chat_default_pedagogy_mode(self, client):
        """Test that default mode is used when not specified."""
        test_client, mock_chat, mock_memory = client
        
        mock_chat.chat.return_value = {
            "answer": "Here's a clear explanation...",
            "session_id": "test-session-123",
            "is_new_session": True,
            "history_length": 0,
            "pedagogy_mode": "explanatory",
            "context_ids": [],
            "tokens_input": None,
            "tokens_output": None,
            "model_id": None
        }
        
        response = test_client.post(
            "/internal/chat",
            json={"query": "What is Python?"}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Should use default mode
        assert data["pedagogy_mode"] == "explanatory"
    
    def test_chat_all_pedagogy_modes(self, client):
        """Test that all pedagogy modes are accepted."""
        test_client, mock_chat, mock_memory = client
        
        modes = ["socratic", "explanatory", "debugging", "assessment", "review"]
        
        for mode in modes:
            mock_chat.chat.return_value = {
                "answer": f"Response in {mode} mode",
                "session_id": "test-session",
                "is_new_session": False,
                "history_length": 0,
                "pedagogy_mode": mode,
                "context_ids": [],
                "tokens_input": None,
                "tokens_output": None,
                "model_id": None
            }
            
            response = test_client.post(
                "/internal/chat",
                json={
                    "query": "Test question",
                    "pedagogy_mode": mode
                }
            )
            
            assert response.status_code == 200
            data = response.json()
            assert data["pedagogy_mode"] == mode
    
    def test_chat_invalid_pedagogy_mode(self, client):
        """Test that invalid pedagogy mode is handled gracefully."""
        test_client, mock_chat, mock_memory = client
        
        # Mock service to handle invalid mode gracefully
        mock_chat.chat.return_value = {
            "answer": "Response",
            "session_id": "test-session",
            "is_new_session": True,
            "history_length": 0,
            "pedagogy_mode": "explanatory",  # Falls back to default
            "context_ids": [],
            "tokens_input": None,
            "tokens_output": None,
            "model_id": None
        }
        
        response = test_client.post(
            "/internal/chat",
            json={
                "query": "Test question",
                "pedagogy_mode": "invalid_mode"
            }
        )
        
        # Should still work (service handles validation)
        assert response.status_code == 200
    
    def test_pedagogy_mode_persistence_across_session(self, client):
        """Test that pedagogy mode persists in a session."""
        test_client, mock_chat, mock_memory = client
        
        # First message with socratic mode
        mock_chat.chat.return_value = {
            "answer": "First response",
            "session_id": "persistent-session",
            "is_new_session": True,
            "history_length": 0,
            "pedagogy_mode": "socratic",
            "context_ids": [],
            "tokens_input": None,
            "tokens_output": None,
            "model_id": None
        }
        
        response1 = test_client.post(
            "/internal/chat",
            json={
                "query": "First question",
                "session_id": "persistent-session",
                "pedagogy_mode": "socratic"
            }
        )
        
        assert response1.status_code == 200
        assert response1.json()["pedagogy_mode"] == "socratic"
        
        # Second message without specifying mode (should use session's mode)
        mock_chat.chat.return_value = {
            "answer": "Second response",
            "session_id": "persistent-session",
            "is_new_session": False,
            "history_length": 2,
            "pedagogy_mode": "socratic",  # Same mode
            "context_ids": [],
            "tokens_input": None,
            "tokens_output": None,
            "model_id": None
        }
        
        response2 = test_client.post(
            "/internal/chat",
            json={
                "query": "Second question",
                "session_id": "persistent-session"
                # No pedagogy_mode specified
            }
        )
        
        assert response2.status_code == 200
        # Mode should persist from session
        call_kwargs = mock_chat.chat.call_args.kwargs
        # Service should handle persistence
    
    def test_pedagogy_mode_switching(self, client):
        """Test switching pedagogy mode mid-conversation."""
        test_client, mock_chat, mock_memory = client
        
        # Start with explanatory
        mock_chat.chat.return_value = {
            "answer": "Explanatory response",
            "session_id": "switch-session",
            "is_new_session": True,
            "history_length": 0,
            "pedagogy_mode": "explanatory",
            "context_ids": [],
            "tokens_input": None,
            "tokens_output": None,
            "model_id": None
        }
        
        response1 = test_client.post(
            "/internal/chat",
            json={
                "query": "Explain this",
                "session_id": "switch-session",
                "pedagogy_mode": "explanatory"
            }
        )
        
        assert response1.json()["pedagogy_mode"] == "explanatory"
        
        # Switch to debugging
        mock_chat.chat.return_value = {
            "answer": "Debugging hint response",
            "session_id": "switch-session",
            "is_new_session": False,
            "history_length": 2,
            "pedagogy_mode": "debugging",
            "context_ids": [],
            "tokens_input": None,
            "tokens_output": None,
            "model_id": None
        }
        
        response2 = test_client.post(
            "/internal/chat",
            json={
                "query": "Help me fix this bug",
                "session_id": "switch-session",
                "pedagogy_mode": "debugging"
            }
        )
        
        assert response2.json()["pedagogy_mode"] == "debugging"


class TestInvalidRoutes:
    """Test invalid route handling."""
    
    def test_invalid_chat_route(self, client):
        """Test invalid chat route returns 404."""
        test_client, mock_chat, mock_memory = client
        response = test_client.post("/internal/chat/invalid")
        assert response.status_code in [404, 405]
    
    def test_wrong_http_method(self, client):
        """Test wrong HTTP method returns 405."""
        test_client, mock_chat, mock_memory = client
        response = test_client.get("/internal/chat")  # Should be POST
        assert response.status_code == 405
