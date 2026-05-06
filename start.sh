#!/bin/bash

echo "========================================"
echo "魔兽世界角色管理系统"
echo "========================================"
echo ""

echo "[1/2] 启动后端服务..."
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload &
BACKEND_PID=$!
cd ..
echo "后端服务启动成功！http://localhost:8000"
echo ""

echo "[2/2] 启动前端服务..."
cd frontend
if [ ! -d "node_modules" ]; then
    echo "正在安装前端依赖..."
    npm install
fi
npm run dev &
FRONTEND_PID=$!
cd ..
echo "前端服务启动成功！http://localhost:5173"
echo ""

echo "========================================"
echo "系统启动完成！"
echo "后端API文档: http://localhost:8000/docs"
echo "前端界面: http://localhost:5173"
echo "========================================"
echo ""
echo "按 Ctrl+C 停止所有服务"

# 等待两个后台进程
wait $BACKEND_PID $FRONTEND_PID