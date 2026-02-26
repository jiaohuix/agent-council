#!/bin/bash

# Agent Council - 启动脚本

echo "启动 Agent Council..."
echo ""

# 端口列表
PORTS=(4000 8002 8001 5173)

echo "检查并关闭可能残留的服务进程..."

for PORT in "${PORTS[@]}"; do
    PID=$(lsof -ti tcp:$PORT)
    if [ ! -z "$PID" ]; then
        echo "→ 关闭端口 $PORT 上的进程 $PID"
        kill -9 $PID 2>/dev/null
    fi
done

sleep 2

# 获取脚本所在目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# 激活虚拟环境
if [ -f ".venv/bin/activate" ]; then
    source .venv/bin/activate
    echo "✓ 已激活虚拟环境: $VIRTUAL_ENV"
else
    echo "⚠ 未找到 .venv，使用系统环境"
fi

# 1. 启动 LiteLLM 代理
echo "[1/4] 启动 LiteLLM on http://localhost:4000..."
litellm --config configs/litellm.yaml --port 4000 &

LITELLM_PID=$!
sleep 5

# 2. 启动 Agno Agent 服务
echo "[2/4] 启动 Agno Agent on http://localhost:8002..."
(cd agents && python agno_server.py) &
AGNO_PID=$!
sleep 3

# 3. 启动后端
echo "[3/4] 启动后端 on http://localhost:8001..."
python -m backend.main &
BACKEND_PID=$!
sleep 2

# 4. 启动前端
echo "[4/4] 启动前端 on http://localhost:5173..."
(cd frontend && npm run dev) &
FRONTEND_PID=$!

echo ""
echo "✓ Agent Council 已启动!"
echo "  LiteLLM:  http://localhost:4000"
echo "  Agno:     http://localhost:8002"
echo "  Backend:  http://localhost:8001"
echo "  Frontend: http://localhost:5173"
echo ""
echo "按 Ctrl+C 停止所有服务"

# 捕获退出信号
trap "kill $LITELLM_PID $AGNO_PID $BACKEND_PID $FRONTEND_PID 2>/dev/null; exit" SIGINT SIGTERM
wait
