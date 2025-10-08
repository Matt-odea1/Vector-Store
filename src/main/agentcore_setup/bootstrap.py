"""
bootstrap.py
Initialises AgentCoreClient runtime singleton for use in provider/controller layers.
"""
import os
from .AgentCoreClient import AgentCoreClient  # Use wrapper for runtime
from .config import get_model_config

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

AGENTCORE_CLIENT = None

def get_runtime():
    """
    Returns a singleton AgentCoreClient instance.
    TODO: Inject config/model registry if SDK supports it in future.
    """
    global AGENTCORE_CLIENT
    if AGENTCORE_CLIENT is None:
        AGENTCORE_CLIENT = AgentCoreClient()
    return AGENTCORE_CLIENT
