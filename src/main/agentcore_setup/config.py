"""
config.py
Centralises model IDs, modes, and validation logic for AgentCore.
"""
import os

BEDROCK_MODEL_CHAT = os.getenv('BEDROCK_MODEL_CHAT', 'amazon.nova-lite-v1:0')
BEDROCK_MODEL_EMBED = os.getenv('BEDROCK_MODEL_EMBED', 'amazon.titan-embed-text-v2:0')
EMBEDDING_DIM = int(os.getenv('BEDROCK_EMBED_DIM', '1024'))

MODEL_REGISTRY = {
    'chat': BEDROCK_MODEL_CHAT,
    'embed': BEDROCK_MODEL_EMBED,
}

MODEL_CAPS = {
    'amazon.nova-lite-v1:0': {'mode': 'chat', 'tool_use': True, 'json_mode': True},
    'amazon.titan-embed-text-v2:0': {'mode': 'embed', 'dim': EMBEDDING_DIM},
    # Add more models as needed
}

def get_model_config():
    return MODEL_REGISTRY

def validate_model_cap(model_id: str, cap: str):
    caps = MODEL_CAPS.get(model_id, {})
    if cap not in caps:
        raise ValueError(f"Model {model_id} does not support capability: {cap}")
    return caps[cap]

