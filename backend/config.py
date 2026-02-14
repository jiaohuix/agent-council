"""Configuration for the LLM Council."""

import os
from dotenv import load_dotenv

load_dotenv()

# ── LiteLLM 配置（统一 LLM 路由） ──
LITELLM_BASE_URL = os.getenv("LITELLM_BASE_URL", "http://0.0.0.0:4000")
LITELLM_API_KEY = os.getenv("LITELLM_API_KEY", "sk-123")

# ── Agno Agent 配置 ──
AGNO_BASE_URL = os.getenv("AGNO_BASE_URL", "http://0.0.0.0:8002")

# ── 模型ID格式约定 ──
# "agent:xxx"        → Agno Agent (OpenAI兼容接口)
# "agent-native:xxx" → Agno Agent (原生runs接口)
# 其他               → LiteLLM 普通模型

# Council 成员 - 支持混合 LLM 和 Agent
COUNCIL_MODELS = [
    "glm4-flash",                    # LiteLLM 模型
    "agent:web_search_agent",        # Agno Agent (OpenAI接口)
    # "agent-native:web_search_agent", # Agno Agent (原生接口)
]

# 主席模型 - 生成最终回复
CHAIRMAN_MODEL = "glm4-flash"
TITLE_MODEL = "agent-native:web_search_agent"

# 数据存储目录
DATA_DIR = "data/conversations"
