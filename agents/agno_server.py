"""
Agno Agent Server - 配置化多 Agent 服务
支持 YAML 配置、MCP 工具、OpenAI 兼容接口
"""
import uuid
import time
import logging
import yaml
from pathlib import Path
from typing import Any

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from agno.agent import Agent
from agno.models.openai import OpenAILike
from agno.tools.mcp import MCPTools
from agno.os import AgentOS

# ── 日志配置 ──
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger(__name__)

# ── 配置路径 ──
CONFIG_PATH = Path(__file__).parent.parent / "configs" / "agents.yaml"

# ── LiteLLM 代理配置（统一路由） ──
LITELLM_BASE_URL = "http://0.0.0.0:4000"
LITELLM_API_KEY = "sk-123"


def load_config(path: Path) -> dict:
    """加载 YAML 配置"""
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def normalize_instructions(instructions: Any) -> list[str]:
    """统一提示词为列表格式"""
    if instructions is None:
        return []
    if isinstance(instructions, str):
        return [instructions]
    if isinstance(instructions, list):
        # 展平嵌套列表，处理 YAML 锚点引用
        result = []
        for item in instructions:
            if isinstance(item, str):
                result.append(item)
            elif isinstance(item, list):
                result.extend(item)
        return result
    return [str(instructions)]


def create_mcp_tools(mcp_configs: list[dict]) -> list[MCPTools]:
    """创建 MCP 工具列表，按 URL 去重"""
    seen_urls = set()
    tools = []
    for cfg in mcp_configs or []:
        url = cfg.get("url")
        if url and url not in seen_urls:
            seen_urls.add(url)
            transport = cfg.get("transport", "http")
            # streamable-http 对应 http transport
            if transport == "http":
                transport = "streamable-http"
            elif transport == "sse":
                transport = "sse"
            else:
                logger.warning(f"不支持的 MCP transport: {transport}")
                continue
            tools.append(MCPTools(transport=transport, url=url))
    return tools


def create_llm(model_name: str, settings: dict) -> OpenAILike:
    """创建 LLM 实例，统一走 LiteLLM 代理"""
    return OpenAILike(
        id=model_name,
        api_key=LITELLM_API_KEY,
        base_url=LITELLM_BASE_URL,
        temperature=settings.get("temperature", 0.3),
        top_p=settings.get("top_p", 0.95),
        extra_body=settings.get("extra_body", {}),
    )


def create_agents(config: dict) -> list[Agent]:
    """根据配置创建所有 Agent"""
    agents = []
    default_settings = config.get("model_settings", {}).get("default", {})
    
    for agent_id, agent_cfg in config.get("agents", {}).items():
        # 合并模型设置
        settings = {**default_settings, **agent_cfg.get("model_settings", {})}
        
        # 创建 LLM
        llm = create_llm(agent_cfg.get("model", "gpt-3.5-turbo"), settings)
        
        # 创建 MCP 工具
        mcp_tools = create_mcp_tools(agent_cfg.get("mcps", []))
        
        # 创建 Agent
        agent = Agent(
            name = agent_id,
            id = agent_id,
            model=llm,
            tools=mcp_tools,
            instructions=normalize_instructions(agent_cfg.get("instructions")),
            markdown=True,
        )
        agents.append(agent)
        logger.info(f"创建 Agent: {agent_id}, 模型: {agent_cfg.get('model')}")
    
    return agents


# ── 加载配置并创建 Agents ──
config = load_config(CONFIG_PATH)
agents = create_agents(config)
agent_map = {a.id: a for a in agents}

# ── FastAPI 应用 ──
app = FastAPI(title="Agno Agent Server")


# ── OpenAI 兼容接口 ──
class ChatRequest(BaseModel):
    model: str
    messages: list[dict]
    stream: bool = False


@app.get("/v1/models")
async def list_models():
    """列出所有可用的 Agent（作为模型）"""
    return {
        "object": "list",
        "data": [
            {"id": aid, "object": "model", "owned_by": "agno"}
            for aid in agent_map.keys()
        ]
    }


@app.post("/v1/chat/completions")
async def chat_completions(request: ChatRequest):
    """OpenAI 兼容的 chat completions 接口
    TODO:
    1 支持多轮对话
    2 支持stream
    """
    agent = agent_map.get(request.model)
    if not agent:
        raise HTTPException(404, f"Agent '{request.model}' 不存在")
    
    # 提取用户消息(最后一条)
    user_msg = request.messages[-1]["content"] if request.messages else ""
    logger.info(f"[{request.model}] 请求: {user_msg[:100]}...")
    
    # 调用 Agent
    response = await agent.arun(user_msg)
    content = response.content or ""
    
    return {
        "id": f"chatcmpl-{uuid.uuid4().hex[:12]}",
        "object": "chat.completion",
        "created": int(time.time()),
        "model": request.model,
        "choices": [{
            "index": 0,
            "message": {"role": "assistant", "content": content},
            "finish_reason": "stop",
        }],
        "usage": {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0},
    }


# ── AgentOS 集成 ──
agent_os = AgentOS(
    agents=agents,
    base_app=app,
    on_route_conflict="preserve_base_app",
)
app = agent_os.get_app()

if __name__ == "__main__":
    agent_os.serve(app="agno_server:app", host="0.0.0.0", port=8002, reload=False)

