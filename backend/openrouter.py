"""
统一模型路由层
支持三种后端：LiteLLM / Agno Agent (OpenAI) / Agno Agent (原生)
"""
import asyncio
import httpx
from typing import List, Dict, Any, Optional
from .config import LITELLM_BASE_URL, LITELLM_API_KEY, AGNO_BASE_URL


def parse_model_id(model: str) -> tuple[str, str]:
    """
    解析模型ID，返回 (类型, 实际ID)
    - "agent:xxx"        → ("agent", "xxx")
    - "agent-native:xxx" → ("agent-native", "xxx")
    - 其他               → ("litellm", model)
    """
    if model.startswith("agent-native:"):
        return "agent-native", model[13:]
    elif model.startswith("agent:"):
        return "agent", model[6:]
    return "litellm", model


async def _query_litellm(
    model: str,
    messages: List[Dict[str, str]],
    timeout: float
) -> Optional[Dict[str, Any]]:
    """调用 LiteLLM OpenAI 兼容接口"""
    url = f"{LITELLM_BASE_URL}/chat/completions"
    headers = {
        "Authorization": f"Bearer {LITELLM_API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {"model": model, "messages": messages}

    async with httpx.AsyncClient(timeout=timeout) as client:
        response = await client.post(url, headers=headers, json=payload)
        response.raise_for_status()
        data = response.json()
        msg = data["choices"][0]["message"]
        return {
            "content": msg.get("content"),
            "reasoning_details": msg.get("reasoning_details"),
        }


async def _query_agno_openai(
    agent_id: str,
    messages: List[Dict[str, str]],
    timeout: float
) -> Optional[Dict[str, Any]]:
    """调用 Agno Agent OpenAI 兼容接口"""
    url = f"{AGNO_BASE_URL}/v1/chat/completions"
    payload = {"model": agent_id, "messages": messages}

    async with httpx.AsyncClient(timeout=timeout) as client:
        response = await client.post(url, json=payload)
        response.raise_for_status()
        data = response.json()
        msg = data["choices"][0]["message"]
        return {
            "content": msg.get("content"),
            "reasoning_details": msg.get("reasoning_details"),
        }


async def _query_agno_native(
    agent_id: str,
    messages: List[Dict[str, str]],
    timeout: float
) -> Optional[Dict[str, Any]]:
    """调用 Agno Agent 原生 runs 接口"""
    url = f"{AGNO_BASE_URL}/agents/{agent_id}/runs"
    # 提取最后一条用户消息
    user_msg = messages[-1]["content"] if messages else ""
    data = {"message": user_msg, "stream": "false"}

    async with httpx.AsyncClient(timeout=timeout) as client:
        response = await client.post(
            url,
            data=data,
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        response.raise_for_status()
        result = response.json()
        return {
            "content": result.get("content"),
            "reasoning_details": result.get("reasoning_content"),
        }


async def query_model(
    model: str,
    messages: List[Dict[str, str]],
    timeout: float = 120.0
) -> Optional[Dict[str, Any]]:
    """
    统一查询接口，根据模型ID自动路由
    """
    model_type, actual_id = parse_model_id(model)

    try:
        if model_type == "agent":
            return await _query_agno_openai(actual_id, messages, timeout)
        elif model_type == "agent-native":
            return await _query_agno_native(actual_id, messages, timeout)
        else:
            return await _query_litellm(actual_id, messages, timeout)
    except Exception as e:
        print(f"[ERROR] 查询 {model} 失败: {e}")
        return None


async def query_models_parallel(
    models: List[str],
    messages: List[Dict[str, str]]
) -> Dict[str, Optional[Dict[str, Any]]]:
    """并行查询多个模型"""
    tasks = [query_model(model, messages) for model in models]
    responses = await asyncio.gather(*tasks)
    return {model: resp for model, resp in zip(models, responses)}
