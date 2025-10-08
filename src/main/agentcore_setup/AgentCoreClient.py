"""
AgentCoreClient.py
Thin wrapper exposing generate, chat, embed, and streaming methods for AgentCoreProvider.
"""
from bedrock_agentcore.runtime import BedrockAgentCoreApp

class AgentCoreClient:
    def __init__(self):
        self.app = BedrockAgentCoreApp()
        # TODO: Extend to call actual Bedrock model endpoints via self.app

    def generate(self, prompt, model_id, **kwargs):
        # TODO: Implement actual call to Bedrock model
        raise NotImplementedError("BedrockAgentCoreApp does not expose 'generate' directly. Implement model call here.")

    def chat(self, messages, model_id, **kwargs):
        # TODO: Implement actual call to Bedrock model
        raise NotImplementedError("BedrockAgentCoreApp does not expose 'chat' directly. Implement model call here.")

    def embed(self, texts, model_id):
        # TODO: Implement actual call to Bedrock model
        raise NotImplementedError("BedrockAgentCoreApp does not expose 'embed' directly. Implement model call here.")

    def generate_stream(self, prompt, model_id, **kwargs):
        # TODO: Implement streaming call
        raise NotImplementedError("Streaming not implemented.")

    def chat_stream(self, messages, model_id, **kwargs):
        # TODO: Implement streaming call
        raise NotImplementedError("Streaming not implemented.")

