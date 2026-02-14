
LiteLLM 是一个统一的模型接口，可以方便地管理多个模型。如果需要使用 LiteLLM：

```bash
# 安装 LiteLLM
pip install litellm litellm[proxy]

# 启动 LiteLLM 代理服务器
litellm --config config.yaml --port 4000
```

LiteLLM 配置文件示例 (`config.yaml`):

```yaml
model_list:
  - model_name: glm4-flash
    litellm_params:
      model: glm-4-flash
      api_base: http://your-model-api-base-url/v1
      api_key: your-api-key

general_settings:
  master_key: your-master-key  # 可选，用于保护 API
```

测试 LiteLLM 服务：

```bash
curl --location 'http://0.0.0.0:4000/chat/completions' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer your-master-key' \
--data '{
  "model": "glm4-flash",
  "messages": [
    {
      "role": "user",
      "content": "what llm are you"
    }
  ]
}'
```

## LiteLLM 使用说明

### 为什么使用 LiteLLM？

LiteLLM 提供了统一的接口来访问多个不同的 LLM 提供商，包括：
- OpenAI（GPT-3.5, GPT-4）
- Anthropic（Claude）
- Google（Gemini）
- 本地部署的模型（如 GLM-4）
- 以及 100+ 其他模型

使用 LiteLLM 的好处：
1. **统一接口**：不同模型使用相同的 API 格式
2. **动态路由**：可以根据负载或成本自动选择模型
3. **故障转移**：主模型失败时自动切换到备用模型
4. **成本追踪**：自动记录 API 调用成本

### LiteLLM 部署步骤

1. **创建配置文件** (`config/litellm_config.yaml`):

```yaml
model_list:
  # 本地部署的模型
  - model_name: glm4-flash
    litellm_params:
      model: glm-4-flash
      api_base: http://your-glm-api-url/v1
      api_key: your-api-key
  
  # OpenAI 模型（可选）
  - model_name: gpt-4
    litellm_params:
      model: gpt-4
      api_key: sk-your-openai-key
  
  # Anthropic 模型（可选）
  - model_name: claude-3
    litellm_params:
      model: claude-3-opus-20240229
      api_key: sk-ant-your-anthropic-key

# 路由规则（可选）
router_settings:
  fallbacks:
    - gpt-4
    - claude-3

# 限流设置
general_settings:
  max_budget: 100  # 每月最大预算（美元）
  master_key: your-master-key  # API 密钥
```

2. **启动 LiteLLM 代理服务器**:

```bash
litellm --config config/litellm_config.yaml --port 4000 --host 0.0.0.0
```


4. **测试连接**:

```bash
curl --location 'http://localhost:4000/chat/completions' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer your-master-key' \
--data '{
  "model": "glm4-flash",
  "messages": [
    {
      "role": "user",
      "content": "Hello, world!"
    }
  ]
}'
```

### LiteLLM 管理命令

查看 API 使用情况：

```bash
# 查看日志
litellm --config config/litellm_config.yaml --port 4000 --debug

# 查看成本追踪（需要在配置中启用）
# 访问 http://localhost:4000/ui 查看 Dashboard
```

## 故障排除

### API 429 错误

如果遇到 API 429（速率限制）错误：
1. 降低 `--max_concurrent` 参数
2. 降低 `--requests_per_second` 参数（Script 3）
3. 使用 `--sync` 参数切换到同步模式
4. 如果使用 LiteLLM，检查代理服务器的限流设置

### LiteLLM 连接问题

如果无法连接到 LiteLLM 代理：
1. 检查 LiteLLM 服务是否正在运行：`curl http://localhost:4000/health`
2. 检查配置文件路径是否正确
3. 检查端口是否被占用：`lsof -i :4000`
4. 查看 LiteLLM 日志了解详细错误信息

### 空结果

如果某些样本的结果为空：
- 检查提示词文件是否正确
- 检查模型配置是否正确
- 如果使用 LiteLLM，检查代理服务器日志
- 查看日志输出了解详细错误信息

### 内存不足

如果处理大量数据时内存不足：
- 降低 `--max_concurrent` 参数
- 分批处理数据
- 如果使用 LiteLLM，考虑使用多实例负载均衡

