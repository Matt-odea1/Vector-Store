"""
AgentCoreProvider.py
Implements LlmProvider using AgentCore runtime.
"""
from typing import List, Dict, Union, Generator
from main.agentcore_setup.bootstrap import get_runtime
from main.agentcore_setup.config import BEDROCK_MODEL_CHAT, BEDROCK_MODEL_EMBED, EMBEDDING_DIM
from main.llm.LlmProvider import LlmProvider
import logging

class LlmError(Exception): pass
class LlmRateLimit(Exception): pass
class LlmTimeout(Exception): pass

class AgentCoreProvider:
    def __init__(self):
        self.client = get_runtime()
        self.logger = logging.getLogger("AgentCoreProvider")

    def generate(self, prompt: str, **kwargs) -> Union[str, Generator[str, None, None]]:
        model_id = BEDROCK_MODEL_CHAT
        try:
            if kwargs.get('stream', False):
                return self._stream('generate', prompt, model_id, **kwargs)
            result = self.client.generate(prompt=prompt, model_id=model_id, **kwargs)
            self.logger.info(f"generate: model={model_id}, tokens={len(prompt.split())}")
            return result['text']
        except Exception as e:
            self.logger.error(f"generate error: {e}")
            raise LlmError(str(e))

    def chat(self, messages: List[Dict], **kwargs) -> Union[str, Generator[str, None, None]]:
        model_id = BEDROCK_MODEL_CHAT
        try:
            if kwargs.get('stream', False):
                return self._stream('chat', messages, model_id, **kwargs)
            result = self.client.chat(messages=messages, model_id=model_id, **kwargs)
            self.logger.info(f"chat: model={model_id}, messages={len(messages)}")
            return result['text']
        except Exception as e:
            self.logger.error(f"chat error: {e}")
            raise LlmError(str(e))

    def embed(self, texts: List[str]) -> List[List[float]]:
        model_id = BEDROCK_MODEL_EMBED
        try:
            result = self.client.embed(texts=texts, model_id=model_id)
            vectors = result['vectors']
            for v in vectors:
                if len(v) != EMBEDDING_DIM:
                    raise LlmError(f"Embedding dim mismatch: expected {EMBEDDING_DIM}, got {len(v)}")
            self.logger.info(f"embed: model={model_id}, texts={len(texts)}")
            return vectors
        except Exception as e:
            self.logger.error(f"embed error: {e}")
            raise LlmError(str(e))

    def _stream(self, mode, data, model_id, **kwargs) -> Generator[str, None, None]:
        # Streaming generator for AgentCore
        try:
            if mode == 'generate':
                stream = self.client.generate_stream(prompt=data, model_id=model_id, **kwargs)
            elif mode == 'chat':
                stream = self.client.chat_stream(messages=data, model_id=model_id, **kwargs)
            else:
                raise LlmError(f"Unknown stream mode: {mode}")
            for delta in stream:
                yield delta['text']
        except Exception as e:
            self.logger.error(f"stream error: {e}")
            raise LlmError(str(e))
