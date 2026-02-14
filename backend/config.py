"""Configuration for the LLM Council."""

import os
from dotenv import load_dotenv

load_dotenv()

# OpenRouter API key
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

# Council members - list of OpenRouter model identifiers
COUNCIL_MODELS = [
    "Qwen/Qwen3-8B",
    "deepseek-ai/DeepSeek-R1-0528-Qwen3-8B",
    "internlm/internlm2_5-7b-chat",
]
# TODO: Agent:MODEL_ID means the model is used by the agent.

# Chairman model - synthesizes final response
CHAIRMAN_MODEL = "deepseek-ai/DeepSeek-V3.2"
TITLE_MODEL = "internlm/internlm2_5-7b-chat"

# OpenRouter API endpoint
OPENROUTER_API_URL = "https://openrouter.ai/api/v1/chat/completions"

# Data directory for conversation storage
DATA_DIR = "data/conversations"
