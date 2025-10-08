# src/main/service/MarkdownService.py
from __future__ import annotations

import json
import os
from pathlib import Path

from src.main.llm.AgentCoreProvider import AgentCoreProvider

from ..utils.ReadPrompt import read_prompt

class TextPreprocessingService:
    def __init__(
        self,
        region: str | None = None,
        model_id: str | None = None,
        prompt_path: str | None = None,
    ) -> None:
        self.region = region or os.getenv("AWS_REGION", "ap-southeast-2")
        self.model_id = model_id or os.getenv("CHAT_MODEL", "amazon.nova-lite-v1:0")
        self.prompt_path = Path(prompt_path or os.getenv("PROMPT_MD", "prompt.md")).resolve()
        self.llm = AgentCoreProvider()

    def preprocess_to_markdown(self, text: str, **kwargs) -> str:
        """
        Apply your prompt (from prompt.md) to the input text via Bedrock Nova Chat,
        returning the model's markdown output as a string.
        Supports streaming and other chat options via **kwargs.
        """
        instructions = read_prompt(prompt_path=self.prompt_path)
        prompt = f"{instructions.strip()}\n\n{text}"
        # Use AgentCoreProvider for chat/generate
        result = self.llm.chat([
            {"role": "user", "content": [{"text": prompt}]}
        ], **kwargs)
        if isinstance(result, str):
            return result
        elif hasattr(result, '__iter__') and not isinstance(result, str):
            return "".join(chunk for chunk in result)
        else:
            raise TypeError(f"Unexpected chat return type: {type(result)}")
