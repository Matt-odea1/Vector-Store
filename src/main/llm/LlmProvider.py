"""
LlmProvider.py
Base class for LLM providers. Implements Amazon Bedrock Titan chat logic (MVP).
"""
import logging
import json
import boto3

class LlmProvider:
    """
    LlmProvider for Amazon Bedrock Titan (nova-lite-v1:0).
    Extend for other models/providers as needed.
    """
    def __init__(self, model_id="amazon.nova-lite-v1:0", bedrock_client=None):
        self.model_id = model_id
        self.bedrock_client = bedrock_client or boto3.client("bedrock-runtime")
        self.logger = logging.getLogger("LlmProvider")
        if not self.logger.hasHandlers():
            logging.basicConfig(level=logging.INFO)

    def chat(self, messages):
        """
        Send chat completion request to Titan via Bedrock.
        Args:
            messages (List[Dict]): List of message dicts with 'role' and 'content'.
        Returns:
            str: Model output text.
        """
        self.logger.info(f"LlmProvider.chat called with model_id={self.model_id}")
        self.logger.info(f"messages={messages}")
        # Extract user message from messages
        user_msg = None
        if messages and isinstance(messages, list):
            for m in reversed(messages):
                if m.get("role") == "user" and m.get("content"):
                    content = m["content"]
                    if isinstance(content, list):
                        texts = []
                        for c in content:
                            if isinstance(c, dict) and "text" in c:
                                texts.append(c["text"])
                            elif isinstance(c, str):
                                texts.append(c)
                        user_msg = "\n".join(texts)
                    elif isinstance(content, str):
                        user_msg = content
                    break
        self.logger.info(f"Titan extracted user_msg={user_msg}")
        if not user_msg or not user_msg.strip():
            self.logger.error("Titan chat: Could not extract user message from payload.")
            raise ValueError("Titan chat: Could not extract user message from payload.")
        payload = json.dumps({"inputText": user_msg})
        self.logger.info(f"Titan payload={payload}")
        try:
            response = self.bedrock_client.invoke_model(
                modelId=self.model_id,
                body=payload,
                contentType="application/json",
                accept="application/json"
            )
            body = json.loads(response["body"].read())
            self.logger.info(f"Titan response={body}")
        except Exception as e:
            self.logger.error(f"Titan Bedrock error: {e}")
            raise
        # Titan returns {"results": [{"outputText": "..."}]}
        if "results" in body and body["results"]:
            return body["results"][0]["outputText"]
        else:
            self.logger.error(f"Unexpected Titan chat response: {body}")
            raise ValueError(f"Unexpected Titan chat response: {body}")

# NOTE: Extend this class for other providers/models as needed.
