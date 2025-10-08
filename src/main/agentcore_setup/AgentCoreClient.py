"""
AgentCoreClient.py
Thin wrapper exposing generate, chat, embed, and streaming methods for AgentCoreProvider.
"""
from bedrock_agentcore.runtime import BedrockAgentCoreApp
import boto3
import json
import logging

class AgentCoreClient:
    def __init__(self):
        self.app = BedrockAgentCoreApp()
        self.bedrock_client = boto3.client("bedrock-runtime")
        self.logger = logging.getLogger("AgentCoreClient")
        if not self.logger.hasHandlers():
            logging.basicConfig(level=logging.INFO)

    def generate(self, prompt, model_id, **kwargs):
        # TODO: Implement actual call to Bedrock model
        raise NotImplementedError("BedrockAgentCoreApp does not expose 'generate' directly. Implement model call here.")

    def chat(self, messages, model_id, **kwargs):
        self.logger.info(f"chat called with model_id={model_id}")
        self.logger.info(f"messages={messages}")
        # Amazon Titan (nova-lite-v1:0) expects 'messages' API format
        if model_id == "amazon.nova-lite-v1:0":
            # Validate messages structure
            if not messages or not isinstance(messages, list):
                self.logger.error("Nova chat: 'messages' must be a non-empty list.")
                raise ValueError("Nova chat: 'messages' must be a non-empty list.")
            if messages[0].get("role") != "user":
                self.logger.error("Nova chat: First message must have role 'user'.")
                raise ValueError("Nova chat: First message must have role 'user'.")
            payload = json.dumps({"messages": messages})
            self.logger.info(f"Nova payload={payload}")
            try:
                response = self.bedrock_client.invoke_model(
                    modelId=model_id,
                    body=payload,
                    contentType="application/json",
                    accept="application/json"
                )
                body = json.loads(response["body"].read())
                self.logger.info(f"Nova response={body}")
            except Exception as e:
                self.logger.error(f"Nova Bedrock error: {e}")
                raise
            # Nova returns {"output": {"message": {"content": [{"text": "..."}], "role": "assistant"}}}
            if "output" in body and "message" in body["output"]:
                msg = body["output"]["message"]
                if "content" in msg and isinstance(msg["content"], list) and msg["content"]:
                    return {"text": msg["content"][0]["text"]}
            # Legacy/other Nova formats
            elif "outputs" in body and body["outputs"]:
                return {"text": body["outputs"][0]["text"]}
            elif "content" in body and isinstance(body["content"], list):
                return {"text": body["content"][0]["text"]}
            else:
                # NOTE: Unexpected Nova chat response structure
                self.logger.error(f"Unexpected Nova chat response: {body}")
                raise ValueError(f"Unexpected Nova chat response: {body}")
        # Validate messages for non-Titan models
        if not messages or not isinstance(messages, list):
            self.logger.error("Bedrock chat: 'messages' must be a non-empty list.")
            raise ValueError("Bedrock chat: 'messages' must be a non-empty list.")
        payload = json.dumps({"messages": messages})
        self.logger.info(f"Non-Titan payload={payload}")
        try:
            response = self.bedrock_client.invoke_model(
                modelId=model_id,
                body=payload,
                contentType="application/json",
                accept="application/json"
            )
            body = json.loads(response["body"].read())
            self.logger.info(f"Non-Titan response={body}")
        except Exception as e:
            self.logger.error(f"Non-Titan Bedrock error: {e}")
            raise
        if "content" in body and isinstance(body["content"], list):
            return {"text": body["content"][0]["text"]}
        elif "completions" in body and isinstance(body["completions"], list):
            return {"text": body["completions"][0]["data"]["text"]}
        elif "completion" in body:
            return {"text": body["completion"]}
        else:
            self.logger.error(f"Unexpected chat response: {body}")
            raise ValueError(f"Unexpected chat response: {body}")

    def embed(self, texts, model_id):
        # Cohere embedding expects 'texts' key
        if model_id == "cohere.embed-english-v3":
            if not texts or not isinstance(texts, list):
                self.logger.error("Cohere embed: 'texts' must be a non-empty list.")
                raise ValueError("Cohere embed: 'texts' must be a non-empty list.")
            payload = json.dumps({"texts": texts,
                                  "input_type": "search_document"})
            self.logger.info(f"Cohere embed payload={payload}")
            try:
                response = self.bedrock_client.invoke_model(
                    modelId=model_id,
                    body=payload,
                    contentType="application/json",
                    accept="application/json"
                )
                body = json.loads(response["body"].read())
                self.logger.info(f"Cohere embed response={body}")
            except Exception as e:
                self.logger.error(f"Cohere embed Bedrock error: {e}")
                raise
            # Cohere returns {"embeddings": [[...]]}
            if "embeddings" in body and body["embeddings"]:
                return {"vectors": body["embeddings"]}
            else:
                self.logger.error(f"Unexpected Cohere embed response: {body}")
                raise ValueError(f"Unexpected Cohere embed response: {body}")
        # Actual embedding using AWS Bedrock
        vectors = []
        for text in texts:
            payload = json.dumps({"inputText": text})
            response = self.bedrock_client.invoke_model(
                modelId=model_id,
                body=payload,
                contentType="application/json",
                accept="application/json"
            )
            body = json.loads(response["body"].read())
            # Titan returns {"embedding": [...]}, Cohere returns {"embeddings": [[...]]}
            if "embedding" in body:
                vectors.append(body["embedding"])
            elif "embeddings" in body:
                vectors.append(body["embeddings"][0])
            else:
                raise ValueError(f"Unexpected embedding response: {body}")
        return {"vectors": vectors}

    def generate_stream(self, prompt, model_id, **kwargs):
        # TODO: Implement streaming call
        raise NotImplementedError("Streaming not implemented.")

    def chat_stream(self, messages, model_id, **kwargs):
        # TODO: Implement streaming call
        raise NotImplementedError("Streaming not implemented.")
