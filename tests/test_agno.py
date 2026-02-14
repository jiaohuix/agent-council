"""
Agno Agent 测试脚本
测试 AgentOS runs 接口和 OpenAI 兼容接口
"""
import asyncio
import httpx

# Agno 服务地址
AGNO_BASE_URL = "http://0.0.0.0:8002"
AGENT_ID = "web_search_agent"
TEST_MESSAGE = "你好，介绍一下你自己"


async def test_agno_runs():
    """测试 AgentOS 原生 /agents/{agent_id}/runs 接口"""
    print("=" * 50)
    print("测试 AgentOS runs 接口")
    print("=" * 50)
    
    url = f"{AGNO_BASE_URL}/agents/{AGENT_ID}/runs"
    data = {
        "message": TEST_MESSAGE,
        "stream": "false",
    }
    
    async with httpx.AsyncClient(timeout=60.0) as client:
        response = await client.post(
            url,
            data=data,  # form-urlencoded 格式
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        print(f"状态码: {response.status_code}")
        print(f"响应:\n{response.text[:500]}...")


async def test_openai_models():
    """测试 OpenAI 兼容 /v1/models 接口"""
    print("\n" + "=" * 50)
    print("测试 OpenAI /v1/models 接口")
    print("=" * 50)
    
    url = f"{AGNO_BASE_URL}/v1/models"
    
    async with httpx.AsyncClient(timeout=10.0) as client:
        response = await client.get(url)
        print(f"状态码: {response.status_code}")
        print(f"响应: {response.json()}")


async def test_openai_chat():
    """测试 OpenAI 兼容 /v1/chat/completions 接口"""
    print("\n" + "=" * 50)
    print("测试 OpenAI /v1/chat/completions 接口")
    print("=" * 50)
    
    url = f"{AGNO_BASE_URL}/v1/chat/completions"
    payload = {
        "model": AGENT_ID,
        "messages": [
            {"role": "user", "content": TEST_MESSAGE}
        ]
    }
    
    async with httpx.AsyncClient(timeout=60.0) as client:
        response = await client.post(
            url,
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        print(f"状态码: {response.status_code}")
        data = response.json()
        print(f"模型: {data.get('model')}")
        print(f"内容: {data['choices'][0]['message']['content'][:500]}...")


async def main():
    """运行所有测试"""
    await test_openai_models()
    await test_openai_chat()
    await test_agno_runs()


if __name__ == "__main__":
    asyncio.run(main())

