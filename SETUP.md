# 魔兽世界角色管理系统 - 配置指南

## 系统要求

### 后端
- Python 3.12+

### 前端
- Node.js 16+
- npm

## 安装步骤

### 1. 后端设置
```bash
cd backend
python -m venv venv
venv\Scripts\activate  # Windows
pip install -r requirements.txt
```

数据库使用 SQLite，首次启动时自动创建，无需额外安装。

### 2. 前端设置
```bash
cd frontend
npm install
```

### 3. 配置 WoW 插件路径

启动应用后，进入设置页面配置以下路径：

| 插件 | 文件 | 说明 |
|------|------|------|
| Accountant | Accountant_Classic.lua | 金币统计插件数据文件 |
| tdInspect | tdInspect.lua | 角色装备和天赋数据文件 |
| AtlasLootMY | 插件目录 | 副本掉落数据目录 |

设置页面提供两种配置方式：
1. **自动检测** - 点击"自动检测"按钮，系统自动扫描常见 WoW 安装目录
2. **手动浏览** - 点击路径旁的文件夹图标，通过服务端目录浏览器选择文件

### 4. 启动服务

```bash
# 后端
cd backend
python -m uvicorn main:app --reload

# 前端
cd frontend
npm run dev
```

## 访问地址

- 前端界面: http://localhost:5173
- 后端API文档: http://localhost:8000/docs

## 数据导入流程

1. **导入副本掉落** - 设置页面 → 重新导入副本数据
2. **导入角色信息** - 设置页面 → 重新导入角色数据（tdInspect）
3. **导入金币数据** - 设置页面 → 重新导入金币数据（Accountant）
4. **装备数据** - 角色刷新时自动从 tdInspect 持久化到 character_equipment 表

## 常见问题

### 插件路径配置
- 在设置页面使用"自动检测"功能
- 如果自动检测失败，手动浏览到 `WTF/Account/你的账号/SavedVariables/` 目录选择对应文件
- AtlasLoot 选择的是 AddOns 下的插件目录，不是 SavedVariables 文件

### 前端无法连接后端
- 确保后端服务正在运行（http://localhost:8000）
- 检查 Vite 代理配置（vite.config.ts 中的 proxy 设置）

## 技术栈
- **后端**: Python 3.12 + FastAPI + SQLite (aiosqlite)
- **前端**: Vue 3 + TypeScript + Element Plus + Pinia
- **数据来源**: WoW 插件（tdInspect, Accountant, AtlasLootMY）

## 许可证
MIT License
