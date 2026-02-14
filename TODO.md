1 修改API，然后跑通silicon的council
2 litellm路由配置
3 agno agent 配置集成，跑通agentos+openai endpoint；yaml管理提示词
4 llm和agno统一接入agent-council，定下协议，llm/agent (agno sdk/openai sdk)
5 端到端跑通mcp、agno、council启动、前端启动，测试问题
6 提示词增加选择题的格式。方便外部的解析。
7 包装成openai兼容的sdk，可由外部调用，如evalscope评测框架
evalscope/APP应用 ← Agent-Council ← agno agent（openai sdk） ← litellm（silicon/baichuan/glm…）


整体架构
1 搜索工具、网页获取工具以外部项目MCP的形式部署并被接入。√
2 LLM API层使用Litellm来统一部署路由，解决不同源模型的配置问题。
3 Agent使用Agno框架，通过它的AgentOS提供API服务，并且在其中挂载自定义的OpenAI端点，从而和已有的LLM-Council兼容。
4 LLM-Council框架需要修改的地方不多，把OpenRouter改成统一的Openai SDK调用,并且提示词修改支持选择题的答案解析返回；but后期需要对前后端的通信做深入修改，参考Agno的WebUI，把流式输出、工具调用信息，集成到LLM-Council的框架，能够实时的查看Agent的工作状态。
整体架构：Agent-Council←Agno Agent(Openai SDK)←LiteLLM（silicon/baichuan/glm…）
额外：
1 或者可以绕过Openai，直接在Agent-Council里面写个Agno接口兼容的query_agno_agent，从而少一层转发。实现上两个都不难，各有优点，应该评测速度性能，支持配置选择。
2 另外，Agno的prompt通过yaml管理 ，方便版本迭代。
3 LLM-Council得支持两种类型的，一种是原生的llm，一种是Agent，可以同时接入，需要一个配置层。Agent-Council←（LLM/Agent）
