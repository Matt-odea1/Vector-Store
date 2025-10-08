"""
test_agentcore_provider.py
Unit tests for AgentCoreProvider using a fake AgentCore runtime.
"""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

import pytest
from main.llm.AgentCoreProvider import AgentCoreProvider, LlmError
from main.agentcore_setup.AgentCoreClient import AgentCoreClient

class FakeAgentCore:
    def generate(self, prompt, model_id, **kwargs):
        return {"text": f"FAKE-{prompt}"}
    def chat(self, messages, model_id, **kwargs):
        return {"text": f"FAKE-CHAT-{messages[0]['content'][0]['text']}"}
    def embed(self, texts, model_id):
        return {"vectors": [[0.1] * 1024 for _ in texts]}
    def generate_stream(self, prompt, model_id, **kwargs):
        for word in prompt.split():
            yield {"text": word}
    def chat_stream(self, messages, model_id, **kwargs):
        for word in messages[0]['content'][0]['text'].split():
            yield {"text": word}

class TestAgentCoreClient(AgentCoreClient):
    def generate(self, prompt, model_id, **kwargs):
        return FakeAgentCore().generate(prompt, model_id, **kwargs)
    def chat(self, messages, model_id, **kwargs):
        return FakeAgentCore().chat(messages, model_id, **kwargs)
    def embed(self, texts, model_id):
        return FakeAgentCore().embed(texts, model_id)
    def generate_stream(self, prompt, model_id, **kwargs):
        return FakeAgentCore().generate_stream(prompt, model_id, **kwargs)
    def chat_stream(self, messages, model_id, **kwargs):
        return FakeAgentCore().chat_stream(messages, model_id, **kwargs)

@pytest.fixture(autouse=True)
def patch_agentcore(monkeypatch):
    # Patch AgentCoreClient in bootstrap.py to TestAgentCoreClient
    import main.agentcore_setup.bootstrap
    main.agentcore_setup.bootstrap.AgentCoreClient = TestAgentCoreClient
    # Patch get_runtime to return TestAgentCoreClient
    monkeypatch.setattr("main.agentcore_setup.bootstrap.get_runtime", lambda: TestAgentCoreClient())

@pytest.mark.parametrize("prompt", ["hello world", "test prompt"])
def test_generate(prompt):
    provider = AgentCoreProvider()
    result = provider.generate(prompt)
    assert result.startswith("FAKE-")

@pytest.mark.parametrize("text", ["embed this", "vectorize me"])
def test_embed(text):
    provider = AgentCoreProvider()
    vectors = provider.embed([text])
    assert len(vectors[0]) == 1024

@pytest.mark.parametrize("msg", ["chat here", "talk to me"])
def test_chat(msg):
    provider = AgentCoreProvider()
    result = provider.chat([
        {"role": "user", "content": [{"text": msg}]}
    ])
    assert result.startswith("FAKE-CHAT-")

def test_streaming():
    provider = AgentCoreProvider()
    gen = provider.generate("stream this please", stream=True)
    tokens = list(gen)
    assert tokens == ["stream", "this", "please"]

def test_get_runtime_returns_agentcoreclient():
    """Test that get_runtime returns an AgentCoreClient instance."""
    from main.agentcore_setup.bootstrap import get_runtime
    from main.agentcore_setup.AgentCoreClient import AgentCoreClient
    client = get_runtime()
    assert isinstance(client, AgentCoreClient)
