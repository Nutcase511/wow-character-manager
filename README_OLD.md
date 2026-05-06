# 魔兽世界角色管理系统

## 项目简介
用于管理魔兽世界角色信息、副本进度、Boss掉落和装备需求的后台管理系统。

## 技术栈
- **前端**: Vue 3 + Element Plus + TypeScript
- **后端**: Python + FastAPI + MongoDB
- **数据源**: 暴雪游戏数据API

## 功能特性
- 多角色管理
- 副本和Boss信息追踪
- 装备需求管理
- 暴雪官方图标集成
- 进度统计和可视化

## 项目结构
```
wow-character-manager/
├── backend/          # FastAPI后端
├── frontend/         # Vue3前端
└── README.md
```

## 快速开始

### 后端启动
```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload
```

### 前端启动
```bash
cd frontend
npm install
npm run dev
```

## 环境要求
- Python 3.8+
- Node.js 16+
- MongoDB 4.4+