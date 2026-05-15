# 魔兽世界角色管理系统 (WoW Character Manager)

专为魔兽世界时光服（WotLK 3.3.5）设计的角色和装备管理系统。

## 核心功能
- 多角色管理 - 从 tdInspect 插件同步角色信息
- 副本/Boss 追踪 - 从 AtlasLootMY 插件导入掉落数据
- 装备需求追踪 - 用户手动记录装备需求和获取进度
- 装备展示 - 从 tdInspect/暴雪 API 获取并持久化装备数据
- 套装收集进度 - 自动解析并展示角色套装收集情况
- 金币追踪 - 从 Accountant 插件导入金币数据
- 天赋模拟 - 天赋树展示和配点方案保存

## 技术栈

### 后端
- **Python 3.12** + **FastAPI**
- **SQLite** (aiosqlite 异步驱动)
- **Pydantic v2** 数据验证

### 前端
- **Vue 3** + **TypeScript**
- **Element Plus** 组件库
- **Pinia** 状态管理
- **ECharts** 图表
- **Vite** 构建

## 数据流

所有游戏数据来自插件导入或网络爬取，页面不提供手动创建入口。
例外：装备需求清单、天赋配点方案、系统设置允许手动 CRUD。

| 数据 | 来源 | 导入方式 |
|------|------|----------|
| 副本/Boss/掉落 | AtlasLootMY 插件 | AtlasLoot 导入端点 |
| 角色信息 | tdInspect 插件 | 角色刷新端点 |
| 装备 | tdInspect / 暴雪API | 装备同步/导入 |
| 金币 | Accountant 插件 | 金币刷新端点 |
| 天赋 | 数据网站 | import_talents.py |

## 快速开始

### 环境要求
- Python 3.12+
- Node.js 16+

### 安装步骤

#### 1. 后端设置
```bash
cd backend
python -m venv venv
venv\Scripts\activate  # Windows
pip install -r requirements.txt
```

#### 2. 前端设置
```bash
cd frontend
npm install
```

#### 3. 配置 WoW 插件路径
启动应用后，在设置页面：
- 点击"自动检测"自动查找 WoW 安装目录
- 或手动浏览选择各插件的 SavedVariables 文件路径

#### 4. 启动服务
```bash
# 后端
cd backend
python -m uvicorn main:app --reload

# 前端
cd frontend
npm run dev
```

#### 5. 访问应用
- 前端界面: http://localhost:5173
- 后端API文档: http://localhost:8000/docs

## 项目结构
```
wow-character-manager/
├── backend/              # 后端服务
│   ├── app/api/          # API路由
│   ├── app/core/         # 配置和数据库
│   ├── app/models/       # Pydantic模型
│   ├── import_*.py       # 各种数据导入脚本
│   └── main.py           # 应用入口
├── frontend/             # 前端应用
│   ├── src/views/        # 页面组件
│   ├── src/stores/       # 状态管理
│   └── src/api/          # API封装
└── README.md
```

## 许可证
MIT License
