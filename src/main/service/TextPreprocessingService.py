# src/main/service/MarkdownService.py
from __future__ import annotations

import json
import os
from pathlib import Path
import boto3

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
        self.client = boto3.client("bedrock-runtime", region_name=self.region)


    def preprocess_to_markdown(self, text: str) -> str:
        """
        Apply your prompt (from prompt.md) to the input text via Bedrock Nova Chat,
        returning the model's markdown output as a string.
        """
        instructions = read_prompt(prompt_path=self.prompt_path)
        body = {
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {
                            "text": (
                                f"{instructions.strip()}\n\n"
                                f"{text}"
                            )
                        }
                    ],
                }
            ],
            "inferenceConfig": {
                "maxTokens": 8192,
                "temperature": 0.2,
                "topP": 0.5,
            },
        }

        resp = self.client.invoke_model(
            modelId=self.model_id,
            body=json.dumps(body).encode("utf-8"),
            contentType="application/json",
            accept="application/json",
        )

        payload = json.loads(resp["body"].read())
        blocks = payload["output"]["message"]["content"]
        return "".join(b.get("text", "") for b in blocks).strip()
